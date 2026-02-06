"""
Python wrapper for C++ matching engine
Provides drop-in replacement for Python LimitOrderBook
"""
import sys
from typing import Optional, List, Dict
import time

try:
    import matching_engine_core as mec
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False
    print("Warning: C++ matching engine not available. Using Python implementation.")


if CPP_AVAILABLE:
    class LimitOrderBook:
        """
        Python wrapper for C++ matching engine
        Drop-in replacement for Python LimitOrderBook with better performance
        """
        
        def __init__(self, tick_size: float = 0.01, max_levels: int = 20):
            self._lob = mec.LimitOrderBook(tick_size, max_levels)
            self.tick_size = tick_size
            self.max_levels = max_levels
        
        def best_bid(self) -> Optional[float]:
            result = self._lob.best_bid()
            return result if result is not None else None
        
        def best_ask(self) -> Optional[float]:
            result = self._lob.best_ask()
            return result if result is not None else None
        
        def mid_price(self) -> Optional[float]:
            result = self._lob.mid_price()
            return result if result is not None else None
        
        def spread(self) -> Optional[float]:
            result = self._lob.spread()
            return result if result is not None else None
        
        def get_book_snapshot(self, levels: int = 10) -> Dict:
            snapshot = self._lob.get_book_snapshot(levels)
            return {
                "bids": snapshot.bids,
                "asks": snapshot.asks,
                "best_bid": snapshot.best_bid,
                "best_ask": snapshot.best_ask,
                "mid": snapshot.mid,
                "spread": snapshot.spread,
                "timestamp": snapshot.timestamp
            }
        
        def add_order(self, order):
            """Add order - expects order from order_book.py Order class"""
            # Convert Python Order to C++ Order
            cpp_order = mec.Order()
            cpp_order.order_id = order.order_id
            cpp_order.client_id = order.client_id
            cpp_order.side = order.side
            cpp_order.type = order.type
            cpp_order.price = order.price if order.price else 0.0
            cpp_order.size = order.size
            cpp_order.timestamp = order.timestamp
            
            # Add order
            cpp_fills = self._lob.add_order(cpp_order)
            
            # Convert C++ fills to Python fills
            from .order_book import Fill
            fills = []
            for cpp_fill in cpp_fills:
                fill = Fill(
                    order_id=cpp_fill.order_id,
                    client_id=cpp_fill.client_id,
                    side=cpp_fill.side,
                    price=cpp_fill.price,
                    size=cpp_fill.size,
                    timestamp=cpp_fill.timestamp
                )
                fill.trade_id = cpp_fill.trade_id
                fills.append(fill)
            
            # Update order status from C++ side
            cpp_order_result = self._lob.get_order(order.order_id)
            if cpp_order_result:
                status_map = {
                    "pending": "pending",
                    "active": "active",
                    "filled": "filled",
                    "partially_filled": "partially_filled",
                    "canceled": "canceled"
                }
                order.status = status_map.get(cpp_order_result.status, "pending")
                order.remaining_size = cpp_order_result.remaining_size
            
            return fills
        
        def cancel_order(self, order_id: str) -> bool:
            return self._lob.cancel_order(order_id)
        
        def get_order(self, order_id: str):
            """Get order - returns Python Order object"""
            cpp_order = self._lob.get_order(order_id)
            if cpp_order is None:
                return None
            
            from .order_book import Order
            order = Order(
                order_id=cpp_order.order_id,
                client_id=cpp_order.client_id,
                side=cpp_order.side,
                type=cpp_order.type,
                price=cpp_order.price,
                size=cpp_order.size
            )
            order.remaining_size = cpp_order.remaining_size
            order.timestamp = cpp_order.timestamp
            order.status = cpp_order.status
            return order
        
        def get_client_fills(self, client_id: str) -> List:
            """Get fills for client"""
            cpp_fills = self._lob.get_client_fills(client_id)
            from .order_book import Fill
            fills = []
            for cpp_fill in cpp_fills:
                fill = Fill(
                    order_id=cpp_fill.order_id,
                    client_id=cpp_fill.client_id,
                    side=cpp_fill.side,
                    price=cpp_fill.price,
                    size=cpp_fill.size,
                    timestamp=cpp_fill.timestamp
                )
                fill.trade_id = cpp_fill.trade_id
                fills.append(fill)
            return fills

else:
    # Fallback to Python implementation
    from .order_book import LimitOrderBook as _LimitOrderBook
    LimitOrderBook = _LimitOrderBook
