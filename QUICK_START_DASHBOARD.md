# Quick Start: Dashboard & Services

## ✅ Current Status

Based on process check:
- **Trading Interface**: ✅ Running on port 8000 (PID visible)
- **Dashboard**: ⚠️ May need to start manually

## 🚀 Start Services Manually

### Option 1: Start Both Services (Recommended)

**Terminal 1 - Trading Interface:**
```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate
python scripts/run_interface.py
```

**Terminal 2 - Dashboard:**
```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate
streamlit run dashboard/app.py
```

### Option 2: Use the Launch Script

```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate
python scripts/run_dashboard.py
```

## 🌐 Access URLs

Once services are running:

- **Dashboard**: http://localhost:8501
- **Trading Interface API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## 🔍 Verify Services

### Check Trading Interface:
```bash
curl http://127.0.0.1:8000/health
```

Should return: `{"status": "ok"}`

### Check Dashboard:
Open browser: http://localhost:8501

## ⚠️ Missing Dependencies

If you see errors about `scipy` or `statsmodels`:

**Try installing manually:**
```bash
source .venv/bin/activate
pip install --user scipy statsmodels
```

Or if permission issues persist, install globally:
```bash
pip3 install scipy statsmodels
```

## 🎯 Quick Test

1. **Open Dashboard**: http://localhost:8501
2. **Check Sidebar**: Should show "✅ API Connected" if trading interface is running
3. **Try Options Calculator**:
   - Navigate to "Options & Greeks"
   - Enter: Spot=100, Strike=100, Expiration=30
   - Click "Calculate"
   - View results!

## 🐛 Troubleshooting

### Dashboard won't start:
- Check if port 8501 is in use: `lsof -i :8501`
- Kill existing process: `kill -9 <PID>`
- Restart dashboard

### API not connected:
- Make sure trading interface is running first
- Check: `lsof -i :8000`
- Restart interface if needed

### Features not working:
- Some features require `scipy` and `statsmodels`
- Install them first (see above)
- Restart dashboard after installing

## 📝 Next Steps

1. ✅ Start both services
2. ✅ Open dashboard in browser
3. ✅ Test features one by one
4. ✅ Explore all 12 pages!

---

**Happy Trading! 📈**
