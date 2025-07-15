# Build stage
FROM node:18-alpine as build-stage

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git python3 make g++ npm

# Copy package files
COPY frontend/package*.json ./
COPY frontend/.npmrc ./

# Install dependencies
RUN rm -rf node_modules package-lock.json && npm install --verbose

# Copy source files
COPY frontend/src ./src/
COPY frontend/public ./public/
COPY frontend/index.html ./
COPY frontend/vite.config.js ./
COPY frontend/.eslintrc.cjs ./
COPY frontend/.prettierrc.json ./
COPY frontend/nginx.conf ./

# Build app
RUN NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Production stage
FROM nginx:stable-alpine

# Install utilities
RUN apk add --no-cache curl procps

# Copy built files
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Create cache directories and set permissions
RUN mkdir -p /var/cache/nginx && \
    chown -R nginx:nginx /var/cache/nginx && \
    mkdir -p /var/run && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 