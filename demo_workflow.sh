#!/bin/bash
# Demo workflow script - shows the platform in action

echo "=========================================="
echo "Proprietary Trading Platform Demo"
echo "=========================================="
echo ""

# Step 1: Check interface
echo "1. Checking trading interface..."
curl -s http://127.0.0.1:8000/book > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Interface is running"
else
    echo "   ✗ Interface not running. Start it with: python3 scripts/run_interface.py"
    exit 1
fi

# Step 2: Submit a test order
echo ""
echo "2. Submitting a test order..."
ORDER_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "demo_client",
    "side": "buy",
    "type": "limit",
    "price": 100.05,
    "size": 10
  }')

echo "   Order response: $ORDER_RESPONSE"

# Step 3: Get order book
echo ""
echo "3. Current order book:"
curl -s http://127.0.0.1:8000/book | python3 -m json.tool 2>/dev/null | head -20

# Step 4: Get risk state
echo ""
echo "4. Risk state for demo_client:"
curl -s http://127.0.0.1:8000/risk/demo_client | python3 -m json.tool 2>/dev/null

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Open API docs: http://127.0.0.1:8000/docs"
echo "2. Run a strategy: python3 scripts/run_strategy.py --strategy symmetric"
echo "3. Train RL agent: python3 scripts/train_rl.py --episodes 500"
echo "=========================================="
