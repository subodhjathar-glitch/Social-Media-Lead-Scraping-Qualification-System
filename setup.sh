#!/bin/bash

# Setup script for Social Media Lead Scraper

echo "=========================================="
echo "Social Media Lead Scraper - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment (optional but recommended)
echo ""
read -p "Create virtual environment? (recommended) [y/N]: " create_venv

if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated."
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo ""
echo "✓ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it with your API keys:"
    echo "  nano .env"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✓ Logs directory created"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys: nano .env"
echo "2. Set up your Airtable base with required fields (see README.md)"
echo "3. Test locally: python -m src.main"
echo "4. Set up GitHub Actions with secrets"
echo ""
echo "For detailed instructions, see README.md"
echo ""
