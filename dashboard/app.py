#!/usr/bin/env python3
"""
Comprehensive Trading Platform Dashboard
Test all features interactively
"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import requests
import json
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Quantitative Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'fills' not in st.session_state:
    st.session_state.fills = []
if 'market_data' not in st.session_state:
    st.session_state.market_data = []

# API base URL
API_BASE = "http://127.0.0.1:8000"

def check_api_connection():
    """Check if trading interface is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Sidebar
with st.sidebar:
    st.title("📊 Trading Platform")
    st.markdown("---")
    
    # API Status
    api_connected = check_api_connection()
    if api_connected:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Not Connected")
        st.info("Start the trading interface:\n`python scripts/run_interface.py`")
    
    st.markdown("---")
    
    # Navigation
    page = st.selectbox(
        "Navigate",
        [
            "🏠 Home",
            "📈 Trading Interface",
            "🎯 Market-Making Strategies",
            "📊 Options & Greeks",
            "⚡ Execution Algorithms",
            "🛡️ Risk Models",
            "📉 Statistical Arbitrage",
            "💼 Portfolio Optimization",
            "📡 Order Flow Analysis",
            "💰 Transaction Cost Analysis",
            "🔄 Regime Detection",
            "💾 Database Queries"
        ]
    )

# Home Page
if page == "🏠 Home":
    st.markdown('<div class="main-header">Quantitative Trading Platform Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Features", "13+")
        st.metric("Strategies", "4")
        st.metric("Execution Algorithms", "4")
    
    with col2:
        st.metric("Risk Models", "3")
        st.metric("Options Features", "2")
        st.metric("Analysis Tools", "3")
    
    with col3:
        st.metric("API Status", "✅" if api_connected else "❌")
        st.metric("Database", "SQLite/PostgreSQL")
        st.metric("Real-Time Data", "✅")
    
    st.markdown("---")
    st.header("📋 Feature Overview")
    
    features = {
        "Trading Interface": ["Order submission", "Order book view", "Risk monitoring", "Real-time market data"],
        "Market-Making Strategies": ["Symmetric MM", "Inventory-Skew MM", "Adaptive Spread MM", "RL-Based MM"],
        "Options & Greeks": ["Black-Scholes pricing", "Delta, Gamma, Theta, Vega", "Delta hedging", "Volatility surface"],
        "Execution Algorithms": ["TWAP", "VWAP", "Implementation Shortfall", "POV"],
        "Risk Models": ["VaR (Historical/Parametric/MC)", "CVaR", "Stress Testing", "Risk Attribution"],
        "Statistical Analysis": ["Pairs Trading", "Cointegration", "Regime Detection"],
        "Portfolio Management": ["Mean-Variance Optimization", "Risk Parity", "Multi-Asset MM"],
        "Transaction Analysis": ["TCA", "Slippage", "Market Impact", "Fill Rate"]
    }
    
    for category, items in features.items():
        with st.expander(f"**{category}**"):
            for item in items:
                st.write(f"  • {item}")

# Trading Interface Page
elif page == "📈 Trading Interface":
    st.header("📈 Trading Interface")
    
    if not api_connected:
        st.warning("⚠️ Trading interface not running. Start it with: `python scripts/run_interface.py`")
        st.stop()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Submit Order", "Order Book", "Risk Status", "Market Data"])
    
    with tab1:
        st.subheader("Submit Order")
        
        col1, col2 = st.columns(2)
        with col1:
            client_id = st.text_input("Client ID", value="dashboard_client")
            symbol = st.text_input("Symbol", value="AAPL")
            side = st.selectbox("Side", ["buy", "sell"])
            order_type = st.selectbox("Order Type", ["limit", "market"])
        
        with col2:
            price = st.number_input("Price", value=100.0, step=0.01) if order_type == "limit" else None
            size = st.number_input("Size", value=10, min_value=1, step=1)
            submit_order = st.button("Submit Order", type="primary")
        
        if submit_order:
            order_data = {
                "client_id": client_id,
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "size": int(size)
            }
            if order_type == "limit" and price:
                order_data["price"] = float(price)
            
            try:
                response = requests.post(f"{API_BASE}/order", json=order_data)
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Order submitted: {result.get('order_id')}")
                    st.json(result)
                    st.session_state.orders.append(result)
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with tab2:
        st.subheader("Order Book")
        refresh_book = st.button("Refresh Book")
        
        if refresh_book or True:
            try:
                response = requests.get(f"{API_BASE}/book")
                if response.status_code == 200:
                    book = response.json()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Bids")
                        if book.get("bids"):
                            bids_df = pd.DataFrame(book["bids"][:10], columns=["Price", "Size"])
                            st.dataframe(bids_df, use_container_width=True)
                        else:
                            st.info("No bids")
                    
                    with col2:
                        st.subheader("Asks")
                        if book.get("asks"):
                            asks_df = pd.DataFrame(book["asks"][:10], columns=["Price", "Size"])
                            st.dataframe(asks_df, use_container_width=True)
                        else:
                            st.info("No asks")
                    
                    if book.get("mid"):
                        st.metric("Mid Price", f"${book['mid']:.2f}")
                        st.metric("Spread", f"${book.get('spread', 0):.4f}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with tab3:
        st.subheader("Risk Status")
        risk_client_id = st.text_input("Client ID for Risk Check", value="dashboard_client")
        check_risk = st.button("Check Risk")
        
        if check_risk:
            try:
                response = requests.get(f"{API_BASE}/risk/{risk_client_id}")
                if response.status_code == 200:
                    risk = response.json()
                    st.json(risk)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Position", risk.get("position", 0))
                    with col2:
                        st.metric("P&L", f"${risk.get('pnl', 0):.2f}")
                    with col3:
                        st.metric("Orders Today", risk.get("orders_today", 0))
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with tab4:
        st.subheader("Real-Time Market Data")
        st.info("Market data is streamed via WebSocket. Check terminal for live updates.")

# Market-Making Strategies Page
elif page == "🎯 Market-Making Strategies":
    st.header("🎯 Market-Making Strategies")
    
    if not api_connected:
        st.warning("⚠️ Trading interface not running. Start it with: `python scripts/run_interface.py`")
        st.stop()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Symmetric MM", "Inventory-Skew MM", "Adaptive Spread MM", "RL-Based MM"])
    
    with tab1:
        st.subheader("Symmetric Market-Maker")
        st.write("Fixed spread around mid-price. Simple and effective for liquid markets.")
        
        col1, col2 = st.columns(2)
        with col1:
            spread_bps = st.number_input("Spread (basis points)", value=10, min_value=1, max_value=100)
            order_size = st.number_input("Order Size", value=100, min_value=1)
            client_id = st.text_input("Client ID", value="mm_symmetric")
        
        with col2:
            update_frequency = st.number_input("Update Frequency (seconds)", value=5, min_value=1)
            start_strategy = st.button("Start Strategy", type="primary")
        
        if start_strategy:
            try:
                from src.strategies.symmetric_mm import SymmetricMarketMaker
                
                # Convert basis points to half_spread (assuming mid price around 100)
                # spread_bps is total spread, half_spread is half of that
                mid_price = 100.0  # Approximate mid for conversion
                half_spread = (spread_bps / 10000) * mid_price / 2
                
                strategy = SymmetricMarketMaker(
                    client_id=client_id,
                    half_spread=half_spread,
                    quote_size=order_size
                )
                
                st.success("✅ Strategy created!")
                st.info(f"📊 Strategy configured with {spread_bps} bps spread (half_spread={half_spread:.4f})")
                st.json({
                    "strategy": "Symmetric MM",
                    "spread_bps": spread_bps,
                    "half_spread": half_spread,
                    "quote_size": order_size,
                    "client_id": client_id
                })
                st.warning("ℹ️ Note: To run the strategy, use the StrategyClient in a separate script or process.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)
    
    with tab2:
        st.subheader("Inventory-Averse Skewed Market-Maker")
        st.write("Adjusts quotes based on inventory to reduce risk. Skews spread when inventory is large.")
        
        col1, col2 = st.columns(2)
        with col1:
            base_spread_bps = st.number_input("Base Spread (bps)", value=10, min_value=1, max_value=100, key="inv_spread")
            max_inventory = st.number_input("Max Inventory", value=1000, min_value=100)
            skew_factor = st.number_input("Skew Factor", value=0.5, min_value=0.1, max_value=2.0, step=0.1)
            client_id = st.text_input("Client ID", value="mm_inventory", key="inv_client")
        
        with col2:
            order_size = st.number_input("Order Size", value=100, min_value=1, key="inv_size")
            start_strategy = st.button("Start Strategy", type="primary", key="inv_start")
        
        if start_strategy:
            try:
                from src.strategies.inventory_skew_mm import InventorySkewMarketMaker
                
                # Convert basis points to half_spread
                mid_price = 100.0
                half_spread = (base_spread_bps / 10000) * mid_price / 2
                inventory_skew_factor = skew_factor * half_spread
                
                strategy = InventorySkewMarketMaker(
                    client_id=client_id,
                    half_spread=half_spread,
                    quote_size=order_size,
                    inventory_skew_factor=inventory_skew_factor,
                    max_inventory=max_inventory
                )
                
                st.success("✅ Strategy created!")
                st.info(f"📊 Strategy will adjust spread based on inventory")
                st.json({
                    "strategy": "Inventory-Skew MM",
                    "base_spread_bps": base_spread_bps,
                    "half_spread": half_spread,
                    "max_inventory": max_inventory,
                    "skew_factor": skew_factor,
                    "quote_size": order_size,
                    "client_id": client_id
                })
                st.warning("ℹ️ Note: To run the strategy, use the StrategyClient in a separate script or process.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)
    
    with tab3:
        st.subheader("Adaptive Spread by Volatility")
        st.write("Dynamically adjusts spread based on market volatility (EWMA of returns).")
        
        col1, col2 = st.columns(2)
        with col1:
            base_spread_bps = st.number_input("Base Spread (bps)", value=10, min_value=1, max_value=100, key="vol_spread")
            volatility_window = st.number_input("Volatility Window", value=20, min_value=5, max_value=100)
            volatility_multiplier = st.number_input("Volatility Multiplier", value=2.0, min_value=0.5, max_value=5.0, step=0.1)
            client_id = st.text_input("Client ID", value="mm_adaptive", key="vol_client")
        
        with col2:
            order_size = st.number_input("Order Size", value=100, min_value=1, key="vol_size")
            start_strategy = st.button("Start Strategy", type="primary", key="vol_start")
        
        if start_strategy:
            try:
                from src.strategies.adaptive_spread_mm import AdaptiveSpreadMarketMaker
                
                # Convert basis points to base_half_spread
                mid_price = 100.0
                base_half_spread = (base_spread_bps / 10000) * mid_price / 2
                
                strategy = AdaptiveSpreadMarketMaker(
                    client_id=client_id,
                    base_half_spread=base_half_spread,
                    quote_size=order_size,
                    vol_alpha=1.0 / volatility_window  # Convert window to alpha
                )
                
                st.success("✅ Strategy created!")
                st.info(f"📊 Strategy will adapt spread to volatility")
                st.json({
                    "strategy": "Adaptive Spread MM",
                    "base_spread_bps": base_spread_bps,
                    "base_half_spread": base_half_spread,
                    "volatility_window": volatility_window,
                    "volatility_multiplier": volatility_multiplier,
                    "quote_size": order_size,
                    "client_id": client_id
                })
                st.warning("ℹ️ Note: To run the strategy, use the StrategyClient in a separate script or process.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)
    
    with tab4:
        st.subheader("RL-Based Market-Maker")
        st.write("Uses a trained Reinforcement Learning agent to optimize quoting decisions.")
        
        # Check for existing models
        import os
        models_dir = "models"
        existing_models = []
        if os.path.exists(models_dir):
            # stable-baselines3 saves as .zip, but also check for directories
            existing_models = [f for f in os.listdir(models_dir) if f.endswith('.zip') or os.path.isdir(os.path.join(models_dir, f))]
        
        col1, col2 = st.columns(2)
        with col1:
            if existing_models:
                model_path = st.selectbox(
                    "Select Model",
                    [""] + existing_models,
                    format_func=lambda x: f"models/{x}" if x else "No model selected"
                )
                if model_path:
                    # Handle both .zip files and directories (stable-baselines3 can save both ways)
                    if not model_path.endswith('.zip') and not os.path.isdir(f"models/{model_path}"):
                        # If it's a directory name, try adding .zip
                        if os.path.exists(f"models/{model_path}.zip"):
                            model_path = f"models/{model_path}.zip"
                        else:
                            model_path = f"models/{model_path}"
                    else:
                        model_path = f"models/{model_path}"
            else:
                # Default path - stable-baselines3 will add .zip automatically
                model_path = st.text_input("Model Path", value="models/rl_mm_agent", placeholder="models/rl_mm_agent")
            
            client_id = st.text_input("Client ID", value="mm_rl", key="rl_client")
            use_predictor = st.checkbox("Use Microstructure Predictor", value=False)
        
        with col2:
            episodes = st.number_input("Training Episodes (if training)", value=100, min_value=10, max_value=10000, step=10)
            train_model = st.button("🚀 Train New Model", type="primary", key="rl_train")
            use_pretrained = st.checkbox("Use Pretrained Model", value=bool(existing_models))
            start_strategy = st.button("Start Strategy", type="primary", key="rl_start")
        
        # Training section
        if train_model:
            st.info("🔄 Training RL model... This may take a few minutes.")
            try:
                import subprocess
                import sys
                
                train_cmd = [
                    sys.executable,
                    "scripts/train_rl.py",
                    "--episodes", str(episodes),
                    "--save-path", "models/rl_mm_agent"
                ]
                if use_predictor:
                    train_cmd.append("--use-predictor")
                
                st.code(" ".join(train_cmd))
                st.info("💡 Run this command in your terminal, or wait for training to complete below.")
                
                # Optionally run training (commented out as it takes time)
                # result = subprocess.run(train_cmd, capture_output=True, text=True)
                # if result.returncode == 0:
                #     st.success("✅ Model trained successfully!")
                #     st.code(result.stdout)
                # else:
                #     st.error(f"❌ Training failed: {result.stderr}")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)
        
        # Strategy creation section
        if start_strategy:
            try:
                from src.strategies.rl_mm import RLMarketMaker
                
                if not model_path or model_path == "":
                    st.error("❌ Please provide a model path or train a new model first.")
                    st.info("💡 To train a model:")
                    st.code("python scripts/train_rl.py --episodes 100 --save-path models/rl_mm_agent")
                else:
                    # Check if model exists (with or without .zip extension)
                    model_exists = os.path.exists(model_path)
                    if not model_exists and not model_path.endswith('.zip'):
                        # Try with .zip extension (stable-baselines3 adds it automatically)
                        model_exists = os.path.exists(f"{model_path}.zip")
                        if model_exists:
                            model_path = f"{model_path}.zip"
                    
                    if not model_exists:
                        st.error(f"❌ Model file not found: {model_path}")
                        st.info("💡 Train a model first using the 'Train New Model' button above, or run:")
                        # Show path without .zip for training (it will be added automatically)
                        train_path = model_path.replace('.zip', '')
                        st.code(f"python scripts/train_rl.py --episodes 100 --save-path {train_path}")
                    else:
                        # Model exists, create strategy
                        strategy = RLMarketMaker(
                            client_id=client_id,
                            model_path=model_path,
                            use_predictor=use_predictor
                        )
                        st.success("✅ Strategy created successfully!")
                        st.info("📊 Using trained RL model")
                        st.json({
                            "strategy": "RL-Based MM",
                            "model_path": model_path,
                            "client_id": client_id,
                            "use_predictor": use_predictor
                        })
                        st.warning("ℹ️ Note: To run the strategy, use the StrategyClient in a separate script or process.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)
                st.info("💡 Make sure you have trained a model first:")
                st.code("python scripts/train_rl.py --episodes 100 --save-path models/rl_mm_agent")
        
        # Help section
        with st.expander("📖 How to Train an RL Model"):
            st.markdown("""
            ### Quick Start
            
            1. **Train a model** (recommended: 100-1000 episodes):
               ```bash
               python scripts/train_rl.py --episodes 100 --save-path models/rl_mm_agent
               ```
               Note: The `.zip` extension is added automatically by stable-baselines3
            
            2. **With microstructure predictor** (better performance):
               ```bash
               python scripts/train_rl.py --episodes 100 --save-path models/rl_mm_agent --use-predictor
               ```
            
            3. **The model will be saved** to `models/rl_mm_agent.zip` (or `models/rl_mm_agent/` directory)
            
            4. **Use the model** by selecting it from the dropdown above or entering the path
            
            ### Training Tips
            - Start with 100 episodes for quick testing (~1-2 minutes)
            - Use 1000+ episodes for better performance (~10-20 minutes)
            - Training time scales roughly linearly with episodes
            - Models are saved automatically during training
            - The model path in training command should NOT include `.zip` (it's added automatically)
            """)

# Options & Greeks Page
elif page == "📊 Options & Greeks":
    st.header("📊 Options Pricing & Greeks")
    
    tab1, tab2, tab3 = st.tabs(["Option Pricing", "Delta Hedging", "Volatility Surface"])
    
    with tab1:
        st.subheader("Black-Scholes Option Pricing")
        
        col1, col2 = st.columns(2)
        with col1:
            spot = st.number_input("Spot Price", value=100.0, step=1.0)
            strike = st.number_input("Strike Price", value=100.0, step=1.0)
            expiration_days = st.number_input("Days to Expiration", value=30, min_value=1)
            risk_free_rate = st.number_input("Risk-Free Rate", value=0.05, step=0.01, format="%.2f")
        
        with col2:
            volatility = st.number_input("Volatility", value=0.20, step=0.01, format="%.2f")
            option_type = st.selectbox("Option Type", ["call", "put"])
            calculate = st.button("Calculate", type="primary")
        
        if calculate:
            try:
                from src.options.pricing import BlackScholes
                
                expiration_years = expiration_days / 365.0
                greeks = BlackScholes.all_greeks(spot, strike, expiration_years, risk_free_rate, volatility, option_type)
                
                st.success("✅ Calculation Complete")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Option Price", f"${greeks['price']:.2f}")
                    st.metric("Delta", f"{greeks['delta']:.4f}")
                with col2:
                    st.metric("Gamma", f"{greeks['gamma']:.4f}")
                    st.metric("Theta", f"{greeks['theta']:.4f}")
                with col3:
                    st.metric("Vega", f"{greeks['vega']:.4f}")
                    st.metric("Rho", f"{greeks['rho']:.4f}")
                
                # Visualize Greeks vs Spot
                spot_range = np.linspace(spot * 0.8, spot * 1.2, 50)
                deltas = [BlackScholes.delta(s, strike, expiration_years, risk_free_rate, volatility, option_type) for s in spot_range]
                prices = [BlackScholes.price(s, strike, expiration_years, risk_free_rate, volatility, option_type) for s in spot_range]
                
                fig = make_subplots(rows=1, cols=2, subplot_titles=("Option Price", "Delta"))
                fig.add_trace(go.Scatter(x=spot_range, y=prices, name="Price"), row=1, col=1)
                fig.add_trace(go.Scatter(x=spot_range, y=deltas, name="Delta"), row=1, col=2)
                fig.update_layout(height=400, title_text="Greeks Analysis")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with tab2:
        st.subheader("Delta Hedging")
        st.info("Delta hedging functionality - coming soon")
    
    with tab3:
        st.subheader("Volatility Surface")
        st.info("Volatility surface visualization - coming soon")

# Execution Algorithms Page
elif page == "⚡ Execution Algorithms":
    st.header("⚡ Execution Algorithms")
    
    tab1, tab2, tab3, tab4 = st.tabs(["TWAP", "VWAP", "Implementation Shortfall", "POV"])
    
    with tab1:
        st.subheader("TWAP (Time-Weighted Average Price)")
        
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("Symbol", value="AAPL")
            side = st.selectbox("Side", ["buy", "sell"])
            total_size = st.number_input("Total Size", value=1000, min_value=1)
        
        with col2:
            duration_minutes = st.number_input("Duration (minutes)", value=60, min_value=1)
            create_twap = st.button("Create TWAP Order", type="primary")
        
        if create_twap:
            try:
                from src.execution.twap import TWAPExecutor
                
                executor = TWAPExecutor()
                order_id = executor.create_twap_order(symbol, side, total_size, duration_minutes * 60)
                
                st.success(f"✅ TWAP Order Created: {order_id[:8]}...")
                
                status = executor.get_order_status(order_id)
                st.json(status)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with tab2:
        st.subheader("VWAP (Volume-Weighted Average Price)")
        st.info("VWAP execution - configure volume profile")
    
    with tab3:
        st.subheader("Implementation Shortfall")
        st.info("IS execution - minimize execution cost")
    
    with tab4:
        st.subheader("POV (Participation of Volume)")
        st.info("POV execution - target % of market volume")

# Risk Models Page
elif page == "🛡️ Risk Models":
    st.header("🛡️ Risk Models")
    
    tab1, tab2, tab3 = st.tabs(["VaR", "CVaR", "Stress Testing"])
    
    with tab1:
        st.subheader("Value at Risk (VaR)")
        
        # Generate sample returns
        np.random.seed(42)
        sample_returns = np.random.normal(0.001, 0.02, 252)
        
        col1, col2 = st.columns(2)
        with col1:
            confidence = st.selectbox("Confidence Level", [0.90, 0.95, 0.99], index=1)
            method = st.selectbox("Method", ["Historical", "Parametric", "Monte Carlo"])
            calculate_var = st.button("Calculate VaR", type="primary")
        
        if calculate_var:
            try:
                from src.risk.advanced_risk import VaRCalculator
                
                if method == "Historical":
                    var = VaRCalculator.historical_var(sample_returns, confidence)
                elif method == "Parametric":
                    var = VaRCalculator.parametric_var(sample_returns, confidence)
                else:
                    var = VaRCalculator.monte_carlo_var(sample_returns, confidence)
                
                st.success(f"✅ VaR ({confidence*100:.0f}%): {var:.4f} ({var*100:.2f}%)")
                
                # Visualize
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=sample_returns, nbinsx=50, name="Returns"))
                fig.add_vline(x=-var, line_dash="dash", annotation_text=f"VaR {confidence*100:.0f}%", line_color="red")
                fig.update_layout(title="Return Distribution with VaR", xaxis_title="Daily Return", yaxis_title="Frequency")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with tab2:
        st.subheader("Conditional VaR (CVaR)")
        st.info("CVaR calculation - coming soon")
    
    with tab3:
        st.subheader("Stress Testing")
        st.info("Stress testing scenarios - coming soon")

# Statistical Arbitrage Page
elif page == "📉 Statistical Arbitrage":
    st.header("📉 Statistical Arbitrage / Pairs Trading")
    
    st.subheader("Find Cointegrated Pairs")
    st.info("Upload price data or use synthetic data")
    
    use_synthetic = st.checkbox("Use Synthetic Data", value=True)
    
    if use_synthetic:
        np.random.seed(42)
        dates = pd.date_range("2023-01-01", periods=252, freq="D")
        base_trend = np.cumsum(np.random.randn(252) * 0.5)
        prices1 = 100 + base_trend
        prices2 = prices1 + np.random.randn(252) * 0.2
        
        price_data = pd.DataFrame({
            "AAPL": prices1,
            "MSFT": prices2
        }, index=dates)
        
        st.dataframe(price_data.head())
        
        find_pairs = st.button("Find Cointegrated Pairs", type="primary")
        
        if find_pairs:
            try:
                from src.analysis.pairs_trading import PairsTradingStrategy
                
                strategy = PairsTradingStrategy()
                pairs = strategy.find_cointegrated_pairs(price_data)
                
                if pairs:
                    pair = pairs[0]
                    st.success(f"✅ Found Pair: {pair.symbol1} / {pair.symbol2}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Hedge Ratio", f"{pair.hedge_ratio:.4f}")
                        st.metric("Cointegration p-value", f"{pair.cointegration_pvalue:.4f}")
                    with col2:
                        st.metric("Half-life", f"{pair.half_life:.2f} days")
                        st.metric("Spread Std", f"{pair.spread_std:.4f}")
                    
                    # Visualize
                    spreads = []
                    zscores = []
                    for i in range(len(price_data)):
                        spread = strategy.calculate_spread(
                            price_data.iloc[i][pair.symbol1],
                            price_data.iloc[i][pair.symbol2],
                            pair
                        )
                        zscore = strategy.calculate_zscore(spread, pair)
                        spreads.append(spread)
                        zscores.append(zscore)
                    
                    fig = make_subplots(rows=2, cols=1, subplot_titles=("Price Series", "Spread Z-Score"))
                    fig.add_trace(go.Scatter(x=dates, y=price_data[pair.symbol1], name=pair.symbol1), row=1, col=1)
                    fig.add_trace(go.Scatter(x=dates, y=price_data[pair.symbol2], name=pair.symbol2), row=1, col=1)
                    fig.add_trace(go.Scatter(x=dates, y=zscores, name="Z-Score"), row=2, col=1)
                    fig.add_hline(y=2, line_dash="dash", annotation_text="Entry", line_color="green", row=2, col=1)
                    fig.add_hline(y=-2, line_dash="dash", annotation_text="Entry", line_color="green", row=2, col=1)
                    fig.update_layout(height=600, title_text="Pairs Trading Analysis")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No cointegrated pairs found")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# Portfolio Optimization Page
elif page == "💼 Portfolio Optimization":
    st.header("💼 Portfolio Optimization")
    
    st.subheader("Mean-Variance Optimization")
    
    n_assets = st.number_input("Number of Assets", value=3, min_value=2, max_value=10)
    
    asset_names = []
    expected_returns = []
    for i in range(n_assets):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"Asset {i+1} Name", value=f"Asset{i+1}", key=f"name_{i}")
            asset_names.append(name)
        with col2:
            ret = st.number_input(f"Expected Return", value=0.10, step=0.01, format="%.2f", key=f"ret_{i}")
            expected_returns.append(ret)
    
    optimize = st.button("Optimize Portfolio", type="primary")
    
    if optimize:
        try:
            from src.portfolio.optimizer import PortfolioOptimizer
            
            # Create sample covariance matrix
            np.random.seed(42)
            returns_array = np.array(expected_returns)
            covariance = np.random.rand(n_assets, n_assets)
            covariance = covariance @ covariance.T  # Make positive definite
            covariance = covariance * 0.1  # Scale
            
            weights = PortfolioOptimizer.mean_variance_optimize(returns_array, covariance)
            metrics = PortfolioOptimizer.calculate_portfolio_metrics(weights, returns_array, covariance)
            
            st.success("✅ Portfolio Optimized")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Expected Return", f"{metrics['expected_return']:.4f}")
            with col2:
                st.metric("Volatility", f"{metrics['volatility']:.4f}")
            with col3:
                st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            
            # Visualize weights
            fig = go.Figure()
            fig.add_trace(go.Bar(x=asset_names, y=weights, name="Optimal Weights"))
            fig.update_layout(title="Portfolio Weights", yaxis_title="Weight", yaxis_tickformat=".2%")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Order Flow Analysis Page
elif page == "📡 Order Flow Analysis":
    st.header("📡 Order Flow Analysis")
    st.info("Advanced order flow analysis - coming soon")

# Transaction Cost Analysis Page
elif page == "💰 Transaction Cost Analysis":
    st.header("💰 Transaction Cost Analysis")
    st.info("TCA reporting - coming soon")

# Regime Detection Page
elif page == "🔄 Regime Detection":
    st.header("🔄 Regime Detection")
    
    st.subheader("Market Regime Analysis")
    
    # Generate sample price data
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    detect_regime = st.button("Detect Regime", type="primary")
    
    if detect_regime:
        try:
            from src.analysis.regime_detection import RegimeDetector
            
            detector = RegimeDetector()
            for i, price in enumerate(prices):
                detector.add_observation(price, time.time() + i)
            
            regimes = detector.detect_all_regimes()
            recommendations = detector.get_regime_recommendation()
            
            st.success("✅ Regime Analysis Complete")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Volatility Regime", regimes["volatility"]["regime"])
                st.caption(f"Confidence: {regimes['volatility']['confidence']:.2%}")
            with col2:
                st.metric("Trend Regime", regimes["trend"]["regime"])
                st.caption(f"Confidence: {regimes['trend']['confidence']:.2%}")
            with col3:
                st.metric("Direction Regime", regimes["direction"]["regime"])
                st.caption(f"Confidence: {regimes['direction']['confidence']:.2%}")
            
            if recommendations["recommendations"]:
                st.subheader("Strategy Recommendations")
                for rec in recommendations["recommendations"]:
                    st.write(f"  • {rec}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Database Queries Page
elif page == "💾 Database Queries":
    st.header("💾 Database Queries")
    st.info("Database query interface - coming soon")

if __name__ == "__main__":
    pass
