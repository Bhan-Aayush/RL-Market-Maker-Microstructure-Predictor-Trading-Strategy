"""
Proprietary Trading Interface: REST API + WebSocket for market data and fills
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, field_validator, model_validator
from typing import Dict, List, Optional, Any
import uvicorn
import asyncio
import time
import uuid
import json
from collections import defaultdict

from ..lob.order_book import LimitOrderBook, Order, Fill
from ..risk.risk_manager import RiskManager, RiskLimits
from ..data.market_data_source import create_data_source
from .real_market_data import RealMarketDataFeed


# Request/Response Models
class OrderRequest(BaseModel):
    client_id: str
    side: str  # "buy" or "sell"
    type: Optional[str] = None  # "limit" or "market"
    order_type: Optional[str] = None  # Alias for type (for dashboard compatibility)
    price: Optional[float] = None
    size: int
    symbol: str = "DEFAULT"  # For multi-symbol support later
    
    @model_validator(mode='after')
    def normalize_order_type(self):
        """Handle order_type as alias for type"""
        if self.type is None and self.order_type is not None:
            self.type = self.order_type
        if self.type is None:
            self.type = "limit"  # Default to limit order
        return self


class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: Optional[str] = None


class CancelResponse(BaseModel):
    order_id: str
    status: str


class BookSnapshot(BaseModel):
    bids: List[List[float]]  # [[price, size], ...]
    asks: List[List[float]]
    best_bid: Optional[float]
    best_ask: Optional[float]
    mid: Optional[float]
    spread: Optional[float]
    timestamp: float


class TradingInterface:
    """
    Main trading interface server
    """
    
    def __init__(
        self,
        risk_limits: Optional[RiskLimits] = None,
        data_source_type: str = "synthetic",
        data_source_config: Optional[Dict] = None,
        symbol: str = "AAPL"
    ):
        # Core components
        self.lob = LimitOrderBook()
        self.risk_manager = RiskManager(risk_limits)
        
        # WebSocket subscribers
        self.md_subscribers: List[WebSocket] = []
        self.fill_subscribers: Dict[str, List[WebSocket]] = defaultdict(list)
        
        # Market data source
        self.data_source_type = data_source_type
        self.data_source_config = data_source_config or {}
        self.symbol = symbol
        
        # Market data generator
        self.md_running = False
        self.md_task: Optional[asyncio.Task] = None
        self.real_data_feed: Optional[RealMarketDataFeed] = None
        
        # Create lifespan context manager
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup: start market data generator
            self.md_running = True
            if self.data_source_type in ["yahoo", "alphavantage"]:
                # Use real market data
                data_source = create_data_source(
                    self.data_source_type,
                    **self.data_source_config
                )
                self.real_data_feed = RealMarketDataFeed(
                    data_source=data_source,
                    symbol=self.symbol,
                    update_interval=1.0,  # 1 second for real data (rate limits)
                    lob=self.lob
                )
                self.md_task = asyncio.create_task(
                    self.real_data_feed.generate_market_data(self.md_subscribers)
                )
            else:
                # Use synthetic data
                self.md_task = asyncio.create_task(self._market_data_generator())
            yield
            # Shutdown: stop market data generator
            self.md_running = False
            if self.real_data_feed:
                self.real_data_feed.stop()
            if self.md_task:
                self.md_task.cancel()
                try:
                    await self.md_task
                except asyncio.CancelledError:
                    pass
        
        self.app = FastAPI(
            title="Proprietary Trading Interface",
            description="REST + WebSocket trading API with LOB and risk controls",
            version="0.1.0",
            lifespan=lifespan
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Register all API routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information"""
            return {
                "service": "Proprietary Trading Interface",
                "version": "0.1.0",
                "status": "running",
                "endpoints": {
                    "order_book": "GET /book",
                    "submit_order": "POST /order",
                    "get_order": "GET /order/{order_id}",
                    "cancel_order": "POST /cancel/{order_id}",
                    "get_fills": "GET /fills/{client_id}",
                    "get_risk": "GET /risk/{client_id}",
                    "market_data_ws": "WS /ws/md",
                    "fills_ws": "WS /ws/fills/{client_id}",
                    "docs": "GET /docs",
                    "health": "GET /health"
                }
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "lob_active": True,
                "market_data_running": self.md_running,
                "timestamp": time.time()
            }
        
        @self.app.post("/order", response_model=OrderResponse)
        async def submit_order(order_req: OrderRequest):
            """Submit a new order"""
            # Ensure type is set (handle order_type alias)
            if order_req.type is None and order_req.order_type is not None:
                order_req.type = order_req.order_type
            if order_req.type is None:
                order_req.type = "limit"  # Default
            
            # Validate order
            mid = self.lob.mid_price()
            valid, error = self.risk_manager.validate_order(
                order_req.client_id,
                order_req.side,
                order_req.size,
                order_req.price if order_req.type == "limit" else None,
                mid
            )
            
            if not valid:
                raise HTTPException(status_code=400, detail=error)
            
            # Create order
            order = Order(
                order_id=str(uuid.uuid4()),
                client_id=order_req.client_id,
                side=order_req.side,
                type=order_req.type,
                price=order_req.price,
                size=order_req.size
            )
            
            # Submit to LOB
            fills = self.lob.add_order(order)
            
            # Process fills
            for fill in fills:
                # Update risk manager
                self.risk_manager.update_position(
                    fill.client_id, fill.side, fill.size, fill.price
                )
                
                # Push fill to client
                await self._push_fill(fill)
            
            return OrderResponse(
                order_id=order.order_id,
                status=order.status,
                message="Order accepted"
            )
        
        @self.app.post("/cancel/{order_id}", response_model=CancelResponse)
        async def cancel_order(order_id: str):
            """Cancel an order"""
            order = self.lob.get_order(order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            success = self.lob.cancel_order(order_id)
            if not success:
                raise HTTPException(status_code=400, detail="Cannot cancel order")
            
            return CancelResponse(order_id=order_id, status="canceled")
        
        @self.app.get("/book", response_model=BookSnapshot)
        async def get_book():
            """Get current order book snapshot"""
            snapshot = self.lob.get_book_snapshot()
            return BookSnapshot(**snapshot)
        
        @self.app.get("/order/{order_id}")
        async def get_order(order_id: str):
            """Get order status"""
            order = self.lob.get_order(order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            return {
                "order_id": order.order_id,
                "client_id": order.client_id,
                "side": order.side,
                "type": order.type,
                "price": order.price,
                "size": order.size,
                "remaining_size": order.remaining_size,
                "status": order.status,
                "timestamp": order.timestamp
            }
        
        @self.app.get("/fills/{client_id}")
        async def get_fills(client_id: str):
            """Get fill history for client"""
            fills = self.lob.get_client_fills(client_id)
            return [{
                "fill_id": f.trade_id,
                "order_id": f.order_id,
                "side": f.side,
                "price": f.price,
                "size": f.size,
                "timestamp": f.timestamp
            } for f in fills]
        
        @self.app.get("/risk/{client_id}")
        async def get_risk_state(client_id: str):
            """Get risk state for client"""
            state = self.risk_manager.get_client_state(client_id)
            if not state:
                return {"client_id": client_id, "position": 0, "pnl": 0.0}
            
            return {
                "client_id": client_id,
                "position": state.position,
                "realized_pnl": state.realized_pnl,
                "unrealized_pnl": state.unrealized_pnl,
                "daily_pnl": state.daily_pnl,
                "is_blocked": state.is_blocked
            }
        
        @self.app.websocket("/ws/md")
        async def market_data_websocket(websocket: WebSocket):
            """WebSocket for market data (L1/L2)"""
            await websocket.accept()
            self.md_subscribers.append(websocket)
            
            try:
                # Send initial snapshot
                snapshot = self.lob.get_book_snapshot()
                await websocket.send_json(snapshot)
                
                # Keep connection alive
                while True:
                    await asyncio.sleep(1.0)
                    # Market data is pushed by background task
            except WebSocketDisconnect:
                self.md_subscribers.remove(websocket)
        
        @self.app.websocket("/ws/fills/{client_id}")
        async def fills_websocket(websocket: WebSocket, client_id: str):
            """WebSocket for fill notifications"""
            await websocket.accept()
            self.fill_subscribers[client_id].append(websocket)
            
            try:
                # Send recent fills
                recent_fills = self.lob.get_client_fills(client_id)[-10:]
                for fill in recent_fills:
                    await websocket.send_json({
                        "event": "fill",
                        "order_id": fill.order_id,
                        "side": fill.side,
                        "price": fill.price,
                        "size": fill.size,
                        "timestamp": fill.timestamp
                    })
                
                # Keep connection alive
                while True:
                    await asyncio.sleep(1.0)
            except WebSocketDisconnect:
                if client_id in self.fill_subscribers:
                    self.fill_subscribers[client_id].remove(websocket)
    
    async def _push_fill(self, fill: Fill):
        """Push fill notification to client's WebSocket"""
        if fill.client_id in self.fill_subscribers:
            message = {
                "event": "fill",
                "order_id": fill.order_id,
                "side": fill.side,
                "price": fill.price,
                "size": fill.size,
                "timestamp": fill.timestamp
            }
            
            # Send to all subscribers for this client
            disconnected = []
            for ws in self.fill_subscribers[fill.client_id]:
                try:
                    await ws.send_json(message)
                except:
                    disconnected.append(ws)
            
            # Remove disconnected clients
            for ws in disconnected:
                self.fill_subscribers[fill.client_id].remove(ws)
    
    async def _market_data_generator(self):
        """Background task to generate synthetic market data"""
        import random
        
        base_price = 100.0
        
        while self.md_running:
            # Generate synthetic mid price (random walk)
            mid = self.lob.mid_price() or base_price
            mid += random.gauss(0, 0.05)
            
            # Generate synthetic orders to create realistic book
            if random.random() < 0.3:  # 30% chance of new order
                side = "buy" if random.random() < 0.5 else "sell"
                price_offset = random.uniform(0.01, 0.10)
                price = mid - price_offset if side == "buy" else mid + price_offset
                size = random.randint(1, 10)
                
                # Create synthetic order (from "market")
                synthetic_order = Order(
                    order_id=f"synthetic_{uuid.uuid4()}",
                    client_id="SYNTHETIC",
                    side=side,
                    type="limit",
                    price=round(price, 2),
                    size=size
                )
                self.lob.add_order(synthetic_order)
            
            # Push market data to subscribers
            snapshot = self.lob.get_book_snapshot()
            disconnected = []
            for ws in self.md_subscribers:
                try:
                    await ws.send_json(snapshot)
                except:
                    disconnected.append(ws)
            
            # Remove disconnected clients
            for ws in disconnected:
                if ws in self.md_subscribers:
                    self.md_subscribers.remove(ws)
            
            await asyncio.sleep(0.1)  # 10 updates per second
    
    def get_app(self) -> FastAPI:
        """Get FastAPI app instance"""
        return self.app


def create_app(
    risk_limits: Optional[RiskLimits] = None,
    data_source_type: str = "synthetic",
    data_source_config: Optional[Dict] = None,
    symbol: str = "AAPL"
) -> FastAPI:
    """
    Factory function to create trading interface app
    
    Args:
        risk_limits: Risk limit configuration
        data_source_type: "synthetic", "yahoo", or "alphavantage"
        data_source_config: Config dict (e.g., {"api_key": "..."} for Alpha Vantage)
        symbol: Trading symbol (e.g., "AAPL", "MSFT")
    """
    interface = TradingInterface(
        risk_limits=risk_limits,
        data_source_type=data_source_type,
        data_source_config=data_source_config,
        symbol=symbol
    )
    return interface.get_app()


if __name__ == "__main__":
    app = create_app()
    print("Starting Proprietary Trading Interface on http://127.0.0.1:8000")
    print("API docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
