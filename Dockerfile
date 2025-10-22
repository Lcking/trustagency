# Dockerfile for Static Site with Nginx
# Base image: nginx:alpine (lightweight, ~42MB)
# Optimized for production use

FROM nginx:alpine

# Install additional tools (optional)
# Uncomment if needed:
# RUN apk add --no-cache curl

# Copy static site files to nginx document root
COPY ./site /usr/share/nginx/html

# Copy custom nginx configuration
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# Create non-root user for nginx (security best practice)
# Note: nginx:alpine already runs with nginx user

# Expose port 80
EXPOSE 80

# Health check to monitor container health
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/robots.txt || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
