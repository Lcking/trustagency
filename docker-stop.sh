#!/bin/bash

# TrustAgency Docker Environment Stop Script
# Usage: ./docker-stop.sh [options]
# Options:
#   --env FILE  - Use specific docker-compose file (default: docker-compose.yml)
#   --remove    - Also remove containers after stopping
#   --help      - Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.yml"
REMOVE=false

# Functions
print_header() {
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --env FILE   Use specific docker-compose file"
    echo "  --remove     Also remove containers after stopping"
    echo "  --help       Show this help message"
    echo ""
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed."
        exit 1
    fi
}

show_status() {
    print_header "Current Service Status"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
}

stop_services() {
    print_header "Stopping services"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" stop
    print_success "Services stopped"
}

remove_containers() {
    print_header "Removing containers"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" rm -f
    print_success "Containers removed"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            DOCKER_COMPOSE_FILE="$2"
            shift 2
            ;;
        --remove)
            REMOVE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
print_header "TrustAgency Docker Environment Stop Script"

check_docker_compose

show_status
echo ""

read -p "Are you sure you want to stop services? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    stop_services
    
    if [ "$REMOVE" = true ]; then
        remove_containers
    fi
    
    print_header "Stop Complete!"
    echo ""
    if [ "$REMOVE" = false ]; then
        echo "To remove containers as well, run: ${BLUE}./docker-stop.sh --remove${NC}"
    fi
else
    print_warning "Operation cancelled"
    exit 1
fi
