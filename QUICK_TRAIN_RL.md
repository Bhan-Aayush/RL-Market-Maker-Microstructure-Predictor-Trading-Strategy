# Quick Guide: Training RL Market-Making Agent

## Quick Start

### 1. Train a Basic Model (100 episodes - ~1-2 minutes)
```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate
python scripts/train_rl.py --episodes 100 --save-path models/rl_mm_agent
```

### 2. Train with Microstructure Predictor (better performance)
```bash
python scripts/train_rl.py --episodes 100 --save-path models/rl_mm_agent --use-predictor
```

### 3. Train for Production (1000+ episodes - ~10-20 minutes)
```bash
python scripts/train_rl.py --episodes 1000 --save-path models/rl_mm_agent --use-predictor
```

## What Happens

1. **Environment Creation**: Creates a LOB market-making environment
2. **Agent Training**: PPO agent learns optimal quoting strategy
3. **Model Saving**: Trained model saved to `models/rl_mm_agent.zip`
4. **Testing**: Agent is tested on sample episodes

## Using the Trained Model

Once trained, the model will appear in the dashboard's RL strategy tab:

1. Go to **Market-Making Strategies** → **RL-Based MM** tab
2. Select the model from the dropdown (or enter path: `models/rl_mm_agent.zip`)
3. Check "Use Pretrained Model"
4. Click "Start Strategy"

## Training Parameters

- **Episodes**: Number of training episodes (100 = quick test, 1000+ = production)
- **Save Path**: Where to save the model (default: `models/rl_mm_agent`)
- **Use Predictor**: Include microstructure predictor in observations (recommended)

## Expected Output

```
Creating RL environment...
Initializing PPO agent...
Training for 100 episodes...
----------------------------------
| rollout/           |          |
| time/              |          |
| fps                |          |
| iterations         |          |
| time_elapsed       |          |
| total_timesteps    |          |
----------------------------------
Model saved to models/rl_mm_agent
Testing trained agent...
Step: 0, Inventory: 0, PnL: 0.00
...
```

## Troubleshooting

**Error: "No module named 'stable_baselines3'"**
```bash
pip install stable-baselines3
```

**Error: "Model file not found"**
- Make sure you've trained a model first
- Check that `models/rl_mm_agent.zip` exists

**Training is slow**
- Reduce episodes for testing (e.g., `--episodes 50`)
- Training time scales roughly linearly with episodes

## Next Steps

After training:
1. Test the model in the dashboard
2. Use it with `StrategyClient` in your trading scripts
3. Monitor performance and retrain if needed
