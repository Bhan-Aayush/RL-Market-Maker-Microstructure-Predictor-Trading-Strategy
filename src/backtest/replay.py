"""
Backtest/Replay system: Replay historical ticks through the same interface
"""
import asyncio
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import time

from ..lob.order_book import LimitOrderBook, Order


class TickReplay:
    """
    Replays historical tick data through LOB
    """
    
    def __init__(self, tick_data: pd.DataFrame):
        """
        Args:
            tick_data: DataFrame with columns: timestamp, price, size, side
        """
        self.tick_data = tick_data.sort_values("timestamp")
        self.current_idx = 0
    
    def get_next_tick(self) -> Optional[Dict]:
        """Get next tick in sequence"""
        if self.current_idx >= len(self.tick_data):
            return None
        
        row = self.tick_data.iloc[self.current_idx]
        self.current_idx += 1
        
        return {
            "timestamp": row["timestamp"],
            "price": row["price"],
            "size": row["size"],
            "side": row["side"]
        }
    
    def reset(self):
        """Reset to beginning"""
        self.current_idx = 0


class BacktestEngine:
    """
    Backtest engine that replays ticks and tracks performance
    """
    
    def __init__(self, lob: LimitOrderBook):
        self.lob = lob
        self.replay = None
        self.metrics = {
            "fills": [],
            "pnl": [],
            "inventory": [],
            "spreads": []
        }
    
    def load_ticks(self, tick_data: pd.DataFrame):
        """Load tick data for replay"""
        self.replay = TickReplay(tick_data)
    
    def run_replay(
        self,
        strategy_client_id: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Dict:
        """
        Run backtest replay
        
        Returns:
            Dictionary with performance metrics
        """
        if self.replay is None:
            raise ValueError("No tick data loaded. Call load_ticks() first.")
        
        self.replay.reset()
        
        initial_mid = self.lob.mid_price() or 100.0
        position = 0
        cash = 0.0
        realized_pnl = 0.0
        
        tick_count = 0
        
        while True:
            tick = self.replay.get_next_tick()
            if tick is None:
                break
            
            # Filter by time if specified
            if start_time and tick["timestamp"] < start_time:
                continue
            if end_time and tick["timestamp"] > end_time:
                break
            
            # Create market order from tick
            order = Order(
                order_id=f"replay_{tick_count}",
                client_id="REPLAY",
                side=tick["side"],
                type="market",
                size=tick["size"]
            )
            
            # Execute order
            fills = self.lob.add_order(order)
            
            # Track fills for strategy client
            for fill in fills:
                if fill.client_id == strategy_client_id:
                    if fill.side == "buy":
                        position += fill.size
                        cash -= fill.price * fill.size
                    else:
                        position -= fill.size
                        cash += fill.price * fill.size
                    
                    # Update realized P&L (simplified)
                    realized_pnl = cash + position * (self.lob.mid_price() or initial_mid)
                    
                    self.metrics["fills"].append({
                        "timestamp": fill.timestamp,
                        "price": fill.price,
                        "size": fill.size,
                        "side": fill.side
                    })
            
            # Record metrics
            mid = self.lob.mid_price() or initial_mid
            spread = self.lob.spread() or 0.0
            
            self.metrics["pnl"].append({
                "timestamp": tick["timestamp"],
                "realized": realized_pnl,
                "unrealized": position * (mid - initial_mid)
            })
            self.metrics["inventory"].append({
                "timestamp": tick["timestamp"],
                "position": position
            })
            self.metrics["spreads"].append({
                "timestamp": tick["timestamp"],
                "spread": spread
            })
            
            tick_count += 1
        
        # Compute final metrics
        final_mid = self.lob.mid_price() or initial_mid
        final_pnl = cash + position * (final_mid - initial_mid)
        
        return {
            "total_ticks": tick_count,
            "total_fills": len(self.metrics["fills"]),
            "final_position": position,
            "final_pnl": final_pnl,
            "realized_pnl": realized_pnl,
            "metrics": self.metrics
        }


def generate_synthetic_ticks(
    n_ticks: int = 1000,
    initial_price: float = 100.0,
    volatility: float = 0.02,
    tick_size: float = 0.01
) -> pd.DataFrame:
    """
    Generate synthetic tick data for testing
    
    Returns:
        DataFrame with columns: timestamp, price, size, side
    """
    np.random.seed(42)
    
    prices = [initial_price]
    for _ in range(n_ticks - 1):
        change = np.random.normal(0, volatility)
        new_price = prices[-1] * (1 + change)
        new_price = round(new_price / tick_size) * tick_size  # Round to tick
        prices.append(new_price)
    
    timestamps = [time.time() + i * 0.1 for i in range(n_ticks)]
    sides = np.random.choice(["buy", "sell"], n_ticks)
    sizes = np.random.randint(1, 10, n_ticks)
    
    return pd.DataFrame({
        "timestamp": timestamps,
        "price": prices,
        "size": sizes,
        "side": sides
    })
