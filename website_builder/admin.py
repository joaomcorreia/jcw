from django.contrib import admin
from .models import WebsiteProject, WebsiteDomain, WebsiteContent, DomainOrder, AIWebsiteTemplate


@admin.register(WebsiteProject)
class WebsiteProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'website_type', 'status', 'is_published', 'created_at']
    list_filter = ['website_type', 'status', 'is_published', 'created_at']
    search_fields = ['name', 'user__username', 'ai_description']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'slug', 'website_type', 'status')
        }),
        ('AI Generated Content', {
            'fields': ('ai_description', 'ai_generated_data', 'custom_modifications'),
            'classes': ('collapse',)
        }),
        ('Branding', {
            'fields': ('brand_colors', 'logo_url', 'favicon_url'),
            'classes': ('collapse',)
        }),
        ('Status & Publishing', {
            'fields': ('is_published', 'published_at', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(WebsiteDomain)
class WebsiteDomainAdmin(admin.ModelAdmin):
    list_display = ['domain_name', 'website', 'domain_type', 'is_active', 'registration_status', 'created_at']
    list_filter = ['domain_type', 'is_active', 'registration_status', 'ssl_enabled']
    search_fields = ['domain_name', 'website__name', 'website__user__username']
    readonly_fields = ['created_at', 'activated_at', 'expires_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('website', 'website__user')


@admin.register(WebsiteContent)
class WebsiteContentAdmin(admin.ModelAdmin):
    list_display = ['website', 'page_title', 'page_type', 'is_published', 'sort_order', 'updated_at']
    list_filter = ['page_type', 'is_published', 'website__website_type']
    search_fields = ['page_title', 'website__name', 'seo_title', 'seo_description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Page Information', {
            'fields': ('website', 'page_type', 'page_slug', 'page_title', 'sort_order', 'is_published')
        }),
        ('Content', {
            'fields': ('content_blocks',)
        }),
        ('SEO Settings', {
            'fields': ('seo_title', 'seo_description', 'seo_keywords'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('website', 'website__user')


@admin.register(DomainOrder)
class DomainOrderAdmin(admin.ModelAdmin):
    list_display = ['domain_name', 'user', 'price', 'payment_status', 'order_status', 'created_at']
    list_filter = ['payment_status', 'order_status', 'currency', 'created_at']
    search_fields = ['domain_name', 'user__username', 'payment_id', 'registrar_order_id']
    readonly_fields = ['id', 'created_at', 'paid_at', 'completed_at', 'total_price']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'website', 'domain_name')
        }),
        ('Pricing', {
            'fields': ('price', 'currency', 'years', 'total_price')
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_method', 'payment_id', 'payment_data', 'paid_at')
        }),
        ('Registration', {
            'fields': ('order_status', 'registrar_order_id', 'error_message', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def total_price(self, obj):
        return f"${obj.total_price} {obj.currency}"
    total_price.short_description = 'Total Price'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'website')


@admin.register(AIWebsiteTemplate)
class AIWebsiteTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'website_type', 'usage_count', 'is_active', 'created_at']
    list_filter = ['website_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['usage_count', 'created_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'website_type', 'description', 'is_active')
        }),
        ('Template Structure', {
            'fields': ('template_data', 'sample_content', 'color_schemes', 'recommended_pages')
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )


# Customize admin site header
admin.site.site_header = "JCW Website Builder Admin"
admin.site.site_title = "Website Builder"
admin.site.index_title = "Welcome to Website Builder Administration"