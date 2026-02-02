#!/bin/bash
# Setup script for Gold & Silver Agent System

echo "=========================================="
echo "Gold & Silver Agent System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 is required"; exit 1; }

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    echo "Warning: pip is not installed."
    echo "Please install pip first:"
    echo "  sudo apt install python3-pip"
    echo "  OR"
    echo "  python3 -m ensurepip --upgrade"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
python3 -m pip install --user -r requirements.txt

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
echo "Next steps:"
echo "1. Edit .env file and add your API keys (optional but recommended)"
echo "2. Run: python3 main.py"
echo ""

