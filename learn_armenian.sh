#!/bin/bash
# Learn Armenian Alphabet Service Start Script

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    . .env
    set +a
    echo "Environment variables loaded from .env"
else
    echo "Warning: .env file not found"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    . venv/bin/activate
    echo "Virtual environment activated"
elif [ -d ".venv" ]; then
    . .venv/bin/activate
    echo "Virtual environment activated"
else
    echo "No virtual environment found, using system Python"
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Check if required packages are installed
if [ -f requirements.txt ]; then
    echo "Installing/updating dependencies..."
    python3 -m pip install -r requirements.txt --quiet
fi

# Start the bot
echo "Starting Learn Armenian Bot..."
exec python3 main.py
