#!/usr/bin/env python3
"""
Run a market-making strategy
"""
import sys
import os
import asyncio
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.strategies.symmetric_mm import SymmetricMarketMaker
from src.strategies.inventory_skew_mm import InventorySkewMarketMaker
from src.strategies.adaptive_spread_mm import AdaptiveSpreadMarketMaker
from src.strategies.strategy_client import StrategyClient


async def main():
    parser = argparse.ArgumentParser(description="Run market-making strategy")
    parser.add_argument("--strategy", type=str, default="symmetric",
                       choices=["symmetric", "inventory_skew", "adaptive", "rl"],
                       help="Strategy type")
    parser.add_argument("--model-path", type=str, default=None,
                       help="Path to RL model (required for 'rl' strategy)")
    parser.add_argument("--client-id", type=str, default="mm_1",
                       help="Client ID")
    parser.add_argument("--half-spread", type=float, default=0.05,
                       help="Half spread for symmetric strategy")
    parser.add_argument("--quote-size", type=int, default=1,
                       help="Quote size")
    parser.add_argument("--quote-interval", type=float, default=0.5,
                       help="Quote update interval (seconds)")
    
    args = parser.parse_args()
    
    # Create strategy
    if args.strategy == "symmetric":
        strategy = SymmetricMarketMaker(
            client_id=args.client_id,
            half_spread=args.half_spread,
            quote_size=args.quote_size
        )
    elif args.strategy == "inventory_skew":
        strategy = InventorySkewMarketMaker(
            client_id=args.client_id,
            half_spread=args.half_spread,
            quote_size=args.quote_size
        )
    elif args.strategy == "adaptive":
        strategy = AdaptiveSpreadMarketMaker(
            client_id=args.client_id,
            base_half_spread=args.half_spread,
            quote_size=args.quote_size
        )
    elif args.strategy == "rl":
        from src.strategies.rl_mm import RLMarketMaker
        from src.strategies.rl_strategy_client import RLStrategyClient
        
        if not args.model_path:
            print("Error: --model-path required for RL strategy")
            print("Train a model first: python3 scripts/train_rl.py")
            sys.exit(1)
        
        if not os.path.exists(args.model_path):
            print(f"Error: Model file not found: {args.model_path}")
            sys.exit(1)
        
        strategy = RLMarketMaker(
            client_id=args.client_id,
            model_path=args.model_path,
            tick_size=0.01,
            initial_mid=100.0
        )
        client = RLStrategyClient(strategy)
        print(f"Starting RL strategy (client_id: {args.client_id}, model: {args.model_path})")
        try:
            await client.run(quote_interval=args.quote_interval)
        except KeyboardInterrupt:
            print("\nStopping strategy...")
            client.stop()
        return
    
    print(f"Starting {args.strategy} strategy (client_id: {args.client_id})")
    
    # Run strategy
    client = StrategyClient(strategy)
    try:
        await client.run(quote_interval=args.quote_interval)
    except KeyboardInterrupt:
        print("\nStopping strategy...")
        client.stop()


if __name__ == "__main__":
    asyncio.run(main())
