"""
Performance metrics and analytics
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class PerformanceMetrics:
    """
    Compute trading performance metrics
    """
    
    @staticmethod
    def compute_metrics(fills: List[Dict], pnl_history: List[Dict]) -> Dict:
        """
        Compute comprehensive performance metrics
        
        Args:
            fills: List of fill dictionaries with price, size, side, timestamp
            pnl_history: List of P&L snapshots with timestamp, realized, unrealized
        
        Returns:
            Dictionary of metrics
        """
        if not fills:
            return {}
        
        df_fills = pd.DataFrame(fills)
        df_pnl = pd.DataFrame(pnl_history)
        
        metrics = {}
        
        # Fill statistics
        if len(df_fills) > 0:
            metrics["total_fills"] = len(df_fills)
            metrics["avg_fill_size"] = df_fills["size"].mean()
            metrics["total_volume"] = df_fills["size"].sum()
            
            # Buy vs sell
            buy_fills = df_fills[df_fills["side"] == "buy"]
            sell_fills = df_fills[df_fills["side"] == "sell"]
            metrics["buy_fills"] = len(buy_fills)
            metrics["sell_fills"] = len(sell_fills)
            metrics["fill_imbalance"] = (len(buy_fills) - len(sell_fills)) / len(df_fills) if len(df_fills) > 0 else 0
        
        # P&L statistics
        if len(df_pnl) > 0:
            df_pnl["total_pnl"] = df_pnl["realized"] + df_pnl.get("unrealized", 0)
            
            metrics["final_pnl"] = df_pnl["total_pnl"].iloc[-1] if len(df_pnl) > 0 else 0
            metrics["max_pnl"] = df_pnl["total_pnl"].max()
            metrics["min_pnl"] = df_pnl["total_pnl"].min()
            metrics["avg_pnl"] = df_pnl["total_pnl"].mean()
            
            # Drawdown
            running_max = df_pnl["total_pnl"].cummax()
            drawdown = df_pnl["total_pnl"] - running_max
            metrics["max_drawdown"] = drawdown.min()
            metrics["max_drawdown_pct"] = (metrics["max_drawdown"] / running_max.max() * 100) if running_max.max() > 0 else 0
            
            # Sharpe ratio (simplified, annualized)
            returns = df_pnl["total_pnl"].diff().dropna()
            if len(returns) > 1 and returns.std() > 0:
                sharpe = (returns.mean() / returns.std()) * np.sqrt(252 * 24 * 60)  # Assuming minute bars
                metrics["sharpe_ratio"] = sharpe
            else:
                metrics["sharpe_ratio"] = 0.0
        
        # Realized spread (if we have quote data)
        # This would require tracking quoted prices vs fill prices
        
        return metrics
    
    @staticmethod
    def compute_inventory_metrics(inventory_history: List[Dict]) -> Dict:
        """
        Compute inventory-related metrics
        
        Args:
            inventory_history: List of inventory snapshots with timestamp, position
        
        Returns:
            Dictionary of inventory metrics
        """
        if not inventory_history:
            return {}
        
        df = pd.DataFrame(inventory_history)
        
        metrics = {
            "max_inventory": df["position"].abs().max(),
            "avg_inventory": df["position"].mean(),
            "final_inventory": df["position"].iloc[-1] if len(df) > 0 else 0,
            "inventory_std": df["position"].std()
        }
        
        # Time-weighted average inventory
        if len(df) > 1:
            df["time_diff"] = df["timestamp"].diff()
            df["weighted_inv"] = df["position"].abs() * df["time_diff"]
            metrics["time_weighted_avg_inventory"] = df["weighted_inv"].sum() / df["time_diff"].sum() if df["time_diff"].sum() > 0 else 0
        else:
            metrics["time_weighted_avg_inventory"] = 0
        
        return metrics
    
    @staticmethod
    def compute_spread_metrics(spread_history: List[Dict]) -> Dict:
        """
        Compute spread-related metrics
        
        Args:
            spread_history: List of spread snapshots with timestamp, spread
        
        Returns:
            Dictionary of spread metrics
        """
        if not spread_history:
            return {}
        
        df = pd.DataFrame(spread_history)
        
        return {
            "avg_spread": df["spread"].mean(),
            "min_spread": df["spread"].min(),
            "max_spread": df["spread"].max(),
            "spread_std": df["spread"].std()
        }
