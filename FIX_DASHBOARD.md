# Fix Dashboard Connection Issue

## 🔍 Problem
The dashboard shows "Connection Failed" because Streamlit is not installed in your virtual environment.

## ✅ Solution

### Step 1: Install Streamlit

Open a terminal and run:

```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate
pip install streamlit
```

If you get permission errors, try:
```bash
pip install --user streamlit
```

Or install globally:
```bash
pip3 install streamlit
```

### Step 2: Verify Installation

```bash
python3 -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
```

Should print the version number.

### Step 3: Start the Dashboard

```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate
streamlit run dashboard/app.py
```

The dashboard will:
- Start on http://localhost:8501
- Open automatically in your browser
- Show all features ready to test

## 🎯 Quick Start (After Installing)

**Terminal 1 - Trading Interface (if not running):**
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

## ✅ Expected Result

Once Streamlit is installed and running:
- Dashboard opens at http://localhost:8501
- Sidebar shows "✅ API Connected" (if trading interface is running)
- All 12 feature pages are accessible
- You can test all features interactively

## 🐛 Still Having Issues?

1. **Check if port 8501 is in use:**
   ```bash
   lsof -i :8501
   ```

2. **Kill existing process if needed:**
   ```bash
   kill -9 <PID>
   ```

3. **Check Streamlit installation:**
   ```bash
   which streamlit
   streamlit --version
   ```

4. **Try running directly:**
   ```bash
   python3 -m streamlit run dashboard/app.py
   ```

---

**After installing Streamlit, the dashboard will work! 🚀**
