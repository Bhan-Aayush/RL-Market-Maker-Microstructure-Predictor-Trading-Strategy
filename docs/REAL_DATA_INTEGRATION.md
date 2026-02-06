# Real Market Data Integration Guide

## Overview

The platform now supports **real market data** from live APIs:
- ✅ **Yahoo Finance** (free, no API key needed)
- ✅ **Alpha Vantage** (free tier available)
- ✅ **Synthetic** (default, for development)

## Quick Start

### Option 1: Yahoo Finance (Recommended - Free)

```bash
# Install yfinance
pip install yfinance

# Run interface with Yahoo Finance data
python3 scripts/run_interface.py --data-source yahoo --symbol AAPL
```

**Supported Symbols**: Any stock ticker (AAPL, MSFT, TSLA, GOOGL, etc.)

### Option 2: Alpha Vantage

```bash
# Get free API key: https://www.alphavantage.co/support/#api-key
export ALPHA_VANTAGE_API_KEY="your_key_here"

# Run interface with Alpha Vantage
python3 scripts/run_interface.py --data-source alphavantage --symbol AAPL --api-key $ALPHA_VANTAGE_API_KEY
```

### Option 3: Synthetic (Default)

```bash
# Use synthetic data (no API needed)
python3 scripts/run_interface.py --data-source synthetic
```

## Usage Examples

### Yahoo Finance - Apple Stock

```bash
python3 scripts/run_interface.py --data-source yahoo --symbol AAPL
```

### Yahoo Finance - Microsoft

```bash
python3 scripts/run_interface.py --data-source yahoo --symbol MSFT
```

### Alpha Vantage - Tesla

```bash
python3 scripts/run_interface.py --data-source alphavantage --symbol TSLA --api-key YOUR_KEY
```

## Data Source Comparison

| Feature | Synthetic | Yahoo Finance | Alpha Vantage |
|---------|-----------|---------------|---------------|
| **Cost** | Free | Free | Free (limited) |
| **API Key** | Not needed | Not needed | Required |
| **Update Rate** | 10 Hz | ~1 Hz | ~1 Hz (rate limited) |
| **Real Prices** | ❌ | ✅ | ✅ |
| **Real Volume** | ❌ | ✅ | ✅ |
| **L2 Data** | ❌ | ❌ | ❌ |
| **Historical** | ✅ | ✅ | ✅ |

## What Data Is Fetched

### Yahoo Finance

- **Current Price**: Real-time last trade price
- **Bid/Ask**: Estimated from price (Yahoo doesn't provide real L2)
- **Volume**: Real trading volume
- **Historical**: Minute bars converted to ticks

### Alpha Vantage

- **Current Price**: Real-time quote
- **Bid/Ask**: High/Low as proxy (no real L2)
- **Volume**: Real trading volume
- **Historical**: Intraday minute data

## Rate Limits

### Yahoo Finance
- **No official limit**, but be respectful
- Recommended: 1 request per second max
- Default update interval: 1 second

### Alpha Vantage
- **Free tier**: 5 API calls per minute
- **Premium tier**: 75+ calls per minute
- Default update interval: 1 second (safe for free tier)

## Configuration

### Environment Variables

```bash
# Alpha Vantage API key
export ALPHA_VANTAGE_API_KEY="your_key_here"

# Default symbol
export TRADING_SYMBOL="AAPL"
```

### Config File

Add to `config/config.yaml`:

```yaml
market_data:
  source: "yahoo"  # or "alphavantage", "synthetic"
  symbol: "AAPL"
  update_interval: 1.0  # seconds
  api_key: null  # or set ALPHA_VANTAGE_API_KEY env var
```

## Programmatic Usage

### In Python Code

```python
from src.data.market_data_source import create_data_source

# Yahoo Finance
yahoo_source = create_data_source("yahoo")
quote = yahoo_source.get_latest_quote("AAPL")
print(f"AAPL: ${quote['last_price']:.2f}")

# Alpha Vantage
av_source = create_data_source("alphavantage", api_key="YOUR_KEY")
quote = av_source.get_latest_quote("MSFT")
print(f"MSFT: ${quote['last_price']:.2f}")

# Historical data
from datetime import datetime, timedelta
end = datetime.now()
start = end - timedelta(days=1)
ticks = yahoo_source.get_historical_ticks("AAPL", start, end)
print(f"Retrieved {len(ticks)} ticks")
```

## Integration with Trading Interface

The trading interface automatically:
1. Fetches real quotes from the data source
2. Updates the order book with real prices
3. Pushes market data to WebSocket subscribers
4. Maintains realistic spreads and depth

## Limitations

### Current Implementation

⚠️ **No Real L2 Data**: Neither Yahoo Finance nor Alpha Vantage provide real Level 2 (order book) data
- We estimate bid/ask from last price
- Synthetic orders are added for depth

⚠️ **Rate Limits**: Real APIs have rate limits
- Yahoo: Be respectful (~1 req/sec)
- Alpha Vantage: 5 calls/min (free tier)

⚠️ **Delayed Data**: Free tiers may have delays
- Yahoo: Usually real-time for active stocks
- Alpha Vantage: May have 15-min delay on free tier

## Getting Real L2 Data

For real Level 2 order book data, you need:
- **Professional data feeds**: Bloomberg, Refinitiv, exchange APIs
- **Cost**: $1000s/month typically
- **Integration**: Custom WebSocket handlers

## Testing

### Test Yahoo Finance Connection

```python
from src.data.market_data_source import create_data_source

source = create_data_source("yahoo")
quote = source.get_latest_quote("AAPL")
print(quote)
```

### Test Alpha Vantage Connection

```python
source = create_data_source("alphavantage", api_key="YOUR_KEY")
quote = source.get_latest_quote("AAPL")
print(quote)
```

## Troubleshooting

### Yahoo Finance Errors

**Error**: "yfinance not installed"
```bash
pip install yfinance
```

**Error**: "No data found"
- Check symbol is correct (e.g., "AAPL" not "apple")
- Stock may be delisted or not trading

### Alpha Vantage Errors

**Error**: "Invalid API key"
- Get free key: https://www.alphavantage.co/support/#api-key
- Set via `--api-key` or `ALPHA_VANTAGE_API_KEY` env var

**Error**: "API call frequency"
- Free tier: 5 calls/minute max
- Wait 12 seconds between calls
- Or upgrade to premium

## Next Steps

1. **Start with Yahoo Finance** (easiest, free)
2. **Test with different symbols** (AAPL, MSFT, TSLA, etc.)
3. **Run strategies** with real data
4. **Upgrade to premium** if you need higher rate limits

---

**Ready to use real market data!** 🚀
