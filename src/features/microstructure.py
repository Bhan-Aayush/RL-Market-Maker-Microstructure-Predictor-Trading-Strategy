"""
Microstructure Feature Extractor
Computes order flow imbalance, depth imbalance, and other microstructure signals
"""
from typing import List, Tuple, Optional, Dict
from collections import deque
import numpy as np


class MicrostructureFeatureExtractor:
    """
    Extracts microstructure features from LOB snapshots
    """
    
    def __init__(self, lookback_window: int = 20):
        self.lookback_window = lookback_window
        self.mid_history = deque(maxlen=lookback_window)
        self.spread_history = deque(maxlen=lookback_window)
        self.volume_history = deque(maxlen=lookback_window)
        self.trade_signs = deque(maxlen=lookback_window)
    
    def extract_features(
        self,
        bids: List[Tuple[float, int]],
        asks: List[Tuple[float, int]],
        last_trade_price: Optional[float] = None,
        last_trade_size: int = 0,
        last_trade_side: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Extract comprehensive microstructure features
        
        Returns:
            Dictionary of feature names and values
        """
        features = {}
        
        # Basic L1 features
        best_bid = bids[0][0] if bids else None
        best_ask = asks[0][0] if asks else None
        
        if best_bid is None or best_ask is None:
            return self._default_features()
        
        mid = (best_bid + best_ask) / 2.0
        spread = best_ask - best_bid
        relative_spread = spread / mid if mid > 0 else 0.0
        
        features['mid'] = mid
        features['spread'] = spread
        features['relative_spread'] = relative_spread
        features['best_bid'] = best_bid
        features['best_ask'] = best_ask
        
        # Depth features
        bid_depth = sum(size for _, size in bids[:5])  # Top 5 levels
        ask_depth = sum(size for _, size in asks[:5])
        total_depth = bid_depth + ask_depth
        
        features['bid_depth'] = bid_depth
        features['ask_depth'] = ask_depth
        features['total_depth'] = total_depth
        
        # Depth imbalance
        if total_depth > 0:
            depth_imbalance = (bid_depth - ask_depth) / total_depth
        else:
            depth_imbalance = 0.0
        features['depth_imbalance'] = depth_imbalance
        
        # Weighted mid (by depth)
        if bid_depth > 0 and ask_depth > 0:
            weighted_mid = (best_bid * ask_depth + best_ask * bid_depth) / (bid_depth + ask_depth)
            features['weighted_mid'] = weighted_mid
            features['mid_skew'] = weighted_mid - mid
        else:
            features['weighted_mid'] = mid
            features['mid_skew'] = 0.0
        
        # Order Flow Imbalance (OFI) - simplified
        # In real implementation, track aggressive vs passive flow
        if len(self.trade_signs) > 0:
            ofi = sum(self.trade_signs) / len(self.trade_signs)
        else:
            ofi = 0.0
        features['order_flow_imbalance'] = ofi
        
        # Price momentum (short-term returns)
        self.mid_history.append(mid)
        if len(self.mid_history) >= 2:
            returns_1s = (mid - self.mid_history[-2]) / self.mid_history[-2] if self.mid_history[-2] > 0 else 0.0
            features['return_1s'] = returns_1s
            
            if len(self.mid_history) >= 5:
                returns_5s = (mid - self.mid_history[-5]) / self.mid_history[-5] if self.mid_history[-5] > 0 else 0.0
                features['return_5s'] = returns_5s
            else:
                features['return_5s'] = 0.0
        else:
            features['return_1s'] = 0.0
            features['return_5s'] = 0.0
        
        # Volatility (EWMA of squared returns)
        self.spread_history.append(spread)
        if len(self.mid_history) >= 2:
            returns = np.diff(list(self.mid_history))
            if len(returns) > 0:
                vol = np.std(returns) if len(returns) > 1 else 0.0
                features['realized_vol'] = vol
            else:
                features['realized_vol'] = 0.0
        else:
            features['realized_vol'] = 0.0
        
        # Update trade sign if available
        if last_trade_side:
            sign = 1.0 if last_trade_side == "buy" else -1.0
            self.trade_signs.append(sign)
            self.volume_history.append(last_trade_size)
        
        # Volume features
        if len(self.volume_history) > 0:
            avg_volume = np.mean(list(self.volume_history))
            features['avg_volume'] = avg_volume
        else:
            features['avg_volume'] = 0.0
        
        return features
    
    def _default_features(self) -> Dict[str, float]:
        """Return default feature values when book is empty"""
        return {
            'mid': 0.0,
            'spread': 0.0,
            'relative_spread': 0.0,
            'best_bid': 0.0,
            'best_ask': 0.0,
            'bid_depth': 0.0,
            'ask_depth': 0.0,
            'total_depth': 0.0,
            'depth_imbalance': 0.0,
            'weighted_mid': 0.0,
            'mid_skew': 0.0,
            'order_flow_imbalance': 0.0,
            'return_1s': 0.0,
            'return_5s': 0.0,
            'realized_vol': 0.0,
            'avg_volume': 0.0
        }
    
    def get_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """
        Convert feature dict to numpy array for ML models
        Order matters for consistency
        """
        feature_order = [
            'mid', 'spread', 'relative_spread',
            'bid_depth', 'ask_depth', 'depth_imbalance',
            'order_flow_imbalance', 'return_1s', 'return_5s',
            'realized_vol', 'avg_volume', 'mid_skew'
        ]
        
        return np.array([features.get(k, 0.0) for k in feature_order], dtype=np.float32)
