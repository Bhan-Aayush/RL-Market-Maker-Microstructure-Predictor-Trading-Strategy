"""
Portfolio Optimization: Mean-Variance, Risk Parity, etc.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from scipy.optimize import minimize
from dataclasses import dataclass


@dataclass
class Portfolio:
    """Portfolio representation"""
    symbols: List[str]
    weights: np.ndarray
    expected_returns: np.ndarray
    covariance_matrix: np.ndarray
    current_prices: Dict[str, float]


class PortfolioOptimizer:
    """
    Portfolio optimization using various methods
    """
    
    @staticmethod
    def mean_variance_optimize(
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        target_return: Optional[float] = None,
        risk_aversion: float = 1.0
    ) -> np.ndarray:
        """
        Mean-variance optimization
        
        Maximize: w' * mu - lambda * w' * Sigma * w
        Subject to: sum(w) = 1, w >= 0
        """
        n = len(expected_returns)
        
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            return -(portfolio_return - risk_aversion * portfolio_risk ** 2)
        
        # Constraints
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
        bounds = [(0, 1) for _ in range(n)]
        
        # Initial guess (equal weights)
        x0 = np.ones(n) / n
        
        # Optimize
        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x if result.success else x0
    
    @staticmethod
    def risk_parity_optimize(covariance_matrix: np.ndarray) -> np.ndarray:
        """
        Risk parity optimization
        Equal risk contribution from each asset
        """
        n = covariance_matrix.shape[0]
        
        def risk_contribution(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            marginal_contrib = np.dot(covariance_matrix, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            return contrib
        
        def objective(weights):
            contrib = risk_contribution(weights)
            # Minimize difference in risk contributions
            target_contrib = np.ones(n) / n
            return np.sum((contrib - target_contrib) ** 2)
        
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
        bounds = [(0, 1) for _ in range(n)]
        x0 = np.ones(n) / n
        
        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x if result.success else x0
    
    @staticmethod
    def min_variance_optimize(covariance_matrix: np.ndarray) -> np.ndarray:
        """
        Minimum variance portfolio
        """
        n = covariance_matrix.shape[0]
        
        def objective(weights):
            return np.dot(weights.T, np.dot(covariance_matrix, weights))
        
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
        bounds = [(0, 1) for _ in range(n)]
        x0 = np.ones(n) / n
        
        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x if result.success else x0
    
    @staticmethod
    def calculate_portfolio_metrics(
        weights: np.ndarray,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray
    ) -> Dict:
        """Calculate portfolio-level metrics"""
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
        portfolio_vol = np.sqrt(portfolio_variance)
        
        # Sharpe ratio (assuming risk-free rate = 0)
        sharpe = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0.0
        
        return {
            "expected_return": float(portfolio_return),
            "volatility": float(portfolio_vol),
            "variance": float(portfolio_variance),
            "sharpe_ratio": float(sharpe),
            "weights": {f"asset_{i}": float(w) for i, w in enumerate(weights)}
        }


class MultiAssetMarketMaker:
    """
    Market-making across multiple assets with portfolio optimization
    """
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.positions: Dict[str, float] = {s: 0.0 for s in symbols}
        self.optimizer = PortfolioOptimizer()
    
    def calculate_portfolio_risk(self, covariance_matrix: np.ndarray) -> float:
        """Calculate total portfolio risk"""
        positions_array = np.array([self.positions[s] for s in self.symbols])
        portfolio_variance = np.dot(positions_array.T, np.dot(covariance_matrix, positions_array))
        return float(np.sqrt(portfolio_variance))
    
    def optimize_quotes(
        self,
        market_states: Dict[str, Dict],  # symbol -> market state
        covariance_matrix: np.ndarray,
        target_risk: float = 100.0
    ) -> Dict[str, Dict]:
        """
        Optimize quotes across multiple assets
        
        Returns:
            Dict of symbol -> {bid_price, ask_price, bid_size, ask_size}
        """
        quotes = {}
        
        # Calculate current portfolio risk
        current_risk = self.calculate_portfolio_risk(covariance_matrix)
        
        # Adjust quote sizes based on portfolio risk
        risk_scale = min(1.0, target_risk / current_risk) if current_risk > 0 else 1.0
        
        for symbol in self.symbols:
            if symbol in market_states:
                state = market_states[symbol]
                mid = state.get("mid", 100.0)
                spread = state.get("spread", 0.02)
                
                # Base quote
                bid_price = mid - spread / 2
                ask_price = mid + spread / 2
                base_size = 1
                
                # Scale by risk
                quote_size = int(base_size * risk_scale)
                
                quotes[symbol] = {
                    "bid_price": round(bid_price, 2),
                    "ask_price": round(ask_price, 2),
                    "bid_size": quote_size,
                    "ask_size": quote_size
                }
        
        return quotes
