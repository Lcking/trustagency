# Multi-stage Dockerfile for TrustAgency Frontend
# Base image: nginx:alpine (lightweight, ~42MB)
# Optimized for production use

# Stage 1: Build stage (if needed for future JS bundling)
FROM nginx:alpine AS builder

# Copy all source files
COPY ./site /tmp/site

# Stage 2: Runtime stage
FROM nginx:alpine

# Install curl for health checks (dumb-init causes issues with non-root user)
RUN apk add --no-cache curl

# Copy static site files from builder
COPY --from=builder /tmp/site /usr/share/nginx/html

# Copy custom nginx configuration
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check to monitor container health
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/robots.txt || exit 1

# Start nginx in foreground (necessary for proper Docker signal handling)
CMD ["nginx", "-g", "daemon off;"]
