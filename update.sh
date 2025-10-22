#!/bin/bash

###############################################################################
# Update Script for Trustagency Static Site
# 
# Usage:
#   bash update.sh [environment] [options]
#   
# Environments:
#   local  - Local Docker update
#   prod   - Production server update
#
# Examples:
#   bash update.sh local                    # Update locally
#   bash update.sh prod --host user@server  # Update production server
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
LOG_FILE="$SCRIPT_DIR/update.log"
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
        error "Docker is not installed"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
}

# Local update
update_local() {
    log "Starting local update..."
    
    cd "$SCRIPT_DIR"
    check_docker
    
    # Rebuild and restart container
    log "Rebuilding and restarting Docker container..."
    docker compose -f docker-compose.build.yml up -d --build --remove-orphans
    
    success "Container updated successfully"
    
    # Health check
    sleep 2
    if docker ps --filter "name=${CONTAINER_NAME}" --filter "health=healthy" -q | grep -q .; then
        success "Container is healthy"
    else
        warning "Container status: $(docker ps --filter "name=${CONTAINER_NAME}" --format '{{.Status}}')"
    fi
    
    log "Update completed at: $TIMESTAMP"
}

# Production update
update_prod() {
    local remote_host="$1"
    
    log "Starting production update on ${remote_host}..."
    
    if [ -z "$remote_host" ]; then
        error "Remote host is required for production update"
        echo "Usage: bash update.sh prod --host user@example.com"
        exit 1
    fi
    
    # Upload latest files
    log "Uploading updated files..."
    scp -r "$SCRIPT_DIR"/site "$remote_host:~/trustagency/" || {
        error "Failed to upload files"
        exit 1
    }
    
    success "Files uploaded"
    
    # Remote update
    log "Updating on remote server..."
    ssh "$remote_host" "cd ~/trustagency && docker compose -f docker-compose.build.yml up -d --build --remove-orphans"
    
    success "Production update completed"
}

# Main script
main() {
    local environment="${1:-local}"
    
    log "Trustagency Update Script"
    log "Environment: $environment"
    log ""
    
    case "$environment" in
        local)
            update_local
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
            update_prod "$host"
            ;;
        *)
            error "Unknown environment: $environment"
            echo ""
            echo "Usage: bash update.sh [local|prod] [options]"
            echo ""
            echo "Examples:"
            echo "  bash update.sh local"
            echo "  bash update.sh prod --host user@example.com"
            exit 1
            ;;
    esac
    
    success "Update completed"
}

# Run main
main "$@"
