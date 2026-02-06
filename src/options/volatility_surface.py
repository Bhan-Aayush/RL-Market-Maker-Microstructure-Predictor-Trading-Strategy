"""
Volatility Surface for Options
Implied volatility vs strike and maturity
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from scipy.interpolate import griddata
from .pricing import BlackScholes


class VolatilitySurface:
    """
    Represents and interpolates volatility surface
    """
    
    def __init__(self):
        self.data_points: List[Dict] = []  # {strike, maturity, implied_vol}
    
    def add_data_point(self, strike: float, maturity: float, implied_vol: float):
        """Add a volatility data point"""
        self.data_points.append({
            "strike": strike,
            "maturity": maturity,
            "implied_vol": implied_vol
        })
    
    def get_implied_vol(self, strike: float, maturity: float) -> float:
        """
        Get implied volatility for given strike and maturity
        Uses interpolation if data points available
        """
        if len(self.data_points) == 0:
            return 0.20  # Default volatility
        
        # Extract data
        strikes = np.array([d["strike"] for d in self.data_points])
        maturities = np.array([d["maturity"] for d in self.data_points])
        vols = np.array([d["implied_vol"] for d in self.data_points])
        
        # Interpolate
        try:
            implied_vol = griddata(
                (strikes, maturities),
                vols,
                (strike, maturity),
                method='linear',
                fill_value=np.mean(vols)
            )
            return float(implied_vol)
        except:
            # Fallback to nearest neighbor
            distances = np.sqrt((strikes - strike)**2 + (maturities - maturity)**2)
            nearest_idx = np.argmin(distances)
            return float(vols[nearest_idx])
    
    def calculate_implied_vol_from_price(
        self,
        option_price: float,
        spot: float,
        strike: float,
        maturity: float,
        risk_free_rate: float,
        option_type: str = "call"
    ) -> float:
        """
        Calculate implied volatility from option price
        Uses binary search
        """
        def price_error(vol):
            price = BlackScholes.price(spot, strike, maturity, risk_free_rate, vol, option_type)
            return abs(price - option_price)
        
        # Binary search for implied vol
        vol_low = 0.001
        vol_high = 2.0
        tolerance = 0.0001
        
        while vol_high - vol_low > tolerance:
            vol_mid = (vol_low + vol_high) / 2
            price_mid = BlackScholes.price(spot, strike, maturity, risk_free_rate, vol_mid, option_type)
            
            if price_mid < option_price:
                vol_low = vol_mid
            else:
                vol_high = vol_mid
        
        return (vol_low + vol_high) / 2
    
    def build_from_market_prices(
        self,
        spot: float,
        strikes: List[float],
        maturities: List[float],
        market_prices: Dict[Tuple[float, float], float],  # (strike, maturity) -> price
        risk_free_rate: float = 0.05,
        option_type: str = "call"
    ):
        """
        Build volatility surface from market option prices
        """
        for strike in strikes:
            for maturity in maturities:
                if (strike, maturity) in market_prices:
                    market_price = market_prices[(strike, maturity)]
                    implied_vol = self.calculate_implied_vol_from_price(
                        market_price, spot, strike, maturity, risk_free_rate, option_type
                    )
                    self.add_data_point(strike, maturity, implied_vol)
    
    def get_surface_data(
        self,
        strike_range: Tuple[float, float],
        maturity_range: Tuple[float, float],
        resolution: int = 50
    ) -> Dict:
        """
        Get volatility surface data for visualization
        
        Returns:
            Dictionary with strikes, maturities, and implied_vols arrays
        """
        strikes = np.linspace(strike_range[0], strike_range[1], resolution)
        maturities = np.linspace(maturity_range[0], maturity_range[1], resolution)
        
        implied_vols = np.zeros((len(maturities), len(strikes)))
        
        for i, maturity in enumerate(maturities):
            for j, strike in enumerate(strikes):
                implied_vols[i, j] = self.get_implied_vol(strike, maturity)
        
        return {
            "strikes": strikes,
            "maturities": maturities,
            "implied_vols": implied_vols
        }


class VolatilitySmile:
    """
    Volatility smile: implied vol vs strike (for fixed maturity)
    """
    
    @staticmethod
    def calculate_smile(
        spot: float,
        strikes: List[float],
        maturity: float,
        risk_free_rate: float,
        market_prices: Dict[float, float]  # strike -> price
    ) -> Dict:
        """
        Calculate volatility smile for given maturity
        """
        surface = VolatilitySurface()
        
        for strike in strikes:
            if strike in market_prices:
                market_price = market_prices[strike]
                implied_vol = surface.calculate_implied_vol_from_price(
                    market_price, spot, strike, maturity, risk_free_rate
                )
                surface.add_data_point(strike, maturity, implied_vol)
        
        # Extract smile
        implied_vols = [surface.get_implied_vol(s, maturity) for s in strikes]
        
        return {
            "strikes": strikes,
            "implied_vols": implied_vols,
            "maturity": maturity,
            "spot": spot
        }
