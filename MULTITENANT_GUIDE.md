# Multi-Tenant Django Project

This Django project has been converted into a multi-tenant application where each tenant can use their own domain and have isolated content and branding.

## 🏢 Multi-Tenancy Features

- **Domain-based tenant isolation**: Each tenant is identified by their domain
- **Tenant-specific content**: Page content can be customized per tenant
- **Tenant branding**: Each tenant can have their own site title and tagline
- **Fallback mechanism**: Global/shared content when tenant-specific content isn't available
- **Admin interface**: Manage all tenants and their content from a single admin panel

## 🚀 Quick Start

### 1. Setup Development Environment

The project is already configured! Just follow these steps:

```bash
# Start the development server (already running)
python manage.py runserver
```

### 2. Configure Host Names for Testing

Add these entries to your `hosts` file to test different tenants:

**Windows**: Edit `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac**: Edit `/etc/hosts`

```
127.0.0.1  acme.localhost
127.0.0.1  techinnov.localhost
127.0.0.1  global.localhost
127.0.0.1  www.acme.localhost
```

### 3. Test Different Tenants

Visit these URLs to see different tenant sites:

- **Default**: http://localhost:8000/ (Default tenant)
- **Acme Corp**: http://acme.localhost:8000/
- **Tech Innovations**: http://techinnov.localhost:8000/
- **Global Services**: http://global.localhost:8000/
- **Alternative Domain**: http://www.acme.localhost:8000/

### 4. Admin Panel Access

- **URL**: http://localhost:8000/admin/
- **Username**: `admin`
- **Password**: `admin123`

## 📁 Project Structure

```
jcw/
├── tenants/                   # Multi-tenant management app
│   ├── models.py             # Tenant, TenantDomain, TenantUser models
│   ├── middleware.py         # Tenant detection middleware
│   ├── admin.py              # Tenant admin interface
│   └── management/commands/
│       └── setup_tenants.py  # Command to create sample tenants
├── home/                      # Homepage app (now tenant-aware)
│   ├── models.py             # PageContent model with tenant field
│   ├── views.py              # Tenant-aware views
│   └── templates/            # Updated templates showing tenant info
└── myproject/
    └── settings.py           # Updated with multi-tenant configuration
```

## 🔧 How It Works

### 1. Tenant Detection
The `TenantMiddleware` identifies tenants by:
1. **Primary domain**: Direct match with `tenant.domain`
2. **Additional domains**: Match with `TenantDomain` entries
3. **Subdomain**: Extract subdomain and match with `tenant.slug`
4. **Fallback**: Create/use default tenant for localhost

### 2. Content Isolation
- Each `PageContent` can be linked to a specific tenant
- Views first look for tenant-specific content
- Fall back to global/shared content if none found
- Use tenant branding (title/tagline) as final fallback

### 3. Admin Management
- All tenants managed from single admin interface
- Tenant-aware content filtering
- Easy tenant creation and domain management

## 🏗️ Architecture

### Models

#### Tenant Model
```python
class Tenant(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    domain = models.CharField(max_length=255, unique=True)
    site_title = models.CharField(max_length=200)
    site_tagline = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
```

#### TenantDomain Model (Additional Domains)
```python
class TenantDomain(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
```

#### PageContent Model (Tenant-aware)
```python
class PageContent(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
```

## 🎯 Usage Examples

### Creating New Tenants

#### Via Admin Panel:
1. Go to http://localhost:8000/admin/
2. Navigate to "Tenants" > "Tenants"
3. Click "Add tenant"
4. Fill in the details and save

#### Via Management Command:
```bash
python manage.py shell
>>> from tenants.models import Tenant
>>> tenant = Tenant.objects.create(
...     name="New Company",
...     slug="newco",
...     domain="newco.localhost",
...     site_title="New Company Inc.",
...     site_tagline="Innovation and excellence"
... )
```

### Adding Custom Content

```python
from home.models import PageContent
from tenants.models import Tenant

# Get tenant
tenant = Tenant.objects.get(slug='acme')

# Create tenant-specific content
PageContent.objects.create(
    tenant=tenant,
    title="Welcome to Acme Corporation",
    message="Custom message for Acme users",
    is_active=True
)
```

## 🚀 Production Considerations

### 1. Database Backend
For production, consider using PostgreSQL with proper schema separation:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'multitenant_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. Domain Configuration
- Configure your DNS to point tenant domains to your server
- Set up SSL certificates for each domain
- Configure web server (nginx/Apache) for domain routing

### 3. Caching
Implement tenant-aware caching:
- Use tenant ID in cache keys
- Separate cache namespaces per tenant
- Consider Redis with tenant-based key prefixes

### 4. Media Files
Implement tenant-specific media storage:
```python
def tenant_upload_path(instance, filename):
    tenant_slug = instance.tenant.slug if instance.tenant else 'shared'
    return f'tenants/{tenant_slug}/{filename}'
```

## 🔐 Security Considerations

1. **Tenant Isolation**: Ensure proper data isolation between tenants
2. **Domain Validation**: Validate domain ownership before tenant creation
3. **User Permissions**: Implement tenant-specific user permissions
4. **Data Export**: Be careful with data export/backup to maintain isolation

## 📈 Scaling

### Database Scaling
- Consider database sharding by tenant
- Use read replicas for tenant-specific queries
- Implement connection pooling per tenant

### Application Scaling
- Use tenant-aware load balancing
- Implement tenant-specific feature flags
- Consider microservices architecture for large tenants

## 🛠️ Development Tools

### Management Commands
```bash
# Setup sample tenants
python manage.py setup_tenants

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate
```

### Debugging
- Check `request.tenant` in views to see current tenant
- Use Django debug toolbar with tenant information
- Log tenant-specific activities for monitoring

## 🎉 Next Steps

1. **Add More Tenant Features**:
   - Tenant-specific themes/CSS
   - Custom logos and branding
   - Tenant-specific email templates

2. **Enhanced Admin**:
   - Tenant dashboard with analytics
   - Bulk tenant operations
   - Tenant health monitoring

3. **API Integration**:
   - Tenant-aware REST API
   - API key management per tenant
   - Webhook configurations

4. **Advanced Features**:
   - Tenant-specific plugins
   - Custom domain SSL automation
   - Tenant billing integration

Your multi-tenant Django project is now ready for development and can be extended based on your specific requirements! 🚀