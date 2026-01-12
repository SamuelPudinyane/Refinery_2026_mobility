# Deployment Guide

This guide covers deploying the Mobility App to various platforms.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Render.com Deployment](#rendercom-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [Railway Deployment](#railway-deployment)
6. [DigitalOcean App Platform](#digitalocean-app-platform)
7. [Traditional VPS Deployment](#traditional-vps-deployment)
8. [Docker Deployment](#docker-deployment)

---

## Prerequisites

- Git repository (GitHub, GitLab, Bitbucket)
- Database configured (PostgreSQL)
- `.env.example` file (for reference)
- All dependencies in `requirements.txt`

## Environment Configuration

Before deploying, ensure you have the following environment variables ready:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
DATABASE_URL=postgresql://user:pass@host:port/database
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
```

---

## Render.com Deployment

### Step 1: Create PostgreSQL Database

1. Log in to [Render.com](https://render.com)
2. Click **New +** → **PostgreSQL**
3. Configure:
   - Name: `mobility-app-db`
   - Database: `rand_refinary`
   - User: (auto-generated)
   - Region: Choose closest to your users
   - Plan: Free or paid
4. Click **Create Database**
5. Copy the **External Database URL** (starts with `postgresql://`)

### Step 2: Create Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `mobility-app`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free or paid

### Step 3: Add Environment Variables

In the **Environment** section, add:

```
DATABASE_URL=[paste External Database URL from Step 1]
SECRET_KEY=[generate random string]
FLASK_ENV=production
DB_NAME=rand_refinary
```

### Step 4: Deploy

1. Click **Create Web Service**
2. Wait for deployment (5-10 minutes)
3. Access your app at: `https://your-app-name.onrender.com`

### Step 5: Run Database Migrations

```bash
# From Render Shell (go to your web service → Shell)
flask db upgrade
```

---

## Heroku Deployment

### Step 1: Install Heroku CLI

```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
# Or use package managers:

# macOS
brew tap heroku/brew && brew install heroku

# Windows (with Chocolatey)
choco install heroku-cli

# Verify installation
heroku --version
```

### Step 2: Login and Create App

```bash
# Login to Heroku
heroku login

# Create new app
heroku create mobility-app

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:essential-0
```

### Step 3: Configure Environment Variables

```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set FLASK_ENV=production
heroku config:set DB_NAME=rand_refinary

# View all config vars
heroku config
```

### Step 4: Deploy

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Add Heroku remote
heroku git:remote -a mobility-app

# Deploy
git push heroku main

# Run migrations
heroku run flask db upgrade

# Open app in browser
heroku open
```

### Step 5: View Logs

```bash
heroku logs --tail
```

---

## Railway Deployment

### Step 1: Create Account

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub

### Step 2: Create New Project

1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Choose your repository

### Step 3: Add PostgreSQL

1. Click **New** → **Database** → **Add PostgreSQL**
2. Railway will automatically create `DATABASE_URL`

### Step 4: Configure Environment Variables

In **Variables** tab, add:

```
SECRET_KEY=your-secret-key
FLASK_ENV=production
DB_NAME=rand_refinary
```

### Step 5: Configure Settings

1. Go to **Settings**
2. Set **Build Command**: `pip install -r requirements.txt`
3. Set **Start Command**: `gunicorn app:app`

### Step 6: Deploy

Railway auto-deploys on git push. Access at the generated URL.

---

## DigitalOcean App Platform

### Step 1: Create App

1. Log in to DigitalOcean
2. Go to **Apps** → **Create App**
3. Connect GitHub repository

### Step 2: Configure App

- **Resource Type**: Web Service
- **Branch**: main
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `gunicorn app:app --bind 0.0.0.0:8080`

### Step 3: Add Database

1. Click **Add Resource** → **Database**
2. Select **PostgreSQL**
3. Create database

### Step 4: Environment Variables

Add in App settings:
```
DATABASE_URL=${db.DATABASE_URL}
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

### Step 5: Launch App

Click **Launch App** and wait for deployment.

---

## Traditional VPS Deployment

For Ubuntu 22.04 LTS server:

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Dependencies

```bash
# Python and pip
sudo apt install python3 python3-pip python3-venv -y

# PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Nginx (web server)
sudo apt install nginx -y

# Supervisor (process manager)
sudo apt install supervisor -y
```

### Step 3: Setup PostgreSQL

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE rand_refinary;
CREATE USER mobility_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE rand_refinary TO mobility_user;
\q
```

### Step 4: Clone and Setup Application

```bash
# Create app directory
sudo mkdir -p /var/www/mobility_app
cd /var/www/mobility_app

# Clone repository
git clone https://github.com/yourusername/mobility_app.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Step 5: Create .env File

```bash
nano .env
```

Add your environment variables:
```env
DB_NAME=rand_refinary
DB_USER=mobility_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_secret_key
FLASK_ENV=production
```

### Step 6: Run Migrations

```bash
source venv/bin/activate
flask db upgrade
```

### Step 7: Configure Gunicorn with Supervisor

```bash
sudo nano /etc/supervisor/conf.d/mobility_app.conf
```

Add:
```ini
[program:mobility_app]
directory=/var/www/mobility_app
command=/var/www/mobility_app/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/mobility_app/err.log
stdout_logfile=/var/log/mobility_app/out.log
```

Create log directory:
```bash
sudo mkdir -p /var/log/mobility_app
sudo chown www-data:www-data /var/log/mobility_app
```

Start supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mobility_app
```

### Step 8: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/mobility_app
```

Add:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/mobility_app/static;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/mobility_app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 9: Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com
```

---

## Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: rand_refinary
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_NAME=rand_refinary
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
    depends_on:
      - db
    volumes:
      - .:/app

volumes:
  postgres_data:
```

### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# Run migrations
docker-compose exec web flask db upgrade

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## Post-Deployment Checklist

- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] SSL certificate installed (HTTPS)
- [ ] Database backups configured
- [ ] Monitoring setup (logs, errors)
- [ ] Domain name configured
- [ ] Test all routes and functionality
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Error logging configured

## Troubleshooting

### Application Won't Start

1. Check logs:
   ```bash
   # Render/Heroku/Railway
   Check dashboard logs
   
   # VPS
   sudo supervisorctl tail -f mobility_app stderr
   ```

2. Verify environment variables
3. Check database connection
4. Verify all dependencies installed

### Database Connection Errors

1. Verify `DATABASE_URL` or individual DB variables
2. Check database is running and accessible
3. Verify firewall rules
4. Test connection manually:
   ```bash
   psql $DATABASE_URL
   ```

### 502 Bad Gateway (Nginx)

1. Check Gunicorn is running:
   ```bash
   sudo supervisorctl status mobility_app
   ```

2. Check Nginx configuration:
   ```bash
   sudo nginx -t
   ```

3. Restart services:
   ```bash
   sudo supervisorctl restart mobility_app
   sudo systemctl restart nginx
   ```

## Additional Resources

- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [PostgreSQL Production Best Practices](https://www.postgresql.org/docs/current/admin.html)
- [Nginx Configuration](https://nginx.org/en/docs/)
