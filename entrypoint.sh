#!/bin/sh

set -e

echo "[INFO] Making migrations ..."
python manage.py makemigrations

echo "[INFO] Running migrations ..."
python manage.py migrate


echo "[INFO] Starting dev server ..."
exec "$@"