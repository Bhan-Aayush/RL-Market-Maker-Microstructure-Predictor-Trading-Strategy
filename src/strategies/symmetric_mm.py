"""
Symmetric Market Maker: Posts quotes symmetrically around mid
"""
from .base_strategy import BaseStrategy, Quote, MarketState


class SymmetricMarketMaker(BaseStrategy):
    """
    Simple symmetric market maker with fixed spread
    """
    
    def __init__(self, client_id: str, half_spread: float = 0.05, quote_size: int = 1):
        super().__init__(client_id)
        self.half_spread = half_spread
        self.quote_size = quote_size
    
    def compute_quotes(self, market_state: MarketState) -> Quote:
        """Compute symmetric quotes around mid"""
        mid = market_state.mid
        
        bid_price = round(mid - self.half_spread, 2)
        ask_price = round(mid + self.half_spread, 2)
        
        return Quote(
            bid_price=bid_price,
            ask_price=ask_price,
            bid_size=self.quote_size,
            ask_size=self.quote_size
        )
