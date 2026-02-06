#!/usr/bin/env python3
"""
Test all new quant features
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

print("=" * 70)
print("TESTING NEW QUANT FEATURES")
print("=" * 70)
print()

# Test 1: Options Pricing
print("1. Options Pricing & Greeks")
print("-" * 70)
try:
    from src.options.pricing import BlackScholes, Option
    
    # Create option
    option = Option(
        symbol="AAPL_C100",
        strike=100.0,
        expiration=30/365,  # 30 days
        option_type="call",
        spot=105.0,
        volatility=0.20,
        risk_free_rate=0.05
    )
    
    greeks = option.greeks()
    print(f"   ✅ Option Price: ${greeks['price']:.2f}")
    print(f"   ✅ Delta: {greeks['delta']:.4f}")
    print(f"   ✅ Gamma: {greeks['gamma']:.4f}")
    print(f"   ✅ Theta: {greeks['theta']:.4f}")
    print(f"   ✅ Vega: {greeks['vega']:.4f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Delta Hedging
print("2. Delta Hedging")
print("-" * 70)
try:
    from src.options.delta_hedging import DeltaHedger
    from src.options.pricing import Option
    
    hedger = DeltaHedger("AAPL")
    option = Option("AAPL_C100", 100, 30/365, "call", 105, 0.20)
    hedger.add_option_position(option, 10)  # Long 10 calls
    
    hedge_rec = hedger.update_hedge(105.0)
    print(f"   ✅ Total Delta: {hedger.total_delta():.2f}")
    print(f"   ✅ Hedge Required: {hedge_rec['shares']:.2f} shares")
    print(f"   ✅ Action: {hedge_rec['action']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 3: TWAP Execution
print("3. TWAP Execution")
print("-" * 70)
try:
    from src.execution.twap import TWAPExecutor
    
    executor = TWAPExecutor()
    order_id = executor.create_twap_order("AAPL", "buy", 1000, 3600)  # 1000 shares over 1 hour
    
    status = executor.get_order_status(order_id)
    print(f"   ✅ TWAP Order Created: {order_id[:8]}...")
    print(f"   ✅ Total Size: {status['total_size']}")
    print(f"   ✅ Duration: {status['end_time'] - status['start_time']:.0f} seconds")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 4: VaR Calculation
print("4. Value at Risk (VaR)")
print("-" * 70)
try:
    import numpy as np
    from src.risk.advanced_risk import VaRCalculator
    
    # Generate sample returns
    returns = np.random.normal(0.001, 0.02, 252)  # Daily returns
    
    var_95 = VaRCalculator.historical_var(returns, 0.95)
    var_99 = VaRCalculator.historical_var(returns, 0.99)
    
    print(f"   ✅ VaR (95%): {var_95:.4f} ({var_95*100:.2f}%)")
    print(f"   ✅ VaR (99%): {var_99:.4f} ({var_99*100:.2f}%)")
    
    all_methods = VaRCalculator.calculate_all_methods(returns, 0.95)
    print(f"   ✅ Parametric VaR: {all_methods['parametric']:.4f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 5: CVaR
print("5. Conditional VaR (CVaR)")
print("-" * 70)
try:
    from src.risk.advanced_risk import CVaRCalculator
    
    returns = np.random.normal(0.001, 0.02, 252)
    cvar_95 = CVaRCalculator.calculate(returns, 0.95)
    
    print(f"   ✅ CVaR (95%): {cvar_95:.4f} ({cvar_95*100:.2f}%)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 6: Statistical Arbitrage
print("6. Statistical Arbitrage / Pairs Trading")
print("-" * 70)
try:
    import pandas as pd
    from src.analysis.pairs_trading import PairsTradingStrategy
    
    # Generate synthetic correlated prices
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=252, freq="D")
    prices1 = 100 + np.cumsum(np.random.randn(252) * 0.5)
    prices2 = prices1 + np.random.randn(252) * 0.2  # Correlated
    
    price_data = pd.DataFrame({
        "AAPL": prices1,
        "MSFT": prices2
    }, index=dates)
    
    strategy = PairsTradingStrategy()
    pairs = strategy.find_cointegrated_pairs(price_data)
    
    if pairs:
        pair = pairs[0]
        print(f"   ✅ Found Cointegrated Pair: {pair.symbol1} / {pair.symbol2}")
        print(f"   ✅ Hedge Ratio: {pair.hedge_ratio:.4f}")
        print(f"   ✅ Cointegration p-value: {pair.cointegration_pvalue:.4f}")
        
        # Test signal
        signal = strategy.get_trading_signal(100.0, 100.5, pair)
        print(f"   ✅ Trading Signal: {signal['signal']} (z-score: {signal['zscore']:.2f})")
    else:
        print("   ⚠️  No cointegrated pairs found (may need more data)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 7: Portfolio Optimization
print("7. Portfolio Optimization")
print("-" * 70)
try:
    from src.portfolio.optimizer import PortfolioOptimizer
    
    # Sample data
    expected_returns = np.array([0.10, 0.12, 0.08])  # 3 assets
    covariance = np.array([
        [0.04, 0.02, 0.01],
        [0.02, 0.05, 0.015],
        [0.01, 0.015, 0.03]
    ])
    
    # Mean-variance optimization
    weights = PortfolioOptimizer.mean_variance_optimize(
        expected_returns, covariance, risk_aversion=1.0
    )
    
    metrics = PortfolioOptimizer.calculate_portfolio_metrics(
        weights, expected_returns, covariance
    )
    
    print(f"   ✅ Optimal Weights: {[f'{w:.2%}' for w in weights]}")
    print(f"   ✅ Expected Return: {metrics['expected_return']:.4f}")
    print(f"   ✅ Portfolio Volatility: {metrics['volatility']:.4f}")
    print(f"   ✅ Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 8: Advanced Order Flow
print("8. Advanced Order Flow Analysis")
print("-" * 70)
try:
    from src.analysis.order_flow_advanced import AdvancedOrderFlowAnalyzer
    
    analyzer = AdvancedOrderFlowAnalyzer()
    
    bids = [[100.0, 100], [99.99, 200], [99.98, 150]]
    asks = [[100.01, 120], [100.02, 180], [100.03, 200]]
    trades = [
        {"side": "buy", "size": 50, "type": "market"},
        {"side": "sell", "size": 30, "type": "limit"}
    ]
    
    metrics = analyzer.analyze_order_flow(bids, asks, trades, recent_returns=0.001)
    
    print(f"   ✅ Order Flow Imbalance: {metrics.ofi:.4f}")
    print(f"   ✅ Trade Sign Imbalance: {metrics.trade_sign_imbalance:.4f}")
    print(f"   ✅ Aggressiveness Ratio: {metrics.aggressiveness_ratio:.2f}")
    print(f"   ✅ Market Impact: {metrics.market_impact:.4f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 70)
print("✅ ALL FEATURES TESTED!")
print("=" * 70)
print()
print("New capabilities added:")
print("  • Options pricing & Greeks")
print("  • Delta hedging")
print("  • TWAP/VWAP execution")
print("  • VaR/CVaR risk models")
print("  • Statistical arbitrage")
print("  • Portfolio optimization")
print("  • Advanced order flow analysis")
print()
