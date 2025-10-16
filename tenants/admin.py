from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Tenant, TenantDomain, TenantUser

class TenantDomainInline(admin.TabularInline):
    model = TenantDomain
    extra = 1

class TenantUserInline(admin.TabularInline):
    model = TenantUser
    extra = 0

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'domain', 'frontend_link', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'domain')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TenantDomainInline, TenantUserInline]
    readonly_fields = ('get_admin_preview_html', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Preview & Actions', {
            'fields': ('get_admin_preview_html',),
        }),
        ('Basic Information', {
            'fields': ('name', 'slug', 'domain', 'is_active')
        }),
        ('Branding', {
            'fields': ('site_title', 'site_tagline', 'homepage_screenshot'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def frontend_link(self, obj):
        """Display a link to visit the tenant's frontend"""
        if obj.domain:
            url = obj.get_frontend_url()
            return format_html(
                '<a href="{}" target="_blank" style="background: #417690; color: white; '
                'padding: 5px 10px; text-decoration: none; border-radius: 3px; '
                'font-size: 11px; font-weight: bold;">🌐 Visit Site</a>',
                url
            )
        return "-"
    frontend_link.short_description = "Frontend"
    frontend_link.allow_tags = True
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Customize the change view to add frontend connect button"""
        extra_context = extra_context or {}
        
        if object_id:
            tenant = self.get_object(request, object_id)
            if tenant:
                extra_context['tenant_frontend_url'] = tenant.get_frontend_url()
                extra_context['show_frontend_button'] = True
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    class Media:
        css = {
            'all': ('admin/css/tenant_admin.css',)
        }
        js = ('admin/js/tenant_admin.js',)

@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary', 'is_active')
    list_filter = ('is_primary', 'is_active', 'tenant')
    search_fields = ('domain', 'tenant__name')

@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'is_admin', 'joined_at')
    list_filter = ('is_admin', 'tenant', 'joined_at')
    search_fields = ('user__username', 'user__email', 'tenant__name')
