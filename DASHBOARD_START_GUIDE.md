# Dashboard Start Guide

## Issue: Permission Error with Plotly

The dashboard is failing to start due to a permission error with the `plotly` package.

## Quick Fix

Run these commands in your terminal:

```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate

# Option 1: Fix permissions
chmod -R u+r .venv/lib/python3.13/site-packages/plotly

# Option 2: Reinstall plotly (if Option 1 doesn't work)
pip install --force-reinstall --no-cache-dir plotly

# Then start the dashboard
streamlit run dashboard/app.py --server.port 8501
```

## Alternative: Use the Fix Script

```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
./fix_plotly_permissions.sh
streamlit run dashboard/app.py --server.port 8501
```

## If Still Not Working

If you still get permission errors, try:

1. **Reinstall plotly and streamlit:**
   ```bash
   pip uninstall plotly streamlit -y
   pip install plotly streamlit
   ```

2. **Check file permissions:**
   ```bash
   ls -la .venv/lib/python3.13/site-packages/plotly/graph_objs/sankey/
   ```

3. **Fix all permissions in venv:**
   ```bash
   chmod -R u+r .venv/lib/python3.13/site-packages/
   ```

## Start Dashboard

Once permissions are fixed:

```bash
source .venv/bin/activate
streamlit run dashboard/app.py --server.port 8501
```

Then open: **http://localhost:8501**
