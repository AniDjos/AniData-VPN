#!/bin/bash

# Make sure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up AniData VPN environment...${NC}"

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install system dependencies if needed
if ! dpkg -l | grep -q "python3-pyqt5"; then
    echo "Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3-pyqt5 python3-pyqt5.qtwebengine
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install pyqtgraph numpy

# Create necessary directories
mkdir -p ~/.anidata/config/wireguard
mkdir -p ~/.anidata/servers

# Make run script executable
chmod +x run_modern_ui.py

echo -e "${GREEN}Setup complete!${NC}"
echo "To run the application, use: ./run_modern_ui.py"

# Deactivate virtual environment
deactivate