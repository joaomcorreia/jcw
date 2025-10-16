from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

class Tenant(models.Model):
    """Model for tenant/client management"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    domain = models.CharField(max_length=255, unique=True, help_text="Primary domain for this tenant")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tenant branding
    site_title = models.CharField(max_length=200, default="My Site")
    site_tagline = models.CharField(max_length=300, blank=True)
    
    # Homepage preview
    homepage_screenshot = models.ImageField(
        upload_to='tenant_screenshots/',
        blank=True,
        null=True,
        help_text="Homepage preview thumbnail (recommended: 400x300px)"
    )
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.domain})"
    
    def get_frontend_url(self):
        """Get the full URL to the tenant's frontend"""
        protocol = 'https' if not self.domain.endswith('.localhost') else 'http'
        port = ':8000' if self.domain.endswith('.localhost') else ''
        return f"{protocol}://{self.domain}{port}/"
    
    def get_admin_preview_html(self):
        """Generate HTML for admin preview"""
        if self.homepage_screenshot:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" alt="Homepage Preview" style="max-width: 200px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px;"><br>'
                '<small>Homepage Preview</small>'
                '</div>',
                self.homepage_screenshot.url
            )
        return format_html(
            '<div style="text-align: center; padding: 20px; border: 1px dashed #ccc; color: #666;">'
            'No preview available<br><small>Upload a screenshot</small>'
            '</div>'
        )
    get_admin_preview_html.short_description = "Homepage Preview"

class TenantDomain(models.Model):
    """Additional domains that can be used for a tenant"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['domain']
        
    def __str__(self):
        return self.domain

class TenantUser(models.Model):
    """Associates users with tenants"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'tenant']
        
    def __str__(self):
        return f"{self.user.username} @ {self.tenant.name}"
