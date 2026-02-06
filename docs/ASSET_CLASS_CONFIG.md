# Asset Class Configuration: Equities vs Commodities

## Current Implementation: Asset-Agnostic

The platform is designed to work with **both equities and commodities** (listed futures). The current defaults are configured for **equities**, but it can easily be adapted for commodities.

## Default Configuration (Equities)

Current settings in `config/config.yaml`:

```yaml
lob:
  tick_size: 0.01        # $0.01 tick (typical for stocks)
  
rl:
  initial_mid: 100.0     # Typical stock price range
  
backtest:
  initial_price: 100.0   # Stock-like price
  volatility: 0.02       # 2% volatility
```

These defaults work well for:
- **Cash equities** (stocks, ETFs)
- **Listed equity futures** (E-mini S&P 500, etc.)

## Configuration for Commodities

### Listed Futures (Recommended)

For commodities futures (WTI crude, gold, corn, etc.):

```yaml
lob:
  tick_size: 0.01        # Contract-specific (e.g., WTI = $0.01 = $10/tick)
  
rl:
  initial_mid: 75.0      # Typical futures price (adjust per contract)
  
backtest:
  initial_price: 75.0
  volatility: 0.025      # Higher volatility for commodities
```

**Key differences for futures:**
- **Tick value**: Each tick = $10 for WTI, $0.25 for gold, etc.
- **Contract months**: Need to handle expiration/roll logic
- **Larger lot sizes**: Typically 1 contract = 1000 barrels (WTI) or 100 oz (gold)

### Physical Commodities (Advanced)

For physical commodities (power, gas, oil shipping):
- Requires scheduling/unit commitment logic
- Storage constraints
- Delivery/settlement mechanics
- Location basis (not implemented in current version)

## How to Configure

### Option 1: Update Config File

Edit `config/config.yaml`:

```yaml
# For WTI Crude Oil Futures
lob:
  tick_size: 0.01        # $0.01 per barrel
  # Note: Tick value = $10 (1000 barrels * $0.01)

# For Gold Futures
lob:
  tick_size: 0.10        # $0.10 per ounce
  # Note: Tick value = $10 (100 oz * $0.10)
```

### Option 2: Per-Strategy Configuration

```python
# Equities
strategy = SymmetricMarketMaker(
    client_id="equity_mm",
    half_spread=0.05,  # $0.05 spread
    quote_size=100     # 100 shares
)

# Commodities Futures
strategy = SymmetricMarketMaker(
    client_id="commodity_mm",
    half_spread=0.02,  # $0.02 spread (2 ticks)
    quote_size=1        # 1 contract
)
```

### Option 3: Environment Variables

```bash
export TICK_SIZE=0.01
export INITIAL_MID=75.0
export ASSET_CLASS=commodities
```

## Feature Comparison

| Feature | Equities | Commodities (Futures) | Physical Commodities |
|---------|----------|----------------------|---------------------|
| **Tick Size** | $0.01 | Contract-specific | N/A |
| **Lot Size** | 1 share | 1 contract (varies) | Unit-specific |
| **Price Range** | $1-$1000+ | Contract-specific | Location-based |
| **Volatility** | 1-5% daily | 2-10% daily | Highly variable |
| **Expiration** | None | Monthly/Quarterly | Delivery dates |
| **Settlement** | T+2 | Cash/Physical | Physical delivery |
| **Current Support** | ✅ Full | ✅ Full (futures) | ⚠️ Partial |

## What Works for Both

The following features work identically for equities and commodities:

✅ **Limit Order Book** - Same matching logic  
✅ **Market-Making Strategies** - Same algorithms  
✅ **RL Agent** - Same environment, just different parameters  
✅ **Risk Management** - Same position/P&L limits  
✅ **Microstructure Features** - Same feature extraction  
✅ **Backtest/Replay** - Same replay system  

## What Needs Adaptation for Commodities

### 1. Contract Roll Logic

For futures, you need to handle:
- Expiration dates
- Rolling from front month to next month
- Calendar spread trading

**Not currently implemented** - would need to add:
```python
class FuturesContract:
    symbol: str
    expiration: datetime
    tick_value: float  # $ per tick
    contract_size: int  # barrels, ounces, etc.
```

### 2. Tick Value Awareness

Commodities need tick value (not just tick size):

```python
# WTI Crude: tick_size = $0.01, tick_value = $10
# Gold: tick_size = $0.10, tick_value = $10
# Corn: tick_size = $0.25, tick_value = $12.50

tick_value = tick_size * contract_size
pnl_per_tick = position * tick_value
```

### 3. Calendar Spreads

Commodities often trade calendar spreads (nearby vs deferred):

```python
# Not currently implemented
spread_price = front_month_price - deferred_month_price
```

## Recommended Approach

### For Equities (Current Default)
✅ **Ready to use** - Current configuration works perfectly

### For Commodities Futures
✅ **Works with minor config changes**:
1. Update `tick_size` in config
2. Adjust `initial_mid` to contract price range
3. Consider tick value in P&L calculations
4. Add contract roll logic if trading multiple months

### For Physical Commodities
⚠️ **Requires significant additions**:
- Scheduling/unit commitment
- Storage constraints
- Location basis
- Delivery mechanics

## Example: WTI Crude Oil Futures

```python
# Configure for WTI
config = {
    "tick_size": 0.01,      # $0.01 per barrel
    "tick_value": 10.0,     # $10 per tick (1000 barrels)
    "contract_size": 1000,  # barrels per contract
    "initial_mid": 75.0,    # Typical WTI price
    "volatility": 0.025     # 2.5% daily vol
}

# Create strategy
strategy = SymmetricMarketMaker(
    client_id="wti_mm",
    half_spread=0.02,  # 2 ticks = $0.02
    quote_size=1       # 1 contract
)
```

## Summary

**Current State**: Asset-agnostic, defaults configured for **equities**

**To Use for Commodities**:
1. Update `tick_size` and `initial_mid` in config
2. Consider tick value in P&L (if needed)
3. Add contract roll logic (if trading multiple months)

**Best For**:
- ✅ Equities (cash stocks, ETFs)
- ✅ Listed futures (equity, commodity, FX)
- ⚠️ Physical commodities (requires additional features)

The core matching engine, strategies, and RL agent work identically for both asset classes - just adjust the parameters!
