# Quick Start Guide

## ✅ Platform is Running!

The trading interface is now running. Here's what you can do:

## 1. Check Interface Status

Open in browser: **http://127.0.0.1:8000/docs**

Or check the order book:
```bash
curl http://127.0.0.1:8000/book
```

## 2. Run a Market-Making Strategy

Open a **new terminal** and run:

```bash
# Symmetric market maker (simplest)
python3 scripts/run_strategy.py --strategy symmetric

# Inventory-aware market maker
python3 scripts/run_strategy.py --strategy inventory_skew

# Adaptive spread market maker
python3 scripts/run_strategy.py --strategy adaptive
```

## 3. Train and Run RL Agent

```bash
# Terminal 1: Train RL agent (takes a few minutes)
python3 scripts/train_rl.py --episodes 500 --save-path models/rl_mm_agent

# Terminal 2: Run trained RL agent
python3 scripts/run_rl_strategy.py --model-path models/rl_mm_agent.zip
```

## 4. Test the API

### Submit an order:
```bash
curl -X POST http://127.0.0.1:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test_client",
    "side": "buy",
    "type": "limit",
    "price": 100.05,
    "size": 5
  }'
```

### Get order book:
```bash
curl http://127.0.0.1:8000/book
```

### Get risk state:
```bash
curl http://127.0.0.1:8000/risk/test_client
```

## 5. Explore Examples

```bash
# Run quick start example
python3 examples/quick_start.py

# Open analysis notebook
jupyter notebook notebooks/example_analysis.ipynb
```

## 6. WebSocket Connections

### Market Data:
```python
import websockets
import asyncio
import json

async def listen_md():
    async with websockets.connect("ws://127.0.0.1:8000/ws/md") as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            print(f"Mid: {data['mid']}, Spread: {data['spread']}")

asyncio.run(listen_md())
```

### Fill Notifications:
```python
async def listen_fills():
    async with websockets.connect("ws://127.0.0.1:8000/ws/fills/mm_1") as ws:
        while True:
            msg = await ws.recv()
            fill = json.loads(msg)
            print(f"Fill: {fill['side']} {fill['size']} @ {fill['price']}")

asyncio.run(listen_fills())
```

## What's Running

- ✅ **Trading Interface**: http://127.0.0.1:8000
- ✅ **API Docs**: http://127.0.0.1:8000/docs
- ✅ **WebSocket MD**: ws://127.0.0.1:8000/ws/md
- ✅ **WebSocket Fills**: ws://127.0.0.1:8000/ws/fills/{client_id}

## Next Steps

1. **Run a strategy** in a new terminal
2. **Monitor the order book** via API or WebSocket
3. **Train an RL agent** for AI-powered market making
4. **Explore the notebooks** for analysis and visualization

## Troubleshooting

### Interface not responding?
```bash
# Check if it's running
lsof -ti:8000

# Restart if needed
pkill -f run_interface.py
python3 scripts/run_interface.py
```

### Strategy can't connect?
- Make sure interface is running first
- Check the client_id matches
- Verify WebSocket URLs are correct

---

**Ready to trade!** 🚀
