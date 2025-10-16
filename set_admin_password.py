from django.contrib.auth.models import User

# Set password for admin user
user = User.objects.get(username='admin')
user.set_password('admin123')
user.save()
print("Admin password set successfully!")