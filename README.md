# Proprietary Trading Platform: RL Market-Maker + Microstructure Predictor

A complete proprietary trading interface and market-making system that combines:
- **Limit Order Book (LOB)** and matching engine
- **REST + WebSocket** trading APIs
- **Multiple market-making strategies** (symmetric, inventory-skew, adaptive spread)
- **Microstructure feature extraction** and short-term prediction
- **Reinforcement Learning** environment for optimal quoting
- **Backtest/replay** system for strategy validation
- **Risk controls** and performance metrics

## 🎯 Project Overview

This is a production-style proprietary trading platform designed for research, strategy development, and demonstrating expertise in:
- **Systems Engineering**: Low-latency interfaces, order lifecycle, matching engines
- **Quantitative Trading**: Market microstructure, order flow, inventory management
- **Machine Learning**: Short-term prediction, RL-based execution optimization

**Asset Class**: The platform is **asset-agnostic** and works for both **equities** and **commodities** (listed futures). Default configuration is optimized for equities, but can be easily adapted for commodities. See `docs/ASSET_CLASS_CONFIG.md` for details.

### Architecture

```
┌─────────────────┐
│  Strategy       │
│  (MM/RL Agent)  │
└────────┬────────┘
         │ REST + WebSocket
         ▼
┌─────────────────┐
│ Trading         │
│ Interface       │
│ (FastAPI)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Matching Engine │◄─────┤ Risk Manager│
│ (LOB)           │      └──────────────┘
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Market Data     │
│ Feed            │
└─────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd RL-Market-Maker-Microstructure-Predictor-Trading-Strategy

# Install dependencies
# On macOS, use pip3 instead of pip
pip3 install -r requirements.txt
# Or on Linux/Windows:
pip install -r requirements.txt
```

### Run the Trading Interface

```bash
# Terminal 1: Start the trading interface server
# On macOS, use python3; on Linux/Windows, use python

# With synthetic data (default)
python3 scripts/run_interface.py

# With real Yahoo Finance data (free, no API key needed)
python3 scripts/run_interface.py --data-source yahoo --symbol AAPL

# With Alpha Vantage (requires API key)
python3 scripts/run_interface.py --data-source alphavantage --symbol AAPL --api-key YOUR_KEY
```

The interface will be available at:
- **API Server**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **WebSocket MD**: ws://127.0.0.1:8000/ws/md
- **WebSocket Fills**: ws://127.0.0.1:8000/ws/fills/{client_id}

### Run a Market-Making Strategy

```bash
# Terminal 2: Run a strategy
python3 scripts/run_strategy.py --strategy symmetric --client-id mm_1

# Or try inventory-skew strategy
python3 scripts/run_strategy.py --strategy inventory_skew --half-spread 0.06

# Or adaptive spread strategy
python3 scripts/run_strategy.py --strategy adaptive --quote-interval 0.3
```

### Train RL Agent

```bash
# Train RL agent
python3 scripts/train_rl.py --episodes 1000 --save-path models/rl_mm_agent

# Run RL-based strategy (after training)
python3 scripts/run_rl_strategy.py --model-path models/rl_mm_agent.zip
```

## 📁 Project Structure

```
.
├── src/
│   ├── lob/              # Limit Order Book and matching engine
│   ├── interface/        # Trading interface (REST + WebSocket)
│   ├── strategies/       # Market-making strategies
│   ├── features/         # Microstructure feature extraction
│   ├── predictor/        # Short-term prediction models
│   ├── rl/              # RL environment for market making
│   ├── backtest/        # Backtest and replay system
│   ├── risk/            # Risk management
│   └── metrics/         # Performance analytics
├── scripts/             # Entry point scripts
├── notebooks/           # Analysis and visualization notebooks
├── models/              # Trained models (RL, predictors)
└── requirements.txt    # Python dependencies
```

## 🔧 Core Components

### 1. Limit Order Book (LOB)

- Price-time priority matching
- Partial fills support
- Market and limit orders
- Real-time book snapshots (L1/L2)

**Location**: `src/lob/order_book.py`

### 2. Trading Interface

- **REST API**: Order submission, cancellation, book queries
- **WebSocket**: Real-time market data and fill notifications
- **Risk Controls**: Position limits, P&L stops, order rate limits

**Location**: `src/interface/trading_interface.py`

### 3. Market-Making Strategies

#### Symmetric Market Maker
Posts quotes symmetrically around mid-price with fixed spread.

#### Inventory-Skew Market Maker
Skews quotes away from inventory to manage risk (if long inventory, makes bid less aggressive).

#### Adaptive Spread Market Maker
Adjusts spread based on realized volatility (EWMA of returns).

**Location**: `src/strategies/`

### 4. Microstructure Features

Extracts features from LOB:
- Spread, depth imbalance
- Order flow imbalance (OFI)
- Price momentum, volatility
- Weighted mid, queue position proxies

**Location**: `src/features/microstructure.py`

### 5. Short-Term Predictor

Neural network or Random Forest that predicts:
- Next-period signed return
- Adverse selection probability

**Location**: `src/predictor/short_term_predictor.py`

### 6. RL Environment

Gym-compatible environment for training RL agents:
- Observation: microstructure features + inventory
- Action: bid/ask offsets and quote size
- Reward: spread capture - inventory penalty + P&L

**Location**: `src/rl/lob_env.py`

### 7. Backtest/Replay

Replays historical ticks through the same interface for deterministic testing.

**Location**: `src/backtest/replay.py`

## 📊 API Reference

### REST Endpoints

