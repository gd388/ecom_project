#!/usr/bin/env bash
python manage.py collectstatic --noinput || true
exec "$@"
