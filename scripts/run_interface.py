#!/usr/bin/env python3
"""
Run the trading interface server
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.interface.trading_interface import create_app
from src.risk.risk_manager import RiskLimits
import uvicorn
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run trading interface with real or synthetic data")
    parser.add_argument("--data-source", type=str, default="synthetic",
                       choices=["synthetic", "yahoo", "alphavantage"],
                       help="Data source: synthetic, yahoo, or alphavantage")
    parser.add_argument("--symbol", type=str, default="AAPL",
                       help="Trading symbol (e.g., AAPL, MSFT, TSLA)")
    parser.add_argument("--api-key", type=str, default=None,
                       help="API key for Alpha Vantage (or set ALPHA_VANTAGE_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Configure risk limits
    risk_limits = RiskLimits(
        max_position=100,
        max_daily_loss=1000.0,
        max_order_rate=100,
        max_order_size=50,
        price_deviation_pct=0.05
    )
    
    # Configure data source
    data_source_config = {}
    if args.data_source == "alphavantage":
        api_key = args.api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            print("Warning: No Alpha Vantage API key provided. Using demo key (limited).")
            print("Get free API key at: https://www.alphavantage.co/support/#api-key")
            api_key = "demo"
        data_source_config["api_key"] = api_key
    
    app = create_app(
        risk_limits=risk_limits,
        data_source_type=args.data_source,
        data_source_config=data_source_config,
        symbol=args.symbol
    )
    
    print("=" * 60)
    print("Proprietary Trading Interface")
    print("=" * 60)
    print(f"Data Source: {args.data_source.upper()}")
    print(f"Symbol: {args.symbol}")
    print("API Server: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("WebSocket MD: ws://127.0.0.1:8000/ws/md")
    print("WebSocket Fills: ws://127.0.0.1:8000/ws/fills/{client_id}")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
