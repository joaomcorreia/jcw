#!/usr/bin/env bash
# build.sh - Render.com build script

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create default tenants (if needed)
python manage.py setup_tenants || echo "Tenants already exist"

# Create superuser if it doesn't exist
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF