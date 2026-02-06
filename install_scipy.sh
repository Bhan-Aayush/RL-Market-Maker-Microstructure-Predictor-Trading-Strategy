#!/bin/bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate

# Set environment variables for OpenBLAS
export LDFLAGS="-L/opt/homebrew/opt/openblas/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openblas/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openblas/lib/pkgconfig"

# Install scipy
pip install scipy

echo ""
echo "✅ scipy installation complete!"
echo "Verify with: python3 -c 'import scipy; print(scipy.__version__)'"
