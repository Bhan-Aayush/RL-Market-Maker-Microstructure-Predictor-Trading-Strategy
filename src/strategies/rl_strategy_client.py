"""
Strategy client for RL-based market maker
Connects RL agent to trading interface
"""
import asyncio
import websockets
import requests
import json
import time
from typing import Optional

from .rl_mm import RLMarketMaker
from .strategy_client import StrategyClient


class RLStrategyClient(StrategyClient):
    """
    Client that connects RL agent to trading interface
    Extends StrategyClient with book snapshot updates
    """
    
    def __init__(
        self,
        strategy: RLMarketMaker,
        api_base: str = "http://127.0.0.1:8000",
        ws_md_url: str = "ws://127.0.0.1:8000/ws/md",
        ws_fills_url: str = "ws://127.0.0.1:8000/ws/fills"
    ):
        super().__init__(strategy, api_base, ws_md_url, ws_fills_url)
    
    async def run(self, quote_interval: float = 0.5):
        """
        Main strategy loop with book snapshot updates for RL agent
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
                        print(f"RL Strategy {self.strategy.client_id} connected")
                        
                        async for message in md_ws:
                            if not self.running:
                                break
                            
                            try:
                                md = json.loads(message)
                                
                                # Update book snapshot for RL agent
                                if isinstance(self.strategy, RLMarketMaker):
                                    bids = md.get("bids", [])
                                    asks = md.get("asks", [])
                                    self.strategy.update_book_snapshot(bids, asks)
                                
                                # Build market state
                                from .base_strategy import MarketState
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
                                
                                # Compute quotes using RL agent
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
                                print(f"Error in RL strategy loop: {e}")
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
