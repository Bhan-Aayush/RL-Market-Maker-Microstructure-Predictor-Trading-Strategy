"""
Base class for market-making strategies
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from dataclasses import dataclass
import time


@dataclass
class Quote:
    """Represents a bid/ask quote"""
    bid_price: float
    ask_price: float
    bid_size: int
    ask_size: int


@dataclass
class MarketState:
    """Current market state snapshot"""
    mid: float
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    timestamp: float
    inventory: int = 0
    position: int = 0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0


class BaseStrategy(ABC):
    """
    Base class for all market-making strategies
    """
    
    def __init__(self, client_id: str, symbol: str = "DEFAULT"):
        self.client_id = client_id
        self.symbol = symbol
        self.inventory = 0
        self.position = 0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.active_orders: Dict[str, Dict] = {}  # order_id -> order info
        
    @abstractmethod
    def compute_quotes(self, market_state: MarketState) -> Quote:
        """
        Compute bid/ask quotes based on market state
        Must be implemented by subclasses
        """
        pass
    
    def update_inventory(self, side: str, size: int):
        """Update inventory after fill"""
        if side == "buy":
            self.inventory += size
            self.position += size
        else:
            self.inventory -= size
            self.position -= size
    
    def update_pnl(self, realized: float, unrealized: float = 0.0):
        """Update P&L"""
        self.realized_pnl += realized
        self.unrealized_pnl = unrealized
    
    def get_state(self) -> Dict:
        """Get current strategy state"""
        return {
            "client_id": self.client_id,
            "inventory": self.inventory,
            "position": self.position,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "total_pnl": self.realized_pnl + self.unrealized_pnl
        }
