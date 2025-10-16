# tenants/management/commands/create_saas_tenant.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tenants.services import TenantCreationService, create_tenant_manually


class Command(BaseCommand):
    help = 'Create a new SaaS tenant for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the tenant owner')
        parser.add_argument('--name', type=str, help='Display name for the tenant')
        parser.add_argument('--domain', type=str, help='Custom domain for the tenant')
        parser.add_argument('--plan', type=str, default='free', 
                          choices=['free', 'starter', 'professional', 'enterprise'],
                          help='Subscription plan')
        parser.add_argument('--no-content', action='store_true', 
                          help='Skip preloading default content')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return

        # Check if user already has a tenant
        if user.owned_tenants.exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already owns these tenants:')
            )
            for tenant in user.owned_tenants.all():
                self.stdout.write(f'  - {tenant.name} ({tenant.schema_name})')
            
            if not input('Continue creating another tenant? (y/N): ').lower().startswith('y'):
                return

        self.stdout.write(f'Creating tenant for user: {username}')
        
        # Use the service to create tenant
        tenant, domain, message = TenantCreationService.create_tenant_for_user(
            user=user,
            tenant_name=options.get('name'),
            subdomain=options.get('domain'),
            plan=options['plan'],
            preload_content=not options['no_content']
        )

        if tenant:
            self.stdout.write(
                self.style.SUCCESS(f'✓ {message}')
            )
            self.stdout.write(f'  Tenant ID: {tenant.id}')
            self.stdout.write(f'  Schema: {tenant.schema_name}')
            self.stdout.write(f'  Domain: {domain.domain}')
            self.stdout.write(f'  Plan: {tenant.plan}')
            self.stdout.write(f'  Owner: {tenant.owner.username}')
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ {message}')
            )