"""
Adaptive Spread Market Maker: Adjusts spread based on volatility
"""
from .base_strategy import BaseStrategy, Quote, MarketState
import numpy as np
from collections import deque


class AdaptiveSpreadMarketMaker(BaseStrategy):
    """
    Market maker that adjusts spread based on realized volatility
    Uses EWMA of returns to estimate volatility
    """
    
    def __init__(
        self,
        client_id: str,
        base_half_spread: float = 0.05,
        quote_size: int = 1,
        vol_alpha: float = 0.1,  # EWMA decay factor
        min_spread: float = 0.01,
        max_spread: float = 0.20
    ):
        super().__init__(client_id)
        self.base_half_spread = base_half_spread
        self.quote_size = quote_size
        self.vol_alpha = vol_alpha
        self.min_spread = min_spread
        self.max_spread = max_spread
        
        # Volatility estimation
        self.ewma_vol = 0.0
        self.last_mid = None
        self.returns_history = deque(maxlen=100)
    
    def _update_volatility(self, current_mid: float):
        """Update EWMA volatility estimate"""
        if self.last_mid is not None:
            ret = (current_mid - self.last_mid) / self.last_mid
            self.returns_history.append(ret)
            
            # EWMA of squared returns
            if self.ewma_vol == 0.0:
                self.ewma_vol = ret ** 2
            else:
                self.ewma_vol = self.vol_alpha * (ret ** 2) + (1 - self.vol_alpha) * self.ewma_vol
        
        self.last_mid = current_mid
    
    def compute_quotes(self, market_state: MarketState) -> Quote:
        """Compute quotes with adaptive spread"""
        mid = market_state.mid
        
        # Update volatility
        self._update_volatility(mid)
        
        # Scale spread by volatility (normalize to reasonable range)
        vol_scale = min(max(np.sqrt(self.ewma_vol) * 100, 0.5), 3.0) if self.ewma_vol > 0 else 1.0
        half_spread = self.base_half_spread * vol_scale
        
        # Clamp spread
        half_spread = max(self.min_spread, min(half_spread, self.max_spread))
        
        bid_price = round(mid - half_spread, 2)
        ask_price = round(mid + half_spread, 2)
        
        return Quote(
            bid_price=bid_price,
            ask_price=ask_price,
            bid_size=self.quote_size,
            ask_size=self.quote_size
        )
