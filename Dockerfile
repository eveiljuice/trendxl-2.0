# Multi-stage build for TrendXL 2.0 Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source files and build
COPY . .
RUN npm run build

# Production stage - serve static files with nginx
FROM nginx:alpine AS frontend

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built files from builder stage
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
