# Trading Interface API Endpoints

## Base URL
**http://localhost:8000**

## Available Endpoints

### 📊 Order Book
- **GET `/book`** - Get current order book snapshot
  ```bash
  curl http://localhost:8000/book
  ```
  Returns: `{bids: [[price, size], ...], asks: [[price, size], ...], best_bid, best_ask, mid, spread, timestamp}`

### 📝 Order Management
- **POST `/order`** - Submit a new order
  ```bash
  curl -X POST http://localhost:8000/order \
    -H "Content-Type: application/json" \
    -d '{
      "client_id": "client1",
      "side": "buy",
      "type": "limit",
      "price": 100.0,
      "size": 10,
      "symbol": "AAPL"
    }'
  ```

- **GET `/order/{order_id}`** - Get order status
  ```bash
  curl http://localhost:8000/order/{order_id}
  ```

- **POST `/cancel/{order_id}`** - Cancel an order
  ```bash
  curl -X POST http://localhost:8000/cancel/{order_id}
  ```

### 📈 Fills & Risk
- **GET `/fills/{client_id}`** - Get fill history for a client
  ```bash
  curl http://localhost:8000/fills/client1
  ```

- **GET `/risk/{client_id}`** - Get risk state for a client
  ```bash
  curl http://localhost:8000/risk/client1
  ```
  Returns: `{client_id, position, realized_pnl, unrealized_pnl, daily_pnl, is_blocked}`

### 🔌 WebSocket Endpoints

- **WebSocket `/ws/md`** - Real-time market data stream
  ```javascript
  const ws = new WebSocket('ws://localhost:8000/ws/md');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Market data:', data);
  };
  ```

- **WebSocket `/ws/fills/{client_id}`** - Real-time fill notifications
  ```javascript
  const ws = new WebSocket('ws://localhost:8000/ws/fills/client1');
  ws.onmessage = (event) => {
    const fill = JSON.parse(event.data);
    console.log('Fill:', fill);
  };
  ```

## Example Usage

### 1. Check Order Book
```bash
curl http://localhost:8000/book
```

### 2. Submit a Buy Order
```bash
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "trader1",
    "side": "buy",
    "type": "limit",
    "price": 150.50,
    "size": 100
  }'
```

### 3. Check Your Risk State
```bash
curl http://localhost:8000/risk/trader1
```

### 4. View Your Fills
```bash
curl http://localhost:8000/fills/trader1
```

## Note

The root endpoint `/` returns `{"detail":"Not Found"}` because it's not defined. Use the endpoints listed above instead.

## FastAPI Docs

For interactive API documentation, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
