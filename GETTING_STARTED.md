# Getting Started - Step by Step

## 🎯 What to Do Right Now

### Option 1: Run a Market-Making Strategy (Recommended First Step)

Open a **new terminal window** and run:

```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy

# Run a simple symmetric market maker
python3 scripts/run_strategy.py --strategy symmetric --client-id mm_1
```

**What this does:**
- Connects to the trading interface
- Subscribes to market data via WebSocket
- Posts bid/ask quotes every 0.5 seconds
- Manages inventory automatically

**You'll see:**
- Real-time market data updates
- Quotes being posted
- Fills when orders execute

---

### Option 2: Explore the API (Interactive)

1. **Open in browser**: http://127.0.0.1:8000/docs
2. **Try the endpoints**:
   - Click "POST /order" → Try it out → Submit an order
   - Click "GET /book" → See the order book
   - Click "GET /risk/{client_id}" → Check risk state

---

### Option 3: Train an RL Agent (Takes 5-10 minutes)

```bash
# Train a reinforcement learning agent
python3 scripts/train_rl.py --episodes 500 --save-path models/rl_mm_agent

# After training, run it:
python3 scripts/run_rl_strategy.py --model-path models/rl_mm_agent.zip
```

**What this does:**
- Trains an AI agent to make optimal quoting decisions
- Learns to balance spread capture vs inventory risk
- Saves the trained model for later use

---

### Option 4: Run the Demo Script

```bash
./demo_workflow.sh
```

This shows:
- Interface status
- Submitting orders
- Viewing order book
- Checking risk state

---

## 📊 What Each Component Does

### Trading Interface (Currently Running)
- **REST API**: Submit orders, query book, check risk
- **WebSocket**: Real-time market data and fill notifications
- **Matching Engine**: Executes orders, maintains order book
- **Risk Manager**: Enforces position limits, P&L stops

### Market-Making Strategies
- **Symmetric**: Posts quotes at fixed spread around mid
- **Inventory-Skew**: Adjusts quotes based on inventory
- **Adaptive Spread**: Adjusts spread based on volatility
- **RL Agent**: AI-powered optimal quoting

### RL Environment
- **Training**: Learn optimal quoting policy
- **Inference**: Use trained model for live trading
- **Features**: Microstructure signals + inventory

---

## 🎓 Learning Path

### Beginner (Start Here)
1. ✅ Run `demo_workflow.sh` to see the system
2. ✅ Open http://127.0.0.1:8000/docs and explore API
3. ✅ Run a simple strategy: `python3 scripts/run_strategy.py --strategy symmetric`

### Intermediate
4. ✅ Try different strategies (inventory_skew, adaptive)
5. ✅ Run backtest: `python3 examples/quick_start.py`
6. ✅ Explore notebooks: `notebooks/example_analysis.ipynb`

### Advanced
7. ✅ Train RL agent: `python3 scripts/train_rl.py`
8. ✅ Build C++ engine: `cd core/cpp && python3 setup.py build_ext --inplace`
9. ✅ Customize strategies or add new features

---

## 🔍 Monitor What's Happening

### View Order Book
```bash
watch -n 1 'curl -s http://127.0.0.1:8000/book | python3 -m json.tool'
```

### Check Strategy Performance
```bash
curl http://127.0.0.1:8000/risk/mm_1
```

### View API Logs
The interface terminal shows:
- Order submissions
- Fills
- Market data updates

---

## 💡 Quick Tips

1. **Keep interface running**: Don't close the terminal with the interface
2. **Use new terminals**: Run strategies in separate terminals
3. **Check API docs**: http://127.0.0.1:8000/docs has everything
4. **Read the code**: All strategies are in `src/strategies/`

---

## 🚀 Recommended First Action

**Run this command in a new terminal:**

```bash
python3 scripts/run_strategy.py --strategy symmetric --client-id mm_1
```

This will:
- Connect to the trading interface
- Start making markets
- Show you real-time activity

Then watch both terminals to see the system in action!

---

## ❓ Need Help?

- **API Documentation**: http://127.0.0.1:8000/docs
- **README**: See `README.md` for full documentation
- **RL Guide**: See `docs/RL_AGENT_GUIDE.md`
- **Asset Config**: See `docs/ASSET_CLASS_CONFIG.md`
