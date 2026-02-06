#!/usr/bin/env python3
"""
Run the Streamlit dashboard
"""
import subprocess
import sys
import os

def main():
    dashboard_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "dashboard",
        "app.py"
    )
    
    print("=" * 70)
    print("Starting Trading Platform Dashboard")
    print("=" * 70)
    print()
    print("The dashboard will open in your browser.")
    print("If it doesn't, navigate to: http://localhost:8501")
    print()
    print("Make sure the trading interface is running:")
    print("  python scripts/run_interface.py")
    print()
    print("=" * 70)
    print()
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])

if __name__ == "__main__":
    main()
