#!/bin/bash

# TrustAgency Docker Production Environment Startup Script
# Usage: ./docker-start-prod.sh [options]
# Options:
#   --build   - Build images before starting
#   --rebuild - Force rebuild all images
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
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

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
        print_error "No $ENV_FILE file found."
        print_warning "Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example "$ENV_FILE"
            print_warning "Created $ENV_FILE - PLEASE UPDATE WITH PRODUCTION VALUES!"
            print_warning "Critical settings to update:"
            print_warning "  - DB_PASSWORD"
            print_warning "  - SECRET_KEY"
            print_warning "  - CORS_ORIGINS"
            print_warning "  - OPENAI_API_KEY (if needed)"
            exit 1
        else
            print_error ".env.example not found"
            exit 1
        fi
    fi
}

check_data_directories() {
    print_header "Checking data directories"
    
    DATA_PATH="${DATA_PATH:-/var/lib/trustagency}"
    
    if [ ! -d "$DATA_PATH" ]; then
        print_warning "Creating data directory: $DATA_PATH"
        mkdir -p "$DATA_PATH/postgres"
        mkdir -p "$DATA_PATH/redis"
        mkdir -p "$DATA_PATH/logs"
        chmod 755 "$DATA_PATH"
        print_success "Data directories created"
    else
        print_success "Data directories exist"
    fi
}

check_ssl_certificates() {
    print_header "Checking SSL certificates"
    
    if [ -d "./nginx/ssl" ]; then
        if [ -f "./nginx/ssl/cert.pem" ] && [ -f "./nginx/ssl/key.pem" ]; then
            print_success "SSL certificates found"
        else
            print_warning "SSL directory exists but certificates missing"
        fi
    else
        print_warning "SSL directory not found - HTTPS disabled"
        print_warning "To enable HTTPS, create certificates in ./nginx/ssl/"
    fi
}

validate_env_file() {
    print_header "Validating environment configuration"
    
    # Check for critical production settings
    if grep -q "change-this-to-strong-password-in-production" "$ENV_FILE"; then
        print_warning "DB_PASSWORD is not set to a strong value"
        print_warning "Update this before running in production!"
    fi
    
    if grep -q "generate-a-strong-secret-key-here" "$ENV_FILE"; then
        print_warning "SECRET_KEY is not set properly"
        print_warning "Update this before running in production!"
    fi
    
    if grep -q "https://trustagency.com" "$ENV_FILE"; then
        print_warning "CORS_ORIGINS still points to example domain"
        print_warning "Update this to your production domain!"
    fi
}

build_images() {
    print_header "Building Docker images for production"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --progress=plain
    print_success "Images built successfully"
}

rebuild_images() {
    print_header "Force rebuilding Docker images"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache --progress=plain
    print_success "Images rebuilt successfully"
}

start_services() {
    print_header "Starting production services"
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    print_success "Services started in detached mode"
}

wait_for_services() {
    print_header "Waiting for services to be ready"
    
    echo "Waiting for PostgreSQL..."
    for i in {1..60}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_isready -U trustagency &> /dev/null; then
            print_success "PostgreSQL is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    echo ""
    echo "Waiting for Redis..."
    for i in {1..60}; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli ping &> /dev/null; then
            print_success "Redis is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    echo ""
    echo "Waiting for Backend API..."
    for i in {1..60}; do
        if curl -f http://localhost:8001/health &> /dev/null; then
            print_success "Backend API is ready"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    echo ""
    echo "Waiting for Frontend..."
    for i in {1..60}; do
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
    echo "API:          ${BLUE}http://localhost:8001${NC}"
    echo ""
    echo "Database:     ${BLUE}localhost:5432${NC}"
    echo "Redis:        ${BLUE}localhost:6379${NC}"
    echo ""
    echo "API documentation and admin panel disabled in production"
}

# Parse arguments
BUILD=false
REBUILD=false

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
print_header "TrustAgency Docker Production Environment"

check_docker
check_docker_compose
check_env_file
check_data_directories
check_ssl_certificates
validate_env_file

if [ "$REBUILD" = true ]; then
    rebuild_images
elif [ "$BUILD" = true ]; then
    build_images
fi

start_services
wait_for_services
show_status
show_urls

print_header "Production Startup Complete!"
echo ""
echo "To view logs:"
echo "  ${BLUE}docker-compose -f $DOCKER_COMPOSE_FILE logs -f [SERVICE]${NC}"
echo ""
echo "To stop services:"
echo "  ${BLUE}./docker-stop.sh${NC}"
echo ""
echo "To backup database:"
echo "  ${BLUE}./docker-backup-db.sh${NC}"
echo ""
