#!/bin/bash

# Wait for database to be ready (if we add one later)
# sleep 5

# Apply database migrations (if we add a database later)
python manage.py migrate

# Create superuser if not exists
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py createsuperuser --noinput
fi

# Start server
exec "$@"
