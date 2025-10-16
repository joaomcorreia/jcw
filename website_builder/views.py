from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import WebsiteProject, WebsiteDomain, WebsiteContent, DomainOrder, AIWebsiteTemplate
from .services import AIContentGenerator, DomainRegistrationService
import json


def builder_home(request):
    """
    Landing page for the website builder
    Shows the main "Build Website" button and features
    """
    context = {
        'website_types': WebsiteProject.WEBSITE_TYPES,
        'recent_websites': WebsiteProject.objects.filter(is_published=True)[:6] if not request.user.is_authenticated else None,
    }
    return render(request, 'website_builder/home.html', context)


def select_website_type(request):
    """
    Step 1: User selects website type (e-commerce, business, blog, etc.)
    """
    if request.method == 'POST':
        website_type = request.POST.get('website_type')
        if website_type in dict(WebsiteProject.WEBSITE_TYPES):
            return redirect('website_builder:register', website_type=website_type)
        else:
            messages.error(request, 'Invalid website type selected.')
    
    context = {
        'website_types': [
            {
                'value': value,
                'label': label,
                'description': get_website_type_description(value),
                'icon': get_website_type_icon(value),
            }
            for value, label in WebsiteProject.WEBSITE_TYPES
        ]
    }
    return render(request, 'website_builder/select_type.html', context)


def business_registration(request, website_type):
    """
    Step 2: User registers with business and admin details
    Creates account and redirects to AI builder
    """
    if request.method == 'POST':
        # User account creation
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Business details
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        business_name = request.POST.get('business_name', '').strip()
        business_phone = request.POST.get('business_phone', '').strip()
        
        # Validate required fields based on user status
        if request.user.is_authenticated:
            # Existing user - only business name is required
            if not business_name:
                messages.error(request, 'Please provide a business name.')
                return render(request, 'website_builder/register.html', {
                    'website_type': website_type,
                    'website_type_display': dict(WebsiteProject.WEBSITE_TYPES).get(website_type),
                    'form_data': request.POST,
                    'is_existing_user': True,
                    'user': request.user
                })
        else:
            # New user - validate all account fields
            if not all([username, email, password, confirm_password, first_name, last_name, business_name]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'website_builder/register.html', {
                    'website_type': website_type,
                    'website_type_display': dict(WebsiteProject.WEBSITE_TYPES).get(website_type),
                    'form_data': request.POST,
                    'is_existing_user': False
                })
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'website_builder/register.html', {
                    'website_type': website_type,
                    'website_type_display': dict(WebsiteProject.WEBSITE_TYPES).get(website_type),
                    'form_data': request.POST,
                    'is_existing_user': False
                })
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose another.')
                return render(request, 'website_builder/register.html', {
                    'website_type': website_type,
                    'website_type_display': dict(WebsiteProject.WEBSITE_TYPES).get(website_type),
                    'form_data': request.POST,
                    'is_existing_user': False
                })
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered. Please use a different email or login.')
                return render(request, 'website_builder/register.html', {
                    'website_type': website_type,
                    'website_type_display': dict(WebsiteProject.WEBSITE_TYPES).get(website_type),
                    'form_data': request.POST,
                    'is_existing_user': False
                })
        
        # Get address fields
        business_address_line1 = request.POST.get('business_address_line1', '').strip()
        business_address_line2 = request.POST.get('business_address_line2', '').strip()
        business_city = request.POST.get('business_city', '').strip()
        business_state = request.POST.get('business_state', '').strip()
        business_postal_code = request.POST.get('business_postal_code', '').strip()
        business_country = request.POST.get('business_country', 'United States').strip()
        
        # Store business details in session for later use
        request.session['business_details'] = {
            'business_name': business_name,
            'business_phone': business_phone,
            'business_address_line1': business_address_line1,
            'business_address_line2': business_address_line2,
            'business_city': business_city,
            'business_state': business_state,
            'business_postal_code': business_postal_code,
            'business_country': business_country,
            'website_type': website_type
        }
        
        # Handle existing users vs new users
        if request.user.is_authenticated:
            # Existing user - just store business details and continue
            messages.success(request, f'Business details saved! Let\'s build your {business_name} website!')
            return redirect('website_builder:ai_builder', website_type=website_type)
        else:
            # New user - create account first
            try:
                # Create user account
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Authenticate and login user
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f'Welcome {first_name}! Your account has been created. Let\'s build your {business_name} website!')
                    return redirect('website_builder:ai_builder', website_type=website_type)
                else:
                    messages.error(request, 'Account created but login failed. Please try logging in manually.')
            
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    
    # Handle already logged in users - they still need to provide business details
    is_existing_user = request.user.is_authenticated
    
    context = {
        'website_type': website_type,
        'website_type_display': dict(WebsiteProject.WEBSITE_TYPES).get(website_type),
        'website_type_icon': get_website_type_icon(website_type),
        'is_existing_user': is_existing_user,
        'user': request.user if is_existing_user else None,
    }
    return render(request, 'website_builder/register.html', context)


