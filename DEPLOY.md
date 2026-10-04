# Going live

The shop runs as one Docker image: Django serves the API, every storefront
page (with its title and share preview filled in for search engines) and,
through WhiteNoise, the built storefront files. Postgres keeps the data and
Caddy adds HTTPS and serves uploaded photos and 3D models.

```
browser ── Caddy (HTTPS, /media) ── web: Django + gunicorn ── Postgres
```

## 1. Server

Any small Linux server with Docker works (2 GB RAM is plenty), e.g. Hetzner
in Germany. Point the domain's DNS `A` record (and `www`) at the server.

## 2. Settings

```bash
git clone https://github.com/abdullahbakir97/baeckrei.git && cd baeckrei
cp .env.production.example .env.production
```

- Put `SITE_DOMAIN=backlover.de` in a file called `.env` next to
  `docker-compose.yml`.
- Fill in `.env.production`: at least a long random `POSTGRES_PASSWORD`,
  `DJANGO_SECRET_KEY` and the email server, so customers get their order
  confirmations. Opening hours, delivery fee and the shop's details are set
  later in the admin (*Settings*); the `SHOP_*` values are only the defaults
  until then.

Neither file is committed.

## 3. Start

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

`createsuperuser` creates the bakery's admin account. Caddy fetches the HTTPS
certificate on first start. The shop's admin is at `/admin` – everything the
bakery manages day to day is there, including the journal, messages,
newsletter, ingredients, settings and the menu screens (see
docs/menu-board.md). Django's own admin at `DJANGO_ADMIN_PATH` is only for
the developer.

To update later: `git pull && docker compose up -d --build` (migrations run
on start).

## 4. Online payment (Stripe)

1. Create a Stripe account and switch on the payment methods you want
   (cards, Apple Pay, Google Pay, PayPal, Klarna …) under *Settings → Payment
   methods*.
2. *Developers → API keys*: copy the secret key into `STRIPE_SECRET_KEY`.
3. *Developers → Webhooks → Add endpoint*:
   `https://<your domain>/api/orders/payments/stripe/webhook/` with the events
   `checkout.session.completed`, `checkout.session.async_payment_succeeded`,
   `checkout.session.async_payment_failed` and `checkout.session.expired`.
   Copy its signing secret into `STRIPE_WEBHOOK_SECRET`.
4. `docker compose up -d` again. "Pay online" now appears at checkout.

Test first with the *test mode* keys (`sk_test_…`) and card `4242 4242 4242 4242`.

How it works: the order is placed and its stock reserved, the customer pays
on Stripe's page, and Stripe tells the shop through the webhook; only then is
the order marked paid and confirmed by email. An unpaid order is canceled
automatically when the payment page expires (30 minutes) and its stock goes
back. Canceling a paid order refunds it.

## 5. Email

Any SMTP provider works (e.g. the one of your email host, Brevo, Postmark).
Set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` and
`DEFAULT_FROM_EMAIL`. `SHOP_NOTIFICATION_EMAIL` receives an email for every
new order (and contact form messages). The admin also shows new orders live,
with a sound and, if allowed, a desktop notification.

## 6. Optional

- **Error reports:** set `SENTRY_DSN` (sentry.io, EU region available).
- **Uploads in a bucket** instead of on the server: set the `AWS_*` values for
  any S3-compatible storage (AWS, Hetzner Object Storage, Cloudflare R2). The
  bucket must be publicly readable and allow `GET` from your domain (CORS), so
  the 3D viewer can load `.glb` models:

  ```json
  [{ "AllowedOrigins": ["https://backlover.de"], "AllowedMethods": ["GET"], "AllowedHeaders": ["*"] }]
  ```

## Backups

```bash
docker compose exec db pg_dump -U backlover backlover > backup-$(date +%F).sql
docker run --rm -v baeckrei_media:/media -v "$PWD":/out alpine tar czf /out/media-$(date +%F).tgz -C /media .
```

## Before opening the doors

- [ ] Admin → Settings: address, contact, legal details (Impressum), opening
      hours, closing days, pickup and delivery; the legal pages reviewed
- [ ] A test order with each payment method, and the emails arrive
- [ ] `DJANGO_SECURE_HSTS_SECONDS` set once HTTPS works
- [ ] The menu screens set up on the shop's TVs (docs/menu-board.md)
