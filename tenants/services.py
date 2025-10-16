# tenants/services.py - Automated Tenant Creation Service
import re
import logging
from django.db import transaction, connection
from django.core.management import call_command
from django.contrib.auth.models import User
from django.conf import settings
from django_tenants.utils import schema_context, get_tenant_model, get_public_schema_name
from .models import Tenant, Domain, TenantUser

logger = logging.getLogger(__name__)


class TenantCreationService:
    """
    Production-ready service for automated tenant creation
    Handles schema creation, migrations, and default content setup
    """
    
    @staticmethod
    def sanitize_schema_name(username):
        """
        Convert username to valid PostgreSQL schema name
        - Must start with letter or underscore
        - Can contain letters, numbers, underscores
        - Max 63 characters (PostgreSQL limit)
        """
        # Remove invalid characters and convert to lowercase
        schema_name = re.sub(r'[^a-zA-Z0-9_]', '_', username.lower())
        
        # Ensure it starts with letter or underscore
        if schema_name and not schema_name[0].isalpha() and schema_name[0] != '_':
            schema_name = f'tenant_{schema_name}'
        
        # Ensure minimum length and truncate if necessary
        if not schema_name:
            schema_name = 'tenant_default'
        
        # Truncate to PostgreSQL limit (leave room for potential suffixes)
        schema_name = schema_name[:60]
        
        # Handle duplicates by adding suffix
        base_name = schema_name
        counter = 1
        while Tenant.objects.filter(schema_name=schema_name).exists():
            schema_name = f"{base_name}_{counter}"
            if len(schema_name) > 63:
                # Truncate base name to fit suffix
                truncate_length = 63 - len(f"_{counter}")
                schema_name = f"{base_name[:truncate_length]}_{counter}"
            counter += 1
            
        return schema_name
    
    @staticmethod
    def create_tenant_for_user(user, tenant_name=None, subdomain=None, plan='free', preload_content=True):
        """
        Create a new tenant for a registered user
        
        Args:
            user (User): Django user instance
            tenant_name (str): Display name for tenant (defaults to username)
            subdomain (str): Subdomain for tenant (defaults to sanitized username)
            plan (str): Subscription plan
            preload_content (bool): Whether to create default content
            
        Returns:
            tuple: (tenant, domain, success_message) or (None, None, error_message)
        """
        try:
            with transaction.atomic():
                # Generate names
                if not tenant_name:
                    tenant_name = f"{user.get_full_name() or user.username}'s Site"
                
                if not subdomain:
                    subdomain = TenantCreationService.sanitize_schema_name(user.username)
                
                # Create tenant
                tenant = Tenant.objects.create(
                    schema_name=subdomain,
                    name=tenant_name,
                    slug=subdomain,
                    owner=user,
                    plan=plan
                )
                
                # Create primary domain
                domain_name = f"{subdomain}.{getattr(settings, 'TENANT_BASE_DOMAIN', 'localhost')}"
                domain = Domain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=True
                )
                
                # Create tenant-user relationship
                TenantUser.objects.create(
                    tenant=tenant,
                    user=user,
                    role='owner'
                )
                
                logger.info(f"Created tenant {tenant.schema_name} for user {user.username}")
                
                # Apply migrations to new schema
                TenantCreationService._apply_tenant_migrations(tenant)
                
                # Preload default content if requested
                if preload_content:
                    TenantCreationService._preload_default_content(tenant)
                
                return tenant, domain, f"Successfully created tenant '{tenant_name}' at {domain_name}"
                
        except Exception as e:
            logger.error(f"Failed to create tenant for user {user.username}: {str(e)}")
            return None, None, f"Failed to create tenant: {str(e)}"
    
    @staticmethod
    def _apply_tenant_migrations(tenant):
        """
        Apply database migrations to the tenant's schema
        """
        try:
            with schema_context(tenant.schema_name):
                # Apply migrations for tenant-specific apps
                tenant_apps = getattr(settings, 'TENANT_APPS', [])
                
                if tenant_apps:
                    for app in tenant_apps:
                        call_command('migrate', app, verbosity=0)
                else:
                    # Apply all migrations
                    call_command('migrate', verbosity=0)
                
                logger.info(f"Applied migrations for tenant {tenant.schema_name}")
                
        except Exception as e:
            logger.error(f"Failed to apply migrations for tenant {tenant.schema_name}: {str(e)}")
            raise
    
    @staticmethod
    def _preload_default_content(tenant):
        """
        Create default content for new tenant
        Runs in the tenant's schema context
        """
        try:
            with schema_context(tenant.schema_name):
                # Import here to avoid circular imports
                from home.models import PageContent
                
                # Create default homepage content
                default_content = {
                    'title': f'Welcome to {tenant.name}',
                    'content': f'''
                    <div style="text-align: center; padding: 50px 20px;">
                        <h1>Welcome to {tenant.name}</h1>
                        <p>Your site is ready! This is your default homepage.</p>
                        <p>You can customize this content in the admin panel.</p>
                        <div style="margin-top: 30px;">
                            <a href="/admin/" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                                Go to Admin Panel
                            </a>
                        </div>
                    </div>
                    ''',
                    'is_published': True
                }
                
                # Check if PageContent has tenant field
                page_content_fields = [f.name for f in PageContent._meta.get_fields()]
                if 'tenant' in page_content_fields:
                    default_content['tenant'] = tenant
                
                PageContent.objects.get_or_create(
                    defaults=default_content,
                    **({'tenant': tenant} if 'tenant' in page_content_fields else {})
                )
                
                logger.info(f"Preloaded default content for tenant {tenant.schema_name}")
                
        except Exception as e:
            logger.error(f"Failed to preload content for tenant {tenant.schema_name}: {str(e)}")
            # Don't raise - content creation failure shouldn't block tenant creation


