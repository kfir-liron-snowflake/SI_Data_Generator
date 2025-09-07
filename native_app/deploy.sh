#!/bin/bash

# ================================================================================
# SI Data Generator Native App Deployment Script
# 
# This script automates the deployment of the SI Data Generator as a Snowflake
# Native Application.
# ================================================================================

set -e  # Exit on any error

# Configuration
APP_NAME="SI_DATA_GENERATOR_APP"
APP_VERSION="v1.0.0"
PACKAGE_NAME="${APP_NAME}_PACKAGE"

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

# Function to check if Snowflake CLI is installed
check_snowflake_cli() {
    if ! command -v snow &> /dev/null; then
        print_error "Snowflake CLI (snow) is not installed or not in PATH"
        print_status "Please install Snowflake CLI: https://docs.snowflake.com/en/user-guide/snowsql-install-config"
        exit 1
    fi
    print_success "Snowflake CLI found"
}

# Function to check if user is logged in
check_snowflake_connection() {
    if ! snow connection list &> /dev/null; then
        print_error "Not connected to Snowflake. Please run 'snow connection login' first"
        exit 1
    fi
    print_success "Connected to Snowflake"
}

# Function to create application package
create_app_package() {
    print_status "Creating application package: $PACKAGE_NAME"
    
    if snow app package create $PACKAGE_NAME --source .; then
        print_success "Application package created successfully"
    else
        print_error "Failed to create application package"
        exit 1
    fi
}

# Function to add version to package
add_version_to_package() {
    print_status "Adding version $APP_VERSION to package"
    
    if snow app package add-version $PACKAGE_NAME --version $APP_VERSION --source .; then
        print_success "Version added to package successfully"
    else
        print_error "Failed to add version to package"
        exit 1
    fi
}

# Function to create the application
create_application() {
    print_status "Creating application: $APP_NAME"
    
    # Check if application already exists
    if snow app list | grep -q $APP_NAME; then
        print_warning "Application $APP_NAME already exists. Upgrading to new version..."
        if snow app upgrade $APP_NAME --version $APP_VERSION; then
            print_success "Application upgraded successfully"
        else
            print_error "Failed to upgrade application"
            exit 1
        fi
    else
        if snow app create $APP_NAME --source . --version $APP_VERSION; then
            print_success "Application created successfully"
        else
            print_error "Failed to create application"
            exit 1
        fi
    fi
}

# Function to show application information
show_app_info() {
    print_status "Application Information:"
    echo "  Name: $APP_NAME"
    echo "  Version: $APP_VERSION"
    echo "  Package: $PACKAGE_NAME"
    echo ""
    print_status "To grant access to users, run:"
    echo "  snow app grant-role $APP_NAME!app_instance_role TO USER 'username'"
    echo ""
    print_status "To view the application, run:"
    echo "  snow app open $APP_NAME"
}

# Function to validate files
validate_files() {
    print_status "Validating required files..."
    
    required_files=("manifest.yml" "setup_script.sql" "ui/Dashboard")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_success "All required files found"
}

# Main deployment function
main() {
    print_status "Starting SI Data Generator Native App deployment..."
    echo ""
    
    # Validate environment
    check_snowflake_cli
    check_snowflake_connection
    validate_files
    
    echo ""
    print_status "Deployment steps:"
    echo "  1. Create application package"
    echo "  2. Add version to package"
    echo "  3. Create/upgrade application"
    echo ""
    
    # Deploy the application
    create_app_package
    add_version_to_package
    create_application
    
    echo ""
    print_success "🎉 SI Data Generator Native App deployed successfully!"
    echo ""
    show_app_info
}

# Run main function
main "$@"
