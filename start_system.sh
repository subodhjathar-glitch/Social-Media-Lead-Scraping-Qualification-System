#!/bin/bash

# Isha Lead Engagement System - Easy Startup Script
# This script handles everything needed to run the system

set -e  # Exit on error

VENV_PYTHON="./venv/bin/python3"
VENV_STREAMLIT="./venv/bin/streamlit"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🕉️  Isha Lead Engagement System - Startup                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Function to print colored messages
print_success() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

print_info() {
    echo "ℹ️  $1"
}

# Check if venv exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Install/update dependencies
print_info "Checking dependencies..."
$VENV_PYTHON -m pip install -q --upgrade pip
$VENV_PYTHON -m pip install -q -r requirements.txt
print_success "Dependencies installed"

# Run system check
print_info "Running system health check..."
echo ""
$VENV_PYTHON system_check.py

# Check if system check passed
if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Choose an option:                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  1. Run Scraper (collect leads from YouTube)"
    echo "  2. Launch UI (approve replies, manage system)"
    echo "  3. Run Scraper + Launch UI (both)"
    echo "  4. Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice

    case $choice in
        1)
            print_info "Starting scraper..."
            $VENV_PYTHON src/main.py
            ;;
        2)
            print_info "Launching UI..."
            print_info "Open browser: http://localhost:8501"
            $VENV_STREAMLIT run streamlit_app.py
            ;;
        3)
            print_info "Starting scraper first..."
            $VENV_PYTHON src/main.py

            echo ""
            print_success "Scraping complete!"
            echo ""
            print_info "Now launching UI..."
            print_info "Open browser: http://localhost:8501"
            $VENV_STREAMLIT run streamlit_app.py
            ;;
        4)
            print_info "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice!"
            exit 1
            ;;
    esac
else
    print_error "System check failed! Please fix issues before running."
    exit 1
fi