@login_required
def ai_builder(request, website_type):
    """
    Step 3: AI-powered website builder
    User describes their business, AI generates website
    """
    # Get business details from registration
    business_details = request.session.get('business_details', {})
    business_name = business_details.get('business_name', f"{request.user.get_full_name()}'s Business")
    
    if request.method == 'POST':
        business_description = request.POST.get('business_description', '').strip()
        website_name = request.POST.get('website_name', '').strip() or business_name
        
        if not business_description:
            messages.error(request, 'Please describe your business to help AI generate your website.')
            return render(request, 'website_builder/ai_builder.html', {
                'website_type': website_type,
                'website_type_display': dict(WebsiteProject.WEBSITE_TYPES).get(website_type),
                'business_name': business_name,
                'business_details': business_details
            })
        
        # Create new website project with business address details
        website = WebsiteProject.objects.create(
            user=request.user,
            name=website_name,
            website_type=website_type,
            ai_description=business_description,
            business_address_line1=business_details.get('business_address_line1', ''),
            business_address_line2=business_details.get('business_address_line2', ''),
            business_city=business_details.get('business_city', ''),
            business_state=business_details.get('business_state', ''),
            business_postal_code=business_details.get('business_postal_code', ''),
            business_country=business_details.get('business_country', 'United States'),
            status='draft'
        )
        
        # Generate AI content
        try:
            ai_generator = AIContentGenerator()
            generated_content = ai_generator.generate_website_structure(
                website_type=website_type,
                business_description=business_description,
                website_name=website_name
            )
            
            website.ai_generated_data = generated_content
            website.status = 'preview'
            website.save()
            
            # Create default pages
            create_default_pages(website, generated_content)
            
            messages.success(request, f'🎉 Your website "{website_name}" has been generated! Review and customize it below.')
            return redirect('website_builder:edit', slug=website.slug)
            
        except Exception as e:
            messages.error(request, f'Failed to generate website: {str(e)}')
            website.delete()  # Clean up failed creation
    
    context = {
        'website_type': website_type,
        'website_type_display': dict(WebsiteProject.WEBSITE_TYPES).get(website_type),
        'business_name': business_name,
        'business_details': business_details,
        'sample_descriptions': get_sample_descriptions(website_type),
    }
    return render(request, 'website_builder/ai_builder.html', context)


@xframe_options_exempt
def template_preview(request, website_type):
    """
    Generate preview template for iframe display in AI builder and website editor
    """
    # Get business details from session or URL parameters
    business_details = request.session.get('business_details', {})
    
    # Allow business name to be passed as URL parameter (for website editor preview)
    business_name = request.GET.get('business_name') or business_details.get('business_name', 'Your Business')
    
    context = {
        'website_type': website_type,
        'business_name': business_name,
        'business_email': business_details.get('business_email', 'contact@yourbusiness.com'),
        'business_phone': business_details.get('business_phone', '(555) 123-4567'),
        'business_city': business_details.get('business_city', 'Your City'),
        'business_state': business_details.get('business_state', 'State'),
    }
    return render(request, 'website_builder/simple_preview_template.html', context)


