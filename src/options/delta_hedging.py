"""
Delta Hedging for Options Market-Making
"""
from typing import Dict, List
from .pricing import Option, BlackScholes


class DeltaHedger:
    """
    Manages delta hedging for options positions
    """
    
    def __init__(self, underlying_symbol: str):
        self.underlying_symbol = underlying_symbol
        self.options_positions: List[Dict] = []  # List of {option, quantity}
        self.underlying_position: float = 0.0  # Shares of underlying
    
    def add_option_position(self, option: Option, quantity: int):
        """Add an option position (positive = long, negative = short)"""
        self.options_positions.append({
            "option": option,
            "quantity": quantity
        })
    
    def total_delta(self) -> float:
        """Calculate total portfolio delta"""
        total = 0.0
        for pos in self.options_positions:
            option = pos["option"]
            quantity = pos["quantity"]
            delta = option.delta()
            total += quantity * delta
        return total
    
    def hedge_required(self) -> float:
        """
        Calculate how many shares of underlying needed to hedge
        Returns negative of total delta (to neutralize)
        """
        return -self.total_delta()
    
    def update_hedge(self, current_spot: float) -> Dict:
        """
        Update hedge based on current spot price
        Returns hedge recommendation
        """
        # Update all option spot prices
        for pos in self.options_positions:
            pos["option"].update_spot(current_spot)
        
        # Calculate required hedge
        required_hedge = self.hedge_required()
        hedge_delta = required_hedge - self.underlying_position
        
        return {
            "current_underlying_position": self.underlying_position,
            "required_underlying_position": required_hedge,
            "hedge_delta": hedge_delta,
            "action": "buy" if hedge_delta > 0 else "sell" if hedge_delta < 0 else "hold",
            "shares": abs(hedge_delta)
        }
    
    def apply_hedge(self, shares: float):
        """Apply hedge by updating underlying position"""
        self.underlying_position += shares
    
    def portfolio_greeks(self) -> Dict[str, float]:
        """Calculate portfolio-level Greeks"""
        total_delta = 0.0
        total_gamma = 0.0
        total_theta = 0.0
        total_vega = 0.0
        total_rho = 0.0
        
        for pos in self.options_positions:
            option = pos["option"]
            quantity = pos["quantity"]
            greeks = option.greeks()
            
            total_delta += quantity * greeks["delta"]
            total_gamma += quantity * greeks["gamma"]
            total_theta += quantity * greeks["theta"]
            total_vega += quantity * greeks["vega"]
            total_rho += quantity * greeks["rho"]
        
        return {
            "delta": total_delta,
            "gamma": total_gamma,
            "theta": total_theta,
            "vega": total_vega,
            "rho": total_rho
        }
