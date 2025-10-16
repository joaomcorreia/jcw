from django.db import models

class PageContent(models.Model):
    """Model for managing homepage content through admin - now tenant-aware"""
    # Link to tenant (will be None for shared content)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True)
    
    title = models.CharField(max_length=200, default="Welcome to My Django Project")
    message = models.TextField(default="This is your custom homepage!")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page Content"
        verbose_name_plural = "Page Contents"
        ordering = ['-updated_at']

    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else "Global"
        return f"{self.title} ({tenant_name})"
