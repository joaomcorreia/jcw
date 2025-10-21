# Render.com Deployment Configuration
# Use production settings and increase workers for better performance

web: gunicorn myproject.wsgi:application --workers 3 --timeout 60 --keep-alive 2