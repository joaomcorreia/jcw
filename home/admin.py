from django.contrib import admin
from .models import PageContent

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    """Custom admin configuration for PageContent model - now tenant-aware"""
    list_display = ('title', 'get_tenant_name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'tenant')
    search_fields = ('title', 'message', 'tenant__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('tenant', 'title', 'message', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_tenant_name(self, obj):
        return obj.tenant.name if obj.tenant else "Global/Shared"
    get_tenant_name.short_description = "Tenant"
    get_tenant_name.admin_order_field = "tenant__name"

# Customize admin site header and title
admin.site.site_header = "Multi-Tenant Django Admin"
admin.site.site_title = "Multi-Tenant Admin"
admin.site.index_title = "Welcome to Multi-Tenant Administration"
