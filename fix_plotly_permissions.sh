#!/bin/bash
# Fix plotly permissions issue

echo "🔧 Fixing plotly permissions..."

# Activate virtual environment
source .venv/bin/activate

# Fix permissions on plotly package
PLOTLY_PATH=".venv/lib/python3.13/site-packages/plotly"
if [ -d "$PLOTLY_PATH" ]; then
    echo "Fixing permissions for plotly package..."
    chmod -R u+r "$PLOTLY_PATH"
    echo "✅ Permissions fixed!"
else
    echo "❌ Plotly package not found at $PLOTLY_PATH"
fi

# Try to reinstall plotly if permissions fix doesn't work
echo ""
echo "If permissions fix doesn't work, try reinstalling:"
echo "  pip install --force-reinstall --no-cache-dir plotly"
