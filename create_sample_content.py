from home.models import PageContent

# Create sample content
content, created = PageContent.objects.get_or_create(
    title="Welcome to My Amazing Django Site",
    defaults={
        'message': 'This content is managed through the Django admin panel! You can edit this by going to /admin/ and logging in with username: admin, password: admin123',
        'is_active': True
    }
)

if created:
    print("Sample content created successfully!")
else:
    print("Sample content already exists.")