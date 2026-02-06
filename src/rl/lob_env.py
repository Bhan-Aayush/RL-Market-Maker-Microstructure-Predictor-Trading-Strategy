"""
Gym-compatible RL environment for market making
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple, Optional
import time

from ..lob.order_book import LimitOrderBook, Order
from ..features.microstructure import MicrostructureFeatureExtractor
from ..predictor.short_term_predictor import PredictorWrapper


class LOBMarketMakingEnv(gym.Env):
    """
    Gym environment for RL-based market making
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 4}
    
    def __init__(
        self,
        episode_length: int = 1000,
        initial_mid: float = 100.0,
        tick_size: float = 0.01,
        use_predictor: bool = False,
        predictor: Optional[PredictorWrapper] = None
    ):
        super().__init__()
        
        self.episode_length = episode_length
        self.initial_mid = initial_mid
        self.tick_size = tick_size
        self.use_predictor = use_predictor
        self.predictor = predictor
        
        # Initialize components
        self.lob = LimitOrderBook(tick_size=tick_size)
        self.feature_extractor = MicrostructureFeatureExtractor()
        
        # State: [mid, inventory, spread, depth_imbalance, ofi, predictor_score, ...]
        # Observation space
        obs_dim = 12 + (1 if use_predictor else 0)  # features + optional predictor
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32
        )
        
        # Action space: [bid_offset, ask_offset, quote_size]
        # Offsets are in ticks (multiples of tick_size)
        self.action_space = spaces.Box(
            low=np.array([0.0, 0.0, 1.0], dtype=np.float32),
            high=np.array([10.0, 10.0, 10.0], dtype=np.float32),
            dtype=np.float32
        )
        
        # Episode state
        self.reset()
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """Reset environment"""
        super().reset(seed=seed)
        
        # Reset LOB
        self.lob = LimitOrderBook(tick_size=self.tick_size)
        
        # Initialize with some synthetic orders
        mid = self.initial_mid
        for i in range(5):
            bid_price = round(mid - (i + 1) * self.tick_size, 2)
            ask_price = round(mid + (i + 1) * self.tick_size, 2)
            
            # Add synthetic orders
            bid_order = Order(
                order_id=f"init_bid_{i}",
                client_id="SYNTHETIC",
                side="buy",
                type="limit",
                price=bid_price,
                size=10
            )
            ask_order = Order(
                order_id=f"init_ask_{i}",
                client_id="SYNTHETIC",
                side="sell",
                type="limit",
                price=ask_price,
                size=10
            )
            self.lob.add_order(bid_order)
            self.lob.add_order(ask_order)
        
        # Agent state
        self.inventory = 0
        self.cash = 0.0
        self.realized_pnl = 0.0
        self.active_orders = {}
        self.t = 0
        
        # Get initial observation
        obs = self._get_observation()
        info = {"inventory": self.inventory, "pnl": self.realized_pnl}
        
        return obs, info
    
    def _get_observation(self) -> np.ndarray:
        """Get current observation"""
        # Get book snapshot
        snapshot = self.lob.get_book_snapshot()
        bids = snapshot["bids"]
        asks = snapshot["asks"]
        
        # Extract features
        features = self.feature_extractor.extract_features(bids, asks)
        feature_vec = self.feature_extractor.get_feature_vector(features)
        
        # Add inventory (normalized)
        inventory_norm = self.inventory / 50.0  # Normalize by max inventory
        
        # Combine features
        obs_list = list(feature_vec) + [inventory_norm]
        
        # Add predictor score if available
        if self.use_predictor and self.predictor is not None:
            predictor_score = self.predictor.predict(feature_vec.reshape(1, -1))
            obs_list.append(predictor_score)
        
        return np.array(obs_list, dtype=np.float32)
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Execute one step"""
        bid_offset, ask_offset, quote_size = action
        
        # Convert offsets to prices
        mid = self.lob.mid_price() or self.initial_mid
        bid_price = round(mid - bid_offset * self.tick_size, 2)
        ask_price = round(mid + ask_offset * self.tick_size, 2)
        quote_size = int(max(1, min(10, quote_size)))
        
        # Cancel old orders
        for order_id in list(self.active_orders.keys()):
            self.lob.cancel_order(order_id)
        self.active_orders.clear()
        
        # Place new quotes
        bid_order = Order(
            order_id=f"rl_bid_{self.t}",
            client_id="RL_AGENT",
            side="buy",
            type="limit",
            price=bid_price,
            size=quote_size
        )
        
        ask_order = Order(
            order_id=f"rl_ask_{self.t}",
            client_id="RL_AGENT",
            side="sell",
            type="limit",
            price=ask_price,
            size=quote_size
        )
        
        fills_bid = self.lob.add_order(bid_order)
        fills_ask = self.lob.add_order(ask_order)
        
        # Track active orders
        if bid_order.status == "active":
            self.active_orders[bid_order.order_id] = bid_order
        if ask_order.status == "active":
            self.active_orders[ask_order.order_id] = ask_order
        
        # Process fills and update inventory/P&L
        for fill in fills_bid + fills_ask:
            if fill.client_id == "RL_AGENT":
                if fill.side == "buy":
                    self.inventory += fill.size
                    self.cash -= fill.price * fill.size
                else:
                    self.inventory -= fill.size
                    self.cash += fill.price * fill.size
        
        # Generate market event (synthetic order flow)
        self._generate_market_event()
        
        # Compute reward
        reward = self._compute_reward()
        
        # Update time
        self.t += 1
        done = self.t >= self.episode_length
        
        # Get next observation
        obs = self._get_observation()
        info = {
            "inventory": self.inventory,
            "pnl": self.realized_pnl,
            "cash": self.cash,
            "t": self.t
        }
        
        return obs, reward, done, False, info
    
    def _generate_market_event(self):
        """Generate synthetic market order to create realistic flow"""
        import random
        
        if random.random() < 0.3:  # 30% chance
            mid = self.lob.mid_price() or self.initial_mid
            side = "buy" if random.random() < 0.5 else "sell"
            size = random.randint(1, 5)
            
            market_order = Order(
                order_id=f"market_{self.t}_{random.randint(0, 1000)}",
                client_id="MARKET",
                side=side,
                type="market",
                size=size
            )
            self.lob.add_order(market_order)
    
    def _compute_reward(self) -> float:
        """
        Reward function for RL
        Combines spread capture, inventory penalty, and P&L
        """
        # Spread capture (simplified - would need to track actual fills)
        spread_reward = 0.0
        
        # Inventory penalty (quadratic)
        inventory_penalty = -0.01 * (self.inventory ** 2)
        
        # P&L component (mark-to-market)
        mid = self.lob.mid_price() or self.initial_mid
        unrealized_pnl = self.inventory * (mid - self.initial_mid)
        pnl_reward = 0.001 * unrealized_pnl
        
        total_reward = spread_reward + inventory_penalty + pnl_reward
        
        return float(total_reward)
    
    def render(self):
        """Render environment state"""
        snapshot = self.lob.get_book_snapshot()
        print(f"Step {self.t}: Mid={snapshot['mid']:.2f}, "
              f"Inventory={self.inventory}, PnL={self.realized_pnl:.2f}")
