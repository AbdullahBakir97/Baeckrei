# Print and social designs

The printed menu, flyers, poster, social posts and the customer guide, in
German (`de`) and Arabic (`ar`). They are HTML templates that Chromium turns
into print-ready PDFs and PNGs, so changing a price or a text is a one-line
edit followed by a rebuild.

| File (in `dist/<de or ar>/`) | What it is | Size |
|---|---|---|
| `speisekarte-a4.pdf` | Menu, front and back | A4 + 3 mm bleed (216 × 303 mm) |
| `flyer-a5.pdf` | "Order online" flyer, front and back | A5 + 3 mm bleed (154 × 216 mm) |
| `postkarte-a6.pdf` | Breakfast offer postcard, front and back | A6 + 3 mm bleed (111 × 154 mm) |
| `plakat-a3.pdf` | Window poster | A3 + 3 mm bleed (303 × 426 mm) |
| `kundeninfo-a4.pdf` | 16-page customer guide with a screenshot of every page of the website | A4 (210 × 297 mm) |
| `handbuch-a4.pdf` | 20-page owner handbook: orders, products, menu board, settings, with screenshots of the admin | A4 (210 × 297 mm) |
| `social-post.png` | Instagram / Facebook post | 1080 × 1350 px |
| `social-story.png` | Instagram / WhatsApp story | 1080 × 1920 px |

`dist/previews/` has a small JPEG of every page for a quick look.

## Before printing

Everything printed comes from `data/`. Check these first:

- `data/shop.mjs`: **website** (printed and used for every QR code), address
  with postcode, opening hours, delivery fee and lead times. Keep the hours
  and fees the same as the server settings (`SHOP_OPENING_HOURS`,
  `SHOP_DELIVERY_FEE`).
- `data/menu.mjs`: products, descriptions and **prices**. The prices in the
  repository are examples.
- `data/offers.mjs`: the breakfast offer on the postcard (price, contents,
  when it is valid).
- `data/copy.mjs`: all other texts in both languages; `data/handbook.mjs`
  holds the owner handbook.

## Build

```bash
cd frontend
npx playwright install chromium   # once
npm run marketing                  # everything, both languages
npm run marketing -- --lang ar --only menu,guide
```

`--only` takes `menu`, `flyer`, `postcard`, `poster`, `guide`, `handbook`,
`post` and `story`.

## Screenshots for the customer guide

The guide uses the screenshots in `assets/screens/`. Take new ones after the
website changes. Start the shop (with products and a customer account that
has placed an order), then:

```bash
npm run marketing:screens -- --base http://localhost:5173 --email kunde@example.com --password '...'
npm run marketing -- --only guide
```

For the owner handbook, sign in with a superuser instead (this also captures
Django's admin, at `--api`, default `http://localhost:8000`):

```bash
npm run marketing:screens -- --base http://localhost:5173 --admin-email inhaber@example.com --admin-password '...'
```

The two email pictures (`admin-email-*.jpg`) are screenshots of the order
emails from `backend/apps/orders/templates/orders/email/`.

The Arabic guide and handbook show the English website and admin, since the
shop itself is in German and English.

## Notes for the print shop

- The PDFs are RGB with 3 mm bleed on every side and no crop marks. Text and
  important content stay well inside the trimmed edge.
- The customer guide and the handbook have no bleed: they are meant for
  screens, email and office printers.
- To keep the files light and smooth to scroll, the build scales pictures to
  300 dpi (print) or 150 dpi (guide and handbook) and turns soft gradients
  and shadows into plain images. `dist/previews/` shows the design as
  written.
- Fonts are embedded (Instrument Serif and Manrope, El Messiri and IBM Plex
  Sans Arabic for Arabic).
- Suggested paper: menu 300 g/m² matte (or laminated), flyer and postcard
  170–350 g/m², poster 170 g/m² glossy.
