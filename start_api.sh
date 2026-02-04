#!/bin/bash
# Start the Flask API server

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first:"
    echo "  ./setup_venv.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start Flask server
echo "Starting API server on http://localhost:5000"
python api_server.py





