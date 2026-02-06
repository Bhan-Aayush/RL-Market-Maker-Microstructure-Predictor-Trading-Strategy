"""
Regime Detection: Identify market regimes (bull/bear, high/low vol)
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
from collections import deque


@dataclass
class MarketRegime:
    """Market regime classification"""
    regime_type: Literal["bull", "bear", "high_vol", "low_vol", "trending", "mean_reverting"]
    confidence: float
    start_time: float
    end_time: Optional[float] = None


class RegimeDetector:
    """
    Detects market regimes using various methods
    """
    
    def __init__(self, lookback_window: int = 60):
        self.lookback_window = lookback_window
        self.returns_history: deque = deque(maxlen=lookback_window)
        self.prices_history: deque = deque(maxlen=lookback_window)
        self.volatility_history: deque = deque(maxlen=lookback_window)
    
    def add_observation(self, price: float, timestamp: float):
        """Add price observation"""
        if len(self.prices_history) > 0:
            prev_price = self.prices_history[-1][0]
            ret = (price - prev_price) / prev_price
            self.returns_history.append(ret)
        
        self.prices_history.append((price, timestamp))
        
        # Update volatility (rolling std)
        if len(self.returns_history) >= 20:
            recent_returns = list(self.returns_history)[-20:]
            vol = np.std(recent_returns)
            self.volatility_history.append(vol)
    
    def detect_volatility_regime(self) -> Dict:
        """
        Detect high/low volatility regime
        """
        if len(self.volatility_history) < 20:
            return {"regime": "unknown", "confidence": 0.0}
        
        recent_vol = list(self.volatility_history)[-20:]
        avg_vol = np.mean(recent_vol)
        historical_vol = np.mean(list(self.volatility_history))
        
        vol_ratio = avg_vol / historical_vol if historical_vol > 0 else 1.0
        
        if vol_ratio > 1.5:
            return {
                "regime": "high_vol",
                "confidence": min(1.0, (vol_ratio - 1.0) / 0.5),
                "volatility_ratio": vol_ratio
            }
        elif vol_ratio < 0.7:
            return {
                "regime": "low_vol",
                "confidence": min(1.0, (1.0 - vol_ratio) / 0.3),
                "volatility_ratio": vol_ratio
            }
        else:
            return {
                "regime": "normal_vol",
                "confidence": 0.5,
                "volatility_ratio": vol_ratio
            }
    
    def detect_trend_regime(self) -> Dict:
        """
        Detect trending vs mean-reverting regime
        """
        if len(self.prices_history) < 30:
            return {"regime": "unknown", "confidence": 0.0}
        
        prices = np.array([p[0] for p in list(self.prices_history)[-30:]])
        
        # Calculate Hurst exponent (simplified)
        # H > 0.5 = trending, H < 0.5 = mean-reverting
        returns = np.diff(prices) / prices[:-1]
        
        # Simplified Hurst calculation
        lags = [2, 5, 10, 20]
        variances = []
        for lag in lags:
            if len(returns) >= lag:
                lagged_returns = returns[lag:] - returns[:-lag]
                variances.append(np.var(lagged_returns))
        
        if len(variances) < 2:
            return {"regime": "unknown", "confidence": 0.0}
        
        # Estimate Hurst from variance scaling
        log_lags = np.log(lags[:len(variances)])
        log_vars = np.log(variances)
        
        if len(log_lags) > 1:
            hurst = 0.5 + 0.5 * np.polyfit(log_lags, log_vars, 1)[0]
        else:
            hurst = 0.5
        
        if hurst > 0.6:
            return {
                "regime": "trending",
                "confidence": min(1.0, (hurst - 0.5) / 0.3),
                "hurst_exponent": hurst
            }
        elif hurst < 0.4:
            return {
                "regime": "mean_reverting",
                "confidence": min(1.0, (0.5 - hurst) / 0.3),
                "hurst_exponent": hurst
            }
        else:
            return {
                "regime": "random_walk",
                "confidence": 0.5,
                "hurst_exponent": hurst
            }
    
    def detect_direction_regime(self) -> Dict:
        """
        Detect bull/bear regime
        """
        if len(self.returns_history) < 20:
            return {"regime": "unknown", "confidence": 0.0}
        
        recent_returns = list(self.returns_history)[-20:]
        avg_return = np.mean(recent_returns)
        return_std = np.std(recent_returns)
        
        # Z-score of average return
        z_score = avg_return / return_std if return_std > 0 else 0
        
        if z_score > 1.0:
            return {
                "regime": "bull",
                "confidence": min(1.0, z_score / 2.0),
                "avg_return": avg_return
            }
        elif z_score < -1.0:
            return {
                "regime": "bear",
                "confidence": min(1.0, abs(z_score) / 2.0),
                "avg_return": avg_return
            }
        else:
            return {
                "regime": "neutral",
                "confidence": 0.5,
                "avg_return": avg_return
            }
    
    def detect_all_regimes(self) -> Dict:
        """
        Detect all regime types
        """
        vol_regime = self.detect_volatility_regime()
        trend_regime = self.detect_trend_regime()
        direction_regime = self.detect_direction_regime()
        
        return {
            "volatility": vol_regime,
            "trend": trend_regime,
            "direction": direction_regime,
            "timestamp": self.prices_history[-1][1] if len(self.prices_history) > 0 else 0
        }
    
    def get_regime_recommendation(self) -> Dict:
        """
        Get strategy recommendation based on current regime
        """
        regimes = self.detect_all_regimes()
        
        recommendations = []
        
        # Volatility-based recommendations
        if regimes["volatility"]["regime"] == "high_vol":
            recommendations.append("Increase spread, reduce position size")
        elif regimes["volatility"]["regime"] == "low_vol":
            recommendations.append("Tighten spread, increase position size")
        
        # Trend-based recommendations
        if regimes["trend"]["regime"] == "trending":
            recommendations.append("Use momentum strategies")
        elif regimes["trend"]["regime"] == "mean_reverting":
            recommendations.append("Use mean-reversion strategies")
        
        # Direction-based recommendations
        if regimes["direction"]["regime"] == "bull":
            recommendations.append("Skew quotes upward")
        elif regimes["direction"]["regime"] == "bear":
            recommendations.append("Skew quotes downward")
        
        return {
            "regimes": regimes,
            "recommendations": recommendations
        }
