# TrendXL 2.0 Frontend Dockerfile
# React + Vite application with Railway optimization

# Stage 1: Build the application
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:1.25-alpine

# Copy custom nginx configuration
RUN echo 'server { \
    listen 80; \
    listen [::]:80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Gzip compression \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    \
    # Security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    \
    # Cache static assets \
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ { \
    expires 1y; \
    add_header Cache-Control "public, immutable"; \
    } \
    \
    # SPA routing - all routes go to index.html \
    location / { \
    try_files $uri $uri/ /index.html; \
    } \
    \
    # Health check endpoint \
    location /health { \
    access_log off; \
    return 200 "healthy\n"; \
    add_header Content-Type text/plain; \
    } \
    }' > /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy public assets if any
COPY --from=builder /app/public /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

