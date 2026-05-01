#!/bin/sh

echo "--------------------------------------------------"
echo "🚀 BLACKROSE SYSTEM STARTUP"
echo "--------------------------------------------------"
echo "PORT: ${PORT:-7860}"
echo "--------------------------------------------------"

# Запуск миграций с таймаутом
echo "📦 Running Database Migrations (Alembic)..."
if timeout 60 alembic upgrade head; then
    echo "✅ Migrations completed successfully."
else
    echo "⚠️ WARNING: Migration timed out or failed. Check DATABASE_URL."
    echo "Startup will continue, but the app might be unstable."
fi

echo "--------------------------------------------------"
echo "🔄 Starting Supervisord (API + Bot + Worker)..."
echo "--------------------------------------------------"
exec supervisord -c /app/supervisord.conf
