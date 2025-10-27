#!/bin/bash

###############################################################################
# AI-Powered Effort Expense Management System - Launcher Script
# This script will set up, install dependencies, and launch the application
###############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored messages
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

###############################################################################
# Step 1: Welcome Message and System Check
###############################################################################

clear
print_header "🚀 AI-Powered Effort Expense Management System"
echo -e "${CYAN}Welcome to the Effort Expense Management System!${NC}"
echo -e "${PURPLE}This script will automatically set up and launch the application.${NC}"
echo ""

# Check if running on Windows (Git Bash, WSL, etc.)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    IS_WINDOWS=true
    print_info "Detected: Windows environment"
else
    IS_WINDOWS=false
    print_info "Detected: Unix/Linux environment"
fi

###############################################################################
# Step 2: Check Python Installation
###############################################################################

print_header "Step 1: Checking Python Installation"

if command_exists python3; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command_exists python; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    print_error "Python is not installed!"
    echo "Please install Python 3.8 or higher from https://python.org"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_success "Python found: $PYTHON_VERSION"

# Check Python version (should be 3.8 or higher)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    echo "Please upgrade Python and try again."
    exit 1
fi

###############################################################################
# Step 3: Create Virtual Environment
###############################################################################

print_header "Step 2: Setting Up Virtual Environment"

VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    print_info "Virtual environment already exists at: $VENV_DIR"
    read -p "Do you want to recreate it? (y/n): " RECREATE_VENV
    
    if [ "$RECREATE_VENV" = "y" ] || [ "$RECREATE_VENV" = "Y" ]; then
        print_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        print_success "Virtual environment removed"
    else
        print_info "Using existing virtual environment"
        SKIP_VENV_CREATE=true
    fi
fi

if [ "$SKIP_VENV_CREATE" != "true" ]; then
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_success "Virtual environment created successfully"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
if [ "$IS_WINDOWS" = true ]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi

print_success "Virtual environment activated"

###############################################################################
# Step 4: Upgrade pip and Install Dependencies
###############################################################################

print_header "Step 3: Installing Dependencies"

print_info "Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip --quiet
print_success "pip upgraded"

if [ -f "requirements.txt" ]; then
    print_info "Installing required packages..."
    print_info "This may take a few minutes..."
    
    # Show progress
    $PIP_CMD install --upgrade pip --quiet
    $PIP_CMD install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "All dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        echo "Please check the error messages above and try again."
        exit 1
    fi
else
    print_error "requirements.txt not found!"
    exit 1
fi

###############################################################################
# Step 5: Environment Configuration
###############################################################################

print_header "Step 4: Environment Configuration"

if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    
    if [ -f "env_example.txt" ]; then
        cp env_example.txt .env
        print_success ".env file created from template"
        print_warning "Please edit .env file with your credentials (optional)"
        print_info "Location: $(pwd)/.env"
    else
        print_warning "env_example.txt not found. Creating empty .env file..."
        touch .env
    fi
else
    print_info ".env file already exists"
fi

###############################################################################
# Step 6: Check Application Files
###############################################################################

print_header "Step 5: Checking Application Files"

MISSING_FILES=0

# Check for required files
required_files=("streamlit_app.py" "data_processor.py" "catboost_model.py" "config.py")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    print_error "$MISSING_FILES required file(s) are missing!"
    exit 1
fi

###############################################################################
# Step 7: Display System Information
###############################################################################

print_header "System Information"

echo -e "${CYAN}Application Details:${NC}"
echo "  • Python Version: $PYTHON_VERSION"
echo "  • Virtual Environment: $VENV_DIR"
echo "  • Platform: $(uname -s)"
echo "  • Working Directory: $(pwd)"
echo ""

echo -e "${CYAN}Key Features:${NC}"
echo "  • AI-powered effort expense prediction"
echo "  • CatBoost machine learning model"
echo "  • Data visualization and analysis"
echo "  • Microsoft 365 integration (optional)"
echo "  • Automated notification system"
echo ""

###############################################################################
# Step 8: Launch Application
###############################################################################

print_header "🎉 Setup Complete!"

echo -e "${GREEN}All systems ready! Launching the application...${NC}"
echo ""
print_info "The application will open in your default browser"
print_info "If it doesn't open automatically, go to: http://localhost:8501"
echo ""
print_warning "Press Ctrl+C to stop the application"
echo ""

# Wait a moment before launching
sleep 2

# Launch Streamlit application
print_info "Starting Streamlit application..."
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Application is starting...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Run the Streamlit app
streamlit run streamlit_app.py --server.headless true

# This will only execute if the app is stopped
echo ""
print_header "Application Stopped"

read -p "Do you want to restart the application? (y/n): " RESTART

if [ "$RESTART" = "y" ] || [ "$RESTART" = "Y" ]; then
    exec "$0" "$@"
else
    print_info "Thank you for using the Effort Expense Management System!"
    exit 0
fi

