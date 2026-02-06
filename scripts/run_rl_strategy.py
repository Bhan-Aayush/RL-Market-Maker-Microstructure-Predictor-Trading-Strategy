#!/usr/bin/env python3
"""
Run RL-based market-making strategy
"""
import sys
import os
import asyncio
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.strategies.rl_mm import RLMarketMaker
from src.strategies.rl_strategy_client import RLStrategyClient


async def main():
    parser = argparse.ArgumentParser(description="Run RL-based market-making strategy")
    parser.add_argument("--model-path", type=str, required=True,
                       help="Path to trained RL model")
    parser.add_argument("--client-id", type=str, default="rl_mm_1",
                       help="Client ID")
    parser.add_argument("--tick-size", type=float, default=0.01,
                       help="Tick size")
    parser.add_argument("--initial-mid", type=float, default=100.0,
                       help="Initial mid price")
    parser.add_argument("--quote-interval", type=float, default=0.5,
                       help="Quote update interval (seconds)")
    parser.add_argument("--use-predictor", action="store_true",
                       help="Use microstructure predictor")
    
    args = parser.parse_args()
    
    # Check if model exists
    if not os.path.exists(args.model_path):
        print(f"Error: Model file not found: {args.model_path}")
        print("Train a model first: python3 scripts/train_rl.py")
        sys.exit(1)
    
    print(f"Loading RL model from {args.model_path}...")
    
    # Create RL strategy
    try:
        strategy = RLMarketMaker(
            client_id=args.client_id,
            model_path=args.model_path,
            tick_size=args.tick_size,
            initial_mid=args.initial_mid,
            use_predictor=args.use_predictor
        )
    except Exception as e:
        print(f"Error creating RL strategy: {e}")
        sys.exit(1)
    
    print(f"RL Strategy {args.client_id} ready")
    print("Connecting to trading interface...")
    
    # Run strategy
    client = RLStrategyClient(strategy)
    try:
        await client.run(quote_interval=args.quote_interval)
    except KeyboardInterrupt:
        print("\nStopping RL strategy...")
        client.stop()


if __name__ == "__main__":
    asyncio.run(main())