# Signal handler for automatic tenant creation after user registration
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def auto_create_tenant_for_user(sender, instance, created, **kwargs):
    """
    Automatically create a tenant when a new user registers
    Only triggers for new users, not updates
    """
    if created and getattr(settings, 'AUTO_CREATE_TENANT', True):
        try:
            # Check if user already has a tenant (in case of race conditions)
            if not instance.owned_tenants.exists():
                tenant, domain, message = TenantCreationService.create_tenant_for_user(
                    user=instance,
                    preload_content=True
                )
                
                if tenant:
                    logger.info(f"Auto-created tenant for new user: {instance.username}")
                else:
                    logger.error(f"Auto-creation failed for user {instance.username}: {message}")
                    
        except Exception as e:
            logger.error(f"Auto-creation error for user {instance.username}: {str(e)}")


# Manual tenant creation function for admin use
def create_tenant_manually(username, tenant_name=None, domain_name=None, plan='free'):
    """
    Manually create a tenant (for admin/management use)
    
    Args:
        username (str): Username of the owner
        tenant_name (str): Display name for tenant
        domain_name (str): Custom domain (optional)
        plan (str): Subscription plan
        
    Returns:
        dict: Creation result with success status and message
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return {
            'success': False,
            'message': f"User '{username}' does not exist"
        }
    
    tenant, domain, message = TenantCreationService.create_tenant_for_user(
        user=user,
        tenant_name=tenant_name,
        subdomain=domain_name.split('.')[0] if domain_name else None,
        plan=plan
    )
    
    # If custom domain provided, create additional domain
    if tenant and domain_name and domain_name != domain.domain:
        try:
            Domain.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=False
            )
            message += f" Custom domain {domain_name} added."
        except Exception as e:
            message += f" Warning: Could not add custom domain {domain_name}: {str(e)}"
    
    return {
        'success': tenant is not None,
        'message': message,
        'tenant': tenant,
        'domain': domain
    }