"""
Strategy client that connects to trading interface via WebSocket and REST
"""
import asyncio
import websockets
import requests
import json
import time
from typing import Optional, Callable
from .base_strategy import BaseStrategy, MarketState, Quote


class StrategyClient:
    """
    Client that connects strategy to trading interface
    """
    
    def __init__(
        self,
        strategy: BaseStrategy,
        api_base: str = "http://127.0.0.1:8000",
        ws_md_url: str = "ws://127.0.0.1:8000/ws/md",
        ws_fills_url: str = "ws://127.0.0.1:8000/ws/fills"
    ):
        self.strategy = strategy
        self.api_base = api_base
        self.ws_md_url = ws_md_url
        self.ws_fills_url = f"{ws_fills_url}/{strategy.client_id}"
        
        self.active_orders = {}  # order_id -> order info
        self.running = False
    
    def post_order(self, side: str, order_type: str, price: Optional[float], size: int) -> dict:
        """Submit order via REST API"""
        url = f"{self.api_base}/order"
        payload = {
            "client_id": self.strategy.client_id,
            "side": side,
            "type": order_type,
            "size": size
        }
        if price is not None:
            payload["price"] = price
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            return response.json()
        except Exception as e:
            print(f"Error posting order: {e}")
            return {"error": str(e)}
    
    def cancel_order(self, order_id: str) -> dict:
        """Cancel order via REST API"""
        url = f"{self.api_base}/cancel/{order_id}"
        try:
            response = requests.post(url, timeout=5)
            return response.json()
        except Exception as e:
            print(f"Error canceling order: {e}")
            return {"error": str(e)}
    
    async def handle_fills(self, ws: websockets.WebSocketClientProtocol):
        """Handle fill notifications from WebSocket"""
        try:
            async for message in ws:
                data = json.loads(message)
                if data.get("event") == "fill":
                    # Update strategy inventory
                    side = data["side"]
                    size = data["size"]
                    self.strategy.update_inventory(side, size)
                    
                    # Remove from active orders if fully filled
                    order_id = data["order_id"]
                    if order_id in self.active_orders:
                        # Check if order is fully filled (would need to query order status)
                        pass
        except websockets.exceptions.ConnectionClosed:
            print("Fills WebSocket closed")
        except Exception as e:
            print(f"Error in fills handler: {e}")
    
    async def run(self, quote_interval: float = 0.5):
        """
        Main strategy loop: subscribe to market data, compute quotes, submit orders
        """
        self.running = True
        
        # Connect to fills WebSocket
        fills_task = None
        try:
            async with websockets.connect(self.ws_fills_url) as fills_ws:
                fills_task = asyncio.create_task(self.handle_fills(fills_ws))
                
                # Connect to market data WebSocket
                try:
                    async with websockets.connect(self.ws_md_url) as md_ws:
                        print(f"Strategy {self.strategy.client_id} connected")
                        
                        async for message in md_ws:
                            if not self.running:
                                break
                            
                            try:
                                md = json.loads(message)
                                
                                # Build market state
                                market_state = MarketState(
                                    mid=md.get("mid", 0.0),
                                    best_bid=md.get("best_bid"),
                                    best_ask=md.get("best_ask"),
                                    spread=md.get("spread"),
                                    timestamp=md.get("timestamp", time.time()),
                                    inventory=self.strategy.inventory,
                                    position=self.strategy.position,
                                    realized_pnl=self.strategy.realized_pnl,
                                    unrealized_pnl=self.strategy.unrealized_pnl
                                )
                                
                                # Compute quotes
                                quote = self.strategy.compute_quotes(market_state)
                                
                                # Cancel old orders
                                for order_id in list(self.active_orders.keys()):
                                    self.cancel_order(order_id)
                                self.active_orders.clear()
                                
                                # Submit new quotes
                                bid_resp = self.post_order("buy", "limit", quote.bid_price, quote.bid_size)
                                ask_resp = self.post_order("sell", "limit", quote.ask_price, quote.ask_size)
                                
                                if "order_id" in bid_resp:
                                    self.active_orders[bid_resp["order_id"]] = {"side": "buy", "price": quote.bid_price}
                                if "order_id" in ask_resp:
                                    self.active_orders[ask_resp["order_id"]] = {"side": "sell", "price": quote.ask_price}
                                
                                # Wait before next quote update
                                await asyncio.sleep(quote_interval)
                                
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                print(f"Error in strategy loop: {e}")
                                await asyncio.sleep(quote_interval)
                
                except websockets.exceptions.ConnectionClosed:
                    print("Market data WebSocket closed")
                except Exception as e:
                    print(f"Error connecting to market data: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            print("Fills WebSocket closed")
        except Exception as e:
            print(f"Error connecting to fills: {e}")
        finally:
            if fills_task:
                fills_task.cancel()
            self.running = False
    
    def stop(self):
        """Stop the strategy"""
        self.running = False


async def run_strategy(strategy: BaseStrategy, quote_interval: float = 0.5):
    """Helper to run a strategy"""
    client = StrategyClient(strategy)
    await client.run(quote_interval)
