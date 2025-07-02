#!/bin/bash

# Run makemigrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Start Gunicorn in background
gunicorn Session_And_Task_Management.wsgi:application --bind 0.0.0.0:8009 &

# Wait for background processes
wait
