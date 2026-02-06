"""
Risk Manager: Position limits, P&L stops, order rate limits
"""
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
import time


@dataclass
class RiskLimits:
    """Risk limit configuration"""
    max_position: int = 100  # Max net position per symbol
    max_daily_loss: float = 1000.0  # Max daily loss in dollars
    max_order_rate: int = 100  # Max orders per second
    max_order_size: int = 50  # Max size per order
    price_deviation_pct: float = 0.05  # Max price deviation from mid (%)


@dataclass
class ClientRiskState:
    """Per-client risk state"""
    position: int = 0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    daily_pnl: float = 0.0
    order_count: int = 0
    last_order_time: float = 0.0
    is_blocked: bool = False


class RiskManager:
    """
    Enforces risk limits and position tracking
    """
    
    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self.client_states: Dict[str, ClientRiskState] = {}
        self.session_start_time = time.time()
    
    def get_or_create_state(self, client_id: str) -> ClientRiskState:
        """Get or create risk state for client"""
        if client_id not in self.client_states:
            self.client_states[client_id] = ClientRiskState()
        return self.client_states[client_id]
    
    def check_order_rate(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """Check if client exceeds order rate limit"""
        state = self.get_or_create_state(client_id)
        now = time.time()
        
        # Reset counter if more than 1 second has passed
        if now - state.last_order_time >= 1.0:
            state.order_count = 0
        
        if state.order_count >= self.limits.max_order_rate:
            return False, "Order rate limit exceeded"
        
        state.order_count += 1
        state.last_order_time = now
        return True, None
    
    def check_position_limit(self, client_id: str, side: str, size: int) -> Tuple[bool, Optional[str]]:
        """Check if order would exceed position limit"""
        state = self.get_or_create_state(client_id)
        
        # Calculate new position
        position_delta = size if side == "buy" else -size
        new_position = state.position + position_delta
        
        if abs(new_position) > self.limits.max_position:
            return False, f"Position limit exceeded: {new_position} > {self.limits.max_position}"
        
        return True, None
    
    def check_order_size(self, size: int) -> Tuple[bool, Optional[str]]:
        """Check if order size is within limits"""
        if size > self.limits.max_order_size:
            return False, f"Order size {size} exceeds limit {self.limits.max_order_size}"
        if size <= 0:
            return False, "Order size must be positive"
        return True, None
    
    def check_price_bounds(self, price: float, mid_price: float) -> Tuple[bool, Optional[str]]:
        """Check if price is within allowed deviation from mid"""
        if mid_price is None:
            return True, None
        
        deviation = abs(price - mid_price) / mid_price
        if deviation > self.limits.price_deviation_pct:
            return False, f"Price deviation {deviation:.2%} exceeds limit {self.limits.price_deviation_pct:.2%}"
        
        return True, None
    
    def check_daily_loss(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """Check if client has exceeded daily loss limit"""
        state = self.get_or_create_state(client_id)
        
        total_pnl = state.realized_pnl + state.unrealized_pnl
        if total_pnl < -self.limits.max_daily_loss:
            state.is_blocked = True
            return False, f"Daily loss limit exceeded: {total_pnl:.2f}"
        
        return True, None
    
    def validate_order(
        self,
        client_id: str,
        side: str,
        size: int,
        price: Optional[float] = None,
        mid_price: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive order validation
        Returns (is_valid, error_message)
        """
        state = self.get_or_create_state(client_id)
        
        # Check if blocked
        if state.is_blocked:
            return False, "Client is blocked due to risk violation"
        
        # Check order rate
        valid, msg = self.check_order_rate(client_id)
        if not valid:
            return False, msg
        
        # Check order size
        valid, msg = self.check_order_size(size)
        if not valid:
            return False, msg
        
        # Check position limit
        valid, msg = self.check_position_limit(client_id, side, size)
        if not valid:
            return False, msg
        
        # Check price bounds (for limit orders)
        if price is not None and mid_price is not None:
            valid, msg = self.check_price_bounds(price, mid_price)
            if not valid:
                return False, msg
        
        # Check daily loss
        valid, msg = self.check_daily_loss(client_id)
        if not valid:
            return False, msg
        
        return True, None
    
    def update_position(self, client_id: str, side: str, size: int, price: float):
        """Update position after fill"""
        state = self.get_or_create_state(client_id)
        position_delta = size if side == "buy" else -size
        state.position += position_delta
    
    def update_pnl(self, client_id: str, realized_pnl: float, unrealized_pnl: float = 0.0):
        """Update P&L for client"""
        state = self.get_or_create_state(client_id)
        state.realized_pnl += realized_pnl
        state.unrealized_pnl = unrealized_pnl
        state.daily_pnl = state.realized_pnl + state.unrealized_pnl
    
    def get_client_state(self, client_id: str) -> Optional[ClientRiskState]:
        """Get risk state for client"""
        return self.client_states.get(client_id)
    
    def reset_daily(self):
        """Reset daily counters (call at start of trading day)"""
        for state in self.client_states.values():
            state.daily_pnl = 0.0
            state.order_count = 0
            state.is_blocked = False