@login_required
def website_editor(request, slug):
    """
    Step 3: Website editor/customization interface
    User can modify AI-generated content
    """
    website = get_object_or_404(WebsiteProject, slug=slug, user=request.user)
    pages = website.pages.all()
    
    context = {
        'website': website,
        'pages': pages,
        'editor_config': {
            'website_id': str(website.id),
            'api_base': '/website-builder/api/',
            'preview_url': website.get_absolute_url(),
        }
    }
    return render(request, 'website_builder/editor.html', context)


@login_required
def website_preview(request, slug):
    """
    Preview the website as it would appear live
    """
    website = get_object_or_404(WebsiteProject, slug=slug, user=request.user)
    pages = website.pages.all()
    
    # Get homepage or first page
    homepage = pages.filter(page_type='home').first() or pages.first()
    
    context = {
        'website': website,
        'page': homepage,
        'pages': pages,
        'is_preview': True,
    }
    return render(request, 'website_builder/preview.html', context)


@login_required
def domain_setup(request, slug):
    """
    Step 4: Domain selection and setup
    User chooses subdomain, buys domain, or connects custom domain
    """
    website = get_object_or_404(WebsiteProject, slug=slug, user=request.user)
    
    if request.method == 'POST':
        domain_type = request.POST.get('domain_type')
        
        if domain_type == 'subdomain':
            # Free subdomain setup
            subdomain = request.POST.get('subdomain', '').strip().lower()
            full_domain = f"{subdomain}.justcodeworks.eu"
            
            if WebsiteDomain.objects.filter(domain_name=full_domain).exists():
                messages.error(request, f'Subdomain "{subdomain}" is already taken.')
            else:
                domain = WebsiteDomain.objects.create(
                    website=website,
                    domain_type='subdomain',
                    domain_name=full_domain,
                    is_active=True,
                    registration_status='active'
                )
                messages.success(request, f'🎉 Your website is ready at {full_domain}!')
                return redirect('website_builder:publish', slug=website.slug)
        
        elif domain_type == 'purchased':
            # Domain purchase flow
            domain_name = request.POST.get('domain_name', '').strip().lower()
            return redirect('website_builder:domain_purchase', slug=website.slug)
        
        elif domain_type == 'custom':
            # Custom domain connection
            custom_domain = request.POST.get('custom_domain', '').strip().lower()
            # TODO: Implement DNS setup instructions
            messages.info(request, 'Custom domain setup requires DNS configuration. Instructions sent to your email.')
    
    # Check if domain already exists
    existing_domain = getattr(website, 'domain', None)
    
    context = {
        'website': website,
        'existing_domain': existing_domain,
        'suggested_subdomains': generate_subdomain_suggestions(website.name),
    }
    return render(request, 'website_builder/domain_setup.html', context)


@login_required
def publish_website(request, slug):
    """
    Final step: Publish the website and make it live
    """
    website = get_object_or_404(WebsiteProject, slug=slug, user=request.user)
    
    if not hasattr(website, 'domain') or not website.domain.is_active:
        messages.error(request, 'Please set up a domain before publishing.')
        return redirect('website_builder:domain_setup', slug=website.slug)
    
    if request.method == 'POST':
        website.is_published = True
        website.published_at = timezone.now()
        website.status = 'published'
        website.save()
        
        messages.success(request, f'🚀 Your website is now live at {website.get_live_url()}!')
        return redirect('website_builder:dashboard')
    
    context = {
        'website': website,
        'domain': website.domain,
        'live_url': website.get_live_url(),
    }
    return render(request, 'website_builder/publish.html', context)


@login_required
def user_dashboard(request):
    """
    User's main dashboard showing all their websites
    """
    websites = WebsiteProject.objects.filter(user=request.user)
    
    context = {
        'websites': websites,
        'draft_count': websites.filter(status='draft').count(),
        'published_count': websites.filter(is_published=True).count(),
    }
    return render(request, 'website_builder/dashboard.html', context)


@login_required
def my_websites(request):
    """
    Detailed list of user's websites with management options
    """
    websites = WebsiteProject.objects.filter(user=request.user)
    return render(request, 'website_builder/my_websites.html', {'websites': websites})


