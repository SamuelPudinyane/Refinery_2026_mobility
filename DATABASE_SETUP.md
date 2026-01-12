# Database Setup Guide

## PostgreSQL Installation

### Windows

1. **Download PostgreSQL**
   - Visit https://www.postgresql.org/download/windows/
   - Download PostgreSQL installer (version 12 or higher)

2. **Install PostgreSQL**
   - Run the installer
   - Set a password for the postgres user (remember this!)
   - Default port: 5432
   - Note the installation directory

3. **Verify Installation**
   ```cmd
   psql --version
   ```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
sudo -u postgres psql --version
```

### macOS

```bash
# Using Homebrew
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Verify installation
psql --version
```

## Database Setup

### 1. Create Database

**Windows/Linux/macOS:**

```bash
# Connect to PostgreSQL as postgres user
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE rand_refinary;

# Verify database was created
\l

# Exit PostgreSQL
\q
```

Or using command line:
```bash
createdb -U postgres rand_refinary
```

### 2. Create Database User (Optional - Recommended for Production)

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create a new user
CREATE USER mobility_app_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE rand_refinary TO mobility_app_user;

-- Exit
\q
```

### 3. Configure Application

Create a `.env` file in the project root:

```env
DB_NAME=rand_refinary
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_secret_key_change_this
```

### 4. Test Database Connection

Run the following Python script to test:

```python
from dbqueries import get_db_connection

conn = get_db_connection()
if conn:
    print("✓ Database connection successful!")
    conn.close()
else:
    print("✗ Database connection failed!")
```

Or simply start the Flask application:
```bash
python app.py
```

## Database Schema Setup

### Option 1: Using Flask-Migrate (Recommended)

```bash
# Initialize migrations (first time only)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations to database
flask db upgrade
```

### Option 2: Manual SQL Script

If you have a SQL dump file:

```bash
# Import SQL file
psql -U postgres -d rand_refinary -f database_schema.sql
```

## Common Database Operations

### Check Connection

```bash
# Connect to database
psql -U postgres -d rand_refinary

# List all tables
\dt

# Describe a table structure
\d table_name

# Run a query
SELECT * FROM rand_refinary_registration LIMIT 5;

# Exit
\q
```

### Backup Database

```bash
# Backup entire database
pg_dump -U postgres rand_refinary > backup_$(date +%Y%m%d).sql

# Backup specific tables
pg_dump -U postgres -t table_name rand_refinary > table_backup.sql
```

### Restore Database

```bash
# Restore from backup
psql -U postgres -d rand_refinary < backup_20260112.sql
```

### Reset Database (CAUTION: Deletes all data)

```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS rand_refinary;"
psql -U postgres -c "CREATE DATABASE rand_refinary;"

# Then run migrations again
flask db upgrade
```

## Troubleshooting

### Connection Refused

**Problem:** `could not connect to server: Connection refused`

**Solutions:**
1. Verify PostgreSQL is running:
   ```bash
   # Windows
   Get-Service -Name postgresql*
   
   # Linux
   sudo systemctl status postgresql
   
   # macOS
   brew services list | grep postgresql
   ```

2. Start PostgreSQL if not running:
   ```bash
   # Windows
   Start-Service postgresql-x64-[version]
   
   # Linux
   sudo systemctl start postgresql
   
   # macOS
   brew services start postgresql
   ```

### Authentication Failed

**Problem:** `FATAL: password authentication failed for user "postgres"`

**Solutions:**
1. Verify password in `.env` file
2. Reset postgres password:
   ```bash
   # Linux/macOS
   sudo -u postgres psql
   ALTER USER postgres PASSWORD 'new_password';
   
   # Windows
   psql -U postgres
   ALTER USER postgres PASSWORD 'new_password';
   ```

### Database Does Not Exist

**Problem:** `FATAL: database "rand_refinary" does not exist`

**Solution:**
```bash
createdb -U postgres rand_refinary
```

### Port Already in Use

**Problem:** Port 5432 is already in use

**Solutions:**
1. Check what's using the port:
   ```bash
   # Windows
   netstat -ano | findstr :5432
   
   # Linux/macOS
   lsof -i :5432
   ```

2. Change PostgreSQL port in `postgresql.conf`
3. Update `DB_PORT` in `.env` file

### Permission Denied

**Problem:** `permission denied for database`

**Solution:**
```sql
-- Grant appropriate permissions
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE rand_refinary TO your_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
```

## Cloud Database Setup

### Render.com PostgreSQL

1. Create PostgreSQL instance on Render
2. Copy the External Database URL
3. Add to `.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@host/database
   ```

### Heroku PostgreSQL

```bash
# Add Heroku Postgres addon
heroku addons:create heroku-postgresql:hobby-dev

# Get database URL
heroku config:get DATABASE_URL

# The URL is automatically added to your app
```

### Other Cloud Providers

For AWS RDS, Azure Database, or Google Cloud SQL:
1. Create PostgreSQL instance
2. Note the host, port, username, password, database name
3. Configure firewall to allow your IP
4. Add credentials to `.env` file

## Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use strong passwords** - Minimum 16 characters
3. **Limit database user privileges** - Don't use superuser for app
4. **Enable SSL in production** - Set `sslmode=require` in connection
5. **Regular backups** - Automate daily backups
6. **Update PostgreSQL** - Keep PostgreSQL up to date with security patches

## Performance Optimization

### Index Creation

```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_company_number ON rand_refinary_registration(company_number);
CREATE INDEX idx_role ON rand_refinary_registration(role);
```

### Connection Pooling

Consider using connection pooling for production:

```python
# Install psycopg2-pool
pip install psycopg2-binary

# Use connection pool in dbqueries.py
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(1, 20, **db_params)
```

## Maintenance

### Vacuum Database (Improves Performance)

```sql
-- Connect to database
psql -U postgres -d rand_refinary

-- Vacuum database
VACUUM ANALYZE;
```

### Monitor Database Size

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('rand_refinary'));

-- Check table sizes
SELECT 
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

## Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
- psycopg2 Documentation: https://www.psycopg.org/docs/
- Database Design Best Practices: https://www.postgresql.org/docs/current/ddl.html
