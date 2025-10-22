#!/bin/bash

###############################################################################
# Deploy Script for Trustagency Static Site
# 
# Usage:
#   bash deploy.sh [environment] [options]
#   
# Environments:
#   local  - Local Docker deployment
#   prod   - Production server deployment
#
# Examples:
#   bash deploy.sh local                    # Deploy locally
#   bash deploy.sh prod --host user@server  # Deploy to production server
#
###############################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
LOG_FILE="$SCRIPT_DIR/deploy.log"
PROJECT_NAME="trustagency"
CONTAINER_NAME="trustagency-web"

# Functions
log() {
    echo -e "${BLUE}[${TIMESTAMP}]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}" | tee -a "$LOG_FILE"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    success "Docker and Docker Compose are installed"
}

# Local deployment
deploy_local() {
    log "Starting local deployment..."
    
    cd "$SCRIPT_DIR"
    
    # Check Docker
    check_docker
    
    # Stop existing container
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log "Stopping existing container..."
        docker compose -f docker-compose.build.yml down --remove-orphans || true
        success "Container stopped"
    fi
    
    # Build and start new container
    log "Building and starting Docker container..."
    docker compose -f docker-compose.build.yml up -d --build --remove-orphans
    
    success "Container built and started successfully"
    
    # Wait for container to be healthy
    log "Waiting for container to be healthy..."
    sleep 3
    
    # Check health
    if docker ps --filter "name=${CONTAINER_NAME}" --filter "health=healthy" -q | grep -q .; then
        success "Container is healthy"
    else
        warning "Container health status: $(docker ps --filter "name=${CONTAINER_NAME}" --format '{{.Status}}')"
    fi
    
    # Display access information
    log ""
    log "========================================"
    log "Local deployment completed!"
    log "========================================"
    log "Access the site at: http://localhost/"
    log "Alternative: http://localhost:8080/ (if port 80 is in use)"
    log ""
    log "Useful commands:"
    log "  View logs: docker logs ${CONTAINER_NAME}"
    log "  Stop: docker compose -f docker-compose.build.yml down"
    log "  Restart: docker compose -f docker-compose.build.yml restart"
    log "========================================"
}

# Production deployment
deploy_prod() {
    local remote_host="$1"
    
    log "Starting production deployment to ${remote_host}..."
    
    if [ -z "$remote_host" ]; then
        error "Remote host is required for production deployment"
        echo "Usage: bash deploy.sh prod --host user@example.com"
        exit 1
    fi
    
    # SSH copy
    log "Uploading files to ${remote_host}..."
    
    ssh "$remote_host" "mkdir -p ~/trustagency" || {
        error "Failed to create remote directory"
        exit 1
    }
    
    scp -r "$SCRIPT_DIR"/site "$remote_host:~/trustagency/"
    scp -r "$SCRIPT_DIR"/nginx "$remote_host:~/trustagency/"
    scp "$SCRIPT_DIR"/Dockerfile "$remote_host:~/trustagency/"
    scp "$SCRIPT_DIR"/docker-compose.build.yml "$remote_host:~/trustagency/"
    
    success "Files uploaded successfully"
    
    # Remote deployment
    log "Running deployment on remote server..."
    ssh "$remote_host" "cd ~/trustagency && bash << 'EOF'
set -euo pipefail

# Remote deployment commands
docker compose -f docker-compose.build.yml down --remove-orphans || true
docker compose -f docker-compose.build.yml up -d --build --remove-orphans

echo 'Deployment completed on remote server'
EOF
"
    
    success "Production deployment completed"
}

# Main script
main() {
    local environment="${1:-local}"
    
    log "Trustagency Deployment Script"
    log "Environment: $environment"
    log ""
    
    case "$environment" in
        local)
            deploy_local
            ;;
        prod)
            shift
            local host=""
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --host)
                        host="$2"
                        shift 2
                        ;;
                    *)
                        error "Unknown option: $1"
                        exit 1
                        ;;
                esac
            done
            deploy_prod "$host"
            ;;
        *)
            error "Unknown environment: $environment"
            echo ""
            echo "Usage: bash deploy.sh [local|prod] [options]"
            echo ""
            echo "Examples:"
            echo "  bash deploy.sh local"
            echo "  bash deploy.sh prod --host user@example.com"
            exit 1
            ;;
    esac
    
    success "Deployment script completed"
}

# Run main
main "$@"
