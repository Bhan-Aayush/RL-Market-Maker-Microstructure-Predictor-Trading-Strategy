"""
Advanced Risk Models: VaR, CVaR, Stress Testing
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from scipy import stats
from dataclasses import dataclass


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics"""
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    volatility: float
    max_drawdown: float
    sharpe_ratio: float


class VaRCalculator:
    """
    Value at Risk (VaR) calculation using multiple methods
    """
    
    @staticmethod
    def historical_var(returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Historical VaR: Percentile of historical returns
        
        Args:
            returns: Array of returns
            confidence: Confidence level (0.95 = 95%)
        
        Returns:
            VaR (positive number, represents loss)
        """
        if len(returns) == 0:
            return 0.0
        
        var = -np.percentile(returns, (1 - confidence) * 100)
        return float(var)
    
    @staticmethod
    def parametric_var(
        returns: np.ndarray,
        confidence: float = 0.95,
        mean: Optional[float] = None
    ) -> float:
        """
        Parametric VaR: Assumes normal distribution
        
        VaR = - (mean + z_score * std)
        """
        if len(returns) == 0:
            return 0.0
        
        if mean is None:
            mean = np.mean(returns)
        std = np.std(returns)
        
        z_score = stats.norm.ppf(1 - confidence)
        var = -(mean + z_score * std)
        
        return float(max(0, var))
    
    @staticmethod
    def monte_carlo_var(
        returns: np.ndarray,
        confidence: float = 0.95,
        n_simulations: int = 10000,
        horizon: int = 1
    ) -> float:
        """
        Monte Carlo VaR: Simulate future returns
        
        Args:
            returns: Historical returns
            confidence: Confidence level
            n_simulations: Number of Monte Carlo simulations
            horizon: Time horizon (days)
        """
        if len(returns) == 0:
            return 0.0
        
        mean = np.mean(returns)
        std = np.std(returns)
        
        # Simulate returns
        simulated_returns = np.random.normal(
            mean * horizon,
            std * np.sqrt(horizon),
            n_simulations
        )
        
        var = -np.percentile(simulated_returns, (1 - confidence) * 100)
        return float(max(0, var))
    
    @staticmethod
    def calculate_all_methods(returns: np.ndarray, confidence: float = 0.95) -> Dict:
        """Calculate VaR using all methods"""
        return {
            "historical": VaRCalculator.historical_var(returns, confidence),
            "parametric": VaRCalculator.parametric_var(returns, confidence),
            "monte_carlo": VaRCalculator.monte_carlo_var(returns, confidence)
        }


class CVaRCalculator:
    """
    Conditional Value at Risk (CVaR) / Expected Shortfall
    Average loss beyond VaR threshold
    """
    
    @staticmethod
    def calculate(returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Calculate CVaR
        
        CVaR = Mean of returns below VaR threshold
        """
        if len(returns) == 0:
            return 0.0
        
        var = VaRCalculator.historical_var(returns, confidence)
        
        # Returns below VaR threshold
        tail_returns = returns[returns <= -var]
        
        if len(tail_returns) == 0:
            return float(var)
        
        cvar = -np.mean(tail_returns)
        return float(max(0, cvar))


class StressTester:
    """
    Stress testing: Scenario analysis
    """
    
    @staticmethod
    def historical_stress(
        returns: np.ndarray,
        stress_periods: List[Tuple[int, int]]
    ) -> Dict:
        """
        Stress test using historical stress periods
        
        Args:
            returns: Historical returns
            stress_periods: List of (start_idx, end_idx) for stress periods
        """
        results = {}
        
        for i, (start, end) in enumerate(stress_periods):
            stress_returns = returns[start:end]
            if len(stress_returns) > 0:
                results[f"stress_period_{i}"] = {
                    "mean_return": float(np.mean(stress_returns)),
                    "volatility": float(np.std(stress_returns)),
                    "max_loss": float(np.min(stress_returns)),
                    "total_return": float(np.sum(stress_returns))
                }
        
        return results
    
    @staticmethod
    def scenario_stress(
        current_portfolio_value: float,
        positions: Dict[str, float],  # symbol -> position
        scenario_returns: Dict[str, float]  # symbol -> return in scenario
    ) -> Dict:
        """
        Stress test using hypothetical scenarios
        
        Example: "What if AAPL drops 10% and MSFT drops 5%?"
        """
        scenario_pnl = 0.0
        
        for symbol, position in positions.items():
            if symbol in scenario_returns:
                scenario_pnl += position * scenario_returns[symbol]
        
        scenario_value = current_portfolio_value + scenario_pnl
        scenario_loss = current_portfolio_value - scenario_value
        
        return {
            "scenario_pnl": scenario_pnl,
            "scenario_value": scenario_value,
            "scenario_loss": scenario_loss,
            "loss_pct": (scenario_loss / current_portfolio_value) * 100 if current_portfolio_value > 0 else 0
        }


class AdvancedRiskManager:
    """
    Comprehensive risk management with advanced metrics
    """
    
    def __init__(self, lookback_window: int = 252):  # 1 year of trading days
        self.lookback_window = lookback_window
        self.returns_history: List[float] = []
    
    def add_return(self, return_value: float):
        """Add a return observation"""
        self.returns_history.append(return_value)
        if len(self.returns_history) > self.lookback_window:
            self.returns_history.pop(0)
    
    def calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        if len(self.returns_history) < 2:
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0)
        
        returns = np.array(self.returns_history)
        
        # VaR
        var_95 = VaRCalculator.historical_var(returns, 0.95)
        var_99 = VaRCalculator.historical_var(returns, 0.99)
        
        # CVaR
        cvar_95 = CVaRCalculator.calculate(returns, 0.95)
        cvar_99 = CVaRCalculator.calculate(returns, 0.99)
        
        # Volatility
        volatility = float(np.std(returns))
        
        # Max drawdown
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        max_drawdown = float(np.min(drawdown))
        
        # Sharpe ratio (annualized, assuming daily returns)
        mean_return = np.mean(returns)
        sharpe = (mean_return / volatility) * np.sqrt(252) if volatility > 0 else 0.0
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            volatility=volatility,
            max_drawdown=max_drawdown,
            sharpe_ratio=float(sharpe)
        )
    
    def stress_test(self, positions: Dict[str, float], scenarios: List[Dict[str, float]]) -> Dict:
        """Run stress tests on portfolio"""
        results = {}
        
        for i, scenario in enumerate(scenarios):
            result = StressTester.scenario_stress(
                current_portfolio_value=100000.0,  # Would get from actual portfolio
                positions=positions,
                scenario_returns=scenario
            )
            results[f"scenario_{i}"] = result
        
        return results
