#!/bin/bash
# Database Backup Script for Docker

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"
KEEP_DAYS=${BACKUP_KEEP_DAYS:-7}

echo "🔄 Starting database backup..."

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo "✅ Backup completed: ${BACKUP_FILE}.gz"

# Remove old backups
echo "🗑️ Cleaning up old backups (older than $KEEP_DAYS days)..."
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$KEEP_DAYS -delete

echo "✅ Backup process completed successfully!"

# List recent backups
echo "📦 Recent backups:"
ls -lh $BACKUP_DIR/backup_*.sql.gz 2>/dev/null | tail -n 5 || echo "No backups found"
