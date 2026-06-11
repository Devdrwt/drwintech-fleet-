# ============================================================
# Drwintech Fleet — Backend Django/DRF (api ASGI, celery, ws-bridge)
# Sert HTTP + WebSocket via daphne (channels). Image = ghcr.io/devdrwt/fleet_back
# ============================================================
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# curl : healthchecks. psycopg[binary] embarque sa propre libpq.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Utilisateur non-root (sécurité — voir SECURITY.md)
RUN chmod +x docker-entrypoint.sh \
    && useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/staticfiles \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# L'entrypoint applique migrations + collectstatic si RUN_MIGRATIONS=1 (service api).
ENTRYPOINT ["./docker-entrypoint.sh"]

# Défaut : serveur ASGI (HTTP + WebSocket). celery/ws-bridge surchargent `command`.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
