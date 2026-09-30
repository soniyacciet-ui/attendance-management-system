#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser automatically if it doesn't exist
if [ "$CREATE_SUPERUSER" = "true" ]; then
    python manage.py createsuperuser --no-input || true
fi