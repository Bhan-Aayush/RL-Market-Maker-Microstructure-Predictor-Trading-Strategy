#!/usr/bin/env python3
"""
Example: Using Real Market Data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.data.market_data_source import create_data_source

def main():
    print("=" * 70)
    print("REAL MARKET DATA EXAMPLES")
    print("=" * 70)
    print()
    
    # Example 1: Yahoo Finance
    print("1. Yahoo Finance - Apple (AAPL)")
    print("-" * 70)
    try:
        yahoo = create_data_source("yahoo")
        quote = yahoo.get_latest_quote("AAPL")
        print(f"   Symbol: {quote['symbol']}")
        print(f"   Last Price: ${quote['last_price']:.2f}")
        print(f"   Bid: ${quote['bid']:.2f}")
        print(f"   Ask: ${quote['ask']:.2f}")
        print(f"   Spread: ${quote['spread']:.4f}")
        print(f"   Volume: {quote['volume']:,}")
        print(f"   Timestamp: {quote['timestamp']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Example 2: Multiple symbols
    print("2. Multiple Symbols")
    print("-" * 70)
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    for symbol in symbols:
        try:
            quote = yahoo.get_latest_quote(symbol)
            print(f"   {symbol}: ${quote['last_price']:.2f} (Vol: {quote['volume']:,})")
        except Exception as e:
            print(f"   {symbol}: Error - {e}")
    
    print()
    print("=" * 70)
    print("To use with trading interface:")
    print("  python3 scripts/run_interface.py --data-source yahoo --symbol AAPL")
    print("=" * 70)

if __name__ == "__main__":
    main()
