"""
Real Market Data Integration for Trading Interface
Replaces synthetic data generator with real API feeds
"""
import asyncio
import time
from typing import Optional
from ..data.market_data_source import create_data_source, MarketDataSource
from ..lob.order_book import Order
import uuid


class RealMarketDataFeed:
    """
    Real market data feed that replaces synthetic generator
    """
    
    def __init__(
        self,
        data_source: MarketDataSource,
        symbol: str = "AAPL",
        update_interval: float = 1.0,
        lob=None
    ):
        self.data_source = data_source
        self.symbol = symbol
        self.update_interval = update_interval
        self.lob = lob
        self.running = False
        self.last_quote = None
    
    async def generate_market_data(self, subscribers: list):
        """Generate and push real market data to subscribers"""
        self.running = True
        
        while self.running:
            try:
                # Fetch latest quote from data source
                quote = self.data_source.get_latest_quote(self.symbol)
                self.last_quote = quote
                
                # Update LOB if provided (add synthetic orders around real price)
                if self.lob:
                    # Add some synthetic orders to create depth
                    mid = quote["mid"]
                    for i in range(3):
                        # Add bid
                        bid_order = Order(
                            order_id=f"real_bid_{uuid.uuid4()}",
                            client_id="MARKET",
                            side="buy",
                            type="limit",
                            price=round(mid - 0.01 * (i + 1), 2),
                            size=10
                        )
                        self.lob.add_order(bid_order)
                        
                        # Add ask
                        ask_order = Order(
                            order_id=f"real_ask_{uuid.uuid4()}",
                            client_id="MARKET",
                            side="sell",
                            type="limit",
                            price=round(mid + 0.01 * (i + 1), 2),
                            size=10
                        )
                        self.lob.add_order(ask_order)
                
                # Get book snapshot
                if self.lob:
                    snapshot = self.lob.get_book_snapshot()
                    # Override with real quote data
                    snapshot["mid"] = quote["mid"]
                    snapshot["best_bid"] = quote.get("bid")
                    snapshot["best_ask"] = quote.get("ask")
                    snapshot["spread"] = quote.get("spread")
                    snapshot["timestamp"] = quote["timestamp"]
                else:
                    # Create snapshot from quote only
                    snapshot = {
                        "mid": quote["mid"],
                        "best_bid": quote.get("bid"),
                        "best_ask": quote.get("ask"),
                        "spread": quote.get("spread"),
                        "bids": [[quote.get("bid", quote["mid"] - 0.01), 100]],
                        "asks": [[quote.get("ask", quote["mid"] + 0.01), 100]],
                        "timestamp": quote["timestamp"]
                    }
                
                # Push to subscribers
                disconnected = []
                for ws in subscribers:
                    try:
                        await ws.send_json(snapshot)
                    except:
                        disconnected.append(ws)
                
                # Remove disconnected clients
                for ws in disconnected:
                    if ws in subscribers:
                        subscribers.remove(ws)
                
                # Wait before next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Error in real market data feed: {e}")
                await asyncio.sleep(self.update_interval)
    
    def stop(self):
        """Stop the feed"""
        self.running = False
