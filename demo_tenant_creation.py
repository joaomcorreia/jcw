# demo_tenant_creation.py - Live Demo of Automated Tenant Creation
"""
This script demonstrates how the automated tenant creation system works
Run this to see the complete flow in action
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.db import connection
from tenants.services import TenantCreationService
from tenants.models import Tenant, Domain, TenantUser

def demo_automated_tenant_creation():
    """
    Step-by-step demonstration of automated tenant creation
    """
    
    print("🚀 DJANGO-TENANTS AUTOMATED CREATION DEMO")
    print("=" * 50)
    
    # Step 1: Create a test user (simulates registration)
    print("\n1️⃣ STEP 1: User Registration")
    print("-" * 30)
    
    username = "demo_user"
    email = "demo@example.com"
    
    # Check if user exists (cleanup from previous runs)
    if User.objects.filter(username=username).exists():
        print(f"🔄 Cleaning up existing user: {username}")
        User.objects.filter(username=username).delete()
    
    # Create new user (this simulates user registration)
    user = User.objects.create_user(
        username=username,
        email=email,
        password="demo123",
        first_name="Demo",
        last_name="User"
    )
    print(f"✅ Created user: {user.username} ({user.email})")
    
    # Step 2: Schema name sanitization
    print("\n2️⃣ STEP 2: Schema Name Sanitization")
    print("-" * 30)
    
    original_username = user.username
    sanitized_schema = TenantCreationService.sanitize_schema_name(original_username)
    
    print(f"📝 Original username: {original_username}")
    print(f"🧹 Sanitized schema name: {sanitized_schema}")
    print(f"✅ PostgreSQL compatible: {len(sanitized_schema) <= 63}")
    
    # Step 3: Automated tenant creation
    print("\n3️⃣ STEP 3: Automated Tenant Creation")
    print("-" * 30)
    
    tenant, domain, message = TenantCreationService.create_tenant_for_user(
        user=user,
        tenant_name=f"{user.get_full_name()}'s Demo Site",
        plan='free',
        preload_content=True
    )
    
    if tenant:
        print(f"✅ {message}")
        print(f"🏢 Tenant Name: {tenant.name}")
        print(f"🗄️ Schema Name: {tenant.schema_name}")
        print(f"🌐 Domain: {domain.domain}")
        print(f"👤 Owner: {tenant.owner.username}")
        print(f"📋 Plan: {tenant.get_plan_display()}")
    else:
        print(f"❌ Error: {message}")
        return
    
    # Step 4: Show database schemas
    print("\n4️⃣ STEP 4: Database Schema Verification")
    print("-" * 30)
    
    with connection.cursor() as cursor:
        # List all schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'pg_temp_1', 'pg_toast_temp_1')
            ORDER BY schema_name;
        """)
        schemas = cursor.fetchall()
        
        print("📊 PostgreSQL Schemas:")
        for schema in schemas:
            schema_name = schema[0]
            if schema_name == 'public':
                print(f"  📋 {schema_name} (shared/public schema)")
            elif schema_name == tenant.schema_name:
                print(f"  🎯 {schema_name} (our new tenant schema)")
            else:
                print(f"  📁 {schema_name}")
    
    # Step 5: Show tenant-specific data
    print("\n5️⃣ STEP 5: Tenant-Specific Data")
    print("-" * 30)
    
    # Show tenant relationships
    tenant_users = TenantUser.objects.filter(tenant=tenant)
    print(f"👥 Tenant Users:")
    for tu in tenant_users:
        print(f"  - {tu.user.username} ({tu.get_role_display()})")
    
    # Show domains
    domains = Domain.objects.filter(tenant=tenant)
    print(f"🌐 Domains:")
    for d in domains:
        primary = " [PRIMARY]" if d.is_primary else ""
        print(f"  - {d.domain}{primary}")
    
    # Step 6: Demonstrate schema context switching
    print("\n6️⃣ STEP 6: Schema Context Switching")
    print("-" * 30)
    
    from django_tenants.utils import schema_context
    
    # Show current schema
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_schema();")
        current_schema = cursor.fetchone()[0]
        print(f"🔍 Current schema: {current_schema}")
    
    # Switch to tenant schema and check
    try:
        from django_tenants.utils import schema_context
        with schema_context(tenant.schema_name):
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_schema();")
                tenant_schema = cursor.fetchone()[0]
                print(f"🎯 Switched to tenant schema: {tenant_schema}")
                
                # Check if tenant-specific tables exist
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    AND table_name LIKE 'home%%'
                    ORDER BY table_name;
                """, [tenant_schema])
                
                tables = cursor.fetchall()
                if tables:
                    print(f"📊 Tenant-specific tables:")
                    for table in tables:
                        print(f"  - {table[0]}")
                else:
                    print("📋 No tenant-specific tables found (normal for fresh schema)")
                
    except Exception as e:
        print(f"⚠️ Schema context switching requires django-tenants setup: {e}")
    
    # Step 7: Show the complete flow
    print("\n7️⃣ STEP 7: Complete Automation Flow")
    print("-" * 30)
    
    print("🔄 The automated flow works like this:")
    print("   1. User registers via web form or API")
    print("   2. Django's post_save signal triggers")
    print("   3. auto_create_tenant_for_user() function runs")
    print("   4. Username gets sanitized for PostgreSQL")
    print("   5. New Tenant record created with schema_name")
    print("   6. PostgreSQL schema created automatically")
    print("   7. Migrations applied to new schema")
    print("   8. Default content preloaded")
    print("   9. Domain and user relationships set up")
    print("   10. User gets their own isolated site!")
    
    # Step 8: Simulate accessing the tenant site
    print("\n8️⃣ STEP 8: Tenant Site Access")
    print("-" * 30)
    
    frontend_url = tenant.get_frontend_url()
    if frontend_url:
        print(f"🌐 Frontend URL: {frontend_url}")
        print(f"⚙️ Admin URL: {frontend_url}admin/")
        print(f"🎯 This would resolve to tenant schema: {tenant.schema_name}")
    
    print(f"\n🎉 SUCCESS! Tenant created and ready to use!")
    print(f"📧 User {user.username} now owns site: {tenant.name}")
    print(f"🔗 Accessible at: {domain.domain}")
    
    # Cleanup option
    print(f"\n🧹 To cleanup this demo:")
    print(f"   User.objects.filter(username='{username}').delete()")
    print(f"   # Tenant and related objects will cascade delete")

if __name__ == "__main__":
    try:
        demo_automated_tenant_creation()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("💡 Make sure you have:")
        print("   - PostgreSQL running")
        print("   - django-tenants installed")
        print("   - Proper database configuration")
        import traceback
        traceback.print_exc()