#!/bin/bash

# TrustAgency Docker Environment Cleanup Script
# Usage: ./docker-clean.sh [options]
# Options:
#   --dangling      - Remove only dangling images
#   --unused        - Remove all unused images
#   --volumes       - Also remove volumes
#   --networks      - Also remove unused networks
#   --all           - Remove everything (images, volumes, networks)
#   --help          - Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
DANGLING=false
UNUSED=false
VOLUMES=false
NETWORKS=false
ALL=false

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
    echo "  --dangling   Remove only dangling images"
    echo "  --unused     Remove all unused images"
    echo "  --volumes    Also remove volumes"
    echo "  --networks   Also remove unused networks"
    echo "  --all        Remove everything (images, volumes, networks)"
    echo "  --help       Show this help message"
    echo ""
}

show_disk_usage() {
    print_header "Docker Disk Usage Before Cleanup"
    
    docker system df || true
}

clean_dangling_images() {
    print_header "Removing dangling images"
    
    DANGLING_IMAGES=$(docker images -f "dangling=true" -q)
    if [ -z "$DANGLING_IMAGES" ]; then
        print_warning "No dangling images found"
    else
        docker rmi $DANGLING_IMAGES
        print_success "Dangling images removed"
    fi
}

clean_unused_images() {
    print_header "Removing unused images"
    
    docker image prune -a -f
    print_success "Unused images removed"
}

clean_volumes() {
    print_header "Removing unused volumes"
    
    docker volume prune -f
    print_success "Unused volumes removed"
}

clean_networks() {
    print_header "Removing unused networks"
    
    docker network prune -f
    print_success "Unused networks removed"
}

clean_stopped_containers() {
    print_header "Removing stopped containers"
    
    docker container prune -f
    print_success "Stopped containers removed"
}

clean_all() {
    print_header "Running full cleanup (images, volumes, networks, containers)"
    
    docker system prune -a --volumes -f
    print_success "Full cleanup completed"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dangling)
            DANGLING=true
            shift
            ;;
        --unused)
            UNUSED=true
            shift
            ;;
        --volumes)
            VOLUMES=true
            shift
            ;;
        --networks)
            NETWORKS=true
            shift
            ;;
        --all)
            ALL=true
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
print_header "TrustAgency Docker Environment Cleanup"

show_disk_usage

read -p "Proceed with cleanup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Cleanup cancelled"
    exit 1
fi

if [ "$ALL" = true ]; then
    clean_all
else
    if [ "$DANGLING" = true ]; then
        clean_dangling_images
    fi
    
    if [ "$UNUSED" = true ]; then
        clean_unused_images
    fi
    
    if [ "$VOLUMES" = true ]; then
        clean_volumes
    fi
    
    if [ "$NETWORKS" = true ]; then
        clean_networks
    fi
    
    # Always clean stopped containers
    clean_stopped_containers
fi

print_header "Docker Disk Usage After Cleanup"

docker system df || true

print_success "Cleanup complete!"
