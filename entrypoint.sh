#!/bin/bash
set -e

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
