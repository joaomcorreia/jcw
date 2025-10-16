# 🚀 How Django-Tenants Automated Creation Works

## The Complete Flow

Here's exactly how the automated tenant creation system works when a user registers:

### 1️⃣ **User Registration Trigger**
```python
# When a user registers (via web form or API)
user = User.objects.create_user(
    username='johndoe',
    email='john@example.com', 
    password='securepass123'
)
# 👆 This triggers the post_save signal automatically
```

### 2️⃣ **Signal Handler Activation**
```python
@receiver(post_save, sender=User)
def auto_create_tenant_for_user(sender, instance, created, **kwargs):
    if created and getattr(settings, 'AUTO_CREATE_TENANT', True):
        tenant, domain, message = TenantCreationService.create_tenant_for_user(
            user=instance,
            preload_content=True
        )
```

### 3️⃣ **Schema Name Sanitization**
```python
# Input: "john.doe@email.com" 
# Output: "john_doe_email_com"

def sanitize_schema_name(username):
    # Clean invalid chars: john.doe@email.com → john_doe_email_com
    schema_name = re.sub(r'[^a-zA-Z0-9_]', '_', username.lower())
    
    # Add prefix if starts with number: 123user → tenant_123user  
    if schema_name[0].isdigit():
        schema_name = f'tenant_{schema_name}'
    
    # Truncate to PostgreSQL 63-char limit
    return schema_name[:60]
```

### 4️⃣ **Tenant Creation (Atomic Transaction)**
```python
with transaction.atomic():
    # Create Tenant record
    tenant = Tenant.objects.create(
        schema_name='john_doe_email_com',  # ← PostgreSQL schema name
        name="John Doe's Site",
        slug='john_doe_email_com',
        owner=user,
        plan='free'
    )
    
    # Create domain
    domain = Domain.objects.create(
        domain='john_doe_email_com.localhost',
        tenant=tenant,
        is_primary=True
    )
    
    # Create ownership relationship
    TenantUser.objects.create(
        tenant=tenant,
        user=user, 
        role='owner'
    )
```

### 5️⃣ **PostgreSQL Schema Creation** 
```python
# Django-tenants automatically creates the PostgreSQL schema
# when the Tenant object is saved (via TenantMixin)

# This creates: CREATE SCHEMA "john_doe_email_com";
```

### 6️⃣ **Apply Migrations to New Schema**
```python
def _apply_tenant_migrations(tenant):
    with schema_context(tenant.schema_name):
        # Switch PostgreSQL search_path to tenant schema
        # SET search_path = "john_doe_email_com";
        
        # Apply migrations to this schema
        call_command('migrate', verbosity=0)
        # Creates tables like: john_doe_email_com.home_pagecontent
```

### 7️⃣ **Preload Default Content**
```python  
def _preload_default_content(tenant):
    with schema_context(tenant.schema_name):
        # Running in tenant's schema context
        from home.models import PageContent
        
        PageContent.objects.create(
            title=f'Welcome to {tenant.name}',
            content='<h1>Your site is ready!</h1>',
            is_published=True
        )
        # 👆 This data goes into john_doe_email_com.home_pagecontent
```

## 🎯 **Real-World Example**

Let's trace through a complete user registration:

```python
# 1. User registers
user = User.objects.create_user(
    username='sarah_wilson',
    email='sarah@startup.com',
    first_name='Sarah',
    last_name='Wilson'
)

# 2. Signal fires automatically → TenantCreationService.create_tenant_for_user()

# 3. Schema name: 'sarah_wilson' (already clean)

# 4. Creates:
#    - Tenant(schema_name='sarah_wilson', name="Sarah Wilson's Site")
#    - Domain(domain='sarah_wilson.localhost') 
#    - TenantUser(user=sarah, tenant=tenant, role='owner')

# 5. PostgreSQL creates: CREATE SCHEMA "sarah_wilson";

# 6. Migrations applied to sarah_wilson schema:
#    - sarah_wilson.django_content_type
#    - sarah_wilson.home_pagecontent  
#    - sarah_wilson.auth_user (tenant-specific users)

# 7. Default content created in sarah_wilson.home_pagecontent

# 8. Result: Sarah can visit sarah_wilson.localhost and see her site!
```

## 🔄 **Domain Routing Magic**

When someone visits `sarah_wilson.localhost`:

1. **Django-Tenants Middleware** checks domain
2. **Finds matching Domain** record → gets tenant
3. **Sets PostgreSQL search_path** to `sarah_wilson` schema  
4. **All queries run** in Sarah's isolated schema
5. **Sarah sees only her data** - complete isolation!

## 📊 **Database Structure After Creation**

```sql
-- PostgreSQL Database Structure

-- Public Schema (shared data)
public.tenants_tenant         -- Tenant definitions  
public.tenants_domain         -- Domain mappings
public.auth_user             -- All users
public.tenants_tenantuser    -- Tenant memberships

-- Tenant Schema (isolated data) 
sarah_wilson.home_pagecontent -- Sarah's content
sarah_wilson.django_session  -- Sarah's sessions
sarah_wilson.auth_group      -- Sarah's groups
```

## ⚡ **Key Benefits**

✅ **Automatic** - No manual setup required  
✅ **Atomic** - All-or-nothing creation  
✅ **Isolated** - Complete data separation  
✅ **Scalable** - Handles thousands of tenants  
✅ **Secure** - PostgreSQL schema-level isolation  
✅ **Fast** - Direct schema switching vs app-level filtering

## 🎮 **Try It Yourself**

```python
# Run the demo script I created
python demo_tenant_creation.py

# Or test via Django shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('testuser', 'test@example.com', 'pass123')  
>>> # Watch the magic happen automatically! ✨
```

That's how **automated multi-tenant provisioning** works with PostgreSQL schema isolation! 🚀