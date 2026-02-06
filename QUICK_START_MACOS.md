# Quick Start Guide for macOS

## Installation

```bash
# Install dependencies (use pip3 on macOS)
pip3 install -r requirements.txt
```

## Running the Platform

### 1. Start the Trading Interface

```bash
# Terminal 1
python3 scripts/run_interface.py
```

The interface will be available at:
- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

### 2. Run a Strategy

```bash
# Terminal 2 (new terminal window)
python3 scripts/run_strategy.py --strategy symmetric
```

### 3. Test the Quick Start Example

```bash
python3 examples/quick_start.py
```

## Common Commands

```bash
# Run interface
python3 scripts/run_interface.py

# Run symmetric strategy
python3 scripts/run_strategy.py --strategy symmetric

# Run inventory-skew strategy
python3 scripts/run_strategy.py --strategy inventory_skew

# Run adaptive spread strategy
python3 scripts/run_strategy.py --strategy adaptive

# Train RL agent
python3 scripts/train_rl.py --episodes 1000
```

## Troubleshooting

### "pip: command not found"
Use `pip3` instead of `pip` on macOS.

### "python: command not found"
Use `python3` instead of `python` on macOS.

### Port 8000 already in use
Change the port in `scripts/run_interface.py` or kill the process using port 8000:
```bash
lsof -ti:8000 | xargs kill
```

## Next Steps

1. Explore the API docs at http://127.0.0.1:8000/docs
2. Check out `notebooks/example_analysis.ipynb` for analysis
3. Read `README.md` for full documentation
