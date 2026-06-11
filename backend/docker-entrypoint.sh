#!/usr/bin/env sh
# Entrypoint backend. Les migrations / collectstatic ne s'exécutent que dans le
# service `api` (RUN_MIGRATIONS=1) pour éviter les courses entre conteneurs.
set -e

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  echo "[entrypoint] migrations base métier (default)…"
  python manage.py migrate --noinput
  echo "[entrypoint] migrations base télémétrie (timescale, hypertable)…"
  python manage.py migrate --database=telemetry --noinput
  echo "[entrypoint] collectstatic…"
  python manage.py collectstatic --noinput
  # Superuser initial (optionnel) — voir DJANGO_SUPERUSER_* dans .env
  if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo "[entrypoint] création superuser (si absent)…"
    python manage.py createsuperuser --noinput 2>/dev/null || true
  fi
fi

exec "$@"
