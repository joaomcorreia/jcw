"""
AI Content Generation and Website Builder Services
Handles AI-powered website creation and domain management
"""
import openai
import json
import re
from django.conf import settings
from typing import Dict, List, Any


class AIContentGenerator:
    """
    Service for generating website content using AI
    Currently uses OpenAI GPT, but can be extended for other providers
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_website_structure(self, website_type: str, business_description: str, website_name: str) -> Dict[str, Any]:
        """
        Generate complete website structure based on business description
        Returns JSON with pages, content blocks, styling suggestions
        """
        
        # If no OpenAI API key, use template-based generation
        if not self.api_key:
            return self._generate_template_based(website_type, business_description, website_name)
        
        try:
            prompt = self._build_generation_prompt(website_type, business_description, website_name)
            
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional web designer and copywriter. Generate complete website structures in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse AI response as JSON
            try:
                generated_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                generated_data = self._parse_ai_text_response(ai_response)
            
            return self._enhance_generated_content(generated_data, website_type)
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_template_based(website_type, business_description, website_name)
    
    def _build_generation_prompt(self, website_type: str, business_description: str, website_name: str) -> str:
        """Build the AI prompt for website generation"""
        
        return f"""
        Generate a complete website structure for:
        
        Business: {website_name}
        Type: {website_type}
        Description: {business_description}
        
        Return a JSON object with this structure:
        {{
            "website_name": "{website_name}",
            "tagline": "Generated catchy tagline",
            "color_scheme": {{
                "primary": "#hexcolor",
                "secondary": "#hexcolor",
                "accent": "#hexcolor"
            }},
            "pages": [
                {{
                    "type": "home",
                    "slug": "home", 
                    "title": "Homepage",
                    "seo_title": "SEO optimized title",
                    "seo_description": "Meta description",
                    "content_blocks": [
                        {{
                            "type": "hero",
                            "heading": "Main headline",
                            "subheading": "Supporting text",
                            "cta_text": "Call to action",
                            "background_style": "gradient"
                        }},
                        {{
                            "type": "features", 
                            "heading": "Why Choose Us",
                            "features": [
                                {{"title": "Feature 1", "description": "Benefit description", "icon": "star"}},
                                {{"title": "Feature 2", "description": "Benefit description", "icon": "heart"}},
                                {{"title": "Feature 3", "description": "Benefit description", "icon": "check"}}
                            ]
                        }},
                        {{
                            "type": "cta",
                            "heading": "Ready to get started?",
                            "text": "Contact us today",
                            "button_text": "Get Started",
                            "style": "centered"
                        }}
                    ]
                }}
            ],
            "suggested_pages": ["about", "services", "contact"],
            "business_info": {{
                "industry": "detected industry",
                "target_audience": "target customer description", 
                "key_benefits": ["benefit1", "benefit2", "benefit3"]
            }}
        }}
        
        Make the content specific to the business description. Write compelling copy that converts visitors to customers.
        """
    
    def _generate_template_based(self, website_type: str, business_description: str, website_name: str) -> Dict[str, Any]:
        """
        Fallback template-based generation when AI is unavailable
        """
        
        templates = {
            'ecommerce': {
                'tagline': f"Premium products from {website_name}",
                'color_scheme': {'primary': '#2563eb', 'secondary': '#1e40af', 'accent': '#f59e0b'},
                'pages': [
                    {
                        'type': 'home',
                        'slug': 'home',
                        'title': 'Homepage',
                        'seo_title': f'{website_name} - Premium Online Store',
                        'seo_description': f'Shop the best products at {website_name}. {business_description[:100]}',
                        'content_blocks': [
                            {
                                'type': 'hero',
                                'heading': f'Welcome to {website_name}',
                                'subheading': business_description[:200] + '...',
                                'cta_text': 'Shop Now',
                                'background_style': 'gradient'
                            },
                            {
                                'type': 'features',
                                'heading': 'Why Shop With Us',
                                'features': [
                                    {'title': 'Quality Products', 'description': 'Only the finest materials and craftsmanship', 'icon': 'star'},
                                    {'title': 'Fast Shipping', 'description': 'Get your order delivered quickly and safely', 'icon': 'truck'},
                                    {'title': 'Secure Payments', 'description': 'Shop with confidence using our secure checkout', 'icon': 'shield'}
                                ]
                            },
                            {
                                'type': 'cta',
                                'heading': 'Ready to Shop?',
                                'text': 'Browse our collection and find your perfect item',
                                'button_text': 'Start Shopping',
                                'style': 'centered'
                            }
                        ]
                    }
                ],
                'suggested_pages': ['products', 'about', 'contact', 'shipping']
            },
            
            'business': {
                'tagline': f"Professional services from {website_name}",
                'color_scheme': {'primary': '#1f2937', 'secondary': '#374151', 'accent': '#10b981'},
                'pages': [
                    {
                        'type': 'home',
                        'slug': 'home', 
                        'title': 'Homepage',
                        'seo_title': f'{website_name} - Professional Business Services',
                        'seo_description': f'Get expert service from {website_name}. {business_description[:100]}',
                        'content_blocks': [
                            {
                                'type': 'hero',
                                'heading': f'Professional Excellence with {website_name}',
                                'subheading': business_description[:200] + '...',
                                'cta_text': 'Get Started',
                                'background_style': 'solid'
                            },
                            {
                                'type': 'features',
                                'heading': 'Our Services',
                                'features': [
                                    {'title': 'Expert Consultation', 'description': 'Get professional advice tailored to your needs', 'icon': 'user'},
                                    {'title': 'Quality Results', 'description': 'We deliver excellence in every project', 'icon': 'award'},
                                    {'title': 'Ongoing Support', 'description': 'Continuous support for your success', 'icon': 'support'}
                                ]
                            },
                            {
                                'type': 'cta',
                                'heading': 'Ready to Work Together?',
                                'text': 'Contact us today for a free consultation',
                                'button_text': 'Contact Us',
                                'style': 'centered'
                            }
                        ]
                    }
                ],
                'suggested_pages': ['about', 'services', 'team', 'contact']
            },
            
            'restaurant': {
                'tagline': f"Delicious dining at {website_name}",
                'color_scheme': {'primary': '#dc2626', 'secondary': '#991b1b', 'accent': '#f59e0b'},
                'pages': [
                    {
                        'type': 'home',
                        'slug': 'home',
                        'title': 'Homepage', 
                        'seo_title': f'{website_name} - Fine Dining Restaurant',
                        'seo_description': f'Experience exceptional dining at {website_name}. {business_description[:100]}',
                        'content_blocks': [
                            {
                                'type': 'hero',
                                'heading': f'Welcome to {website_name}',
                                'subheading': business_description[:200] + '...',
                                'cta_text': 'View Menu',
                                'background_style': 'image'
                            },
                            {
                                'type': 'features',
                                'heading': 'Why Dine With Us',
                                'features': [
                                    {'title': 'Fresh Ingredients', 'description': 'Locally sourced, premium quality ingredients', 'icon': 'leaf'},
                                    {'title': 'Expert Chefs', 'description': 'Skilled culinary artists creating amazing dishes', 'icon': 'chef'},
                                    {'title': 'Great Atmosphere', 'description': 'Perfect setting for any dining experience', 'icon': 'heart'}
                                ]
                            },
                            {
                                'type': 'cta',
                                'heading': 'Ready to Dine?',
                                'text': 'Make a reservation or order online',
                                'button_text': 'Reserve Table',
                                'style': 'centered'
                            }
                        ]
                    }
                ],
                'suggested_pages': ['menu', 'about', 'reservations', 'contact']
            }
        }
        
        # Get template for website type, fallback to business
        template = templates.get(website_type, templates['business'])
        
        # Customize with business info
        template['website_name'] = website_name
        template['business_description'] = business_description
        template['business_info'] = {
            'industry': website_type.replace('_', ' ').title(),
            'target_audience': 'Local customers and online visitors',
            'key_benefits': ['Quality Service', 'Professional Results', 'Customer Satisfaction']
        }
        
        return template
    
    def _enhance_generated_content(self, content: Dict[str, Any], website_type: str) -> Dict[str, Any]:
        """
        Enhance and validate AI-generated content
        """
        # Ensure required fields exist
        if 'pages' not in content:
            content['pages'] = []
        
        if 'color_scheme' not in content:
            content['color_scheme'] = {'primary': '#2563eb', 'secondary': '#1e40af', 'accent': '#f59e0b'}
        
        # Add website type specific enhancements
        if website_type == 'ecommerce' and not any(p.get('type') == 'products' for p in content['pages']):
            content['suggested_pages'].append('products')
        
        return content
    
    def _parse_ai_text_response(self, text_response: str) -> Dict[str, Any]:
        """
        Parse AI text response when JSON parsing fails
        Extract key information and structure it
        """
        # Basic parsing logic for non-JSON responses
        return {
            'website_name': 'Your Business',
            'tagline': 'Professional services you can trust',
            'pages': [{
                'type': 'home',
                'slug': 'home',
                'title': 'Homepage',
                'content_blocks': [{
                    'type': 'hero',
                    'heading': 'Welcome to Your Business',
                    'subheading': text_response[:200] + '...',
                    'cta_text': 'Learn More'
                }]
            }],
            'color_scheme': {'primary': '#2563eb', 'secondary': '#1e40af', 'accent': '#f59e0b'}
        }


class DomainRegistrationService:
    """
    Service for handling domain registration and DNS management
    Uses OpenProvider API for domain registration
    """
    
    def __init__(self):
        self.registrar_api_key = getattr(settings, 'DOMAIN_REGISTRAR_API_KEY', None)
        self.registrar_api_secret = getattr(settings, 'DOMAIN_REGISTRAR_API_SECRET', None)
        self.registrar_endpoint = getattr(settings, 'DOMAIN_REGISTRAR_API_URL', 'https://api.openprovider.eu/v1beta')
        self.provider = getattr(settings, 'DOMAIN_REGISTRAR_PROVIDER', 'openprovider')
    
    def check_domain_availability(self, domain_name: str) -> Dict[str, Any]:
        """
        Check if a domain is available for registration
        """
        # TODO: Implement actual domain registrar API integration
        # For now, return mock data
        
        # Basic validation
        if not self._is_valid_domain(domain_name):
            return {
                'available': False,
                'error': 'Invalid domain name format',
                'suggestions': []
            }
        
        # Mock availability check (replace with real API)
        return {
            'available': True,  # Mock - assume available
            'domain': domain_name,
            'price': 12.99,
            'currency': 'USD',
            'registration_period': 1,  # years
            'suggestions': self._generate_domain_suggestions(domain_name)
        }
    
    def register_domain(self, domain_name: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a domain with the registrar
        """
        # TODO: Implement actual domain registration API
        
        return {
            'success': True,  # Mock success
            'domain': domain_name,
            'registration_id': f'REG_{domain_name.replace(".", "_").upper()}',
            'status': 'pending',
            'expires_at': '2025-10-16T00:00:00Z'
        }
    
    def setup_dns_records(self, domain_name: str, target_ip: str) -> Dict[str, Any]:
        """
        Setup DNS records to point domain to our hosting
        """
        # TODO: Implement DNS management API
        
        return {
            'success': True,
            'dns_records': [
                {'type': 'A', 'name': '@', 'value': target_ip, 'ttl': 300},
                {'type': 'CNAME', 'name': 'www', 'value': domain_name, 'ttl': 300}
            ]
        }
    
    def _is_valid_domain(self, domain: str) -> bool:
        """
        Validate domain name format
        """
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, domain)) and len(domain) <= 253
    
    def _generate_domain_suggestions(self, domain: str) -> List[str]:
        """
        Generate alternative domain suggestions
        """
        base_name = domain.split('.')[0]
        extensions = ['.com', '.net', '.org', '.io', '.co']
        
        suggestions = []
        for ext in extensions:
            if f"{base_name}{ext}" != domain:
                suggestions.append(f"{base_name}{ext}")
        
        # Add modifier suggestions
        modifiers = ['get', 'the', 'my', 'try', 'go']
        for modifier in modifiers:
            suggestions.append(f"{modifier}{base_name}.com")
        
        return suggestions[:5]  # Return top 5 suggestions