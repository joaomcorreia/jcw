from django.core.management.base import BaseCommand
from tenants.models import Tenant, TenantDomain

class Command(BaseCommand):
    help = 'Create JCW Trading Hub tenant'

    def handle(self, *args, **options):
        self.stdout.write('Creating JCW Trading Hub tenant...')
        
        # Create JCW Trading Hub tenant
        tenant, created = Tenant.objects.get_or_create(
            slug='jcw-trading-hub',
            defaults={
                'name': 'JCW Trading Hub',
                'domain': 'jcwtradehub.com',
                'site_title': 'JCW Trading Hub',
                'site_tagline': 'Professional Trading Solutions & Analytics',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created tenant: {tenant.name}')
            )
            
            # Add additional domains
            domains = [
                'www.jcwtradehub.com',
                'jcwtradehub.localhost'  # For local testing
            ]
            
            for domain in domains:
                domain_obj, domain_created = TenantDomain.objects.get_or_create(
                    domain=domain,
                    defaults={
                        'tenant': tenant,
                        'is_active': True,
                        'is_primary': domain == 'www.jcwtradehub.com'
                    }
                )
                if domain_created:
                    self.stdout.write(f'  ✓ Added domain: {domain}')
            
        else:
            self.stdout.write(f'  - Tenant {tenant.name} already exists')
            
        self.stdout.write('\n' + '='*50)
        self.stdout.write('JCW TRADING HUB TENANT READY!')
        self.stdout.write('='*50)
        self.stdout.write(f'\nTenant: {tenant.name}')
        self.stdout.write(f'Primary Domain: {tenant.domain}')
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Visit the admin to upload a homepage screenshot')
        self.stdout.write('2. Use the "Connect to Frontend" button to view the site')
        self.stdout.write('3. Customize content for this tenant')