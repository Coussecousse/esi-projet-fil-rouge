#!/bin/bash
set -e

# Extract DB_HOST and DB_PORT from DATABASE_URL if set
if [ -n "$DATABASE_URL" ]; then
  DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
  DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
fi

echo "Waiting for PostgreSQL at ${DB_HOST:-db-patient}:${DB_PORT:-5432}..."
while ! nc -z ${DB_HOST:-db-patient} ${DB_PORT:-5432}; do
  sleep 0.5
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
