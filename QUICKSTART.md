# Quick Start Guide

Get the Mobility App running in 5 minutes!

## Choose Your Setup Method

### 🐳 Method 1: Docker (Recommended - Easiest!)

**Perfect for:** Everyone, especially if you want zero setup hassle.

```bash
# 1. Clone repository
git clone https://github.com/IDBRSsimulator/Mobility_for-rand_refinery.git
cd mobility_app

# 2. Configure environment
cp .env.docker .env
# Edit .env: Change DB_PASSWORD and SECRET_KEY

# 3. Start everything
docker-compose up -d

# 4. Access app at http://localhost:8000
```

**That's it!** Docker handles everything: Python, PostgreSQL, dependencies, migrations.

**Useful Docker commands:**
```bash
docker-compose logs -f          # View logs
docker-compose down            # Stop
docker-compose restart         # Restart
docker-compose exec web bash   # Access container shell
```

---

### 💻 Method 2: Traditional Setup (Manual)

**Perfect for:** Developers who want full control or can't use Docker.

### 1. Prerequisites Check
- ✅ Python 3.11+ installed
- ✅ PostgreSQL installed and running
- ✅ Git installed

Check your versions:
```bash
python --version    # Should be 3.11 or higher
psql --version      # Should be 12 or higher
git --version
```

## 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/IDBRSsimulator/Mobility_for-rand_refinery.git
cd mobility_app

# Create virtual environment
python -m venv myvenv

# Activate virtual environment
# Windows:
.\myvenv\Scripts\Activate.ps1
# Linux/Mac:
source myvenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE rand_refinary;
\q
```

### 4. Configure Environment

Copy the example environment file and edit it:

```bash
# Copy the example
cp .env.example .env

# Edit .env with your settings
# Windows:
notepad .env
# Linux/Mac:
nano .env
```

**Minimum required settings in .env:**
```env
DB_NAME=rand_refinary
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=change_this_to_something_random_and_secure
```

### 5. Initialize Database

```bash
# Run migrations to create tables
flask db upgrade
```

If you get an error, try:
```bash
# Initialize migrations first
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Run the Application

```bash
# Start the development server
python app.py
```

The app should now be running at: **http://127.0.0.1:5000**

---

## Access the Application

Open your browser and go to:
```
http://localhost:5000
```

You should see the login page!

## Default Login Credentials

If you have seeded data, use these credentials (check with your admin):
- **Master Admin**: Contact your system administrator
- **Admin**: Contact your system administrator  
- **Operator**: Contact your system administrator

## Troubleshooting

### "Database connection error"
```bash
# Check if PostgreSQL is running
# Windows:
Get-Service -Name postgresql*

# Linux:
sudo systemctl status postgresql

# Mac:
brew services list | grep postgresql
```

### "Module not found" errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### "Port 5000 already in use"
```bash
# Change the port in app.py or kill the process
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000
```

### "Permission denied" on activate script (Windows)
```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Next Steps

1. **Read the full README**: [README.md](README.md)
2. **Setup database properly**: [DATABASE_SETUP.md](DATABASE_SETUP.md)
3. **Learn about deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Configure for production**: Update `.env` with production values

## Common Commands

```bash
# Activate virtual environment
# Windows:
.\myvenv\Scripts\Activate.ps1
# Linux/Mac:
source myvenv/bin/activate

# Run development server
python app.py

# Run with Gunicorn (production-like)
gunicorn app:app

# Database migrations
flask db migrate -m "Description"
flask db upgrade
flask db downgrade

# Deactivate virtual environment
deactivate
```

## Project Structure Overview

```
mobility_app/
├── app.py              # Main application (start here!)
├── config.py           # Configuration settings
├── dbqueries.py        # Database operations
├── encryption.py       # Password hashing
├── .env                # Your environment variables (create this!)
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── static/            # CSS, JS, images
└── migrations/        # Database migrations
```

## Getting Help

- **Issues**: Check [DATABASE_SETUP.md](DATABASE_SETUP.md) troubleshooting section
- **Configuration**: See [README.md](README.md) configuration section
- **Deployment**: Read [DEPLOYMENT.md](DEPLOYMENT.md)

## Development Workflow

1. Make changes to code
2. Test locally
3. Run migrations if database changed:
   ```bash
   flask db migrate -m "Describe changes"
   flask db upgrade
   ```
4. Commit changes:
   ```bash
   git add .
   git commit -m "Description"
   git push
   ```

---

**Ready to go!** 🚀

For detailed documentation, see the full [README.md](README.md)
