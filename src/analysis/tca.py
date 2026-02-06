"""
Transaction Cost Analysis (TCA)
Measures execution quality: slippage, market impact, fill rates
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class TCAMetrics:
    """Transaction Cost Analysis metrics"""
    total_orders: int
    total_fills: int
    fill_rate: float
    avg_slippage: float
    avg_market_impact: float
    avg_execution_price: float
    arrival_price: float
    implementation_shortfall: float
    is_bps: float  # Implementation shortfall in basis points
    avg_latency_ms: float
    vwap_deviation: float


class TransactionCostAnalyzer:
    """
    Analyzes transaction costs and execution quality
    """
    
    def __init__(self):
        self.orders: List[Dict] = []
        self.fills: List[Dict] = []
    
    def add_order(self, order: Dict):
        """Add an order for analysis"""
        self.orders.append(order)
    
    def add_fill(self, fill: Dict):
        """Add a fill for analysis"""
        self.fills.append(fill)
    
    def calculate_slippage(
        self,
        order_price: float,
        execution_price: float,
        side: str
    ) -> float:
        """
        Calculate slippage
        
        Slippage = Execution Price - Order Price (for buys)
        Positive = worse (paid more than expected)
        """
        if side == "buy":
            return execution_price - order_price
        else:  # sell
            return order_price - execution_price
    
    def calculate_market_impact(
        self,
        arrival_price: float,
        execution_price: float,
        side: str
    ) -> float:
        """
        Calculate market impact
        
        Market Impact = Execution Price - Arrival Price
        Measures how much the order moved the market
        """
        if side == "buy":
            return execution_price - arrival_price
        else:  # sell
            return arrival_price - execution_price
    
    def calculate_implementation_shortfall(
        self,
        arrival_price: float,
        execution_price: float,
        side: str
    ) -> float:
        """
        Calculate Implementation Shortfall
        
        IS = Execution Price - Arrival Price (for buys)
        Measures total execution cost
        """
        if side == "buy":
            return execution_price - arrival_price
        else:  # sell
            return arrival_price - execution_price
    
    def analyze_execution(
        self,
        order_id: str,
        arrival_price: float,
        benchmark_price: Optional[float] = None
    ) -> Dict:
        """
        Analyze execution for a specific order
        
        Args:
            order_id: Order to analyze
            arrival_price: Price when order was submitted
            benchmark_price: Optional benchmark (e.g., VWAP, TWAP)
        """
        # Find order
        order = next((o for o in self.orders if o.get("order_id") == order_id), None)
        if not order:
            return {"error": "Order not found"}
        
        # Find fills for this order
        order_fills = [f for f in self.fills if f.get("order_id") == order_id]
        
        if len(order_fills) == 0:
            return {
                "order_id": order_id,
                "status": "no_fills",
                "fill_rate": 0.0
            }
        
        # Calculate metrics
        total_filled = sum(f.get("size", 0) for f in order_fills)
        total_value = sum(f.get("price", 0) * f.get("size", 0) for f in order_fills)
        avg_execution_price = total_value / total_filled if total_filled > 0 else 0
        
        side = order.get("side", "buy")
        order_price = order.get("price", arrival_price)
        
        slippage = self.calculate_slippage(order_price, avg_execution_price, side)
        market_impact = self.calculate_market_impact(arrival_price, avg_execution_price, side)
        implementation_shortfall = self.calculate_implementation_shortfall(
            arrival_price, avg_execution_price, side
        )
        
        # Calculate latency (order time to first fill)
        order_time = order.get("timestamp", 0)
        first_fill_time = min(f.get("timestamp", 0) for f in order_fills)
        latency_ms = (first_fill_time - order_time) * 1000 if first_fill_time > order_time else 0
        
        # VWAP deviation (if benchmark provided)
        vwap_deviation = 0.0
        if benchmark_price:
            vwap_deviation = (avg_execution_price - benchmark_price) / benchmark_price
        
        # Implementation shortfall in basis points
        is_bps = (implementation_shortfall / arrival_price) * 10000 if arrival_price > 0 else 0
        
        return {
            "order_id": order_id,
            "symbol": order.get("symbol"),
            "side": side,
            "order_size": order.get("size", 0),
            "filled_size": total_filled,
            "fill_rate": total_filled / order.get("size", 1) if order.get("size", 0) > 0 else 0,
            "order_price": order_price,
            "arrival_price": arrival_price,
            "avg_execution_price": avg_execution_price,
            "slippage": slippage,
            "slippage_bps": (slippage / order_price) * 10000 if order_price > 0 else 0,
            "market_impact": market_impact,
            "market_impact_bps": (market_impact / arrival_price) * 10000 if arrival_price > 0 else 0,
            "implementation_shortfall": implementation_shortfall,
            "is_bps": is_bps,
            "latency_ms": latency_ms,
            "vwap_deviation": vwap_deviation,
            "num_fills": len(order_fills)
        }
    
    def generate_tca_report(
        self,
        client_id: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> TCAMetrics:
        """
        Generate comprehensive TCA report
        """
        # Filter orders and fills
        filtered_orders = self.orders
        filtered_fills = self.fills
        
        if client_id:
            filtered_orders = [o for o in filtered_orders if o.get("client_id") == client_id]
            filtered_fills = [f for f in filtered_fills if f.get("client_id") == client_id]
        
        if symbol:
            filtered_orders = [o for o in filtered_orders if o.get("symbol") == symbol]
            filtered_fills = [f for f in filtered_fills if f.get("symbol") == symbol]
        
        if start_time:
            filtered_orders = [o for o in filtered_orders if o.get("timestamp", 0) >= start_time]
            filtered_fills = [f for f in filtered_fills if f.get("timestamp", 0) >= start_time]
        
        if end_time:
            filtered_orders = [o for o in filtered_orders if o.get("timestamp", 0) <= end_time]
            filtered_fills = [f for f in filtered_fills if f.get("timestamp", 0) <= end_time]
        
        total_orders = len(filtered_orders)
        total_fills = len(filtered_fills)
        
        # Calculate fill rate
        filled_orders = len(set(f.get("order_id") for f in filtered_fills))
        fill_rate = filled_orders / total_orders if total_orders > 0 else 0.0
        
        # Calculate average slippage and market impact
        slippages = []
        market_impacts = []
        latencies = []
        execution_prices = []
        arrival_prices = []
        
        for order in filtered_orders:
            order_id = order.get("order_id")
            order_fills = [f for f in filtered_fills if f.get("order_id") == order_id]
            
            if len(order_fills) > 0:
                order_price = order.get("price", 0)
                arrival_price = order.get("arrival_price", order_price)
                side = order.get("side", "buy")
                
                total_value = sum(f.get("price", 0) * f.get("size", 0) for f in order_fills)
                total_size = sum(f.get("size", 0) for f in order_fills)
                avg_exec_price = total_value / total_size if total_size > 0 else 0
                
                slippage = self.calculate_slippage(order_price, avg_exec_price, side)
                market_impact = self.calculate_market_impact(arrival_price, avg_exec_price, side)
                
                slippages.append(slippage)
                market_impacts.append(market_impact)
                execution_prices.append(avg_exec_price)
                arrival_prices.append(arrival_price)
                
                # Latency
                order_time = order.get("timestamp", 0)
                first_fill_time = min(f.get("timestamp", 0) for f in order_fills)
                if first_fill_time > order_time:
                    latencies.append((first_fill_time - order_time) * 1000)
        
        avg_slippage = np.mean(slippages) if slippages else 0.0
        avg_market_impact = np.mean(market_impacts) if market_impacts else 0.0
        avg_execution_price = np.mean(execution_prices) if execution_prices else 0.0
        avg_arrival_price = np.mean(arrival_prices) if arrival_prices else 0.0
        avg_latency_ms = np.mean(latencies) if latencies else 0.0
        
        # Implementation shortfall
        implementation_shortfall = avg_execution_price - avg_arrival_price
        is_bps = (implementation_shortfall / avg_arrival_price) * 10000 if avg_arrival_price > 0 else 0
        
        # VWAP deviation (simplified)
        vwap_deviation = 0.0
        
        return TCAMetrics(
            total_orders=total_orders,
            total_fills=total_fills,
            fill_rate=fill_rate,
            avg_slippage=avg_slippage,
            avg_market_impact=avg_market_impact,
            avg_execution_price=avg_execution_price,
            arrival_price=avg_arrival_price,
            implementation_shortfall=implementation_shortfall,
            is_bps=is_bps,
            avg_latency_ms=avg_latency_ms,
            vwap_deviation=vwap_deviation
        )
