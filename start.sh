#!/bin/sh

# Set environment variables if not provided
export PORT=${PORT:-8000}

echo "🚀 Running database migrations..."
alembic upgrade head

echo "✨ Starting EMR Backend on port $PORT..."
# Using gunicorn with uvicorn workers for production
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT
