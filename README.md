# Baeckrei

> Bakery management system — production scheduling, recipe-driven inventory deduction, customer accounts, online orders. Django + Vue 3.

> **Status:** Built end-to-end for a real bakery client; the client closed the business before launch. It is not live and is not used by any bakery.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Stars](https://img.shields.io/github/stars/AbdullahBakir97/Baeckrei?style=flat-square&color=FFD700) ![Forks](https://img.shields.io/github/forks/AbdullahBakir97/Baeckrei?style=flat-square&color=blue) ![Last commit](https://img.shields.io/github/last-commit/AbdullahBakir97/Baeckrei?style=flat-square)

---

## Overview

Bakery management system — production scheduling, recipe-driven inventory deduction, customer accounts, online orders. Django + Vue 3.

## Tech stack

- **Language:** Python
- **Tags:** bakery, django, inventory-management, pos, python, vue3

## Quick start

```bash
git clone https://github.com/AbdullahBakir97/Baeckrei.git
cd Baeckrei/backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env         # sets DJANGO_DEBUG=True for local development
python manage.py migrate
python manage.py seed_demo        # optional: a few demo categories and products
python manage.py createsuperuser
python manage.py runserver
```

Frontend (in a second terminal):

```bash
cd Baeckrei/frontend
npm ci
npm run dev
```

Tests:

```bash
cd backend && pytest apps/orders/ apps/cart/tests/test_cart_api.py   # see .github/workflows/ci.yml
cd frontend && npm run build && npm run test:e2e                     # browser tests (Playwright)
```

Deploying (Docker, Postgres, HTTPS, Stripe, email): see [DEPLOY.md](DEPLOY.md).

## Topics

`bakery` · `django` · `inventory-management` · `pos` · `python` · `vue3`

## Author

**Abdullah Bakir** — [@AbdullahBakir97](https://github.com/AbdullahBakir97)

Full-Stack Developer based in Germany - Python · Django · Vue · Nuxt.

## License

[MIT](LICENSE)
