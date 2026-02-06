"""
Implementation Shortfall Execution Algorithm
Minimizes execution cost vs arrival price
"""
import time
from typing import Dict, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class ISOrder:
    """Implementation Shortfall order"""
    symbol: str
    side: str
    total_size: int
    arrival_price: float  # Price when order arrived
    urgency: float = 0.5  # 0 = patient, 1 = urgent
    executed_size: int = 0
    executed_prices: List[float] = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.executed_prices is None:
            self.executed_prices = []


class ImplementationShortfallExecutor:
    """
    Executes orders to minimize implementation shortfall
    Implementation Shortfall = Execution Cost - Arrival Price Cost
    """
    
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.active_orders: Dict[str, ISOrder] = {}
    
    def create_is_order(
        self,
        symbol: str,
        side: str,
        total_size: int,
        arrival_price: float,
        urgency: float = 0.5
    ) -> str:
        """Create Implementation Shortfall order"""
        import uuid
        order_id = str(uuid.uuid4())
        
        order = ISOrder(
            symbol=symbol,
            side=side,
            total_size=total_size,
            arrival_price=arrival_price,
            urgency=urgency
        )
        
        self.active_orders[order_id] = order
        return order_id
    
    def calculate_implementation_shortfall(self, order_id: str) -> Dict:
        """
        Calculate implementation shortfall for order
        
        IS = (Avg Execution Price - Arrival Price) * Side
        Positive IS = worse than arrival price
        """
        if order_id not in self.active_orders:
            return {"error": "Order not found"}
        
        order = self.active_orders[order_id]
        
        if len(order.executed_prices) == 0:
            return {
                "implementation_shortfall": 0.0,
                "avg_execution_price": order.arrival_price,
                "arrival_price": order.arrival_price,
                "executed_size": 0
            }
        
        avg_execution_price = np.mean(order.executed_prices)
        side_multiplier = 1 if order.side == "buy" else -1
        is_value = (avg_execution_price - order.arrival_price) * side_multiplier
        
        return {
            "implementation_shortfall": is_value,
            "avg_execution_price": avg_execution_price,
            "arrival_price": order.arrival_price,
            "executed_size": order.executed_size,
            "is_per_share": is_value / order.executed_size if order.executed_size > 0 else 0,
            "is_bps": (is_value / order.arrival_price) * 10000 if order.arrival_price > 0 else 0  # Basis points
        }
    
    def get_execution_strategy(self, order_id: str, current_price: float) -> Dict:
        """
        Determine execution strategy based on urgency and market conditions
        """
        if order_id not in self.active_orders:
            return {"error": "Order not found"}
        
        order = self.active_orders[order_id]
        
        # Calculate price deviation from arrival
        price_deviation = abs(current_price - order.arrival_price) / order.arrival_price
        
        # Higher urgency = more aggressive execution
        # Higher price deviation = more patient (wait for better price)
        aggressiveness = order.urgency * (1 - price_deviation)
        
        # Calculate slice size based on aggressiveness
        remaining = order.total_size - order.executed_size
        slice_size = int(remaining * aggressiveness)
        slice_size = max(1, min(slice_size, remaining))
        
        return {
            "slice_size": slice_size,
            "aggressiveness": aggressiveness,
            "strategy": "aggressive" if aggressiveness > 0.7 else "patient" if aggressiveness < 0.3 else "normal"
        }
    
    async def execute_slice(self, order_id: str, current_price: float) -> Dict:
        """Execute slice with IS optimization"""
        if order_id not in self.active_orders:
            return {"error": "Order not found"}
        
        order = self.active_orders[order_id]
        
        if order.status == "completed":
            return {"status": "completed"}
        
        # Get execution strategy
        strategy = self.get_execution_strategy(order_id, current_price)
        slice_size = strategy["slice_size"]
        
        if slice_size > 0 and self.api_client:
            # Execute slice
            executed = slice_size
            execution_price = current_price  # Would get from actual execution
            
            order.executed_size += executed
            order.executed_prices.append(execution_price)
            
            if order.executed_size >= order.total_size:
                order.status = "completed"
            
            # Calculate current IS
            is_metrics = self.calculate_implementation_shortfall(order_id)
            
            return {
                "status": "executing",
                "slice_size": executed,
                "execution_price": execution_price,
                "total_executed": order.executed_size,
                "implementation_shortfall": is_metrics
            }
        
        return {"status": "waiting"}
