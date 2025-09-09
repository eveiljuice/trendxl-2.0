# Multi-stage build for TrendXL 2.0 Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files and install ALL dependencies (including devDependencies for build)
# CACHE_BUST=2024-01-09
COPY package*.json ./
RUN npm ci --include=dev

# Copy source files and build
COPY . .

# Use production environment variables for build
COPY .env.production .env

RUN npm run build

# Production stage - serve static files with nginx
FROM nginx:alpine AS frontend

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built files from builder stage
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Provide nginx template consumed by official entrypoint
# It will be rendered to /etc/nginx/conf.d/default.conf using envsubst
COPY nginx.default.conf.template /etc/nginx/templates/default.conf.template

# Expose port 80
EXPOSE 80

# Health check (uses dynamic PORT provided by Railway)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD sh -c 'curl -sf http://127.0.0.1:${PORT:-80}/health || exit 1'

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