# API Views
@require_http_methods(["GET"])
def check_domain_availability(request):
    """
    AJAX API to check if a domain/subdomain is available
    """
    domain = request.GET.get('domain', '').strip().lower()
    domain_type = request.GET.get('type', 'subdomain')
    
    if domain_type == 'subdomain':
        full_domain = f"{domain}.justcodeworks.eu"
        available = not WebsiteDomain.objects.filter(domain_name=full_domain).exists()
        suggested = []
        
        if not available:
            # Generate suggestions
            for i in range(1, 4):
                suggestion = f"{domain}{i}.justcodeworks.eu"
                if not WebsiteDomain.objects.filter(domain_name=suggestion).exists():
                    suggested.append(suggestion.replace('.justcodeworks.eu', ''))
    else:
        # Check external domain availability (requires domain registrar API)
        available = True  # TODO: Implement real domain checking
        suggested = []
    
    return JsonResponse({
        'available': available,
        'domain': domain,
        'full_domain': full_domain if domain_type == 'subdomain' else domain,
        'suggestions': suggested,
    })


# Helper Functions
def get_website_type_description(website_type):
    descriptions = {
        'ecommerce': 'Sell products online with shopping cart, payments, and inventory management',
        'business': 'Professional company website with services, team, and contact information',
        'blog': 'Personal or professional blog with articles, categories, and social sharing',
        'portfolio': 'Showcase your creative work, projects, and artistic achievements',
        'agency': 'Marketing agency site with case studies, client testimonials, and lead generation',
        'education': 'Educational platform for courses, tutorials, and learning resources',
        'restaurant': 'Restaurant website with menu, reservations, and online ordering',
        'real_estate': 'Real estate site with property listings, search, and agent profiles',
        'nonprofit': 'Non-profit organization site with donation system and volunteer management',
        'other': 'Custom website tailored to your specific business needs',
    }
    return descriptions.get(website_type, 'Custom website for your business')


def get_website_type_icon(website_type):
    icons = {
        'ecommerce': '🏪', 'business': '💼', 'blog': '📝', 'portfolio': '🎨',
        'agency': '📊', 'education': '🎓', 'restaurant': '🍕', 'real_estate': '🏠',
        'nonprofit': '🤝', 'other': '🔧'
    }
    return icons.get(website_type, '🌐')


def get_sample_descriptions(website_type):
    samples = {
        'ecommerce': [
            "We sell handmade jewelry with unique designs inspired by nature. Our customers love eco-friendly materials and personalized pieces.",
            "Online electronics store specializing in gaming accessories and computer components with fast shipping worldwide.",
        ],
        'business': [
            "Professional accounting firm serving small businesses for over 15 years. We handle bookkeeping, taxes, and financial consulting.",
            "Digital marketing agency helping local businesses grow their online presence through SEO, social media, and advertising.",
        ],
        'restaurant': [
            "Family-owned Italian restaurant serving authentic pasta dishes made from scratch with imported ingredients from Italy.",
            "Modern coffee shop with artisanal roasts, fresh pastries, and a cozy atmosphere perfect for remote work.",
        ],
    }
    return samples.get(website_type, [])


def generate_subdomain_suggestions(website_name):
    """Generate subdomain suggestions based on website name"""
    import re
    base = re.sub(r'[^a-zA-Z0-9]', '', website_name.lower())[:15]
    return [base, f"{base}site", f"{base}online", f"my{base}"]


