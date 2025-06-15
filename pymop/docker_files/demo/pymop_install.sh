#!/bin/bash
set -e  # Exit on error

echo "Creating a virtual environment for PyMOP..."
python3 -m venv /experiment/pymop-venv
source /experiment/pymop-venv/bin/activate

echo "Installing dependencies..."
pip install /experiment/pymop-artifacts-rv/pymop/

echo "Installation complete."