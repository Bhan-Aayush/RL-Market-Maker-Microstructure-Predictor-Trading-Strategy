"""
Inventory-Aware Market Maker: Skews quotes based on inventory
"""
from .base_strategy import BaseStrategy, Quote, MarketState
import numpy as np


class InventorySkewMarketMaker(BaseStrategy):
    """
    Market maker that skews quotes away from inventory
    Uses quadratic inventory penalty
    """
    
    def __init__(
        self,
        client_id: str,
        half_spread: float = 0.05,
        quote_size: int = 1,
        inventory_skew_factor: float = 0.02,
        max_inventory: int = 50
    ):
        super().__init__(client_id)
        self.half_spread = half_spread
        self.quote_size = quote_size
        self.inventory_skew_factor = inventory_skew_factor
        self.max_inventory = max_inventory
    
    def compute_quotes(self, market_state: MarketState) -> Quote:
        """Compute quotes with inventory skew"""
        mid = market_state.mid
        inventory = market_state.inventory
        
        # Normalize inventory to [-1, 1]
        normalized_inv = inventory / max(self.max_inventory, abs(inventory)) if inventory != 0 else 0
        
        # Skew: if long inventory, make bid less aggressive (further from mid)
        # and ask more aggressive (closer to mid) to encourage selling
        skew = normalized_inv * self.inventory_skew_factor
        
        bid_price = round(mid - self.half_spread - skew, 2)
        ask_price = round(mid + self.half_spread - skew, 2)
        
        return Quote(
            bid_price=bid_price,
            ask_price=ask_price,
            bid_size=self.quote_size,
            ask_size=self.quote_size
        )
