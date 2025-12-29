#!/bin/sh
# Exit immediately if a command fails
set -e

echo "Running Django migrations..."
python manage.py migrate

echo "Seeding database..."
python manage.py seed_database

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django server..."
# Start your server (adjust port as needed)
gunicorn gezamko.wsgi:application --bind 0.0.0.0:8000
