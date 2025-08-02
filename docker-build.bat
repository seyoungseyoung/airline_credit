@echo off
REM Korean Airlines Credit Risk Analysis System - Docker Build Script for Windows
REM This script builds and runs the credit_rating_transition conda environment in Docker

setlocal enabledelayedexpansion

REM Set colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Function to print colored output
:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM Check if Docker is installed
:check_docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker is not running. Please start Docker Desktop first."
    exit /b 1
)

call :print_success "Docker is available and running"
goto :eof

REM Check if docker-compose is installed
:check_docker_compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :print_error "docker-compose is not installed. Please install docker-compose first."
    exit /b 1
)

call :print_success "docker-compose is available"
goto :eof

REM Create .env file if it doesn't exist
:create_env_file
if not exist .env (
    call :print_status "Creating .env file from template..."
    if exist config\env_example.txt (
        copy config\env_example.txt .env >nul
        call :print_success "Created .env file from template"
        call :print_warning "Please edit .env file with your API keys before running the application"
    ) else (
        call :print_warning "No env_example.txt found. Creating empty .env file"
        type nul > .env
    )
) else (
    call :print_status ".env file already exists"
)
goto :eof

REM Build Docker image
:build_image
call :print_status "Building Docker image for credit_rating_transition environment..."

docker build -t credit-rating-transition:latest .

if errorlevel 1 (
    call :print_error "Failed to build Docker image"
    exit /b 1
) else (
    call :print_success "Docker image built successfully"
)
goto :eof

REM Run the application
:run_app
call :print_status "Starting Korean Airlines Credit Risk Analysis System..."

REM Stop any existing containers
docker-compose down >nul 2>&1

REM Start the application
docker-compose up -d

if errorlevel 1 (
    call :print_error "Failed to start application"
    exit /b 1
) else (
    call :print_success "Application started successfully!"
    call :print_status "Dashboard is available at: http://localhost:8501"
    call :print_status "To view logs: docker-compose logs -f"
    call :print_status "To stop: docker-compose down"
)
goto :eof

REM Run with Jupyter (development mode)
:run_with_jupyter
call :print_status "Starting application with Jupyter notebook (development mode)..."

REM Stop any existing containers
docker-compose down >nul 2>&1

REM Start with Jupyter profile
docker-compose --profile development up -d

if errorlevel 1 (
    call :print_error "Failed to start application with Jupyter"
    exit /b 1
) else (
    call :print_success "Application started successfully with Jupyter!"
    call :print_status "Dashboard is available at: http://localhost:8501"
    call :print_status "Jupyter notebook is available at: http://localhost:8888"
    call :print_status "To view logs: docker-compose logs -f"
    call :print_status "To stop: docker-compose down"
)
goto :eof

REM Show usage
:show_usage
echo Usage: %~nx0 [OPTION]
echo.
echo Options:
echo   build     Build the Docker image only
echo   run       Build and run the application
echo   dev       Build and run with Jupyter notebook (development mode)
echo   stop      Stop the running containers
echo   logs      Show application logs
echo   clean     Remove all containers and images
echo   help      Show this help message
echo.
echo Examples:
echo   %~nx0 run     # Build and run the application
echo   %~nx0 dev     # Build and run with Jupyter
echo   %~nx0 stop    # Stop the application
goto :eof

REM Main script logic
set "action=%1"
if "%action%"=="" set "action=run"

if "%action%"=="build" (
    call :check_docker
    call :create_env_file
    call :build_image
) else if "%action%"=="run" (
    call :check_docker
    call :check_docker_compose
    call :create_env_file
    call :build_image
    call :run_app
) else if "%action%"=="dev" (
    call :check_docker
    call :check_docker_compose
    call :create_env_file
    call :build_image
    call :run_with_jupyter
) else if "%action%"=="stop" (
    call :print_status "Stopping containers..."
    docker-compose down
    call :print_success "Containers stopped"
) else if "%action%"=="logs" (
    docker-compose logs -f
) else if "%action%"=="clean" (
    call :print_status "Cleaning up Docker resources..."
    docker-compose down --rmi all --volumes --remove-orphans
    docker system prune -f
    call :print_success "Cleanup completed"
) else if "%action%"=="help" (
    call :show_usage
) else (
    call :print_error "Unknown option: %action%"
    call :show_usage
    exit /b 1
)

endlocal 