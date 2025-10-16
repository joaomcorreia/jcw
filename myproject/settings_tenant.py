# myproject/settings_tenant.py - Django-Tenants Configuration
"""
Django-Tenants settings for SaaS multi-tenancy
This extends your existing settings with tenant-specific configuration
"""
from .settings import *

# Django-Tenants Configuration
INSTALLED_APPS = [
    'django_tenants',  # Must be first
] + INSTALLED_APPS

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
] + MIDDLEWARE

# Database configuration for django-tenants
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

# Tenant configuration
TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"

# Shared apps (available to all tenants)
SHARED_APPS = [
    'django_tenants',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your tenant management
    'tenants',
]

# Tenant-specific apps (isolated per tenant)
TENANT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Your tenant-specific apps
    'home',
]

# Auto-create tenant on user registration
AUTO_CREATE_TENANT = True

# Base domain for subdomains
TENANT_BASE_DOMAIN = 'localhost'  # Change to your domain in production

# Public schema name (for shared data)
PUBLIC_SCHEMA_NAME = 'public'

# Tenant URL routing
PUBLIC_SCHEMA_URLCONF = 'myproject.urls_public'  # Landing page, registration, etc.
ROOT_URLCONF = 'myproject.urls'  # Tenant-specific URLs

# Cache configuration for multi-tenancy
CACHES = {
    'default': {
        'BACKEND': 'django_tenants.cache.backends.redis.RedisTenantCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'KEY_PREFIX': 'tenant',
    }
} if 'redis' in locals() else {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'tenant': {
            'format': '[{asctime}] {levelname} [{name}] [Schema: {tenant_schema}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'tenant',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'tenant.log',
            'formatter': 'tenant',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'tenants': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Production settings for django-tenants
if not DEBUG:
    # Use Redis for caching in production
    CACHES['default'] = {
        'BACKEND': 'django_tenants.cache.backends.redis.RedisTenantCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'KEY_PREFIX': 'tenant',
    }
    
    # Update base domain for production
    TENANT_BASE_DOMAIN = os.environ.get('TENANT_BASE_DOMAIN', 'jcwtradehub.com')
    
    # Secure tenant isolation
    TENANT_LIMIT_SET_CALLS = True
    TENANT_MULTIPROCESSING_MAX_PROCESSES = 2