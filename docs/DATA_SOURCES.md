# Data Sources: What Data Are We Using?

## Current Implementation: **Synthetic Data**

The platform currently uses **synthetic (simulated) market data** for development and testing.

### Why Synthetic Data?

✅ **No API keys required** - Works immediately  
✅ **Controlled environment** - Predictable for testing  
✅ **Fast iteration** - No rate limits or costs  
✅ **Perfect for development** - Test strategies safely  

### What Synthetic Data Is Generated

#### 1. **Live Market Data** (Trading Interface)

**Location**: `src/interface/trading_interface.py` → `_market_data_generator()`

**What it generates**:
- **Price movements**: Random walk with Gaussian noise
  - Base price: 100.0
  - Volatility: ~0.05 per update
  - Updates: 10 times per second (0.1s interval)

- **Synthetic orders**: Random limit orders
  - 30% chance per update
  - Random side (buy/sell)
  - Price offset: 0.01 to 0.10 from mid
  - Size: 1-10 shares

**Data structure**:
```python
{
    "mid": 100.33,
    "best_bid": 100.32,
    "best_ask": 100.34,
    "spread": 0.02,
    "bids": [[100.32, 3], [100.30, 3], ...],
    "asks": [[100.34, 7], [100.35, 6], ...],
    "timestamp": 1234567890.123
}
```

#### 2. **Backtest Data** (Replay System)

**Location**: `src/backtest/replay.py` → `generate_synthetic_ticks()`

**What it generates**:
- **Tick-by-tick data**: Price, size, side, timestamp
- **Random walk prices**: With configurable volatility
- **Random trade signs**: Buy/sell with random sizes

**Parameters**:
- Initial price: 100.0 (configurable)
- Volatility: 0.02 (2% daily, configurable)
- Tick size: 0.01
- Number of ticks: 1000 (default)

**Data structure**:
```python
DataFrame with columns:
- timestamp: float
- price: float
- size: int
- side: "buy" or "sell"
```

#### 3. **RL Training Data** (Environment)

**Location**: `src/rl/lob_env.py` → `_generate_market_event()`

**What it generates**:
- **Market orders**: 30% chance per step
- **Random side and size**: Creates realistic order flow
- **Price based on current mid**: Maintains realistic spreads

## Data Flow

```
┌─────────────────────┐
│ Synthetic Generator │
│ (Random Walk)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Limit Order Book     │
│ (Real Matching)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Market Data Feed    │
│ (WebSocket)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Strategies          │
│ (MM/RL Agents)      │
└─────────────────────┘
```

## Configuration

Current settings in `config/config.yaml`:

```yaml
market_data:
  update_frequency: 0.1  # seconds (10 Hz)
  synthetic_volatility: 0.02  # 2% volatility

backtest:
  default_ticks: 1000
  initial_price: 100.0
  volatility: 0.02
```

## How to Add Real Market Data

### Option 1: Historical Tick Data

Replace `generate_synthetic_ticks()` with real data loader:

```python
def load_real_ticks(file_path: str) -> pd.DataFrame:
    """Load real tick data from CSV/Parquet"""
    df = pd.read_parquet(file_path)
    # Expected columns: timestamp, price, size, side
    return df
```

### Option 2: Live Market Data API

Replace `_market_data_generator()` with API integration:

```python
async def _market_data_generator(self):
    """Connect to real market data API"""
    # Example: Connect to exchange WebSocket
    async with websockets.connect("wss://exchange.com/ws") as ws:
        while self.md_running:
            msg = await ws.recv()
            data = parse_market_data(msg)
            # Process and push to subscribers
```

### Option 3: Data Providers

**Free/Cheap Options**:
- **Alpha Vantage**: Free tier available
- **Yahoo Finance**: `yfinance` library
- **Polygon.io**: Free tier for delayed data
- **IEX Cloud**: Free tier available

**Professional Options**:
- **Bloomberg API**: Real-time data
- **Refinitiv (LSEG)**: Professional feeds
- **Exchange APIs**: Direct from exchanges

## Example: Adding Yahoo Finance Data

```python
import yfinance as yf

# Get real stock data
ticker = yf.Ticker("AAPL")
data = ticker.history(period="1d", interval="1m")

# Convert to tick format
ticks = []
for idx, row in data.iterrows():
    ticks.append({
        "timestamp": idx.timestamp(),
        "price": row["Close"],
        "size": 100,  # Default size
        "side": "buy" if row["Close"] > row["Open"] else "sell"
    })
```

## Current Data Characteristics

| Property | Value |
|----------|-------|
| **Type** | Synthetic (simulated) |
| **Update Rate** | 10 Hz (10 updates/second) |
| **Price Range** | ~100.0 ± volatility |
| **Volatility** | 2% (configurable) |
| **Order Arrival** | Poisson-like (30% chance) |
| **Order Sizes** | 1-10 shares (random) |
| **Spread** | Dynamic (based on book) |

## Why This Works for Development

1. **Realistic enough**: Random walk mimics real price behavior
2. **Fast**: No API rate limits or network delays
3. **Reproducible**: Can seed random number generator
4. **Flexible**: Easy to adjust volatility, arrival rates
5. **Safe**: No risk of real trading mistakes

## Next Steps: Real Data Integration

To use real data:

1. **Choose data source** (Yahoo Finance, Alpha Vantage, etc.)
2. **Create data loader** in `src/data/` directory
3. **Replace synthetic generator** with real data feed
4. **Update config** to point to real data source

The platform is designed to work with **any data source** - just replace the generator function!

---

**Current Status**: Using synthetic data (perfect for development)  
**Future**: Can easily integrate real market data when ready
