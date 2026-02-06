"""
Advanced Order Flow Analysis
Market impact, trade sign prediction, queue position
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from collections import deque
from dataclasses import dataclass


@dataclass
class OrderFlowMetrics:
    """Advanced order flow metrics"""
    ofi: float  # Order Flow Imbalance
    trade_sign_imbalance: float
    volume_imbalance: float
    aggressiveness_ratio: float
    market_impact: float


class AdvancedOrderFlowAnalyzer:
    """
    Advanced order flow analysis and prediction
    """
    
    def __init__(self, lookback_window: int = 100):
        self.lookback_window = lookback_window
        self.trade_history: deque = deque(maxlen=lookback_window)
        self.order_flow_history: deque = deque(maxlen=lookback_window)
    
    def calculate_ofi(self, bids: List, asks: List, trades: List) -> float:
        """
        Calculate Order Flow Imbalance (OFI)
        
        OFI = Sum of (bid_size_changes - ask_size_changes)
        """
        if not bids or not asks:
            return 0.0
        
        # Simplified: use depth imbalance as proxy
        bid_depth = sum(size for _, size in bids[:5])
        ask_depth = sum(size for _, size in asks[:5])
        
        if bid_depth + ask_depth == 0:
            return 0.0
        
        ofi = (bid_depth - ask_depth) / (bid_depth + ask_depth)
        return float(ofi)
    
    def calculate_trade_sign_imbalance(self, trades: List[Dict]) -> float:
        """
        Calculate trade sign imbalance
        
        Positive = more buy-initiated trades
        Negative = more sell-initiated trades
        """
        if len(trades) == 0:
            return 0.0
        
        buy_volume = sum(t.get("size", 0) for t in trades if t.get("side") == "buy")
        sell_volume = sum(t.get("size", 0) for t in trades if t.get("side") == "sell")
        total_volume = buy_volume + sell_volume
        
        if total_volume == 0:
            return 0.0
        
        imbalance = (buy_volume - sell_volume) / total_volume
        return float(imbalance)
    
    def estimate_market_impact(
        self,
        order_size: float,
        average_volume: float,
        volatility: float
    ) -> float:
        """
        Estimate market impact of an order
        
        Uses simplified Almgren-Chriss model
        Impact = temporary_impact + permanent_impact
        """
        # Participation rate
        participation = order_size / average_volume if average_volume > 0 else 0
        
        # Temporary impact (linear in participation)
        temp_impact = 0.1 * participation * volatility
        
        # Permanent impact (square root)
        perm_impact = 0.05 * np.sqrt(participation) * volatility
        
        total_impact = temp_impact + perm_impact
        return float(total_impact)
    
    def predict_trade_sign(
        self,
        ofi: float,
        depth_imbalance: float,
        recent_returns: float
    ) -> Dict:
        """
        Predict next trade sign (buy or sell)
        
        Returns probability of buy-initiated trade
        """
        # Simple heuristic model (can be replaced with ML)
        # Positive OFI -> more buy pressure -> higher prob of buy
        # Positive depth imbalance -> more bids -> higher prob of buy
        # Positive returns -> momentum -> higher prob of buy
        
        buy_prob = 0.5  # Base probability
        
        # Adjust based on signals
        buy_prob += 0.2 * ofi  # OFI contribution
        buy_prob += 0.15 * depth_imbalance  # Depth contribution
        buy_prob += 0.1 * np.sign(recent_returns) * min(abs(recent_returns) * 10, 1)  # Momentum
        
        # Clamp to [0, 1]
        buy_prob = max(0, min(1, buy_prob))
        
        return {
            "buy_probability": buy_prob,
            "sell_probability": 1 - buy_prob,
            "predicted_sign": "buy" if buy_prob > 0.5 else "sell"
        }
    
    def estimate_queue_position(
        self,
        price: float,
        side: str,
        book_snapshot: Dict
    ) -> Optional[int]:
        """
        Estimate queue position at a price level
        
        Returns: Position in queue (0 = front, higher = further back)
        """
        if side == "buy":
            levels = book_snapshot.get("bids", [])
        else:
            levels = book_snapshot.get("asks", [])
        
        if not levels:
            return None
        
        # Find price level
        for i, (level_price, level_size) in enumerate(levels):
            if abs(level_price - price) < 0.01:  # At this price level
                # Estimate position (simplified: assume uniform distribution)
                # In reality, would need order-level data
                estimated_position = level_size / 2  # Middle of queue
                return int(estimated_position)
        
        return None
    
    def calculate_aggressiveness_ratio(self, trades: List[Dict]) -> float:
        """
        Calculate ratio of aggressive (market) vs passive (limit) orders
        """
        if len(trades) == 0:
            return 0.0
        
        # Simplified: assume all trades are from aggressive orders
        # In reality, would track order types
        aggressive_count = len([t for t in trades if t.get("type") == "market"])
        total_count = len(trades)
        
        return aggressive_count / total_count if total_count > 0 else 0.0
    
    def analyze_order_flow(
        self,
        bids: List,
        asks: List,
        trades: List[Dict],
        recent_returns: float = 0.0
    ) -> OrderFlowMetrics:
        """Comprehensive order flow analysis"""
        ofi = self.calculate_ofi(bids, asks, trades)
        trade_sign_imbalance = self.calculate_trade_sign_imbalance(trades)
        aggressiveness = self.calculate_aggressiveness_ratio(trades)
        
        # Market impact (simplified)
        total_volume = sum(t.get("size", 0) for t in trades)
        avg_volume = total_volume / len(trades) if len(trades) > 0 else 0
        volatility = abs(recent_returns)
        market_impact = self.estimate_market_impact(avg_volume, avg_volume, volatility)
        
        return OrderFlowMetrics(
            ofi=ofi,
            trade_sign_imbalance=trade_sign_imbalance,
            volume_imbalance=trade_sign_imbalance,  # Same for simplicity
            aggressiveness_ratio=aggressiveness,
            market_impact=market_impact
        )
