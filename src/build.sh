#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=cofig.settings

python src/manage.py collectstatic --no-input
python src/manage.py migrate
