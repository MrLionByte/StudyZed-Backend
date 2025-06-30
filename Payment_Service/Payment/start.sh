#!/bin/bash

# Run migrations
python manage.py migrate

# Start Gunicorn in background
gunicorn Payment.wsgi:application --bind 0.0.0.0:8008 &

# Start consumer
python manage.py consume_messages

# Wait for background processes (optional)
wait
