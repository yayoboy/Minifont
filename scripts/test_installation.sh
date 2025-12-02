#!/bin/bash
# Test installation script for Minifont

set -e

echo "=========================================="
echo "Minifont Installation Test"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python -m venv test_venv
source test_venv/bin/activate

# Install package
echo "Installing Minifont..."
pip install -e .

# Run tests
echo "Running tests..."
pytest -v

# Test CLI
echo "Testing CLI..."
minifont --version
minifont --list-presets

echo ""
echo "=========================================="
echo "✓ Installation test completed successfully!"
echo "=========================================="

# Cleanup
deactivate
rm -rf test_venv
