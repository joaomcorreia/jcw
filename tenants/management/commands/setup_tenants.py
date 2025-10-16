from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tenants.models import Tenant, TenantDomain, TenantUser
from home.models import PageContent

class Command(BaseCommand):
    help = 'Create sample tenants for testing multi-tenancy'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample tenants...')
        
        # Create sample tenants
        tenants_data = [
            {
                'name': 'Acme Corporation',
                'slug': 'acme',
                'domain': 'acme.localhost',
                'site_title': 'Acme Corporation',
                'site_tagline': 'Leading solutions for your business'
            },
            {
                'name': 'Tech Innovations',
                'slug': 'techinnov',
                'domain': 'techinnov.localhost',
                'site_title': 'Tech Innovations Inc.',
                'site_tagline': 'Innovation through technology'
            },
            {
                'name': 'Global Services',
                'slug': 'global',
                'domain': 'global.localhost',
                'site_title': 'Global Services Ltd.',
                'site_tagline': 'Worldwide excellence in service delivery'
            }
        ]
        
        for tenant_data in tenants_data:
            tenant, created = Tenant.objects.get_or_create(
                slug=tenant_data['slug'],
                defaults=tenant_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created tenant: {tenant.name}')
                )
                
                # Create sample content for each tenant
                PageContent.objects.create(
                    tenant=tenant,
                    title=f"Welcome to {tenant.name}",
                    message=f"This is the custom homepage for {tenant.name}. "
                           f"You are viewing the {tenant.domain} domain. "
                           f"This content is specific to this tenant and managed through the admin panel.",
                    is_active=True
                )
                
                self.stdout.write(f'  ✓ Created content for {tenant.name}')
                
                # Add additional domain examples
                if tenant.slug == 'acme':
                    TenantDomain.objects.create(
                        tenant=tenant,
                        domain='www.acme.localhost',
                        is_active=True
                    )
                    self.stdout.write(f'  ✓ Added www.acme.localhost domain')
                    
            else:
                self.stdout.write(f'  - Tenant {tenant.name} already exists')
        
        # Create a global/shared content
        global_content, created = PageContent.objects.get_or_create(
            tenant=None,
            defaults={
                'title': 'Welcome to Our Multi-Tenant Platform',
                'message': 'This is shared content that appears when no tenant-specific content is available. '
                          'This demonstrates the fallback mechanism in our multi-tenant system.',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✓ Created global/shared content')
            )
        else:
            self.stdout.write('  - Global content already exists')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('MULTI-TENANT SETUP COMPLETE!')
        self.stdout.write('='*50)
        self.stdout.write('\nTo test the multi-tenant functionality:')
        self.stdout.write('\n1. Add these entries to your hosts file (C:\\Windows\\System32\\drivers\\etc\\hosts):')
        self.stdout.write('   127.0.0.1  acme.localhost')
        self.stdout.write('   127.0.0.1  techinnov.localhost')
        self.stdout.write('   127.0.0.1  global.localhost')
        self.stdout.write('   127.0.0.1  www.acme.localhost')
        
        self.stdout.write('\n2. Start the development server: python manage.py runserver')
        
        self.stdout.write('\n3. Visit these URLs to see different tenants:')
        self.stdout.write('   • http://localhost:8000/ (default tenant)')
        self.stdout.write('   • http://acme.localhost:8000/ (Acme Corporation)')
        self.stdout.write('   • http://techinnov.localhost:8000/ (Tech Innovations)')
        self.stdout.write('   • http://global.localhost:8000/ (Global Services)')
        self.stdout.write('   • http://www.acme.localhost:8000/ (Acme - alternative domain)')
        
        self.stdout.write('\n4. Admin panel: http://localhost:8000/admin/')
        self.stdout.write('   Username: admin, Password: admin123')
        self.stdout.write('\nEach tenant will show different content and branding!')