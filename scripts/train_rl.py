#!/usr/bin/env python3
"""
Train RL agent for market making
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from src.rl.lob_env import LOBMarketMakingEnv
import argparse


def main():
    parser = argparse.ArgumentParser(description="Train RL market-making agent")
    parser.add_argument("--episodes", type=int, default=1000,
                       help="Number of training episodes")
    parser.add_argument("--save-path", type=str, default="models/rl_mm_agent",
                       help="Path to save trained model")
    parser.add_argument("--use-predictor", action="store_true",
                       help="Use microstructure predictor in observations")
    
    args = parser.parse_args()
    
    print("Creating RL environment...")
    
    # Create environment
    env = LOBMarketMakingEnv(
        episode_length=1000,
        initial_mid=100.0,
        use_predictor=args.use_predictor
    )
    
    # Create vectorized environment for faster training
    vec_env = make_vec_env(lambda: env, n_envs=4)
    
    print("Initializing PPO agent...")
    
    # Create PPO agent
    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01
    )
    
    print(f"Training for {args.episodes} episodes...")
    
    # Train
    model.learn(total_timesteps=args.episodes * 1000)
    
    # Save model
    os.makedirs(os.path.dirname(args.save_path), exist_ok=True)
    model.save(args.save_path)
    
    print(f"Model saved to {args.save_path}")
    
    # Test the trained agent
    print("\nTesting trained agent...")
    obs = env.reset()
    for _ in range(100):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = env.step(action)
        if done or truncated:
            obs = env.reset()
        print(f"Step: {info.get('t', 0)}, Inventory: {info.get('inventory', 0)}, PnL: {info.get('pnl', 0):.2f}")


if __name__ == "__main__":
    main()
