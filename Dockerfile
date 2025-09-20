# TrendXL 2.0 - Unified Frontend + Backend Dockerfile for Railway
# Multi-stage build: React/Vite Frontend + Python FastAPI Backend + Nginx Proxy

# Stage 1: Build React/Vite Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --include=dev

# Copy source code and build
COPY . ./
RUN npm run build

# Stage 2: Prepare Python Backend
FROM python:3.10-slim-bullseye AS backend-builder

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./

# Stage 3: Production - Nginx + Python Backend
FROM nginx:alpine AS production

# Install Python, curl, and supervisor for process management
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    supervisor \
    && ln -sf python3 /usr/bin/python

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend

# Create directories
RUN mkdir -p /app/backend /var/log/supervisor /etc/supervisor/conf.d

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy backend from backend-builder stage
COPY --from=backend-builder /app/backend /app/backend

# Install Python dependencies in production
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy Nginx configuration
COPY nginx.fullstack.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy startup script
COPY start-services.sh /start-services.sh
RUN chmod +x /start-services.sh

# Create non-root user for security
RUN addgroup -g 1000 trendxl && \
    adduser -D -s /bin/sh -u 1000 -G trendxl trendxl && \
    chown -R trendxl:trendxl /app/backend

# Expose port (Railway will set $PORT environment variable)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=15s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT:-80}/health || exit 1

# Start all services
CMD ["/start-services.sh"]