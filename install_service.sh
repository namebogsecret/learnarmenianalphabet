#!/bin/bash
# Installation script for Learn Armenian Alphabet Service

set -e

echo "Installing Learn Armenian Alphabet Service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# Get the actual script directory (works even when run via sudo)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define installation directory
INSTALL_DIR="/root/learnarmenianalphabet"

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
fi

# Copy files to installation directory
echo "Copying files to $INSTALL_DIR..."
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' --exclude='.venv' "$SCRIPT_DIR/" "$INSTALL_DIR/"

# Make the startup script executable
chmod +x "$INSTALL_DIR/learn_armenian.sh"

# Copy systemd service file
echo "Installing systemd service..."
cp "$INSTALL_DIR/learnarmenian.service" /etc/systemd/system/

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service
echo "Enabling service to start on boot..."
systemctl enable learnarmenian.service

# Check if .env file exists
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Please create $INSTALL_DIR/.env based on $INSTALL_DIR/.env.example"
    echo "and configure your Telegram bot token and other settings."
    echo ""
fi

# Ask if user wants to start the service now
read -p "Do you want to start the service now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting service..."
    systemctl start learnarmenian.service
    sleep 2
    echo ""
    echo "Service status:"
    systemctl status learnarmenian.service --no-pager
fi

echo ""
echo "Installation complete!"
echo ""
echo "Useful commands:"
echo "  Start service:   sudo systemctl start learnarmenian.service"
echo "  Stop service:    sudo systemctl stop learnarmenian.service"
echo "  Restart service: sudo systemctl restart learnarmenian.service"
echo "  View status:     sudo systemctl status learnarmenian.service"
echo "  View logs:       sudo journalctl -u learnarmenian.service -f"
