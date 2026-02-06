#!/usr/bin/env python3
"""
Quick Start Example: Demonstrates the full trading platform workflow
"""
import sys
import os
import asyncio
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lob.order_book import LimitOrderBook, Order
from src.backtest.replay import BacktestEngine, generate_synthetic_ticks
from src.metrics.performance import PerformanceMetrics


def main():
    print("=" * 60)
    print("Proprietary Trading Platform - Quick Start Example")
    print("=" * 60)
    print()
    
    # Step 1: Create LOB
    print("1. Creating Limit Order Book...")
    lob = LimitOrderBook(tick_size=0.01)
    print("   ✓ LOB created")
    print()
    
    # Step 2: Add some initial orders to create a book
    print("2. Building initial order book...")
    mid = 100.0
    for i in range(5):
        bid_price = round(mid - (i + 1) * 0.01, 2)
        ask_price = round(mid + (i + 1) * 0.01, 2)
        
        bid_order = Order(
            order_id=f"init_bid_{i}",
            client_id="MARKET",
            side="buy",
            type="limit",
            price=bid_price,
            size=10
        )
        ask_order = Order(
            order_id=f"init_ask_{i}",
            client_id="MARKET",
            side="sell",
            type="limit",
            price=ask_price,
            size=10
        )
        lob.add_order(bid_order)
        lob.add_order(ask_order)
    
    snapshot = lob.get_book_snapshot()
    print(f"   ✓ Book built: Mid={snapshot['mid']:.2f}, Spread={snapshot['spread']:.2f}")
    print()
    
    # Step 3: Submit a market-making order
    print("3. Submitting market-making quote...")
    mm_bid = Order(
        order_id="mm_bid_1",
        client_id="mm_1",
        side="buy",
        type="limit",
        price=round(mid - 0.05, 2),
        size=5
    )
    mm_ask = Order(
        order_id="mm_ask_1",
        client_id="mm_1",
        side="sell",
        type="limit",
        price=round(mid + 0.05, 2),
        size=5
    )
    
    fills_bid = lob.add_order(mm_bid)
    fills_ask = lob.add_order(mm_ask)
    
    print(f"   ✓ Quotes posted: Bid={mm_bid.price:.2f}, Ask={mm_ask.price:.2f}")
    print(f"   ✓ Fills: {len(fills_bid)} bid fills, {len(fills_ask)} ask fills")
    print()
    
    # Step 4: Generate synthetic ticks and run backtest
    print("4. Running backtest with synthetic data...")
    ticks = generate_synthetic_ticks(n_ticks=500, initial_price=mid, volatility=0.02)
    print(f"   ✓ Generated {len(ticks)} synthetic ticks")
    
    engine = BacktestEngine(lob)
    engine.load_ticks(ticks)
    results = engine.run_replay(strategy_client_id="mm_1")
    
    print(f"   ✓ Backtest complete:")
    print(f"     - Total ticks processed: {results['total_ticks']}")
    print(f"     - Total fills: {results['total_fills']}")
    print(f"     - Final position: {results['final_position']}")
    print(f"     - Final PnL: {results['final_pnl']:.2f}")
    print()
    
    # Step 5: Compute performance metrics
    print("5. Computing performance metrics...")
    metrics = PerformanceMetrics.compute_metrics(
        fills=results['metrics']['fills'],
        pnl_history=results['metrics']['pnl']
    )
    
    print("   ✓ Key Metrics:")
    print(f"     - Total Fills: {metrics.get('total_fills', 0)}")
    print(f"     - Final PnL: {metrics.get('final_pnl', 0):.2f}")
    print(f"     - Max Drawdown: {metrics.get('max_drawdown', 0):.2f}")
    if 'sharpe_ratio' in metrics:
        print(f"     - Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print()
    
    print("=" * 60)
    print("Quick Start Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("  1. Start the trading interface: python scripts/run_interface.py")
    print("  2. Run a strategy: python scripts/run_strategy.py --strategy symmetric")
    print("  3. Train RL agent: python scripts/train_rl.py")
    print("  4. Explore notebooks/example_analysis.ipynb for detailed analysis")
    print()


if __name__ == "__main__":
    main()
