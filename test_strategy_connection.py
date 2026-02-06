#!/usr/bin/env python3
"""
Quick test to verify strategy can connect to trading interface
"""
import sys
import os
import asyncio
import time

sys.path.insert(0, os.path.dirname(__file__))

from src.strategies.symmetric_mm import SymmetricMarketMaker
from src.strategies.strategy_client import StrategyClient

async def test_connection():
    print("=" * 60)
    print("Testing Strategy Connection to Trading Interface")
    print("=" * 60)
    print()
    
    # Check if interface is running
    import requests
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        if response.status_code == 200:
            print("✓ Trading interface is running at http://127.0.0.1:8000")
        else:
            print("⚠ Interface responded but with status:", response.status_code)
    except Exception as e:
        print(f"✗ Cannot connect to trading interface: {e}")
        print("  Start it with: python3 scripts/run_interface.py")
        return
    
    print()
    print("Creating symmetric market maker...")
    strategy = SymmetricMarketMaker(
        client_id="test_mm",
        half_spread=0.05,
        quote_size=1
    )
    print("✓ Strategy created")
    
    print()
    print("Connecting to trading interface...")
    print("  - Market data WebSocket: ws://127.0.0.1:8000/ws/md")
    print("  - Fills WebSocket: ws://127.0.0.1:8000/ws/fills/test_mm")
    print()
    print("Starting strategy (will run for 10 seconds)...")
    print("  You should see:")
    print("    - Market data updates")
    print("    - Quotes being posted")
    print("    - Any fills that occur")
    print()
    print("-" * 60)
    
    client = StrategyClient(strategy)
    
    # Run for 10 seconds then stop
    async def run_with_timeout():
        try:
            await asyncio.wait_for(client.run(quote_interval=0.5), timeout=10.0)
        except asyncio.TimeoutError:
            print("\n" + "-" * 60)
            print("Test completed (10 seconds)")
            client.stop()
    
    try:
        await run_with_timeout()
    except KeyboardInterrupt:
        print("\nStopped by user")
        client.stop()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