def create_default_pages(website, ai_content):
    """Create comprehensive default pages with business-specific content"""
    
    # Get business information
    business_name = website.name
    business_description = website.ai_description
    business_type = website.get_website_type_display()
    user = website.user
    
    # Build address string
    address_parts = []
    if website.business_address_line1:
        address_parts.append(website.business_address_line1)
    if website.business_address_line2:
        address_parts.append(website.business_address_line2)
    if website.business_city:
        city_state = website.business_city
        if website.business_state:
            city_state += f", {website.business_state}"
        if website.business_postal_code:
            city_state += f" {website.business_postal_code}"
        address_parts.append(city_state)
    if website.business_country and website.business_country != 'United States':
        address_parts.append(website.business_country)
    
    full_address = ", ".join(address_parts) if address_parts else ""
    
    # Generate services based on business type
    services = generate_default_services(website.website_type, business_description)
    
    # Create Home Page with comprehensive content
    home_content_blocks = [
        # Hero Section
        {
            "type": "hero",
            "heading": f"Welcome to {business_name}",
            "subheading": f"Professional {business_type.lower()} services you can trust",
            "text": business_description[:200] + "..." if len(business_description) > 200 else business_description,
            "cta_text": "Learn More About Us",
            "cta_link": "#about",
            "background_image": "/static/images/hero-bg.jpg",
            "style": "centered"
        },
        
        # About Section
        {
            "type": "about",
            "heading": f"About {business_name}",
            "text": f"""
                <p>{business_description}</p>
                <p>At {business_name}, we are committed to delivering exceptional {business_type.lower()} services. 
                Our experienced team understands the unique needs of our clients and works tirelessly to exceed expectations.</p>
                <p>Whether you're looking for {get_business_focus(website.website_type)}, we have the expertise and 
                dedication to help you achieve your goals.</p>
            """,
            "image": "/static/images/about-us.jpg",
            "features": [
                "Experienced professionals",
                "Customer-focused approach", 
                "Quality guaranteed",
                "Competitive pricing"
            ]
        },
        
        # Services Section
        {
            "type": "services",
            "heading": "Our Services",
            "subheading": f"Comprehensive {business_type.lower()} solutions tailored to your needs",
            "services": services
        },
        
        # Contact Section
        {
            "type": "contact",
            "heading": "Get In Touch",
            "subheading": "Ready to get started? Contact us today for a consultation.",
            "contact_info": {
                "business_name": business_name,
                "address": full_address,
                "phone": "Contact us for phone number",
                "email": user.email,
                "hours": get_default_hours(website.website_type)
            },
            "form_fields": [
                {"name": "name", "label": "Full Name", "type": "text", "required": True},
                {"name": "email", "label": "Email Address", "type": "email", "required": True},
                {"name": "phone", "label": "Phone Number", "type": "tel", "required": False},
                {"name": "service", "label": "Service Interested In", "type": "select", "required": False,
                 "options": [service["title"] for service in services]},
                {"name": "message", "label": "Message", "type": "textarea", "required": True}
            ],
            "map_embed": generate_map_embed(full_address) if full_address else None
        }
    ]
    
    # Create Home Page
    WebsiteContent.objects.create(
        website=website,
        page_type='home',
        page_slug='home',
        page_title=f'{business_name} - {business_type}',
        content_blocks=home_content_blocks,
        seo_title=f'{business_name} - Professional {business_type} Services',
        seo_description=f'{business_description[:150]}... Contact us today!'
    )
    
    # Create About Page
    about_content_blocks = [
        {
            "type": "page_header",
            "heading": f"About {business_name}",
            "subheading": f"Learn more about our {business_type.lower()} company"
        },
        {
            "type": "text_image",
            "heading": "Our Story",
            "text": f"""
                <p>{business_description}</p>
                <p>Founded with a vision to provide exceptional {business_type.lower()} services, {business_name} 
                has grown to become a trusted name in the industry. We believe in building lasting relationships 
                with our clients through transparency, quality, and outstanding customer service.</p>
                <p>Our team of professionals brings years of experience and expertise to every project, 
                ensuring that you receive the best possible service and results.</p>
            """,
            "image": "/static/images/our-story.jpg",
            "layout": "text_left"
        },
        {
            "type": "team",
            "heading": "Our Team",
            "text": "Meet the professionals behind our success",
            "team_members": [
                {
                    "name": user.get_full_name() or user.username,
                    "title": "Founder & Owner",
                    "bio": f"Leading {business_name} with passion and expertise.",
                    "image": "/static/images/team-placeholder.jpg"
                }
            ]
        }
    ]
    
    WebsiteContent.objects.create(
        website=website,
        page_type='about',
        page_slug='about',
        page_title=f'About {business_name}',
        content_blocks=about_content_blocks,
        seo_title=f'About {business_name} - Our Story and Team',
        seo_description=f'Learn about {business_name} and our commitment to excellence in {business_type.lower()} services.'
    )
    
    # Create Services Page
    services_content_blocks = [
        {
            "type": "page_header",
            "heading": "Our Services",
            "subheading": f"Comprehensive {business_type.lower()} solutions"
        },
        {
            "type": "services_detailed",
            "services": services
        },
        {
            "type": "cta",
            "heading": "Ready to Get Started?",
            "text": "Contact us today to discuss your needs and get a personalized quote.",
            "cta_text": "Get a Quote",
            "cta_link": "/contact"
        }
    ]
    
    WebsiteContent.objects.create(
        website=website,
        page_type='services',
        page_slug='services',
        page_title=f'{business_name} Services',
        content_blocks=services_content_blocks,
        seo_title=f'{business_name} Services - Professional {business_type}',
        seo_description=f'Explore our comprehensive {business_type.lower()} services. Quality solutions tailored to your needs.'
    )
    
    # Create Contact Page
    contact_content_blocks = [
        {
            "type": "page_header",
            "heading": "Contact Us",
            "subheading": "Get in touch with our team"
        },
        {
            "type": "contact_full",
            "contact_info": {
                "business_name": business_name,
                "address": full_address,
                "phone": "Contact us for phone number",
                "email": user.email,
                "hours": get_default_hours(website.website_type)
            },
            "form_fields": [
                {"name": "name", "label": "Full Name", "type": "text", "required": True},
                {"name": "email", "label": "Email Address", "type": "email", "required": True},
                {"name": "phone", "label": "Phone Number", "type": "tel", "required": False},
                {"name": "service", "label": "Service Interested In", "type": "select", "required": False,
                 "options": [service["title"] for service in services]},
                {"name": "message", "label": "Message", "type": "textarea", "required": True}
            ],
            "map_embed": generate_map_embed(full_address) if full_address else None
        }
    ]
    
    WebsiteContent.objects.create(
        website=website,
        page_type='contact',
        page_slug='contact',
        page_title=f'Contact {business_name}',
        content_blocks=contact_content_blocks,
        seo_title=f'Contact {business_name} - Get in Touch',
        seo_description=f'Contact {business_name} for professional {business_type.lower()} services. {full_address}'
    )


