"""
Statistical Arbitrage / Pairs Trading
Cointegration-based mean reversion strategy
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import stats
from statsmodels.tsa.stattools import coint, adfuller
from dataclasses import dataclass


@dataclass
class Pair:
    """Represents a trading pair"""
    symbol1: str
    symbol2: str
    hedge_ratio: float  # How many units of symbol2 per unit of symbol1
    cointegration_pvalue: float
    half_life: float  # Mean reversion half-life (days)
    spread_mean: float
    spread_std: float


class PairsTradingStrategy:
    """
    Statistical arbitrage using pairs trading
    """
    
    def __init__(self, lookback_window: int = 252):
        self.lookback_window = lookback_window
        self.pairs: List[Pair] = []
        self.spread_history: Dict[Tuple[str, str], List[float]] = {}
    
    def find_cointegrated_pairs(
        self,
        price_data: pd.DataFrame,
        pvalue_threshold: float = 0.05
    ) -> List[Pair]:
        """
        Find cointegrated pairs from price data
        
        Args:
            price_data: DataFrame with columns as symbols, rows as timestamps
            pvalue_threshold: Maximum p-value for cointegration test
        
        Returns:
            List of cointegrated pairs
        """
        symbols = price_data.columns.tolist()
        pairs = []
        
        for i, symbol1 in enumerate(symbols):
            for symbol2 in symbols[i+1:]:
                # Get price series
                prices1 = price_data[symbol1].dropna()
                prices2 = price_data[symbol2].dropna()
                
                # Align series
                common_idx = prices1.index.intersection(prices2.index)
                if len(common_idx) < 50:  # Need minimum data
                    continue
                
                p1 = prices1.loc[common_idx]
                p2 = prices2.loc[common_idx]
                
                # Test for cointegration
                try:
                    score, pvalue, _ = coint(p1, p2)
                    
                    if pvalue < pvalue_threshold:
                        # Calculate hedge ratio (OLS regression)
                        hedge_ratio = np.polyfit(p1, p2, 1)[0]
                        
                        # Calculate spread
                        spread = p2 - hedge_ratio * p1
                        
                        # Calculate half-life of mean reversion
                        spread_lag = spread.shift(1).dropna()
                        spread_diff = spread.diff().dropna()
                        
                        if len(spread_lag) > 0 and len(spread_diff) > 0:
                            # Align
                            common = spread_lag.index.intersection(spread_diff.index)
                            if len(common) > 10:
                                X = spread_lag.loc[common].values.reshape(-1, 1)
                                y = spread_diff.loc[common].values
                                
                                # OLS: spread_diff = alpha + beta * spread_lag
                                beta = np.linalg.lstsq(X, y, rcond=None)[0][0]
                                
                                if beta < 0:
                                    half_life = -np.log(2) / beta
                                else:
                                    half_life = np.inf
                        else:
                            half_life = np.inf
                        
                        pair = Pair(
                            symbol1=symbol1,
                            symbol2=symbol2,
                            hedge_ratio=hedge_ratio,
                            cointegration_pvalue=pvalue,
                            half_life=half_life,
                            spread_mean=float(spread.mean()),
                            spread_std=float(spread.std())
                        )
                        pairs.append(pair)
                except Exception as e:
                    # Skip if cointegration test fails
                    continue
        
        self.pairs = pairs
        return pairs
    
    def calculate_spread(self, price1: float, price2: float, pair: Pair) -> float:
        """Calculate current spread for pair"""
        return price2 - pair.hedge_ratio * price1
    
    def calculate_zscore(self, spread: float, pair: Pair) -> float:
        """Calculate z-score of spread"""
        return (spread - pair.spread_mean) / pair.spread_std if pair.spread_std > 0 else 0
    
    def get_trading_signal(
        self,
        price1: float,
        price2: float,
        pair: Pair,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5
    ) -> Dict:
        """
        Get trading signal for pair
        
        Returns:
            {
                "signal": "long", "short", or "close",
                "zscore": z-score of spread,
                "spread": current spread,
                "entry_price1": price1,
                "entry_price2": price2
            }
        """
        spread = self.calculate_spread(price1, price2, pair)
        zscore = self.calculate_zscore(spread, pair)
        
        # Long spread: buy symbol1, sell symbol2 (when spread is low)
        # Short spread: sell symbol1, buy symbol2 (when spread is high)
        
        if abs(zscore) > entry_threshold:
            if zscore < -entry_threshold:
                # Spread is low, go long (buy spread)
                signal = "long"
            else:
                # Spread is high, go short (sell spread)
                signal = "short"
        elif abs(zscore) < exit_threshold:
            # Close position
            signal = "close"
        else:
            signal = "hold"
        
        return {
            "signal": signal,
            "zscore": zscore,
            "spread": spread,
            "entry_price1": price1,
            "entry_price2": price2,
            "hedge_ratio": pair.hedge_ratio
        }
    
    def calculate_pnl(
        self,
        entry_price1: float,
        entry_price2: float,
        current_price1: float,
        current_price2: float,
        pair: Pair,
        position_size: float = 1.0,
        side: str = "long"
    ) -> float:
        """
        Calculate P&L for pairs position
        
        Args:
            side: "long" (bought spread) or "short" (sold spread)
        """
        if side == "long":
            # Long: +1 unit symbol1, -hedge_ratio units symbol2
            pnl = (current_price1 - entry_price1) - pair.hedge_ratio * (current_price2 - entry_price2)
        else:
            # Short: -1 unit symbol1, +hedge_ratio units symbol2
            pnl = -(current_price1 - entry_price1) + pair.hedge_ratio * (current_price2 - entry_price2)
        
        return pnl * position_size
