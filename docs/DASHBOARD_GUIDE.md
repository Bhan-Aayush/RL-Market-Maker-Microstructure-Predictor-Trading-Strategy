# Trading Platform Dashboard Guide

## 🎯 Overview

The Streamlit dashboard provides a comprehensive UI to test and interact with all features of the trading platform.

## 🚀 Quick Start

### 1. Start the Trading Interface

In one terminal:
```bash
python scripts/run_interface.py
```

### 2. Start the Dashboard

In another terminal:
```bash
python scripts/run_dashboard.py
```

Or directly:
```bash
streamlit run dashboard/app.py
```

The dashboard will open at: **http://localhost:8501**

---

## 📊 Dashboard Features

### 🏠 Home
- Overview of all features
- Feature count and status
- Quick navigation

### 📈 Trading Interface
- **Submit Order**: Place buy/sell orders (limit or market)
- **Order Book**: View current order book (bids/asks)
- **Risk Status**: Check position, P&L, order counts
- **Market Data**: Real-time market data stream

### 🎯 Market-Making Strategies
- Run different market-making strategies
- Monitor strategy performance
- Adjust strategy parameters

### 📊 Options & Greeks
- **Option Pricing**: Black-Scholes calculator
- **Greeks Visualization**: Delta, Gamma, Theta, Vega, Rho
- **Delta Hedging**: Portfolio hedging calculator
- **Volatility Surface**: Implied volatility visualization

### ⚡ Execution Algorithms
- **TWAP**: Time-Weighted Average Price execution
- **VWAP**: Volume-Weighted Average Price execution
- **Implementation Shortfall**: Minimize execution cost
- **POV**: Participation of Volume execution

### 🛡️ Risk Models
- **VaR**: Value at Risk (Historical/Parametric/Monte Carlo)
- **CVaR**: Conditional VaR
- **Stress Testing**: Scenario analysis

### 📉 Statistical Arbitrage
- **Pairs Trading**: Find cointegrated pairs
- **Z-Score Analysis**: Trading signals
- **Spread Visualization**: Mean-reversion analysis

### 💼 Portfolio Optimization
- **Mean-Variance Optimization**: Optimal portfolio weights
- **Risk Parity**: Equal risk contribution
- **Multi-Asset Analysis**: Portfolio metrics

### 📡 Order Flow Analysis
- Order flow imbalance (OFI)
- Trade sign prediction
- Market impact estimation

### 💰 Transaction Cost Analysis
- Slippage analysis
- Market impact measurement
- Fill rate statistics
- Implementation shortfall

### 🔄 Regime Detection
- Volatility regime (high/low vol)
- Trend regime (trending/mean-reverting)
- Direction regime (bull/bear)
- Strategy recommendations

### 💾 Database Queries
- Query historical ticks
- View order history
- Analyze fills
- Export data

---

## 🎨 Features

### Interactive Controls
- Real-time parameter adjustment
- Live visualization updates
- Instant calculations

### Visualizations
- Plotly charts for all analyses
- Interactive graphs
- Real-time updates

### API Integration
- Direct connection to trading interface
- Real-time order submission
- Live market data

---

## 🔧 Configuration

### API Connection
The dashboard connects to the trading interface at:
- Default: `http://127.0.0.1:8000`
- Can be changed in `dashboard/app.py`

### Data Sources
- Synthetic data (default)
- Real market data (Yahoo Finance, Alpha Vantage)
- Historical data from database

---

## 📝 Usage Examples

### Example 1: Calculate Option Greeks
1. Navigate to "Options & Greeks"
2. Enter spot price, strike, expiration
3. Click "Calculate"
4. View price and all Greeks
5. See visualization of Greeks vs spot price

### Example 2: Run TWAP Execution
1. Navigate to "Execution Algorithms" → "TWAP"
2. Enter symbol, side, total size
3. Set duration in minutes
4. Click "Create TWAP Order"
5. View execution status

### Example 3: Calculate VaR
1. Navigate to "Risk Models" → "VaR"
2. Select confidence level (90%, 95%, 99%)
3. Choose method (Historical/Parametric/Monte Carlo)
4. Click "Calculate VaR"
5. View VaR value and distribution chart

### Example 4: Find Pairs for Trading
1. Navigate to "Statistical Arbitrage"
2. Use synthetic data or upload your own
3. Click "Find Cointegrated Pairs"
4. View pair statistics and spread analysis
5. See trading signals (z-scores)

### Example 5: Optimize Portfolio
1. Navigate to "Portfolio Optimization"
2. Set number of assets
3. Enter expected returns for each asset
4. Click "Optimize Portfolio"
5. View optimal weights and metrics

---

## 🐛 Troubleshooting

### Dashboard Won't Start
- Check if Streamlit is installed: `pip install streamlit`
- Check Python version: `python --version` (need 3.8+)

### API Not Connected
- Make sure trading interface is running
- Check if port 8000 is available
- Verify API_BASE URL in dashboard/app.py

### Features Not Working
- Check if required dependencies are installed
- Verify imports in dashboard/app.py
- Check terminal for error messages

---

## 🎯 Best Practices

1. **Start Trading Interface First**: Always start the trading interface before the dashboard
2. **Use Synthetic Data**: For testing, use synthetic data first
3. **Check API Status**: Monitor the API connection status in sidebar
4. **Save Results**: Export important calculations and visualizations
5. **Test Incrementally**: Test one feature at a time

---

## 🚀 Next Steps

1. **Customize Dashboard**: Add your own features
2. **Connect Real Data**: Integrate with live market data
3. **Add More Visualizations**: Enhance charts and graphs
4. **Export Reports**: Generate PDF reports
5. **Add Alerts**: Set up notifications for important events

---

## 📚 Related Documentation

- `README.md` - Main project documentation
- `GETTING_STARTED.md` - Getting started guide
- `docs/NEW_FEATURES_SUMMARY.md` - Feature documentation
- `docs/ADDITIONAL_FEATURES.md` - Additional features

---

## 💡 Tips

- Use the sidebar to quickly navigate between features
- All calculations are performed in real-time
- Visualizations are interactive (zoom, pan, hover)
- Results can be exported as JSON or CSV
- Bookmark frequently used pages

---

**Enjoy testing all the features! 🎉**