def generate_default_services(website_type, business_description):
    """Generate default services based on website type and description"""
    services_map = {
        'restaurant': [
            {"title": "Dine-In Experience", "description": "Enjoy our carefully crafted dishes in a comfortable atmosphere.", "icon": "🍽️"},
            {"title": "Takeout & Delivery", "description": "Get your favorite meals delivered or ready for pickup.", "icon": "🚚"},
            {"title": "Catering Services", "description": "Let us cater your special events and gatherings.", "icon": "🎉"},
            {"title": "Private Events", "description": "Host your private parties and celebrations with us.", "icon": "🥂"},
            {"title": "Custom Menu Planning", "description": "Work with our chefs to create custom menus.", "icon": "📋"},
            {"title": "Cooking Classes", "description": "Learn to cook your favorite dishes with our experts.", "icon": "👩‍🍳"}
        ],
        'business': [
            {"title": "Consulting Services", "description": "Expert advice to help your business grow and succeed.", "icon": "💼"},
            {"title": "Strategy Development", "description": "Create comprehensive strategies for your business goals.", "icon": "📊"},
            {"title": "Process Optimization", "description": "Streamline your operations for maximum efficiency.", "icon": "⚙️"},
            {"title": "Training & Development", "description": "Enhance your team's skills and capabilities.", "icon": "🎓"},
            {"title": "Project Management", "description": "Professional project management from start to finish.", "icon": "📅"},
            {"title": "Technology Solutions", "description": "Implement the right technology for your business needs.", "icon": "💻"}
        ],
        'ecommerce': [
            {"title": "Product Catalog", "description": "Browse our extensive selection of quality products.", "icon": "🛍️"},
            {"title": "Secure Checkout", "description": "Safe and secure payment processing for your peace of mind.", "icon": "🔒"},
            {"title": "Fast Shipping", "description": "Quick and reliable delivery to your doorstep.", "icon": "📦"},
            {"title": "Customer Support", "description": "Dedicated support team ready to help with any questions.", "icon": "🎧"},
            {"title": "Returns & Exchanges", "description": "Easy returns and exchanges with our hassle-free policy.", "icon": "↩️"},
            {"title": "Loyalty Program", "description": "Earn rewards and discounts with every purchase.", "icon": "⭐"}
        ],
        'portfolio': [
            {"title": "Creative Design", "description": "Innovative and unique design solutions for your projects.", "icon": "🎨"},
            {"title": "Brand Development", "description": "Create a strong brand identity that stands out.", "icon": "🏷️"},
            {"title": "Digital Marketing", "description": "Comprehensive digital marketing strategies and campaigns.", "icon": "📱"},
            {"title": "Web Development", "description": "Custom websites and web applications built to perfection.", "icon": "💻"},
            {"title": "Photography", "description": "Professional photography services for all occasions.", "icon": "📸"},
            {"title": "Video Production", "description": "High-quality video content for your business needs.", "icon": "🎬"}
        ]
    }
    
    # Default generic services
    default_services = [
        {"title": "Professional Services", "description": "High-quality professional services tailored to your needs.", "icon": "⭐"},
        {"title": "Customer Support", "description": "Dedicated customer support to ensure your satisfaction.", "icon": "🎧"},
        {"title": "Quality Guarantee", "description": "We stand behind our work with a comprehensive quality guarantee.", "icon": "✅"},
        {"title": "Flexible Solutions", "description": "Customizable solutions that adapt to your specific requirements.", "icon": "🔧"},
        {"title": "Expert Team", "description": "Work with experienced professionals who know the industry.", "icon": "👥"},
        {"title": "Ongoing Support", "description": "Continued support and maintenance for long-term success.", "icon": "🤝"}
    ]
    
    return services_map.get(website_type, default_services)


