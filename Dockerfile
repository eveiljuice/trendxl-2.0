# TrendXL 2.0 Frontend - Multi-stage React/Vite build with Nginx
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --include=dev

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration template
COPY nginx.default.conf.template /etc/nginx/templates/default.conf.template

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD sh -c 'curl -sf http://127.0.0.1:${PORT:-80}/health || exit 1'

# Start nginx
CMD ["nginx", "-g", "daemon off;"]