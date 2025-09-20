#!/bin/sh
# TrendXL 2.0 - Service Startup Script for Railway

set -e

echo "🚀 Starting TrendXL 2.0 Fullstack Application..."

# Set Railway port if available, otherwise use default
export PORT=${PORT:-80}
export BACKEND_PORT=8000

echo "📋 Configuration:"
echo "   - Frontend Port: ${PORT}"
echo "   - Backend Port: ${BACKEND_PORT}"
echo "   - Python Path: ${PYTHONPATH:-/app/backend}"

# Replace PORT placeholder in nginx config
envsubst '${PORT}' < /etc/nginx/nginx.conf > /tmp/nginx.conf
mv /tmp/nginx.conf /etc/nginx/nginx.conf

echo "🔧 Nginx configuration updated with PORT=${PORT}"

# Ensure log directories exist
mkdir -p /var/log/supervisor /var/log/nginx

# Set proper permissions
chown -R trendxl:trendxl /app/backend
chmod -R 755 /app/backend

echo "✅ Permissions set"

# Test nginx configuration
echo "🧪 Testing Nginx configuration..."
nginx -t

echo "🔍 Testing backend availability..."
cd /app/backend

# Test if backend dependencies are installed
python -c "import fastapi, uvicorn; print('✅ Backend dependencies OK')" || {
    echo "❌ Backend dependencies missing"
    exit 1
}

echo "🎯 Starting services with Supervisor..."

# Start supervisor which will manage both nginx and backend
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
