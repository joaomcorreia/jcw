# 🚀 Deploy to Render.com Guide

## What I've Prepared for Render.com Deployment

✅ **Production-Ready Configuration**
- Added `gunicorn` WSGI server
- Configured `whitenoise` for static files
- Added `dj-database-url` for PostgreSQL
- Created `build.sh` script for Render
- Added `Procfile` for web service
- Updated `requirements.txt` with all dependencies

✅ **Django Settings Updated**
- Production database configuration (PostgreSQL)
- Environment-based DEBUG setting
- Render.com allowed hosts
- Static files configuration for production
- WhiteNoise middleware for serving static files

## 🔄 Manual Steps (Since I can't push to GitHub directly)

### 1. **Push to GitHub** 
```bash
cd c:\projects\jcw
git init
git add .
git commit -m "Initial commit: Multi-tenant Django project ready for Render deployment"
git remote add origin https://github.com/joaomcorreia/jcw.git
git branch -M main
git push -u origin main
```

### 2. **Deploy on Render.com**

1. **Go to Render.com** and sign up/login
2. **Connect GitHub** repository `joaomcorreia/jcw`
3. **Create New Web Service** with these settings:

**Basic Settings:**
- **Name**: `jcw-multi-tenant`
- **Environment**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn myproject.wsgi:application`

**Environment Variables:**
```
DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this
```

4. **Add PostgreSQL Database**:
   - Go to Dashboard → New → PostgreSQL
   - Name: `jcw-database`
   - Copy the **External Database URL**
   
5. **Add Database URL to Web Service**:
   - Go to your web service → Environment
   - Add: `DATABASE_URL=your-postgresql-url-here`

### 3. **Domain Configuration**
Once deployed, you'll get a Render URL like: `https://jcw-multi-tenant.onrender.com`

**For Custom Domain (jcwtradehub.com):**
1. In Render Dashboard → Custom Domains
2. Add: `jcwtradehub.com` and `www.jcwtradehub.com`
3. Update your DNS provider with Render's CNAME records

## 🎯 **What Will Work After Deployment**

✅ **Multi-Tenant Features**
- Domain-based tenant detection
- Admin interface with frontend connect buttons
- Homepage previews and tenant management
- JCW Trade Hub tenant ready

✅ **Production Features**
- PostgreSQL database
- Static files served via WhiteNoise
- Gunicorn WSGI server
- Environment-based configuration

## 🔧 **Post-Deployment Steps**

1. **Visit your admin**: `https://your-render-url.onrender.com/admin/`
2. **Login**: admin/admin123 (change this!)
3. **Upload homepage screenshot** for JCW Trade Hub tenant
4. **Test frontend connect** buttons
5. **Configure custom domains** in Render dashboard

## 📝 **Files Ready for Deployment**

- ✅ `build.sh` - Render build script
- ✅ `Procfile` - Web service configuration  
- ✅ `requirements.txt` - Updated with production packages
- ✅ `myproject/settings.py` - Production-ready settings
- ✅ `.gitignore` - Excludes sensitive files

Your multi-tenant Django project is **100% ready for Render.com deployment**! 🎉

Just push to GitHub and follow the Render setup steps above.