#!/bin/sh
# Starts the backend for the end-to-end tests: production settings, a
# throwaway database and media folder, the demo bakery, and the built
# storefront (frontend/dist) served by Django itself.
set -e
PORT="${1:-8765}"
FRONTEND="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$(mktemp -d)"
PYTHON="${PYTHON:-python}"

if [ ! -f "$FRONTEND/dist/index.html" ]; then
  echo "Build the storefront first: npm run build" >&2
  exit 1
fi

export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY="e2e-only-not-a-secret-0123456789abcdefghijklmnopqrstuvwxyz"
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
export DJANGO_SECURE_SSL_REDIRECT=False
export DATABASE_URL="sqlite:///$DATA/db.sqlite3"
export DJANGO_MEDIA_ROOT="$DATA/media"
export FRONTEND_DIST_DIR="$FRONTEND/dist"
export FRONTEND_INDEX_FILE="$FRONTEND/dist/index.html"
export FRONTEND_URL="http://localhost:$PORT"
export DJANGO_LOG_LEVEL=WARNING
# Every day open, so there are always pickup times to choose.
export SHOP_OPENING_HOURS="mon-sun 00:00-23:30"

cd "$FRONTEND/../backend"
"$PYTHON" manage.py migrate --noinput -v0
"$PYTHON" manage.py seed_demo \
  --customer "$(node -p "require('$FRONTEND/e2e/account.cjs').email")" \
  --password "$(node -p "require('$FRONTEND/e2e/account.cjs').password")"
exec "$PYTHON" manage.py runserver "127.0.0.1:$PORT" --noreload
