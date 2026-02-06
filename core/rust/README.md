# Rust Low-Latency Core

This directory contains the Rust implementation of the matching engine.

## Building

```bash
# Install PyO3 dependencies
pip3 install maturin

# Build and install
maturin develop --release
```

## Structure

- `src/lib.rs`: Main library
- `src/matching_engine.rs`: Matching engine
- `src/order_book.rs`: Order book
- `Cargo.toml`: Rust dependencies

## Usage

```python
from matching_engine_rust import MatchingEngine

engine = MatchingEngine()
# Same interface as Python version, but much faster
```

## Performance Targets

- Matching latency: <10 microseconds
- Throughput: >1M orders/second
- Memory safety guaranteed by Rust
