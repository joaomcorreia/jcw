# myproject/urls_public.py - Public Schema URLs (Landing page, registration, etc.)
"""
Public schema URLs - served on the main domain
Handles landing page, user registration, tenant selection, etc.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views_public

urlpatterns = [
    # Admin for managing tenants (public schema)
    path('admin/', admin.site.urls),
    
    # Landing page and authentication
    path('', views_public.landing_page, name='landing_page'),
    path('register/', views_public.register_view, name='register'),
    path('login/', views_public.login_view, name='login'),
    path('logout/', views_public.logout_view, name='logout'),
    
    # Tenant management
    path('my-sites/', views_public.my_tenants_view, name='my_tenants'),
    path('create-site/', views_public.create_tenant_view, name='create_tenant'),
    
    # API endpoints
    path('api/check-availability/', views_public.check_domain_availability, name='check_availability'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)