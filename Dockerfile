# Backlover: one image with the API and the storefront. See DEPLOY.md.

# 1. Build the storefront
FROM node:22-alpine AS storefront
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
# Public address, for canonical links and share previews.
ARG VITE_SITE_URL=
ARG VITE_SPLINE_SCENE=
ENV VITE_SITE_URL=$VITE_SITE_URL VITE_SPLINE_SCENE=$VITE_SPLINE_SCENE
RUN npm run build

# 2. Django serves the API, the storefront pages (with their meta tags filled
#    in) and, through WhiteNoise, the storefront's files.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY backend/requirements.txt backend/requirements-prod.txt ./
RUN pip install -r requirements-prod.txt
COPY backend/ ./
COPY --from=storefront /app/frontend/dist /app/storefront
ENV FRONTEND_DIST_DIR=/app/storefront \
    FRONTEND_INDEX_FILE=/app/storefront/index.html \
    DJANGO_MEDIA_ROOT=/data/media
RUN DJANGO_SECRET_KEY=collectstatic-only python manage.py collectstatic --noinput \
    && useradd --create-home --uid 1000 app \
    && mkdir -p /data/media \
    && chown -R app /data
USER app
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn project.wsgi --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout 60 --access-logfile -"]
