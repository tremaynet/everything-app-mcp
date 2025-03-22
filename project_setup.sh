#!/bin/bash

# Setup script for The Everything App MCP
# This script sets up the Python code quality monitoring system

set -e

echo "Setting up The Everything App MCP..."

# Create directories
mkdir -p mcp_results
mkdir -p aws_lambdas

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install Node.js and npm first."
    exit 1
fi

# Install pyright
echo "Installing pyright..."
npm install -g pyright

# Verify installation
if ! command -v pyright &> /dev/null; then
    echo "pyright installation failed. Please install manually."
    exit 1
fi

echo "Testing pyright..."
pyright --version

# Make the monitor script executable
chmod +x mcp_monitor.py

echo "Setup complete!"
echo "Usage: ./mcp_monitor.py [file_path]"