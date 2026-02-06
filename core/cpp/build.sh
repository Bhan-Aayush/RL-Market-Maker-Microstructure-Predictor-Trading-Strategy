#!/bin/bash
# Build script for C++ matching engine

set -e

echo "Building C++ Matching Engine..."

# Check if pybind11 is installed
python3 -c "import pybind11" 2>/dev/null || {
    echo "Installing pybind11..."
    pip3 install pybind11
}

# Build using setuptools (recommended)
echo "Building Python extension..."
python3 setup.py build_ext --inplace

echo "Build complete!"
echo "You can now import matching_engine_core from Python"
