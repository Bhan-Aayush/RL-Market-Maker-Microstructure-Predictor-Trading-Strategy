"""
TWAP (Time-Weighted Average Price) Execution Algorithm
Splits large orders evenly over time
"""
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class TWAPOrder:
    """TWAP order configuration"""
    symbol: str
    side: str  # "buy" or "sell"
    total_size: int
    duration_seconds: float
    start_time: float
    end_time: float
    executed_size: int = 0
    executed_value: float = 0.0
    status: str = "pending"  # pending, executing, completed, canceled


class TWAPExecutor:
    """
    Executes orders using TWAP algorithm
    """
    
    def __init__(self, api_client=None):
        self.api_client = api_client  # Trading interface client
        self.active_orders: Dict[str, TWAPOrder] = {}
    
    def create_twap_order(
        self,
        symbol: str,
        side: str,
        total_size: int,
        duration_seconds: float
    ) -> str:
        """
        Create a TWAP order
        
        Returns:
            Order ID
        """
        import uuid
        order_id = str(uuid.uuid4())
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        order = TWAPOrder(
            symbol=symbol,
            side=side,
            total_size=total_size,
            duration_seconds=duration_seconds,
            start_time=start_time,
            end_time=end_time
        )
        
        self.active_orders[order_id] = order
        return order_id
    
    def get_slice_size(self, order_id: str, current_time: float) -> int:
        """
        Calculate size for current time slice
        """
        if order_id not in self.active_orders:
            return 0
        
        order = self.active_orders[order_id]
        
        if current_time < order.start_time:
            return 0
        
        if current_time >= order.end_time:
            # Final slice - execute remaining
            return order.total_size - order.executed_size
        
        # Calculate elapsed and remaining time
        elapsed = current_time - order.start_time
        remaining = order.end_time - current_time
        
        if remaining <= 0:
            return order.total_size - order.executed_size
        
        # Calculate target execution rate
        total_duration = order.end_time - order.start_time
        target_executed = (elapsed / total_duration) * order.total_size
        
        # Size for this slice
        slice_size = int(target_executed) - order.executed_size
        
        return max(0, slice_size)
    
    async def execute_slice(self, order_id: str, current_time: float) -> Dict:
        """
        Execute one time slice of TWAP order
        """
        if order_id not in self.active_orders:
            return {"error": "Order not found"}
        
        order = self.active_orders[order_id]
        
        if order.status == "completed":
            return {"status": "completed", "executed": order.executed_size}
        
        if current_time < order.start_time:
            return {"status": "pending", "wait": order.start_time - current_time}
        
        # Calculate slice size
        slice_size = self.get_slice_size(order_id, current_time)
        
        if slice_size <= 0:
            if current_time >= order.end_time:
                order.status = "completed"
                return {"status": "completed", "executed": order.executed_size}
            return {"status": "waiting", "next_slice": True}
        
        # Execute slice (would call trading interface)
        if self.api_client:
            # In real implementation, submit order via API
            # For now, simulate execution
            executed = slice_size
            avg_price = 100.0  # Would get from execution
            
            order.executed_size += executed
            order.executed_value += executed * avg_price
            
            if order.executed_size >= order.total_size:
                order.status = "completed"
            
            return {
                "status": "executing",
                "slice_size": executed,
                "total_executed": order.executed_size,
                "remaining": order.total_size - order.executed_size
            }
        
        return {"status": "no_api_client"}
    
    def get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get TWAP order status"""
        if order_id not in self.active_orders:
            return None
        
        order = self.active_orders[order_id]
        current_time = time.time()
        
        return {
            "order_id": order_id,
            "symbol": order.symbol,
            "side": order.side,
            "total_size": order.total_size,
            "executed_size": order.executed_size,
            "remaining_size": order.total_size - order.executed_size,
            "execution_progress": order.executed_size / order.total_size if order.total_size > 0 else 0,
            "status": order.status,
            "start_time": order.start_time,
            "end_time": order.end_time,
            "current_time": current_time,
            "time_remaining": max(0, order.end_time - current_time)
        }