def get_business_focus(website_type):
    """Get business focus description based on website type"""
    focus_map = {
        'restaurant': 'delicious dining experiences, catering, or private events',
        'business': 'professional consulting, strategy development, or process optimization',
        'ecommerce': 'quality products, secure shopping, or customer service',
        'portfolio': 'creative design, brand development, or digital marketing',
        'agency': 'marketing solutions, campaign management, or brand strategy',
        'education': 'learning solutions, training programs, or educational content',
        'real_estate': 'property sales, rentals, or real estate consulting',
        'nonprofit': 'community support, fundraising, or volunteer opportunities'
    }
    return focus_map.get(website_type, 'professional services and solutions')


def get_default_hours(website_type):
    """Generate default business hours based on website type"""
    hours_map = {
        'restaurant': {
            'Monday': '11:00 AM - 10:00 PM',
            'Tuesday': '11:00 AM - 10:00 PM', 
            'Wednesday': '11:00 AM - 10:00 PM',
            'Thursday': '11:00 AM - 10:00 PM',
            'Friday': '11:00 AM - 11:00 PM',
            'Saturday': '11:00 AM - 11:00 PM',
            'Sunday': '12:00 PM - 9:00 PM'
        },
        'business': {
            'Monday': '9:00 AM - 5:00 PM',
            'Tuesday': '9:00 AM - 5:00 PM',
            'Wednesday': '9:00 AM - 5:00 PM', 
            'Thursday': '9:00 AM - 5:00 PM',
            'Friday': '9:00 AM - 5:00 PM',
            'Saturday': 'By Appointment',
            'Sunday': 'Closed'
        }
    }
    
    # Default business hours
    default_hours = {
        'Monday': '9:00 AM - 6:00 PM',
        'Tuesday': '9:00 AM - 6:00 PM',
        'Wednesday': '9:00 AM - 6:00 PM',
        'Thursday': '9:00 AM - 6:00 PM', 
        'Friday': '9:00 AM - 6:00 PM',
        'Saturday': '10:00 AM - 4:00 PM',
        'Sunday': 'Closed'
    }
    
    return hours_map.get(website_type, default_hours)


def generate_map_embed(address):
    """Generate Google Maps embed URL from address"""
    if not address:
        return None
    
    # Clean and encode address for Google Maps
    import urllib.parse
    encoded_address = urllib.parse.quote(address)
    
    # Return Google Maps embed URL
    return f"https://www.google.com/maps/embed/v1/place?key=YOUR_GOOGLE_MAPS_API_KEY&q={encoded_address}"


