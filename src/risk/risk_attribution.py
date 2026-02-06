"""
Risk Attribution: Decompose portfolio risk by factor
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RiskAttribution:
    """Risk attribution breakdown"""
    total_risk: float
    factor_contributions: Dict[str, float]  # factor -> contribution
    asset_contributions: Dict[str, float]  # asset -> contribution
    factor_loadings: Dict[str, Dict[str, float]]  # asset -> {factor -> loading}


class RiskAttributionAnalyzer:
    """
    Analyzes risk attribution by factors and assets
    """
    
    def __init__(self):
        self.factors: List[str] = []
        self.assets: List[str] = []
        self.factor_loadings: Dict[str, Dict[str, float]] = {}  # asset -> {factor -> loading}
        self.factor_covariance: np.ndarray = None
    
    def set_factors(self, factors: List[str]):
        """Set factor names"""
        self.factors = factors
    
    def set_assets(self, assets: List[str]):
        """Set asset names"""
        self.assets = assets
    
    def set_factor_loadings(
        self,
        asset: str,
        loadings: Dict[str, float]
    ):
        """Set factor loadings for an asset"""
        self.factor_loadings[asset] = loadings
    
    def set_factor_covariance(self, covariance_matrix: np.ndarray):
        """Set factor covariance matrix"""
        self.factor_covariance = covariance_matrix
    
    def calculate_asset_covariance(
        self,
        weights: Dict[str, float]
    ) -> np.ndarray:
        """
        Calculate asset covariance from factor model
        
        Cov(assets) = B * Cov(factors) * B'
        where B is factor loading matrix
        """
        n_assets = len(self.assets)
        asset_cov = np.zeros((n_assets, n_assets))
        
        # Build factor loading matrix
        B = np.zeros((n_assets, len(self.factors)))
        for i, asset in enumerate(self.assets):
            if asset in self.factor_loadings:
                for j, factor in enumerate(self.factors):
                    B[i, j] = self.factor_loadings[asset].get(factor, 0.0)
        
        # Calculate asset covariance
        if self.factor_covariance is not None:
            asset_cov = B @ self.factor_covariance @ B.T
        
        return asset_cov
    
    def attribute_risk(
        self,
        weights: Dict[str, float],
        asset_covariance: Optional[np.ndarray] = None
    ) -> RiskAttribution:
        """
        Attribute portfolio risk to factors and assets
        """
        # Get asset covariance
        if asset_covariance is None:
            asset_covariance = self.calculate_asset_covariance(weights)
        
        # Portfolio weights vector
        w = np.array([weights.get(asset, 0.0) for asset in self.assets])
        
        # Portfolio variance
        portfolio_variance = w.T @ asset_covariance @ w
        total_risk = np.sqrt(portfolio_variance)
        
        # Factor contributions
        factor_contributions = {}
        if self.factor_covariance is not None:
            # Build factor loading matrix
            B = np.zeros((len(self.assets), len(self.factors)))
            for i, asset in enumerate(self.assets):
                if asset in self.factor_loadings:
                    for j, factor in enumerate(self.factors):
                        B[i, j] = self.factor_loadings[asset].get(factor, 0.0)
            
            # Factor exposures
            factor_exposures = B.T @ w
            
            # Factor contributions to variance
            for i, factor in enumerate(self.factors):
                # Contribution = exposure * (factor variance * exposure)
                factor_var = self.factor_covariance[i, i]
                factor_contributions[factor] = float(factor_exposures[i]**2 * factor_var)
        
        # Asset contributions
        asset_contributions = {}
        for i, asset in enumerate(self.assets):
            # Marginal contribution = weight * (covariance @ weights)[i]
            marginal = (asset_covariance @ w)[i]
            contribution = w[i] * marginal
            asset_contributions[asset] = float(contribution)
        
        return RiskAttribution(
            total_risk=float(total_risk),
            factor_contributions=factor_contributions,
            asset_contributions=asset_contributions,
            factor_loadings=self.factor_loadings.copy()
        )
    
    def calculate_var_attribution(
        self,
        weights: Dict[str, float],
        returns_data: pd.DataFrame,
        confidence: float = 0.95
    ) -> Dict:
        """
        Attribute VaR to factors/assets
        """
        # Calculate asset returns
        asset_returns = returns_data[self.assets].values
        
        # Portfolio returns
        w = np.array([weights.get(asset, 0.0) for asset in self.assets])
        portfolio_returns = asset_returns @ w
        
        # Portfolio VaR
        portfolio_var = -np.percentile(portfolio_returns, (1 - confidence) * 100)
        
        # Component VaR (contribution of each asset)
        component_var = {}
        for i, asset in enumerate(self.assets):
            # Marginal VaR contribution
            asset_returns_i = asset_returns[:, i]
            correlation = np.corrcoef(portfolio_returns, asset_returns_i)[0, 1]
            asset_std = np.std(asset_returns_i)
            portfolio_std = np.std(portfolio_returns)
            
            marginal_var = correlation * asset_std / portfolio_std * portfolio_var
            component_var[asset] = float(w[i] * marginal_var)
        
        return {
            "portfolio_var": float(portfolio_var),
            "component_var": component_var
        }
