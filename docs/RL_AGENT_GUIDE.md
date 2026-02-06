# RL Agent Implementation Guide

## Overview

The platform includes a complete RL (Reinforcement Learning) agent implementation for market making:

1. **RL Environment** (`src/rl/lob_env.py`) - Gym-compatible environment
2. **Training Script** (`scripts/train_rl.py`) - Train PPO agent
3. **RL Strategy** (`src/strategies/rl_mm.py`) - Use trained agent for trading
4. **RL Client** (`src/strategies/rl_strategy_client.py`) - Connect to trading interface

## Quick Start

### 1. Train the RL Agent

```bash
# Basic training
python3 scripts/train_rl.py --episodes 1000 --save-path models/rl_mm_agent

# With microstructure predictor
python3 scripts/train_rl.py --episodes 1000 --use-predictor --save-path models/rl_mm_agent
```

### 2. Run RL Strategy

```bash
# Terminal 1: Start trading interface
python3 scripts/run_interface.py

# Terminal 2: Run RL strategy
python3 scripts/run_rl_strategy.py --model-path models/rl_mm_agent.zip

# Or use the unified script
python3 scripts/run_strategy.py --strategy rl --model-path models/rl_mm_agent.zip
```

## RL Environment Details

### Observation Space

The agent observes:
- **Microstructure features** (12 features):
  - Mid price, spread, relative spread
  - Bid/ask depth, depth imbalance
  - Order flow imbalance (OFI)
  - Returns (1s, 5s)
  - Realized volatility
  - Average volume, mid skew
- **Inventory** (normalized)
- **Predictor score** (optional, if `--use-predictor`)

**Total**: 13-14 features (depending on predictor)

### Action Space

The agent controls:
- **Bid offset** (0-10 ticks from mid)
- **Ask offset** (0-10 ticks from mid)
- **Quote size** (1-10 shares)

### Reward Function

The agent is rewarded for:
- **Spread capture**: Earning the bid-ask spread
- **Inventory management**: Penalty for large inventory (quadratic)
- **P&L**: Mark-to-market unrealized P&L

```
reward = spread_capture - 0.01 * inventory² + 0.001 * unrealized_pnl
```

## Training Process

### Training Configuration

The default PPO configuration:
- **Algorithm**: PPO (Proximal Policy Optimization)
- **Learning rate**: 3e-4
- **Batch size**: 64
- **Gamma**: 0.99 (discount factor)
- **GAE lambda**: 0.95
- **Clip range**: 0.2
- **Entropy coefficient**: 0.01

### Training Tips

1. **Start small**: Train for 100-500 episodes first to verify it works
2. **Monitor rewards**: Watch for increasing rewards over time
3. **Adjust hyperparameters**: If not learning, try different learning rates
4. **Use predictor**: `--use-predictor` can help if you have a trained predictor

### Example Training Session

```bash
# Train for 1000 episodes
python3 scripts/train_rl.py --episodes 1000 --save-path models/rl_mm_agent

# Output:
# Creating RL environment...
# Initializing PPO agent...
# Training for 1000 episodes...
# | 1000/1000000 | ...
# Model saved to models/rl_mm_agent.zip
```

## Using Trained Agent

### Basic Usage

```python
from src.strategies.rl_mm import RLMarketMaker
from src.strategies.rl_strategy_client import RLStrategyClient
import asyncio

# Load trained agent
strategy = RLMarketMaker(
    client_id="rl_mm_1",
    model_path="models/rl_mm_agent.zip"
)

# Connect to trading interface
client = RLStrategyClient(strategy)
await client.run()
```

### Integration with Trading Interface

The RL strategy automatically:
1. Connects to market data WebSocket
2. Extracts microstructure features
3. Gets action from RL agent
4. Submits quotes via REST API
5. Updates inventory from fills

## Performance Evaluation

### Compare Strategies

```python
# Compare RL vs heuristic strategies
from src.strategies.symmetric_mm import SymmetricMarketMaker
from src.strategies.rl_mm import RLMarketMaker

# Run backtest with both
# Compare: P&L, Sharpe ratio, inventory management
```

### Metrics to Track

- **Realized spread**: Actual spread captured
- **Fill rate**: Percentage of quotes filled
- **Inventory management**: Time-weighted average inventory
- **P&L**: Total profit/loss
- **Sharpe ratio**: Risk-adjusted returns

## Advanced: Custom Reward Functions

You can customize the reward function in `src/rl/lob_env.py`:

```python
def _compute_reward(self) -> float:
    # Your custom reward logic
    spread_reward = ...  # Track actual spread capture
    inventory_penalty = ...  # Custom inventory penalty
    pnl_reward = ...  # P&L component
    
    return spread_reward + inventory_penalty + pnl_reward
```

## Troubleshooting

### Agent Not Learning

1. **Check reward scale**: Rewards might be too small/large
2. **Adjust learning rate**: Try 1e-4 or 1e-3
3. **Increase training**: Train for more episodes
4. **Feature normalization**: Ensure features are normalized

### Model Not Loading

```bash
# Check model file exists
ls -lh models/rl_mm_agent.zip

# Verify it's a valid model
python3 -c "from stable_baselines3 import PPO; PPO.load('models/rl_mm_agent.zip')"
```

### Poor Performance

1. **Train longer**: RL needs many episodes
2. **Tune hyperparameters**: Learning rate, batch size, etc.
3. **Add predictor**: Use `--use-predictor` if available
4. **Adjust reward function**: Make rewards more informative

## Next Steps

1. **Train on real data**: Use historical tick data for training
2. **Hyperparameter tuning**: Optimize PPO parameters
3. **Multi-agent**: Train multiple agents for different market conditions
4. **Transfer learning**: Fine-tune pre-trained models
5. **Ensemble**: Combine multiple RL agents

## References

- **Stable-Baselines3**: https://stable-baselines3.readthedocs.io/
- **PPO Paper**: "Proximal Policy Optimization Algorithms" (Schulman et al., 2017)
- **RL Environment**: `src/rl/lob_env.py`
- **Training Script**: `scripts/train_rl.py`
