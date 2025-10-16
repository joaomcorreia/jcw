from django.utils.deprecation import MiddlewareMixin
from .models import Tenant, TenantDomain
import logging

logger = logging.getLogger(__name__)

class TenantMiddleware(MiddlewareMixin):
    """
    Simple tenant middleware that identifies tenants by domain.
    Uses MiddlewareMixin for better compatibility with Django middleware chain.
    """

    def process_request(self, request):
        """Process the request to identify and set the tenant."""
        # Get the current domain/host
        host = request.get_host()
        if ':' in host:
            host = host.split(':')[0].lower()  # Remove port if present
        
        # Try to find tenant by primary domain first
        tenant = None
        try:
            tenant = Tenant.objects.filter(domain=host, is_active=True).first()
            
            # If not found by primary domain, check additional domains
            if not tenant:
                tenant_domain = TenantDomain.objects.filter(
                    domain=host, is_active=True
                ).select_related('tenant').first()
                if tenant_domain:
                    tenant = tenant_domain.tenant
                    
            # If still not found, try subdomain matching
            if not tenant and '.' in host and not host.startswith('www.'):
                # Extract subdomain (first part before first dot)
                subdomain = host.split('.')[0]
                tenant = Tenant.objects.filter(
                    slug=subdomain, is_active=True
                ).first()
                
        except Exception as e:
            logger.error(f"Error finding tenant for host {host}: {e}")
            
        # Set default tenant if none found (for development)
        if not tenant:
            # Create or get default tenant for localhost/127.0.0.1
            if host in ['localhost', '127.0.0.1', 'testserver']:
                try:
                    tenant, created = Tenant.objects.get_or_create(
                        slug='default',
                        defaults={
                            'name': 'Default Tenant',
                            'domain': 'localhost',
                            'site_title': 'Default Site',
                            'site_tagline': 'Development Environment',
                            'is_active': True
                        }
                    )
                    if created:
                        logger.info("Created default tenant for development")
                except Exception as e:
                    logger.error(f"Error creating default tenant: {e}")
            else:
                logger.warning(f"No tenant found for host: {host}")
        
        # Store tenant in request for use in views
        request.tenant = tenant
        
        # Log tenant detection for debugging
        if tenant:
            logger.debug(f"Tenant detected: {tenant.name} ({tenant.domain}) for host: {host}")
        else:
            logger.debug(f"No tenant detected for host: {host}")

    def process_response(self, request, response):
        """
        Process the response to optionally store tenant info in session.
        This runs after all other middleware, so session should be available.
        """
        tenant = getattr(request, 'tenant', None)
        
        # Store tenant info in session if available (optional - for template context)
        if tenant and hasattr(request, 'session'):
            try:
                request.session['tenant_id'] = tenant.id
                request.session['tenant_name'] = tenant.name
                request.session['tenant_domain'] = tenant.domain
                request.session['site_title'] = tenant.site_title
                request.session['site_tagline'] = tenant.site_tagline
            except Exception as e:
                logger.debug(f"Could not store tenant info in session: {e}")
        
        return response