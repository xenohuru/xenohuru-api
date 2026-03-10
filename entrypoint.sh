#!/bin/bash
set -e

# Always ensure /data/ exists and seed chui.db on first deploy
# (safe: only copies if /data/chui.db doesn't already exist)
mkdir -p /data
if [ ! -f /data/chui.db ]; then
    if [ -f /app/chui.db ]; then
        echo "==> Seeding /data/chui.db from committed database..."
        cp /app/chui.db /data/chui.db
    else
        echo "==> WARNING: /app/chui.db not found — Django will create a fresh database."
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
