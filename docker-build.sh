#!/bin/bash

# Korean Airlines Credit Risk Analysis System - Docker Build Script
# This script builds and runs the credit_rating_transition conda environment in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is available and running"
}

# Check if docker-compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install docker-compose first."
        exit 1
    fi
    
    print_success "docker-compose is available"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        if [ -f config/env_example.txt ]; then
            cp config/env_example.txt .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your API keys before running the application"
        else
            print_warning "No env_example.txt found. Creating empty .env file"
            touch .env
        fi
    else
        print_status ".env file already exists"
    fi
}

# Build Docker image
build_image() {
    print_status "Building Docker image for credit_rating_transition environment..."
    
    # Build the image
    docker build -t credit-rating-transition:latest .
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Run the application
run_app() {
    print_status "Starting Korean Airlines Credit Risk Analysis System..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Start the application
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "Application started successfully!"
        print_status "Dashboard is available at: http://localhost:8501"
        print_status "To view logs: docker-compose logs -f"
        print_status "To stop: docker-compose down"
    else
        print_error "Failed to start application"
        exit 1
    fi
}

# Run with Jupyter (development mode)
run_with_jupyter() {
    print_status "Starting application with Jupyter notebook (development mode)..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Start with Jupyter profile
    docker-compose --profile development up -d
    
    if [ $? -eq 0 ]; then
        print_success "Application started successfully with Jupyter!"
        print_status "Dashboard is available at: http://localhost:8501"
        print_status "Jupyter notebook is available at: http://localhost:8888"
        print_status "To view logs: docker-compose logs -f"
        print_status "To stop: docker-compose down"
    else
        print_error "Failed to start application with Jupyter"
        exit 1
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  build     Build the Docker image only"
    echo "  run       Build and run the application"
    echo "  dev       Build and run with Jupyter notebook (development mode)"
    echo "  stop      Stop the running containers"
    echo "  logs      Show application logs"
    echo "  clean     Remove all containers and images"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 run     # Build and run the application"
    echo "  $0 dev     # Build and run with Jupyter"
    echo "  $0 stop    # Stop the application"
}

# Main script logic
main() {
    case "${1:-run}" in
        "build")
            check_docker
            create_env_file
            build_image
            ;;
        "run")
            check_docker
            check_docker_compose
            create_env_file
            build_image
            run_app
            ;;
        "dev")
            check_docker
            check_docker_compose
            create_env_file
            build_image
            run_with_jupyter
            ;;
        "stop")
            print_status "Stopping containers..."
            docker-compose down
            print_success "Containers stopped"
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "clean")
            print_status "Cleaning up Docker resources..."
            docker-compose down --rmi all --volumes --remove-orphans
            docker system prune -f
            print_success "Cleanup completed"
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 