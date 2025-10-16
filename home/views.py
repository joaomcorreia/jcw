from django.shortcuts import render
from django.http import HttpResponse
from .models import PageContent
import django

def home(request):
    """Homepage view with tenant-aware dynamic content"""
    tenant = getattr(request, 'tenant', None)
    
    try:
        # Get tenant-specific content first, then fall back to global content
        page_content = None
        
        if tenant:
            # Try to get tenant-specific content
            page_content = PageContent.objects.filter(
                tenant=tenant, is_active=True
            ).first()
        
        # If no tenant-specific content, try global content
        if not page_content:
            page_content = PageContent.objects.filter(
                tenant=None, is_active=True
            ).first()
        
        if page_content:
            title = page_content.title
            message = page_content.message
        else:
            # Use tenant branding if available
            if tenant:
                title = tenant.site_title or f"Welcome to {tenant.name}"
                message = tenant.site_tagline or "This is your custom multi-tenant homepage!"
            else:
                title = "Welcome to My Django Project"
                message = "This is your custom homepage! Configure content in the admin panel."
    except Exception as e:
        # Fallback if database is not ready or model doesn't exist yet
        title = "Welcome to My Django Project"
        message = "This is your custom homepage!"
    
    return render(request, 'home/index.html', {
        'title': title,
        'message': message,
        'tenant': tenant,
        'django_version': django.get_version()
    })
