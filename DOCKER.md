# Docker Setup Guide

Complete guide to running the Mobility App using Docker.

## Quick Start (TL;DR)

```bash
# 1. Copy environment file
cp .env.docker .env

# 2. Edit .env with your settings
nano .env

# 3. Build and run
docker-compose up -d

# 4. Access the app
# Open http://localhost:8000
```

## Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ ([Install Docker Compose](https://docs.docker.com/compose/install/))

Verify installation:
```bash
docker --version
docker-compose --version
```

## Project Structure

```
mobility_app/
├── Dockerfile              # Application container definition
├── docker-compose.yml      # Multi-container orchestration
├── .dockerignore          # Files to exclude from image
├── nginx.conf             # Nginx reverse proxy config
├── docker-entrypoint.sh   # Container startup script
├── .env.docker            # Docker environment template
└── .env                   # Your actual environment variables
```

## Setup Instructions

### 1. Prepare Environment Variables

```bash
# Copy the Docker environment template
cp .env.docker .env

# Edit with your values
nano .env  # or use any text editor
```

**Minimum required settings:**
```env
DB_NAME=rand_refinary
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key_minimum_32_characters_long
FLASK_ENV=production
```

### 2. Build the Docker Images

```bash
# Build the application image
docker-compose build

# Or build without cache (for clean rebuild)
docker-compose build --no-cache
```

### 3. Start the Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web
docker-compose logs -f db
```

### 4. Verify Everything is Running

```bash
# Check container status
docker-compose ps

# Should see:
# - mobility_db (postgres)
# - mobility_app (flask)
# - mobility_nginx (nginx) - if using production profile
```

### 5. Access the Application

- **Development**: http://localhost:8000
- **With Nginx**: http://localhost:80

## Docker Commands Reference

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart web

# View logs
docker-compose logs -f

# Follow logs for specific service
docker-compose logs -f web
```

### Container Management

```bash
# List running containers
docker-compose ps

# Execute command in container
docker-compose exec web bash

# Run Python shell in container
docker-compose exec web python

# Run Flask shell
docker-compose exec web flask shell

# Check application health
docker-compose exec web curl http://localhost:8000/
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d rand_refinary

# Run SQL file
docker-compose exec -T db psql -U postgres -d rand_refinary < backup.sql

# Backup database
docker-compose exec -T db pg_dump -U postgres rand_refinary > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U postgres -d rand_refinary < backup_20260112.sql
```

### Migrations

```bash
# Run migrations
docker-compose exec web flask db upgrade

# Create new migration
docker-compose exec web flask db migrate -m "Description"

# Rollback migration
docker-compose exec web flask db downgrade

# View migration history
docker-compose exec web flask db history
```

### Debugging

```bash
# View container logs
docker-compose logs --tail=100 web

# Get shell access to web container
docker-compose exec web bash

# Check environment variables
docker-compose exec web env

# Check Python packages
docker-compose exec web pip list

# Test database connection
docker-compose exec web python -c "from dbqueries import get_db_connection; conn = get_db_connection(); print('✓ Connected!' if conn else '✗ Failed')"
```

## Production Deployment

### Using Nginx Reverse Proxy

```bash
# Start with nginx profile
docker-compose --profile production up -d

# This starts:
# - Database (db)
# - Application (web)
# - Nginx reverse proxy (nginx)
```

Access at: http://localhost

### Environment Configuration for Production

Update `.env` for production:

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=generate_strong_random_key_here
DB_PASSWORD=very_secure_password
```

Generate strong secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### SSL/HTTPS Setup

1. **Get SSL certificates** (Let's Encrypt, commercial CA, or self-signed)

2. **Create SSL directory**:
   ```bash
   mkdir -p ssl
   ```

3. **Copy certificates**:
   ```bash
   cp your-cert.pem ssl/cert.pem
   cp your-key.pem ssl/key.pem
   ```

4. **Update nginx.conf** (uncomment HTTPS section)

5. **Restart nginx**:
   ```bash
   docker-compose restart nginx
   ```

## Volume Management

### Data Persistence

Docker volumes ensure data persists across container restarts:

- `postgres_data`: Database files
- `static_volume`: Static assets
- `migrations_volume`: Migration files

### Backup Volumes

```bash
# Backup database volume
docker run --rm \
  -v mobility_app_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore database volume
