#!/bin/sh

# Run makemigrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Start Gunicorn in background
gunicorn Usermanagement.wsgi:application --bind 0.0.0.0:8005 &

# Wait for background processes
wait
