#!/bin/sh

echo "=== BlackRose ==="
echo "PORT=${PORT:-7860}"

# Запуск миграций с таймаутом (не блокирует старт при проблемах с БД)
echo "Running Alembic migrations..."
timeout 60 alembic upgrade head || echo "WARNING: Migration timed out or failed - continuing startup"

echo "Starting supervisord (API + Bot + Worker)..."
exec supervisord -c /app/supervisord.conf
