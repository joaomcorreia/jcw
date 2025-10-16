from django.core.management.base import BaseCommand
from django.db import models
from tenants.models import Tenant, TenantDomain

class Command(BaseCommand):
    help = 'Update JCW Trading Hub domain from jcwtradinghub.com to jcwtradehub.com'

    def handle(self, *args, **options):
        self.stdout.write('Updating JCW Trading Hub domain...')
        
        try:
            # Find the tenant by old domain or slug
            tenant = Tenant.objects.filter(
                models.Q(domain='jcwtradinghub.com') | 
                models.Q(slug='jcw-trading-hub')
            ).first()
            
            if tenant:
                # Update main domain
                old_domain = tenant.domain
                tenant.domain = 'jcwtradehub.com'
                tenant.save()
                
                self.stdout.write(f'✓ Updated main domain: {old_domain} → {tenant.domain}')
                
                # Update additional domains
                domain_updates = {
                    'www.jcwtradinghub.com': 'www.jcwtradehub.com',
                    'jcwtradinghub.localhost': 'jcwtradehub.localhost'
                }
                
                for old_domain, new_domain in domain_updates.items():
                    domain_obj = TenantDomain.objects.filter(domain=old_domain).first()
                    if domain_obj:
                        domain_obj.domain = new_domain
                        domain_obj.save()
                        self.stdout.write(f'✓ Updated additional domain: {old_domain} → {new_domain}')
                    else:
                        # Create the new domain if it doesn't exist
                        TenantDomain.objects.create(
                            tenant=tenant,
                            domain=new_domain,
                            is_active=True,
                            is_primary=new_domain.startswith('www.')
                        )
                        self.stdout.write(f'✓ Created new domain: {new_domain}')
                
                self.stdout.write('\n' + '='*50)
                self.stdout.write('DOMAIN UPDATE COMPLETE!')
                self.stdout.write('='*50)
                self.stdout.write(f'Tenant: {tenant.name}')
                self.stdout.write(f'New Primary Domain: {tenant.domain}')
                self.stdout.write('\nAll references updated to jcwtradehub.com')
                
            else:
                self.stdout.write(self.style.WARNING('JCW Trading Hub tenant not found'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating domain: {e}'))
            
            # Fallback: try simple lookup
            tenant = Tenant.objects.filter(slug='jcw-trading-hub').first()
            if tenant:
                tenant.domain = 'jcwtradehub.com'
                tenant.save()
                self.stdout.write(f'✓ Updated tenant domain to: {tenant.domain}')