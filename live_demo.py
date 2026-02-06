#!/usr/bin/env python3
"""
Live Demo: Shows the strategy connecting and trading in real-time
"""
import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.dirname(__file__))

from src.strategies.symmetric_mm import SymmetricMarketMaker
from src.strategies.strategy_client import StrategyClient

async def main():
    print("=" * 70)
    print("PROPRIETARY TRADING PLATFORM - LIVE DEMO")
    print("=" * 70)
    print()
    print("This demo will:")
    print("  1. Connect to trading interface")
    print("  2. Subscribe to real-time market data")
    print("  3. Post bid/ask quotes automatically")
    print("  4. Show live activity (quotes, fills, inventory)")
    print()
    print("Press Ctrl+C to stop")
    print()
    print("-" * 70)
    print()
    
    # Create strategy
    strategy = SymmetricMarketMaker(
        client_id="demo_mm",
        half_spread=0.05,
        quote_size=1
    )
    
    # Create client
    client = StrategyClient(strategy)
    
    print("Starting strategy...")
    print("Connecting to: ws://127.0.0.1:8000/ws/md")
    print()
    
    try:
        await client.run(quote_interval=0.5)
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("Demo stopped by user")
        print("=" * 70)
        client.stop()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
