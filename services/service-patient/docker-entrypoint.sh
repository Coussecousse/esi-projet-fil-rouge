#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
python manage.py migrate --noinput

# Create superuser if needed
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@medisecure.com', 'Admin123!')
    print('Superuser created')
END

exec "$@"