docker run --rm \
  -v mobility_app_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

### Clean Up Volumes

```bash
# Remove all volumes (⚠️ deletes all data)
docker-compose down -v

# Remove specific volume
docker volume rm mobility_app_postgres_data

# List all volumes
docker volume ls
```

## Performance Tuning

### Adjust Worker Processes

Edit `docker-compose.yml` or `Dockerfile`:

```yaml
# For high-traffic applications
command: gunicorn --bind 0.0.0.0:8000 --workers 8 --threads 4 app:app
```

Formula: `workers = (2 × CPU cores) + 1`

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Database Connection Pooling

Add to `.env`:
```env
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Common issues:
# 1. Port already in use
docker-compose ps  # Check if another instance is running
lsof -i :8000     # Check what's using port 8000

# 2. Build failed
docker-compose build --no-cache

# 3. Database connection failed
docker-compose exec web ping db
```

### Database Connection Errors

```bash
# Verify database is ready
docker-compose exec db pg_isready -U postgres

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Reset database (⚠️ deletes data)
docker-compose down -v
docker-compose up -d
```

### Permission Errors

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run as root (not recommended)
docker-compose exec -u root web bash
```

### Out of Memory

```bash
# Check container memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → Increase limit

# Clear Docker cache
docker system prune -a --volumes
```

### Image Build Fails

```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check disk space
docker system df
```

## Development with Docker

### Hot Reload for Development

Uncomment in `docker-compose.yml`:

```yaml
services:
  web:
    volumes:
      - .:/app  # Mount current directory
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=True
    command: flask run --host=0.0.0.0 --port=8000 --reload
```

### Access Container Shell

```bash
# Bash shell
docker-compose exec web bash

# Python REPL
docker-compose exec web python

# Flask shell
docker-compose exec web flask shell
```

### Install New Dependencies

```bash
# Install in running container (temporary)
docker-compose exec web pip install package-name

# Make permanent:
# 1. Add to requirements.txt
# 2. Rebuild image
docker-compose build web
docker-compose up -d
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker-compose build
      - name: Run tests
        run: docker-compose run web pytest
```

### GitLab CI Example

```yaml
docker-build:
  stage: build
  script:
    - docker-compose build
    - docker-compose up -d
    - docker-compose exec -T web pytest
```

## Security Best Practices

1. **Use non-root user** ✅ (Already configured in Dockerfile)
2. **Scan images for vulnerabilities**:
   ```bash
   docker scan mobility_app_web
   ```
3. **Keep base images updated**:
   ```bash
   docker-compose pull
   docker-compose build --no-cache
   ```
4. **Use secrets management** (Docker secrets or environment variables)
5. **Enable read-only root filesystem** (add to docker-compose.yml)
6. **Limit container capabilities**

## Monitoring

### Health Checks

Built-in health checks in `docker-compose.yml`:

```bash
# Check health status
docker-compose ps

# Should show "healthy" status
```

### View Resource Usage

```bash
# Real-time stats
docker stats

# Container-specific stats
docker stats mobility_app
```

### Logging

```bash
# Follow all logs
docker-compose logs -f

# Filter logs
docker-compose logs -f web | grep ERROR

# Export logs
docker-compose logs --no-color > app_logs.txt
```

## Scaling

### Horizontal Scaling

```bash
# Scale web service to 3 instances
docker-compose up -d --scale web=3

# With load balancer (nginx)
docker-compose --profile production up -d --scale web=3
```

### Vertical Scaling

Increase resources in `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Flask in Docker](https://flask.palletsprojects.com/en/latest/deploying/docker/)
- [PostgreSQL Docker Official Image](https://hub.docker.com/_/postgres)

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Review [Troubleshooting](#troubleshooting) section
3. Check Docker documentation
4. Verify environment variables in `.env`

---

**Quick Command Reference:**

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Shell
docker-compose exec web bash

# Database
docker-compose exec db psql -U postgres -d rand_refinary

# Rebuild
docker-compose build --no-cache && docker-compose up -d
```
