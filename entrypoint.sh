#!/bin/bash
set -e

# If ON_BACK4APP is set, ensure /data/ exists and seed chui.db from the
# committed copy at /app/chui.db (only on first deploy — never overwrites existing data)
if [ "${ON_BACK4APP}" = "True" ] || [ "${ON_BACK4APP}" = "true" ] || [ "${ON_BACK4APP}" = "1" ]; then
    mkdir -p /data
    if [ ! -f /data/chui.db ]; then
        echo "==> Seeding /data/chui.db from committed database..."
        cp /app/chui.db /data/chui.db
    fi
fi

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
exec gunicorn cofig.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 3 \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile -
