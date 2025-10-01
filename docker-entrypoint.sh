#!/bin/sh
# TrendXL Frontend Nginx Entrypoint for Railway
# Dynamically configures nginx to use Railway's PORT environment variable

set -e

echo "🚀 Starting TrendXL Frontend on Railway"

# Get PORT from Railway or default to 80
NGINX_PORT="${PORT:-80}"
echo "📡 Using PORT: $NGINX_PORT"

# Replace placeholder in nginx config with actual port
sed -i "s/RAILWAY_PORT_PLACEHOLDER/${NGINX_PORT}/g" /etc/nginx/nginx.conf

echo "✅ Nginx configuration updated"
echo "🌐 Starting Nginx server..."

# Start nginx
exec nginx -g "daemon off;"

