"""
Options Pricing: Black-Scholes, Binomial, Greeks
"""
import numpy as np
from scipy.stats import norm
from typing import Dict, Literal
import math


class BlackScholes:
    """
    Black-Scholes option pricing model
    """
    
    @staticmethod
    def price(
        S: float,  # Spot price
        K: float,  # Strike price
        T: float,  # Time to expiration (years)
        r: float,  # Risk-free rate
        sigma: float,  # Volatility
        option_type: Literal["call", "put"] = "call"
    ) -> float:
        """
        Calculate Black-Scholes option price
        """
        if T <= 0:
            # At expiration
            if option_type == "call":
                return max(S - K, 0)
            else:
                return max(K - S, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == "call":
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:  # put
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        return float(price)
    
    @staticmethod
    def delta(
        S: float, K: float, T: float, r: float, sigma: float,
        option_type: Literal["call", "put"] = "call"
    ) -> float:
        """Calculate Delta (price sensitivity to underlying)"""
        if T <= 0:
            if option_type == "call":
                return 1.0 if S > K else 0.0
            else:
                return -1.0 if S < K else 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        
        if option_type == "call":
            return float(norm.cdf(d1))
        else:  # put
            return float(norm.cdf(d1) - 1)
    
    @staticmethod
    def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Gamma (delta sensitivity)"""
        if T <= 0:
            return 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        return float(gamma)
    
    @staticmethod
    def theta(
        S: float, K: float, T: float, r: float, sigma: float,
        option_type: Literal["call", "put"] = "call"
    ) -> float:
        """Calculate Theta (time decay)"""
        if T <= 0:
            return 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        term1 = -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
        
        if option_type == "call":
            term2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
        else:  # put
            term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
        
        return float(term1 + term2)
    
    @staticmethod
    def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Vega (volatility sensitivity)"""
        if T <= 0:
            return 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T)
        return float(vega)
    
    @staticmethod
    def rho(
        S: float, K: float, T: float, r: float, sigma: float,
        option_type: Literal["call", "put"] = "call"
    ) -> float:
        """Calculate Rho (interest rate sensitivity)"""
        if T <= 0:
            return 0.0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == "call":
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        else:  # put
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        
        return float(rho)
    
    @staticmethod
    def all_greeks(
        S: float, K: float, T: float, r: float, sigma: float,
        option_type: Literal["call", "put"] = "call"
    ) -> Dict[str, float]:
        """Calculate all Greeks at once"""
        return {
            "price": BlackScholes.price(S, K, T, r, sigma, option_type),
            "delta": BlackScholes.delta(S, K, T, r, sigma, option_type),
            "gamma": BlackScholes.gamma(S, K, T, r, sigma),
            "theta": BlackScholes.theta(S, K, T, r, sigma, option_type),
            "vega": BlackScholes.vega(S, K, T, r, sigma),
            "rho": BlackScholes.rho(S, K, T, r, sigma, option_type)
        }


class Option:
    """Represents an option contract"""
    
    def __init__(
        self,
        symbol: str,
        strike: float,
        expiration: float,  # Time to expiration in years
        option_type: Literal["call", "put"],
        spot: float,
        volatility: float,
        risk_free_rate: float = 0.05
    ):
        self.symbol = symbol
        self.strike = strike
        self.expiration = expiration
        self.option_type = option_type
        self.spot = spot
        self.volatility = volatility
        self.risk_free_rate = risk_free_rate
    
    def price(self) -> float:
        """Get current option price"""
        return BlackScholes.price(
            self.spot, self.strike, self.expiration,
            self.risk_free_rate, self.volatility, self.option_type
        )
    
    def greeks(self) -> Dict[str, float]:
        """Get all Greeks"""
        return BlackScholes.all_greeks(
            self.spot, self.strike, self.expiration,
            self.risk_free_rate, self.volatility, self.option_type
        )
    
    def delta(self) -> float:
        """Get Delta"""
        return BlackScholes.delta(
            self.spot, self.strike, self.expiration,
            self.risk_free_rate, self.volatility, self.option_type
        )
    
    def update_spot(self, new_spot: float):
        """Update spot price and recalculate"""
        self.spot = new_spot
