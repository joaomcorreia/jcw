# tenants/models.py - Django-Tenants Compatible Model
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django_tenants.models import TenantMixin, DomainMixin


class Tenant(TenantMixin):
    """
    Django-Tenants compatible tenant model for SaaS multi-tenancy
    Each tenant gets its own PostgreSQL schema
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=63, unique=True)  # PostgreSQL schema name limit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tenant branding
    site_title = models.CharField(max_length=200, default="My Site")
    site_tagline = models.CharField(max_length=300, blank=True)
    
    # Owner relationship
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_tenants',
        null=True, 
        blank=True
    )
    
    # Subscription/Plan info
    plan = models.CharField(
        max_length=50, 
        choices=[
            ('free', 'Free'),
            ('starter', 'Starter'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='free'
    )
    
    # Homepage preview
    homepage_screenshot = models.ImageField(
        upload_to='tenant_screenshots/',
        blank=True,
        null=True,
        help_text="Homepage preview thumbnail (recommended: 400x300px)"
    )
    
    # Auto-created tenants are active by default
    auto_create_schema = True
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.schema_name})"
    
    def get_frontend_url(self):
        """Get the full URL to the tenant's frontend"""
        domain = self.domains.filter(is_primary=True).first()
        if domain:
            protocol = 'https' if not domain.domain.endswith('.localhost') else 'http'
            port = ':8000' if domain.domain.endswith('.localhost') else ''
            return f"{protocol}://{domain.domain}{port}/"
        return None
    
    def get_admin_preview_html(self):
        """Generate HTML for admin preview with connect button"""
        preview_html = ""
        
        if self.homepage_screenshot:
            preview_html += format_html(
                '<div style="text-align: center; margin-bottom: 10px;">'
                '<img src="{}" alt="Homepage Preview" style="max-width: 200px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px;"><br>'
                '<small>Homepage Preview</small>'
                '</div>',
                self.homepage_screenshot.url
            )
        
        # Add connect button
        frontend_url = self.get_frontend_url()
        if frontend_url:
            preview_html += format_html(
                '<div style="text-align: center; margin-top: 10px;">'
                '<a href="{}" target="_blank" class="btn btn-primary" style="background: #417690; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">'
                '🌐 Connect to Frontend'
                '</a>'
                '</div>',
                frontend_url
            )
        
        return preview_html or format_html(
            '<div style="text-align: center; padding: 20px; border: 1px dashed #ccc; color: #666;">'
            'No preview available<br>'
            '<small>Upload a homepage screenshot</small>'
            '</div>'
        )


class Domain(DomainMixin):
    """
    Domain model for django-tenants
    Each tenant can have multiple domains
    """
    pass


class TenantUser(models.Model):
    """
    Many-to-many relationship between tenants and users
    Allows users to access multiple tenants with different roles
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='tenant_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_memberships')
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Administrator'),
            ('member', 'Member'),
            ('viewer', 'Viewer'),
        ],
        default='member'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('tenant', 'user')
        
    def __str__(self):
        return f"{self.user.username} - {self.tenant.name} ({self.role})"