@require_http_methods(["POST"])
def generate_ai_content(request):
    """
    API endpoint for generating AI content
    Used by AJAX calls from the frontend
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        website_type = data.get('website_type')
        business_description = data.get('business_description')
        website_name = data.get('website_name')
        
        if not all([website_type, business_description]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Generate AI content
        ai_generator = AIContentGenerator()
        ai_content = ai_generator.generate_website_content(
            website_type=website_type,
            business_description=business_description,
            website_name=website_name or f"My {website_type.title()} Website"
        )
        
        return JsonResponse({
            'success': True,
            'content': ai_content
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def save_website_changes(request):
    """
    API endpoint for saving website changes
    Used by AJAX calls from the website editor
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        website_id = data.get('website_id')
        changes = data.get('changes', {})
        
        if not website_id:
            return JsonResponse({'error': 'Website ID required'}, status=400)
        
        # Get the website project
        website = get_object_or_404(WebsiteProject, id=website_id, user=request.user)
        
        # Update website data
        if 'name' in changes:
            website.website_name = changes['name']
        if 'description' in changes:
            website.business_description = changes['description']
        
        website.save()
        
        # Update content if provided
        if 'content' in changes:
            content_data = changes['content']
            for page_data in content_data.get('pages', []):
                content, created = WebsiteContent.objects.get_or_create(
                    website=website,
                    page_slug=page_data.get('slug', 'home'),
                    defaults={
                        'page_type': page_data.get('type', 'custom'),
                        'page_title': page_data.get('title', 'Untitled'),
                    }
                )
                content.content_blocks = page_data.get('content_blocks', [])
                content.seo_title = page_data.get('seo_title', '')
                content.seo_description = page_data.get('seo_description', '')
                content.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Website updated successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def domain_purchase(request, slug):
    """
    Handle domain purchase process
    """
    domain = get_object_or_404(WebsiteDomain, slug=slug, website__user=request.user)
    
    if request.method == 'POST':
        # Create domain order
        order = DomainOrder.objects.create(
            user=request.user,
            domain=domain,
            domain_name=domain.domain_name,
            domain_price=domain.price,
            order_status='pending'
        )
        
        # In a real implementation, redirect to payment processor
        # For now, simulate successful purchase
        order.order_status = 'completed'
        order.save()
        
        domain.registration_status = 'registered'
        domain.save()
        
        messages.success(request, f'Domain {domain.domain_name} purchased successfully!')
        return redirect('website_builder:payment_success', order_id=order.id)
    
    context = {
        'domain': domain,
        'website': domain.website,
    }
    return render(request, 'website_builder/domain_purchase.html', context)


def payment_success(request, order_id):
    """
    Payment success page
    """
    order = get_object_or_404(DomainOrder, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'domain': order.domain,
        'website': order.domain.website if order.domain else None,
    }
    return render(request, 'website_builder/payment_success.html', context)


def payment_cancel(request, order_id):
    """
    Payment cancellation page
    """
    order = get_object_or_404(DomainOrder, id=order_id, user=request.user)
    
    # Update order status
    order.order_status = 'cancelled'
    order.save()
    
    context = {
        'order': order,
        'domain': order.domain,
        'website': order.domain.website if order.domain else None,
    }
    return render(request, 'website_builder/payment_cancel.html', context)


@login_required
@require_http_methods(["POST"])
def generate_default_pages_api(request, slug):
    """
    API endpoint to generate default pages for a website
    """
    website = get_object_or_404(WebsiteProject, slug=slug, user=request.user)
    
    try:
        # Generate AI content based on website details
        business_details = {
            'business_name': website.name,
            'website_type': website.website_type,
        }
        
        ai_generator = AIContentGenerator()
        generated_content = ai_generator.generate_website_structure(
            website_type=website.website_type,
            business_description=f"A {website.get_website_type_display()} website",
            website_name=website.name
        )
        
        # Create default pages using existing function
        create_default_pages(website, generated_content)
        
        return JsonResponse({
            'success': True,
            'message': 'Default pages generated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })