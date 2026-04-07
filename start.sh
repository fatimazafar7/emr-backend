#!/bin/sh

# Set environment variables if not provided
export PORT=${PORT:-8000}

# Automatically fix Railway's postgres:// to postgresql+asyncpg://
if [ ! -z "$DATABASE_URL" ]; then
  case "$DATABASE_URL" in
    postgres://*) export DATABASE_URL=$(echo $DATABASE_URL | sed 's/^postgres:\/\//postgresql+asyncpg:\/\//') ;;
  esac
fi

echo "🔍 Environment: $ENVIRONMENT"
echo "🌐 Port: $PORT"

echo "🛠️ Initializing database schema (verifying tables)..."
python3 -c "import asyncio; from app.database import create_all_tables; asyncio.run(create_all_tables())"

echo "🚀 Running database migrations (alembic)..."
python3 -m alembic upgrade head || echo "⚠️ Migration warning: some migrations may have already been applied."

echo "✨ Starting EMR Backend on port $PORT..."
# Using gunicorn with uvicorn workers for production
# Optimized for small cloud instances with 1 worker and 120s timeout
python3 -m gunicorn app.main:app \
  --workers 1 \
  --timeout 120 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT
