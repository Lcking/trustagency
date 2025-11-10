#!/bin/bash

# TrustAgency Docker Development Environment Startup Script
# Usage: ./docker-start.sh [options]
# Options:
#   --build   - Build images before starting
#   --rebuild - Force rebuild all images
#   --clean   - Remove old containers and volumes before starting
#   --help    - Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="trustagency"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

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
    echo "  --build     Build images before starting"
    echo "  --rebuild   Force rebuild all images"
    echo "  --clean     Remove old containers and volumes"
    echo "  --help      Show this help message"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
}

check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "No $ENV_FILE file found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example "$ENV_FILE"
            print_success "Created $ENV_FILE from .env.example"
            print_warning "Please review and update $ENV_FILE if needed"
        else
            print_error ".env.example not found"
            exit 1
        fi
    fi
}

clean_containers() {
    print_header "Cleaning up old containers and volumes"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" down -v --remove-orphans 2>/dev/null || true
    print_success "Cleaned up containers and volumes"
}

build_images() {
    print_header "Building Docker images"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --progress=plain
    print_success "Images built successfully"
}

rebuild_images() {
    print_header "Force rebuilding Docker images"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache --progress=plain
    print_success "Images rebuilt successfully"
}

start_services() {
    print_header "Starting services"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    print_success "Services started"
}

wait_for_services() {
    print_header "Waiting for services to be ready"
    
    echo "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_isready -U trustagency &> /dev/null; then
            print_success "PostgreSQL is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    echo ""
    echo "Waiting for Redis..."
    for i in {1..30}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli ping &> /dev/null; then
            print_success "Redis is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    echo ""
    echo "Waiting for Backend API..."
    for i in {1..30}; do
        if curl -f http://localhost:8001/health &> /dev/null; then
            print_success "Backend API is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    echo ""
    echo "Waiting for Frontend..."
    for i in {1..30}; do
        if curl -f http://localhost/robots.txt &> /dev/null; then
            print_success "Frontend is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
}

show_status() {
    print_header "Service Status"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
}

show_urls() {
    print_header "Service URLs"
    
    echo "Frontend:     ${BLUE}http://localhost${NC}"
    echo "API Docs:     ${BLUE}http://localhost:8001/docs${NC}"
    echo "Admin Panel:  ${BLUE}http://localhost:8001/admin${NC}"
    echo "API:          ${BLUE}http://localhost:8001${NC}"
    echo ""
    echo "Database:     ${BLUE}localhost:5432${NC}"
    echo "Redis:        ${BLUE}localhost:6379${NC}"
}

show_logs() {
    print_header "Recent logs (last 20 lines)"
    echo ""
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=20
}

# Parse arguments
BUILD=false
REBUILD=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD=true
            shift
            ;;
        --rebuild)
            REBUILD=true
            BUILD=false
            shift
            ;;
        --clean)
            CLEAN=true
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
print_header "TrustAgency Docker Development Environment"

check_docker
check_docker_compose
check_env_file

if [ "$CLEAN" = true ]; then
    clean_containers
fi

if [ "$REBUILD" = true ]; then
    rebuild_images
elif [ "$BUILD" = true ]; then
    build_images
fi

start_services
wait_for_services
show_status
show_urls

print_header "Startup Complete!"
echo ""
echo "To view logs:"
echo "  ${BLUE}docker-compose logs -f [SERVICE]${NC}"
echo ""
echo "To stop services:"
echo "  ${BLUE}./docker-stop.sh${NC}"
echo ""
echo "To clean up:"
echo "  ${BLUE}./docker-clean.sh${NC}"
echo ""
