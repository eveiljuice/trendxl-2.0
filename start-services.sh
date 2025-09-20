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
echo "   - Virtual Env: ${VIRTUAL_ENV:-/app/venv}"

# Debug: Show environment variables
echo "🔍 Environment Variables:"
env | grep -E "(PORT|PATH|PYTHON)" || echo "   No relevant env vars found"

# Replace PORT placeholder in nginx config
echo "🔧 Processing Nginx configuration..."
echo "   Original config preview:"
head -n 75 /etc/nginx/nginx.conf | tail -n 10

envsubst '${PORT}' < /etc/nginx/nginx.conf > /tmp/nginx.conf
mv /tmp/nginx.conf /etc/nginx/nginx.conf

echo "   Updated config preview:"
head -n 75 /etc/nginx/nginx.conf | tail -n 10

echo "✅ Nginx configuration updated with PORT=${PORT}"

# Ensure log directories exist with proper permissions
echo "📁 Creating directories..."
mkdir -p /var/log/supervisor /var/log/nginx /var/run
chmod 755 /var/log/supervisor /var/log/nginx /var/run

# Set proper permissions
chown -R trendxl:trendxl /app/backend /app/venv
chmod -R 755 /app/backend
# Make sure venv binaries are executable
chmod +x /app/venv/bin/*

echo "✅ Permissions set"

# Test nginx configuration
echo "🧪 Testing Nginx configuration..."
nginx -t || {
    echo "❌ Nginx configuration test failed!"
    echo "Config content around listen directive:"
    grep -n -A 5 -B 5 "listen" /etc/nginx/nginx.conf || echo "Could not find listen directive"
    exit 1
}

echo "🔍 Testing backend availability..."
cd /app/backend

# Activate virtual environment
export PATH="/app/venv/bin:$PATH"
export VIRTUAL_ENV="/app/venv"
export PYTHONPATH="/app/backend"

# Test if virtual environment and backend dependencies are installed
echo "   Testing Python imports and backend files..."
/app/venv/bin/python -c "
import sys
print('Python executable:', sys.executable)
print('Python path:', sys.path[:3])  # First 3 paths
try:
    import fastapi, uvicorn
    print('✅ Backend dependencies OK in venv')
except ImportError as e:
    print('❌ Import error:', e)
    raise
" || {
    echo "❌ Backend dependencies missing in virtual environment"
    echo "🔧 Available Python packages:"
    /app/venv/bin/pip list | head -20 || echo "Failed to list packages"
    echo "🔧 Python executable info:"
    /app/venv/bin/python --version
    ls -la /app/venv/bin/python*
    exit 1
}

# Extended backend testing
echo "🔍 Backend files structure:"
echo "   Directory: /app/backend"
ls -la /app/backend/ | head -10

echo "🔍 Critical backend files:"
echo "   run_server.py: $(test -f /app/backend/run_server.py && echo '✅ exists' || echo '❌ missing')"
echo "   main.py: $(test -f /app/backend/main.py && echo '✅ exists' || echo '❌ missing')"  
echo "   config.py: $(test -f /app/backend/config.py && echo '✅ exists' || echo '❌ missing')"
echo "   requirements.txt: $(test -f /app/backend/requirements.txt && echo '✅ exists' || echo '❌ missing')"

# Test backend script syntax
echo "🧪 Backend script syntax check:"
if [ -f /app/backend/run_server.py ]; then
    if /app/venv/bin/python -m py_compile /app/backend/run_server.py 2>/dev/null; then
        echo "✅ run_server.py syntax OK"
    else 
        echo "❌ run_server.py syntax ERROR:"
        /app/venv/bin/python -m py_compile /app/backend/run_server.py || true
    fi
else
    echo "❌ run_server.py not found!"
fi

# Test backend import in proper directory
echo "🧪 Backend module import test:"
cd /app/backend
if /app/venv/bin/python -c "
import sys
sys.path.insert(0, '/app/backend')
try:
    import main
    print('✅ Backend main module imports OK')
except Exception as e:
    print('❌ Backend main import error:', e)
    import traceback
    traceback.print_exc()
" 2>/dev/null; then
    echo "✅ Backend import successful"
else
    echo "❌ Backend import FAILED - detailed error:"
    /app/venv/bin/python -c "
import sys
sys.path.insert(0, '/app/backend')
import main
" 2>&1 | head -20 || echo "Import failed completely"
fi
cd /

# Check if supervisor config exists
echo "🔧 Checking supervisor configuration..."
if [ ! -f /etc/supervisor/conf.d/supervisord.conf ]; then
    echo "❌ Supervisor config not found!"
    ls -la /etc/supervisor/conf.d/
    exit 1
fi

echo "   Supervisor config preview:"
head -20 /etc/supervisor/conf.d/supervisord.conf

echo "🎯 Starting services with Supervisor..."

# Test if backend port is available
echo "🔌 Testing if port 8000 is available..."
if netstat -tuln | grep :8000; then
    echo "⚠️ Port 8000 is already in use!"
    netstat -tuln | grep :8000
else
    echo "✅ Port 8000 is available"
fi

# Start supervisor in debug mode initially
echo "   Starting supervisor daemon..."
echo "   Supervisor will start:"
echo "   - nginx (port 80/PORT)"
echo "   - backend (port 8000)"

# Add a function to monitor services
(
    echo "📊 Starting service monitoring (background task)..."
    
    # Initial wait
    sleep 5
    echo "📊 Service Status Check (after 5 seconds):"
    
    # Check if processes are running
    echo "   Nginx processes:"
    ps aux | grep nginx | grep -v grep || echo "   ❌ No nginx processes found"
    
    echo "   Python processes:"
    ps aux | grep python | grep -v grep || echo "   ❌ No python processes found"
    
    echo "   Port usage:"
    netstat -tuln | grep -E ":80|:8000" || echo "   ❌ No processes listening on ports 80/8000"
    
    # Check supervisor process status
    echo "   Supervisor process status:"
    if command -v supervisorctl >/dev/null 2>&1; then
        supervisorctl -c /etc/supervisor/conf.d/supervisord.conf status || echo "   ❌ Cannot get supervisor status"
    else
        echo "   ❌ supervisorctl not available"
    fi
    
    # Test internal connectivity
    echo "   Testing internal connectivity:"
    echo "   - Backend health: $(curl -s -w '%{http_code}' -o /dev/null http://127.0.0.1:8000/health || echo 'failed')"
    echo "   - Backend direct: $(curl -s -w '%{http_code}' -o /dev/null http://127.0.0.1:8000 || echo 'failed')"
    echo "   - Nginx status: $(curl -s -w '%{http_code}' -o /dev/null http://127.0.0.1:${PORT:-80}/nginx-status || echo 'failed')"
    
    # Wait longer and check again
    sleep 15
    echo "📊 Extended Status Check (after 20 seconds total):"
    
    echo "   Python processes (extended):"
    ps aux | grep -E "(python|uvicorn|fastapi)" | grep -v grep || echo "   ❌ No backend processes found"
    
    echo "   Listening ports (extended):"
    netstat -tuln | grep -E ":80|:8000" || echo "   ❌ Still no processes on ports 80/8000"
    
    # Check supervisor logs briefly
    echo "   Recent supervisor logs:"
    if [ -f /var/log/supervisor/backend.log ]; then
        echo "   Backend stdout (last 5 lines):"
        tail -5 /var/log/supervisor/backend.log | sed 's/^/     /'
    fi
    
    if [ -f /var/log/supervisor/backend_error.log ]; then
        echo "   Backend stderr (last 5 lines):"  
        tail -5 /var/log/supervisor/backend_error.log | sed 's/^/     /'
    fi
    
) &

exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
