from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import uuid

class WebsiteProject(models.Model):
    """
    Core model for user's website projects
    Each project represents a website being built
    """
    WEBSITE_TYPES = [
        ('ecommerce', '🏪 E-Commerce Store'),
        ('business', '💼 Business Website'),
        ('blog', '📝 Blog & Personal'),
        ('portfolio', '🎨 Portfolio & Creative'),
        ('agency', '📊 Agency & Marketing'),
        ('education', '🎓 Education & Courses'),
        ('restaurant', '🍕 Restaurant & Food'),
        ('real_estate', '🏠 Real Estate'),
        ('nonprofit', '🤝 Non-Profit'),
        ('other', '🔧 Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft - Building'),
        ('preview', 'Preview - Ready to Review'),
        ('published', 'Published - Live'),
        ('archived', 'Archived'),
    ]
    
    # Basic Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='websites')
    name = models.CharField(max_length=100, help_text="Website name (e.g., 'Sweet Bakery')")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    # Website Configuration  
    website_type = models.CharField(max_length=20, choices=WEBSITE_TYPES)
    ai_description = models.TextField(
        help_text="Tell us about your business - AI will use this to build your site"
    )
    
    # Business Address Information
    business_address_line1 = models.CharField(max_length=255, blank=True, help_text="Street address")
    business_address_line2 = models.CharField(max_length=255, blank=True, help_text="Apartment, suite, etc. (optional)")
    business_city = models.CharField(max_length=100, blank=True, help_text="City")
    business_state = models.CharField(max_length=100, blank=True, help_text="State/Province")
    business_postal_code = models.CharField(max_length=20, blank=True, help_text="Postal/ZIP code")
    business_country = models.CharField(max_length=100, blank=True, default='United States', help_text="Country")
    
    # Generated Content
    ai_generated_data = models.JSONField(
        default=dict,
        help_text="AI-generated website structure, content, and suggestions"
    )
    custom_modifications = models.JSONField(
        default=dict,
        help_text="User's custom changes to AI-generated content"
    )
    
    # Status & Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Branding & SEO
    brand_colors = models.JSONField(
        default=dict,
        help_text="Primary and secondary colors for the website"
    )
    logo_url = models.URLField(blank=True, help_text="URL to uploaded logo")
    favicon_url = models.URLField(blank=True, help_text="URL to uploaded favicon")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while WebsiteProject.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL to edit/preview this website"""
        return reverse('website_builder:edit', kwargs={'slug': self.slug})
    
    def get_live_url(self):
        """URL where this website is published"""
        try:
            domain = self.domain
            if domain.is_active:
                protocol = 'https' if domain.ssl_enabled else 'http'
                return f"{protocol}://{domain.domain_name}/"
        except WebsiteDomain.DoesNotExist:
            pass
        return None


class WebsiteDomain(models.Model):
    """
    Domain configuration for each website
    Handles subdomains, custom domains, and purchased domains
    """
    DOMAIN_TYPES = [
        ('subdomain', '🆓 Free Subdomain (sitename.justcodeworks.eu)'),
        ('purchased', '🛒 Purchased Domain (sitename.com)'),
        ('custom', '🔗 Custom Domain (bring your own)'),
    ]
    
    REGISTRATION_STATUS = [
        ('pending', 'Pending Registration'),
        ('registering', 'Registration in Progress'),
        ('registered', 'Successfully Registered'),
        ('active', 'Active & Live'),
        ('expired', 'Expired'),
        ('failed', 'Registration Failed'),
    ]
    
    website = models.OneToOneField(WebsiteProject, on_delete=models.CASCADE, related_name='domain')
    domain_type = models.CharField(max_length=20, choices=DOMAIN_TYPES)
    domain_name = models.CharField(max_length=255, unique=True)
    
    # Domain Status
    is_active = models.BooleanField(default=False)
    ssl_enabled = models.BooleanField(default=True)
    registration_status = models.CharField(max_length=20, choices=REGISTRATION_STATUS, default='pending')
    
    # DNS & Technical
    dns_configured = models.BooleanField(default=False)
    nameservers = models.JSONField(default=list, help_text="DNS nameservers")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.domain_name} ({self.get_domain_type_display()})"
    
    @property
    def is_subdomain(self):
        return self.domain_type == 'subdomain'
    
    @property
    def is_custom_domain(self):
        return self.domain_type in ['purchased', 'custom']


class WebsiteContent(models.Model):
    """
    Page content for each website
    Stores the actual page content, SEO data, etc.
    """
    PAGE_TYPES = [
        ('home', 'Homepage'),
        ('about', 'About Us'),
        ('services', 'Services'),
        ('products', 'Products'),
        ('portfolio', 'Portfolio'),
        ('blog', 'Blog'),
        ('contact', 'Contact'),
        ('custom', 'Custom Page'),
    ]
    
    website = models.ForeignKey(WebsiteProject, on_delete=models.CASCADE, related_name='pages')
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES)
    page_slug = models.CharField(max_length=100)
    page_title = models.CharField(max_length=200)
    
    # Content Structure
    content_blocks = models.JSONField(
        default=list,
        help_text="Page content as structured blocks (hero, text, gallery, etc.)"
    )
    
    # SEO
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(max_length=500, blank=True)
    seo_keywords = models.TextField(blank=True)
    
    # Page Settings
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['website', 'page_slug']
        ordering = ['sort_order', 'page_title']
        
    def __str__(self):
        return f"{self.website.name} - {self.page_title}"
    
    def get_absolute_url(self):
        """URL to this page on the live website"""
        base_url = self.website.get_live_url()
        if base_url:
            if self.page_slug == 'home':
                return base_url
            return f"{base_url}{self.page_slug}/"
        return None


class DomainOrder(models.Model):
    """
    Tracks domain purchases and payments
    Handles the commercial aspect of domain registration
    """
    PAYMENT_STATUS = [
        ('pending', 'Payment Pending'),
        ('processing', 'Processing Payment'),
        ('paid', 'Payment Successful'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    ]
    
    ORDER_STATUS = [
        ('created', 'Order Created'),
        ('payment_pending', 'Awaiting Payment'),
        ('processing', 'Processing Domain Registration'),
        ('completed', 'Domain Registered & Active'),
        ('failed', 'Registration Failed'),
        ('cancelled', 'Order Cancelled'),
    ]
    
    # Order Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='domain_orders')
    website = models.ForeignKey(WebsiteProject, on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=255)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    years = models.PositiveIntegerField(default=1, help_text="Registration years")
    
    # Payment Processing
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)  # 'stripe', 'paypal', etc.
    payment_id = models.CharField(max_length=100, blank=True)  # External payment ID
    payment_data = models.JSONField(default=dict)  # Payment processor response
    
    # Order Processing
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='created')
    registrar_order_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order {self.domain_name} - ${self.price} ({self.order_status})"
    
    @property
    def total_price(self):
        return self.price * self.years


class AIWebsiteTemplate(models.Model):
    """
    Pre-built website templates generated by AI
    Used as starting points for different business types
    """
    name = models.CharField(max_length=100)
    website_type = models.CharField(max_length=20, choices=WebsiteProject.WEBSITE_TYPES)
    description = models.TextField()
    
    # Template Structure
    template_data = models.JSONField(
        help_text="Complete website structure - pages, content blocks, styling"
    )
    sample_content = models.JSONField(
        help_text="Sample content that can be customized by AI"
    )
    
    # Template Metadata
    color_schemes = models.JSONField(default=list, help_text="Suggested color combinations")
    recommended_pages = models.JSONField(default=list, help_text="Suggested pages for this type")
    
    # Usage & Performance
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['website_type', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.get_website_type_display()})"