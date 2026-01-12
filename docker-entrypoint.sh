#!/bin/bash
set -e

echo "🚀 Starting Mobility App..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
done
echo "✅ Database is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
if [ ! -d "migrations" ]; then
    echo "📝 Initializing migrations..."
    flask db init
fi

flask db migrate -m "Auto migration" 2>/dev/null || echo "No new migrations to create"
flask db upgrade

echo "✅ Migrations complete!"

# Start the application
echo "🌟 Starting application server..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
