#!/bin/bash

# TrendXL 2.0 Backend Startup Script

echo "🚀 Starting TrendXL 2.0 Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before running again."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt .requirements_installed ] || [ ! -f .requirements_installed ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    touch .requirements_installed
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️ Redis is not running. Starting Redis with Docker..."
    if command -v docker >/dev/null 2>&1; then
        docker run -d --name trendxl-redis -p 6379:6379 redis:7-alpine
        echo "⏳ Waiting for Redis to start..."
        sleep 3
    else
        echo "❌ Redis is not running and Docker is not available."
        echo "Please install Redis or start it manually:"
        echo "  sudo apt install redis-server"
        echo "  sudo systemctl start redis-server"
        exit 1
    fi
fi

# Start the server
echo "🌟 Starting FastAPI server..."
python3 run_server.py
