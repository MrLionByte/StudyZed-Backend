# Exit on errors
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start consuming messages in the background
echo "Starting message consumer..."
python manage.py consume_messages.py &

# Start Daphne server
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8006 Message_Video.asgi:application
