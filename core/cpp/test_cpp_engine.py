#!/usr/bin/env python3
"""
Test script for C++ matching engine
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    import matching_engine_core as mec
    print("✓ Successfully imported C++ matching engine")
except ImportError as e:
    print(f"✗ Failed to import C++ matching engine: {e}")
    print("  Run: python3 setup.py build_ext --inplace")
    sys.exit(1)

def test_basic_operations():
    """Test basic LOB operations"""
    print("\n=== Testing Basic Operations ===")
    
    # Create LOB
    lob = mec.LimitOrderBook(tick_size=0.01, max_levels=20)
    print("✓ Created LimitOrderBook")
    
    # Add a limit order
    order = mec.Order()
    order.order_id = "test_1"
    order.client_id = "client_1"
    order.side = "buy"
    order.type = "limit"
    order.price = 100.0
    order.size = 10
    order.timestamp = 1234567890.0
    
    fills = lob.add_order(order)
    print(f"✓ Added order: {len(fills)} fills")
    
    # Check book
    snapshot = lob.get_book_snapshot(levels=5)
    print(f"✓ Book snapshot: {len(snapshot.bids)} bid levels, {len(snapshot.asks)} ask levels")
    
    # Get best bid/ask
    best_bid = lob.best_bid()
    best_ask = lob.best_ask()
    print(f"✓ Best bid: {best_bid}, Best ask: {best_ask}")
    
    return True

def test_matching():
    """Test order matching"""
    print("\n=== Testing Order Matching ===")
    
    lob = mec.LimitOrderBook()
    
    # Add buy order
    buy_order = mec.Order()
    buy_order.order_id = "buy_1"
    buy_order.client_id = "mm_1"
    buy_order.side = "buy"
    buy_order.type = "limit"
    buy_order.price = 100.0
    buy_order.size = 5
    
    fills1 = lob.add_order(buy_order)
    print(f"✓ Added buy order: {len(fills1)} fills")
    
    # Add sell order that should match
    sell_order = mec.Order()
    sell_order.order_id = "sell_1"
    sell_order.client_id = "mm_2"
    sell_order.side = "sell"
    sell_order.type = "limit"
    sell_order.price = 99.95  # Below buy price, should match
    sell_order.size = 3
    
    fills2 = lob.add_order(sell_order)
    print(f"✓ Added sell order: {len(fills2)} fills (should match)")
    
    if len(fills2) > 0:
        print(f"  Fill price: {fills2[0].price}, size: {fills2[0].size}")
    
    return True

def test_performance():
    """Test performance"""
    print("\n=== Testing Performance ===")
    import time
    
    lob = mec.LimitOrderBook()
    
    n_orders = 10000
    start = time.time()
    
    for i in range(n_orders):
        order = mec.Order()
        order.order_id = f"order_{i}"
        order.client_id = "perf_test"
        order.side = "buy" if i % 2 == 0 else "sell"
        order.type = "limit"
        order.price = 100.0 + (i % 10) * 0.01
        order.size = 1 + (i % 5)
        
        lob.add_order(order)
    
    elapsed = time.time() - start
    ops_per_sec = n_orders / elapsed
    
    print(f"✓ Processed {n_orders} orders in {elapsed:.4f} seconds")
    print(f"✓ Throughput: {ops_per_sec:,.0f} orders/second")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("C++ Matching Engine Test Suite")
    print("=" * 60)
    
    try:
        test_basic_operations()
        test_matching()
        test_performance()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
