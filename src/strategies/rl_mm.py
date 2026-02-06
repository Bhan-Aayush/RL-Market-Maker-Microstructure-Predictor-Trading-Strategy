"""
RL-based Market Maker: Uses trained RL agent to make quoting decisions
"""
import numpy as np
from typing import Optional
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from .base_strategy import BaseStrategy, Quote, MarketState
from ..rl.lob_env import LOBMarketMakingEnv
from ..features.microstructure import MicrostructureFeatureExtractor


class RLMarketMaker(BaseStrategy):
    """
    Market maker that uses a trained RL agent to decide quotes
    """
    
    def __init__(
        self,
        client_id: str,
        model_path: str,
        tick_size: float = 0.01,
        initial_mid: float = 100.0,
        use_predictor: bool = False
    ):
        super().__init__(client_id)
        self.tick_size = tick_size
        self.initial_mid = initial_mid
        self.use_predictor = use_predictor
        
        # Load trained RL model
        try:
            self.model = PPO.load(model_path)
            print(f"✓ Loaded RL model from {model_path}")
        except Exception as e:
            raise ValueError(f"Failed to load RL model from {model_path}: {e}")
        
        # Create environment for feature extraction
        self.env = LOBMarketMakingEnv(
            episode_length=1000,
            initial_mid=initial_mid,
            tick_size=tick_size,
            use_predictor=use_predictor
        )
        
        # Feature extractor
        self.feature_extractor = MicrostructureFeatureExtractor()
        
        # Track last market state for feature extraction
        self.last_bids = []
        self.last_asks = []
    
    def _get_observation(self, market_state: MarketState) -> np.ndarray:
        """Extract observation from market state"""
        # Use last book snapshot if available, otherwise create synthetic
        if self.last_bids and self.last_asks:
            bids = self.last_bids
            asks = self.last_asks
        else:
            # Create synthetic book snapshot
            mid = market_state.mid
            bids = [(mid - 0.01 * i, 10) for i in range(1, 6)]
            asks = [(mid + 0.01 * i, 10) for i in range(1, 6)]
        
        # Extract features
        features = self.feature_extractor.extract_features(bids, asks)
        feature_vec = self.feature_extractor.get_feature_vector(features)
        
        # Add inventory (normalized)
        inventory_norm = market_state.inventory / 50.0
        
        # Combine features
        obs_list = list(feature_vec) + [inventory_norm]
        
        # Add predictor score if available
        if self.use_predictor and hasattr(self.env, 'predictor') and self.env.predictor:
            predictor_score = self.env.predictor.predict(feature_vec.reshape(1, -1))
            obs_list.append(predictor_score)
        
        return np.array(obs_list, dtype=np.float32)
    
    def compute_quotes(self, market_state: MarketState) -> Quote:
        """Compute quotes using RL agent"""
        # Get observation
        obs = self._get_observation(market_state)
        
        # Get action from RL agent
        action, _ = self.model.predict(obs, deterministic=True)
        
        # Action: [bid_offset, ask_offset, quote_size]
        bid_offset, ask_offset, quote_size = action
        
        # Convert offsets to prices
        mid = market_state.mid
        bid_price = round(mid - bid_offset * self.tick_size, 2)
        ask_price = round(mid + ask_offset * self.tick_size, 2)
        quote_size = int(max(1, min(10, quote_size)))
        
        return Quote(
            bid_price=bid_price,
            ask_price=ask_price,
            bid_size=quote_size,
            ask_size=quote_size
        )
    
    def update_book_snapshot(self, bids: list, asks: list):
        """Update book snapshot for feature extraction"""
        self.last_bids = bids
        self.last_asks = asks
