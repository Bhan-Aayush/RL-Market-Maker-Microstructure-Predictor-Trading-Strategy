# OCaml Low-Latency Core

This directory contains the OCaml implementation (Jane Street style).

## Building

```bash
# Install OCaml and dune
opam install dune

# Build
dune build

# Generate Python bindings
dune build matching_engine_core.so
```

## Structure

- `matching_engine.ml`: Matching engine
- `order_book.ml`: Order book
- `dune-project`: Build configuration

## Usage

```python
import ctypes
matching_engine = ctypes.CDLL('./matching_engine_core.so')
# Use via FFI
```

## Performance Targets

- Matching latency: <10 microseconds
- Throughput: >1M orders/second
- Strong type safety via OCaml
