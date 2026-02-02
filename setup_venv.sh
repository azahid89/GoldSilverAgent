#!/bin/bash
# Setup script with virtual environment for Gold & Silver Agent System

echo "=========================================="
echo "Gold & Silver Agent System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 is required"; exit 1; }

# Check if venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo "python3-venv is not installed."
    echo "Please install it first:"
    echo "  sudo apt install python3.12-venv"
    echo ""
    echo "Or use the --user flag method instead (see README)"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from env.sample..."
    if [ -f env.sample ]; then
        cp env.sample .env
        echo "Created .env file. Please edit it and add your API keys."
    else
        echo "Warning: env.sample not found. Creating basic .env file..."
        cat > .env << EOF
# Gold & Silver Agent System - Environment Variables
FRED_API_KEY=
OPENAI_API_KEY=
EOF
        echo "Created basic .env file. Please add your API keys."
    fi
else
    echo ".env file already exists."
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To run the project:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: python main.py"
echo ""
echo "Or use the run script: ./run.sh"
echo ""

