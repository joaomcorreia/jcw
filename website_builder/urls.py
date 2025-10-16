from django.urls import path
from . import views

app_name = 'website_builder'

urlpatterns = [
    # Main Builder Flow
    path('', views.builder_home, name='home'),
    path('select-type/', views.select_website_type, name='select_type'),
    path('register/<str:website_type>/', views.business_registration, name='register'),
    path('build/<str:website_type>/', views.ai_builder, name='ai_builder'),
    path('template-preview/<str:website_type>/', views.template_preview, name='template_preview'),
    path('edit/<slug:slug>/', views.website_editor, name='edit'),
    path('preview/<slug:slug>/', views.website_preview, name='preview'),
    
    # Domain & Publishing
    path('domain/<slug:slug>/', views.domain_setup, name='domain_setup'),
    path('publish/<slug:slug>/', views.publish_website, name='publish'),
    
    # User Dashboard
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('my-websites/', views.my_websites, name='my_websites'),
    
    # API Endpoints
    path('api/check-domain/', views.check_domain_availability, name='check_domain'),
    path('api/generate-content/', views.generate_ai_content, name='generate_content'),
    path('api/save-website/', views.save_website_changes, name='save_changes'),
    path('api/generate-default-pages/<slug:slug>/', views.generate_default_pages_api, name='generate_default_pages'),
    
    # Payment & Orders
    path('order/domain/<slug:slug>/', views.domain_purchase, name='domain_purchase'),
    path('payment/success/<uuid:order_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/<uuid:order_id>/', views.payment_cancel, name='payment_cancel'),
]