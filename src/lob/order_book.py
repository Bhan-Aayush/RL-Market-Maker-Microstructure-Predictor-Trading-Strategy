"""
Limit Order Book (LOB) and Matching Engine
Implements price-time priority matching with partial fills
"""
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import time
import uuid


@dataclass
class Order:
    """Represents a limit or market order"""
    order_id: str
    client_id: str
    side: str  # "buy" or "sell"
    type: str  # "limit" or "market"
    price: Optional[float] = None
    size: int = 0
    remaining_size: int = 0
    timestamp: float = field(default_factory=time.time)
    status: str = "pending"  # pending, filled, partially_filled, canceled


@dataclass
class Fill:
    """Represents a trade execution"""
    order_id: str
    client_id: str
    side: str
    price: float
    size: int
    timestamp: float
    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class LimitOrderBook:
    """
    In-memory limit order book with price-time priority matching
    """
    
    def __init__(self, tick_size: float = 0.01, max_levels: int = 20):
        self.tick_size = tick_size
        self.max_levels = max_levels
        
        # Price-sorted deques: price -> deque of (order_id, size)
        self.bids: Dict[float, deque] = defaultdict(deque)
        self.asks: Dict[float, deque] = defaultdict(deque)
        
        # Order registry
        self.orders: Dict[str, Order] = {}
        
        # Fill history
        self.fills: List[Fill] = []
        
        # Market data cache
        self.last_trade_price: Optional[float] = None
        self.last_trade_size: int = 0
        
    def _round_price(self, price: float) -> float:
        """Round price to nearest tick"""
        return round(price / self.tick_size) * self.tick_size
    
    def best_bid(self) -> Optional[float]:
        """Get best bid price"""
        return max(self.bids.keys()) if self.bids else None
    
    def best_ask(self) -> Optional[float]:
        """Get best ask price"""
        return min(self.asks.keys()) if self.asks else None
    
    def mid_price(self) -> Optional[float]:
        """Calculate mid price"""
        bb = self.best_bid()
        ba = self.best_ask()
        if bb is not None and ba is not None:
            return (bb + ba) / 2.0
        return self.last_trade_price
    
    def spread(self) -> Optional[float]:
        """Calculate bid-ask spread"""
        bb = self.best_bid()
        ba = self.best_ask()
        if bb is not None and ba is not None:
            return ba - bb
        return None
    
    def get_depth(self, side: str, levels: int = 5) -> List[Tuple[float, int]]:
        """Get aggregated depth at top N levels"""
        book = self.bids if side == "buy" else self.asks
        sorted_prices = sorted(book.keys(), reverse=(side == "buy"))[:levels]
        return [(p, sum(size for _, size in book[p])) for p in sorted_prices]
    
    def get_book_snapshot(self, levels: int = 10) -> Dict:
        """Get full L2 snapshot"""
        return {
            "bids": self.get_depth("buy", levels),
            "asks": self.get_depth("sell", levels),
            "best_bid": self.best_bid(),
            "best_ask": self.best_ask(),
            "mid": self.mid_price(),
            "spread": self.spread(),
            "timestamp": time.time()
        }
    
    def add_order(self, order: Order) -> List[Fill]:
        """
        Add order to book and match if possible
        Returns list of fills
        """
        self.orders[order.order_id] = order
        order.remaining_size = order.size
        
        if order.type == "market":
            return self._match_market_order(order)
        else:
            return self._add_limit_order(order)
    
    def _match_market_order(self, order: Order) -> List[Fill]:
        """Match market order immediately against opposite side"""
        fills = []
        opposite_book = self.asks if order.side == "buy" else self.bids
        
        if not opposite_book:
            order.status = "rejected"
            return fills
        
        # Sort prices: lowest ask first for buys, highest bid first for sells
        prices = sorted(opposite_book.keys(), reverse=(order.side == "sell"))
        
        for price in prices:
            if order.remaining_size <= 0:
                break
            
            queue = opposite_book[price]
            while queue and order.remaining_size > 0:
                other_order_id, available_size = queue[0]
                
                if other_order_id not in self.orders:
                    queue.popleft()
                    continue
                
                other_order = self.orders[other_order_id]
                fill_size = min(order.remaining_size, other_order.remaining_size)
                
                # Create fills for both orders
                fill1 = Fill(
                    order_id=order.order_id,
                    client_id=order.client_id,
                    side=order.side,
                    price=price,
                    size=fill_size,
                    timestamp=time.time()
                )
                fill2 = Fill(
                    order_id=other_order_id,
                    client_id=other_order.client_id,
                    side=other_order.side,
                    price=price,
                    size=fill_size,
                    timestamp=time.time()
                )
                
                fills.append(fill1)
                self.fills.append(fill1)
                self.fills.append(fill2)
                
                # Update sizes
                order.remaining_size -= fill_size
                other_order.remaining_size -= fill_size
                
                # Update other order status
                if other_order.remaining_size == 0:
                    other_order.status = "filled"
                    queue.popleft()
                else:
                    other_order.status = "partially_filled"
                    queue[0] = (other_order_id, other_order.remaining_size)
                
                # Update last trade
                self.last_trade_price = price
                self.last_trade_size = fill_size
        
        # Clean empty queues
        for price in list(opposite_book.keys()):
            if not opposite_book[price]:
                del opposite_book[price]
        
        # Update order status
        if order.remaining_size == 0:
            order.status = "filled"
        else:
            order.status = "partially_filled"
        
        return fills
    
    def _add_limit_order(self, order: Order) -> List[Fill]:
        """Add limit order and match if possible"""
        fills = []
        price = self._round_price(order.price)
        order.price = price
        
        # Try to match against opposite side
        opposite_book = self.asks if order.side == "buy" else self.bids
        
        if opposite_book:
            if order.side == "buy":
                # Buy order: match if price >= best ask
                best_opposite = min(opposite_book.keys())
                if price >= best_opposite:
                    fills.extend(self._match_market_order(order))
            else:
                # Sell order: match if price <= best bid
                best_opposite = max(opposite_book.keys())
                if price <= best_opposite:
                    fills.extend(self._match_market_order(order))
        
        # If still has remaining size, add to book
        if order.remaining_size > 0:
            book = self.bids if order.side == "buy" else self.asks
            book[price].append((order.order_id, order.remaining_size))
            if order.status == "pending":
                order.status = "active"
        
        return fills
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order from the book"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status in ["filled", "canceled"]:
            return False
        
        # Remove from book
        book = self.bids if order.side == "buy" else self.asks
        price = order.price
        
        if price in book:
            # Rebuild queue without this order
            new_queue = deque([
                (oid, sz) for oid, sz in book[price]
                if oid != order_id
            ])
            if new_queue:
                book[price] = new_queue
            else:
                del book[price]
        
        order.status = "canceled"
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_client_fills(self, client_id: str) -> List[Fill]:
        """Get all fills for a client"""
        return [f for f in self.fills if f.client_id == client_id]
