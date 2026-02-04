#!/bin/bash
# Run script for Gold & Silver Agent System

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first:"
    echo "  ./setup_venv.sh"
    echo "  OR"
    echo "  bash setup_venv.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the main script
python main.py





