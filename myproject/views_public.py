# myproject/views_public.py - Public Schema Views
"""
Views for the public schema (main domain)
Handles landing page, registration, and tenant management
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from tenants.models import Tenant, Domain
from tenants.services import TenantCreationService


def landing_page(request):
    """
    Main landing page for the SaaS platform
    """
    context = {
        'site_title': 'JCW Trade Hub - Multi-Tenant SaaS Platform',
        'features': [
            'Instant Site Creation',
            'Custom Domains',
            'Multi-Tenant Architecture',
            'Secure Data Isolation',
            'Scalable Infrastructure',
        ]
    }
    return render(request, 'public/landing.html', context)


def register_view(request):
    """
    User registration with automatic tenant creation
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-create tenant for new user
            tenant, domain, message = TenantCreationService.create_tenant_for_user(
                user=user,
                preload_content=True
            )
            
            if tenant:
                # Log user in and redirect to their new site
                login(request, user)
                messages.success(request, f'Account created! Your site is ready at {domain.domain}')
                return redirect('my_tenants')
            else:
                messages.error(request, f'Account created but site setup failed: {message}')
                login(request, user)
                return redirect('my_tenants')
    else:
        form = UserCreationForm()
    
    return render(request, 'public/register.html', {'form': form})


def login_view(request):
    """
    User login
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'my_tenants')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'public/login.html')


def logout_view(request):
    """
    User logout
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('landing_page')


@login_required
def my_tenants_view(request):
    """
    Display user's tenants and allow creation of new ones
    """
    owned_tenants = request.user.owned_tenants.all()
    member_tenants = request.user.tenant_memberships.exclude(
        tenant__in=owned_tenants
    ).select_related('tenant')
    
    context = {
        'owned_tenants': owned_tenants,
        'member_tenants': member_tenants,
    }
    return render(request, 'public/my_tenants.html', context)


@login_required
def create_tenant_view(request):
    """
    Create a new tenant for the logged-in user
    """
    if request.method == 'POST':
        tenant_name = request.POST.get('tenant_name', '').strip()
        subdomain = request.POST.get('subdomain', '').strip()
        plan = request.POST.get('plan', 'free')
        
        if not tenant_name:
            messages.error(request, 'Tenant name is required')
            return render(request, 'public/create_tenant.html')
        
        # Create tenant
        tenant, domain, message = TenantCreationService.create_tenant_for_user(
            user=request.user,
            tenant_name=tenant_name,
            subdomain=subdomain or None,
            plan=plan,
            preload_content=True
        )
        
        if tenant:
            messages.success(request, message)
            return redirect('my_tenants')
        else:
            messages.error(request, message)
    
    return render(request, 'public/create_tenant.html')


@require_http_methods(["GET"])
def check_domain_availability(request):
    """
    AJAX endpoint to check if a subdomain is available
    """
    subdomain = request.GET.get('subdomain', '').strip().lower()
    
    if not subdomain:
        return JsonResponse({'available': False, 'message': 'Subdomain is required'})
    
    # Sanitize subdomain
    clean_subdomain = TenantCreationService.sanitize_schema_name(subdomain)
    
    # Check availability
    available = not Tenant.objects.filter(schema_name=clean_subdomain).exists()
    
    response_data = {
        'available': available,
        'subdomain': clean_subdomain,
        'message': 'Available' if available else 'Already taken'
    }
    
    if clean_subdomain != subdomain:
        response_data['suggested'] = clean_subdomain
        response_data['message'] = f'Suggested: {clean_subdomain}'
    
    return JsonResponse(response_data)