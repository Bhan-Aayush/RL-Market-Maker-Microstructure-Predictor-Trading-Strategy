"""
Options Market-Making Strategy with Delta Hedging
"""
from typing import Optional
from .base_strategy import BaseStrategy, Quote, MarketState
from ..options.pricing import Option, BlackScholes
from ..options.delta_hedging import DeltaHedger


class OptionsMarketMaker(BaseStrategy):
    """
    Market maker for options with delta hedging
    """
    
    def __init__(
        self,
        client_id: str,
        underlying_symbol: str,
        strike: float,
        expiration_days: float,
        volatility: float,
        risk_free_rate: float = 0.05,
        target_spread_pct: float = 0.02  # 2% spread
    ):
        super().__init__(client_id, symbol=underlying_symbol)
        self.underlying_symbol = underlying_symbol
        self.strike = strike
        self.expiration_years = expiration_days / 365.0
        self.volatility = volatility
        self.risk_free_rate = risk_free_rate
        self.target_spread_pct = target_spread_pct
        
        # Create option contracts
        self.call_option = Option(
            symbol=f"{underlying_symbol}_C{strike}",
            strike=strike,
            expiration=self.expiration_years,
            option_type="call",
            spot=100.0,  # Will be updated
            volatility=volatility,
            risk_free_rate=risk_free_rate
        )
        
        self.put_option = Option(
            symbol=f"{underlying_symbol}_P{strike}",
            strike=strike,
            expiration=self.expiration_years,
            option_type="put",
            spot=100.0,  # Will be updated
            volatility=volatility,
            risk_free_rate=risk_free_rate
        )
        
        # Delta hedger
        self.hedger = DeltaHedger(underlying_symbol)
        
        # Track option positions
        self.call_position = 0  # Number of calls (positive = long, negative = short)
        self.put_position = 0
    
    def compute_quotes(self, market_state: MarketState) -> Quote:
        """Compute option quotes based on current market state"""
        spot = market_state.mid
        
        # Update option spot prices
        self.call_option.update_spot(spot)
        self.put_option.update_spot(spot)
        
        # Get option prices
        call_price = self.call_option.price()
        put_price = self.put_option.price()
        
        # Calculate bid/ask with target spread
        call_spread = call_price * self.target_spread_pct
        put_spread = put_price * self.target_spread_pct
        
        call_bid = call_price - call_spread / 2
        call_ask = call_price + call_spread / 2
        
        put_bid = put_price - put_spread / 2
        put_ask = put_price + put_spread / 2
        
        # For now, return call quotes (can extend to handle both)
        # In production, you'd quote both calls and puts
        return Quote(
            bid_price=round(call_bid, 2),
            ask_price=round(call_ask, 2),
            bid_size=1,
            ask_size=1
        )
    
    def get_greeks(self) -> Dict:
        """Get current Greeks for portfolio"""
        # Update hedger with current positions
        self.hedger.options_positions = []
        if self.call_position != 0:
            self.hedger.add_option_position(self.call_option, self.call_position)
        if self.put_position != 0:
            self.hedger.add_option_position(self.put_option, self.put_position)
        
        return self.hedger.portfolio_greeks()
    
    def get_hedge_recommendation(self, current_spot: float) -> Dict:
        """Get delta hedge recommendation"""
        return self.hedger.update_hedge(current_spot)
