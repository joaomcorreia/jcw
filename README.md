# Multi-Tenant Django Project (JCW)

A sophisticated Django multi-tenant web application with custom homepage, admin interface, and domain-based tenant isolation.

## 🚀 Features

### **Multi-Tenancy**
- **Domain-based tenant detection**: Each tenant identified by their domain/subdomain
- **Tenant isolation**: Separate content and branding per tenant
- **Multiple domains per tenant**: Support for www, custom subdomains, etc.
- **Development-friendly**: localhost support with automatic tenant creation

### **Admin Interface**
- **Enhanced tenant management**: Visual admin with frontend connect buttons
- **Homepage previews**: Upload and preview tenant homepage screenshots
- **Custom styling**: Professional admin interface with modern design
- **Tenant-aware content**: All content linked to specific tenants

### **Frontend Features**
- **Custom Homepage**: Beautiful, responsive homepage with modern design
- **Dynamic Content**: Homepage content managed through admin panel
- **Tenant branding**: Custom titles, taglines, and styling per tenant
- **Responsive Design**: Works on all devices and screen sizes

## Quick Start

### 1. Install Dependencies
```bash
# The Python virtual environment is already set up
# Django is already installed
```

### 2. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

### 3. Access the Admin Panel
- URL: http://127.0.0.1:8000/admin/
- Username: `admin`
- Password: `admin123`

## Project Structure

```
jcw/
├── manage.py              # Django management script
├── myproject/             # Main project directory
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py
├── home/                  # Home app directory
│   ├── __init__.py
│   ├── admin.py          # Admin configuration
│   ├── apps.py
│   ├── models.py         # PageContent model
│   ├── views.py          # Homepage view
│   ├── urls.py           # App URL patterns
│   ├── migrations/       # Database migrations
│   └── templates/
│       └── home/
│           └── index.html # Homepage template
└── .venv/                # Virtual environment
```

## Admin Features

- **PageContent Management**: Create and edit homepage content
- **User Management**: Manage users and permissions
- **Custom Admin Interface**: Branded admin panel with custom headers
- **Rich Admin UI**: List views, filters, and search functionality

## Usage

1. **Visit the Homepage**: Go to http://127.0.0.1:8000/ to see your custom homepage
2. **Login to Admin**: Go to http://127.0.0.1:8000/admin/ and login with the credentials above
3. **Edit Content**: In admin, go to "Page Contents" to edit the homepage title and message
4. **See Changes**: Refresh the homepage to see your changes

## Development

### Adding New Features
- Create new apps: `python manage.py startapp appname`
- Add models in `models.py`
- Register models in `admin.py` for admin access
- Create migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`

### Creating Superusers
```bash
python manage.py createsuperuser
```

## Technology Stack

- **Django 5.2.7**: Web framework
- **SQLite**: Database (default)
- **Python 3.11**: Programming language
- **HTML/CSS**: Frontend styling

## Next Steps

- Add more models and admin configurations
- Create additional views and templates
- Add static files (CSS, JavaScript, images)
- Configure production settings
- Deploy to a production server

Enjoy building with Django! 🚀