# Fix scipy/OpenBLAS Installation

## ✅ OpenBLAS is Installed

OpenBLAS has been installed via Homebrew, but it's "keg-only" (not in default path).

## 🔧 Solution: Set Environment Variables

Run these commands in your terminal:

```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy
source .venv/bin/activate

# Set environment variables so pip can find OpenBLAS
export LDFLAGS="-L/opt/homebrew/opt/openblas/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openblas/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openblas/lib/pkgconfig"

# Now install scipy
pip install scipy
```

## 🚀 Alternative: Use Pre-built Wheel

If the above doesn't work, try installing a pre-built wheel:

```bash
pip install --only-binary=scipy scipy
```

Or install a newer version that might have better Python 3.13 support:

```bash
pip install scipy --upgrade
```

## 📝 One-Liner (Copy-Paste)

```bash
cd /Users/aayushbhan/RL-Market-Maker-Microstructure-Predictor-Trading-Strategy && source .venv/bin/activate && export LDFLAGS="-L/opt/homebrew/opt/openblas/lib" && export CPPFLAGS="-I/opt/homebrew/opt/openblas/include" && export PKG_CONFIG_PATH="/opt/homebrew/opt/openblas/lib/pkgconfig" && pip install scipy
```

## ✅ Verify Installation

After installing, verify:

```bash
python3 -c "import scipy; print('✅ scipy version:', scipy.__version__)"
```

## 🎯 If Still Having Issues

1. **Try installing via conda** (if you have it):
   ```bash
   conda install scipy
   ```

2. **Or use a pre-built binary**:
   ```bash
   pip install --prefer-binary scipy
   ```

3. **Or wait for Python 3.13 wheels** - scipy may get pre-built wheels soon

## 💡 Note

The dashboard works without scipy! But if you need it for statistical arbitrage or other features, follow the steps above.

---

**Run the commands above to install scipy with OpenBLAS support!**