#### Submit Order
```bash
POST /order
{
  "client_id": "mm_1",
  "side": "buy",
  "type": "limit",
  "price": 100.05,
  "size": 5
}
```

#### Cancel Order
```bash
POST /cancel/{order_id}
```

#### Get Order Book
```bash
GET /book
```

#### Get Fills
```bash
GET /fills/{client_id}
```

#### Get Risk State
```bash
GET /risk/{client_id}
```

### WebSocket Endpoints

#### Market Data
```javascript
ws://127.0.0.1:8000/ws/md
// Receives: {mid, best_bid, best_ask, spread, bids, asks, timestamp}
```

#### Fill Notifications
```javascript
ws://127.0.0.1:8000/ws/fills/{client_id}
// Receives: {event: "fill", order_id, side, price, size, timestamp}
```

## 🧪 Testing Strategies

### Backtest Example

```python
from src.backtest.replay import BacktestEngine, generate_synthetic_ticks
from src.lob.order_book import LimitOrderBook

# Generate synthetic tick data
ticks = generate_synthetic_ticks(n_ticks=1000)

# Create LOB and backtest engine
lob = LimitOrderBook()
engine = BacktestEngine(lob)
engine.load_ticks(ticks)

# Run backtest
results = engine.run_replay(strategy_client_id="mm_1")
print(f"Final PnL: {results['final_pnl']:.2f}")
```

### Performance Metrics

```python
from src.metrics.performance import PerformanceMetrics

metrics = PerformanceMetrics.compute_metrics(
    fills=results['metrics']['fills'],
    pnl_history=results['metrics']['pnl']
)

print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2f}")
```

## 🎓 Resume Bullets

**Strong (Recommended)**:
> Built a proprietary trading interface (REST + WebSocket) and implemented adaptive market-making strategies using microstructure features and reinforcement learning, validated through replay-based backtesting.

**With Metrics**:
> Designed a proprietary market-making platform with internal order APIs and live market-data feeds; deployed inventory-aware and ML-driven quoting strategies and evaluated P&L and risk via LOB replay.

**Technical + Leadership**:
> Led end-to-end development of a proprietary trading interface and strategy suite: designed order lifecycle (ACKs, fills, cancels), implemented risk controls (position & rate limits), and integrated backtest/replay, enabling deterministic offline validation and safe live testing.

## 🔬 Evaluation Metrics

Track these metrics to evaluate strategies:

- **Realized Spread**: Difference between quoted spread and actual execution
- **Fill Rate**: Percentage of quotes that get filled
- **Time-Weighted Average Inventory**: Average inventory over time
- **P&L Distribution**: Mean, median, Sharpe ratio, max drawdown
- **Latency**: Round-trip time for order → ACK → fill

## 🛡️ Risk Controls

The system includes:

- **Position Limits**: Max net position per symbol
- **Daily Loss Limits**: Automatic kill switch
- **Order Rate Limits**: Prevent order spam
- **Price Bounds**: Circuit breakers for limit orders
- **Audit Log**: All orders and fills are logged

## 🚢 Deployment

### Docker

```bash
# Build
docker build -t proptrade .

# Run
docker run -p 8000:8000 proptrade
```

### Docker Compose

```bash
docker-compose up
```

## 📈 Next Steps / Extensions

1. **Add Real Data**: Integrate with exchange APIs or historical tick data
2. **Enhanced RL**: Implement more sophisticated reward functions, multi-agent scenarios
3. **Options Hedging**: Extend to options market-making with delta hedging
4. **Low-Latency Core**: Port matching engine to C++/Rust/OCaml for production
   - See `docs/LOW_LATENCY_ARCHITECTURE.md` for detailed guide
   - Current Python implementation: ~100-1000μs latency
   - Target with C++/Rust core: <10μs latency, >1M orders/sec
5. **Multi-Symbol**: Support multiple instruments simultaneously
6. **Advanced Features**: Calendar spreads, cross-asset hedging, execution algorithms

## ⚡ Low-Latency Architecture (Python + C++)

The platform supports both Python (for development) and C++ (for production performance):

### Current: Python Implementation
- **Latency**: ~100-1000μs per order
- **Throughput**: ~10K-100K orders/sec
- **Best for**: Research, prototyping, strategy development

### Optional: C++ Core (Available Now!)
- **Latency**: <10μs per order (30x faster)
- **Throughput**: >1M orders/sec (20x faster)
- **Best for**: Production, high-frequency trading

### Quick Start with C++

```bash
# Build C++ matching engine
cd core/cpp
pip3 install pybind11
python3 setup.py build_ext --inplace

# Test it
python3 test_cpp_engine.py

# Use in Python (automatic fallback to Python if C++ not available)
from src.lob.order_book_cpp import LimitOrderBook
lob = LimitOrderBook()  # Uses C++ if built, Python otherwise
```

See `docs/PYTHON_CPP_INTEGRATION.md` for complete integration guide.

The C++ engine is a **drop-in replacement** - same interface, automatic fallback to Python if not built. Perfect for:
- ✅ Validated strategies ready for production
- ✅ High-frequency trading requirements
- ✅ Ultra-low latency needs

See `docs/LOW_LATENCY_ARCHITECTURE.md` for architecture details and migration strategies.

## 📝 License

See LICENSE file.

## 🙏 Acknowledgments

This project demonstrates production-style trading system architecture suitable for:
- Quantitative trading interviews (Citadel, Jane Street, Two Sigma, etc.)
- Research in market microstructure and execution
- Learning order-driven markets and market-making strategies

---

**Built for quantitative trading research and portfolio demonstration**
