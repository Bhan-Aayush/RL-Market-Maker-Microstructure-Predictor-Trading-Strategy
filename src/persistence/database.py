"""
Database Persistence Layer
Supports PostgreSQL/TimescaleDB for tick data, orders, fills
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from dataclasses import dataclass, asdict


@dataclass
class TickData:
    """Market tick data point"""
    timestamp: float
    symbol: str
    bid: float
    ask: float
    mid: float
    spread: float
    bid_size: float
    ask_size: float
    last_price: Optional[float] = None
    last_size: Optional[float] = None
    volume: Optional[float] = None


@dataclass
class OrderRecord:
    """Order record for persistence"""
    order_id: str
    client_id: str
    symbol: str
    side: str
    order_type: str
    price: Optional[float]
    size: int
    timestamp: float
    status: str
    filled_size: int = 0
    avg_fill_price: Optional[float] = None


@dataclass
class FillRecord:
    """Fill record for persistence"""
    fill_id: str
    order_id: str
    client_id: str
    symbol: str
    side: str
    price: float
    size: int
    timestamp: float
    trade_id: str


class DatabaseInterface:
    """
    Abstract interface for database operations
    Can be implemented with PostgreSQL, TimescaleDB, or SQLite
    """
    
    def connect(self):
        """Connect to database"""
        raise NotImplementedError
    
    def disconnect(self):
        """Disconnect from database"""
        raise NotImplementedError
    
    def create_tables(self):
        """Create required tables"""
        raise NotImplementedError
    
    def insert_tick(self, tick: TickData):
        """Insert market tick data"""
        raise NotImplementedError
    
    def insert_order(self, order: OrderRecord):
        """Insert order record"""
        raise NotImplementedError
    
    def insert_fill(self, fill: FillRecord):
        """Insert fill record"""
        raise NotImplementedError
    
    def query_ticks(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[TickData]:
        """Query historical tick data"""
        raise NotImplementedError
    
    def query_orders(
        self,
        client_id: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[OrderRecord]:
        """Query historical orders"""
        raise NotImplementedError
    
    def query_fills(
        self,
        client_id: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[FillRecord]:
        """Query historical fills"""
        raise NotImplementedError


class SQLiteDatabase(DatabaseInterface):
    """
    SQLite implementation (for development/testing)
    """
    
    def __init__(self, db_path: str = "trading_data.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to SQLite database"""
        import sqlite3
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create required tables"""
        cursor = self.conn.cursor()
        
        # Ticks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                timestamp REAL,
                symbol TEXT,
                bid REAL,
                ask REAL,
                mid REAL,
                spread REAL,
                bid_size REAL,
                ask_size REAL,
                last_price REAL,
                last_size REAL,
                volume REAL
            )
        """)
        
        # Create index for time-series queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticks_time_symbol 
            ON ticks(timestamp, symbol)
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                client_id TEXT,
                symbol TEXT,
                side TEXT,
                order_type TEXT,
                price REAL,
                size INTEGER,
                timestamp REAL,
                status TEXT,
                filled_size INTEGER,
                avg_fill_price REAL
            )
        """)
        
        # Fills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fills (
                fill_id TEXT PRIMARY KEY,
                order_id TEXT,
                client_id TEXT,
                symbol TEXT,
                side TEXT,
                price REAL,
                size INTEGER,
                timestamp REAL,
                trade_id TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_client_time 
            ON orders(client_id, timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fills_order 
            ON fills(order_id)
        """)
        
        self.conn.commit()
    
    def insert_tick(self, tick: TickData):
        """Insert market tick data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ticks 
            (timestamp, symbol, bid, ask, mid, spread, bid_size, ask_size, 
             last_price, last_size, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tick.timestamp, tick.symbol, tick.bid, tick.ask, tick.mid,
            tick.spread, tick.bid_size, tick.ask_size,
            tick.last_price, tick.last_size, tick.volume
        ))
        self.conn.commit()
    
    def insert_order(self, order: OrderRecord):
        """Insert order record"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO orders
            (order_id, client_id, symbol, side, order_type, price, size,
             timestamp, status, filled_size, avg_fill_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order.order_id, order.client_id, order.symbol, order.side,
            order.order_type, order.price, order.size, order.timestamp,
            order.status, order.filled_size, order.avg_fill_price
        ))
        self.conn.commit()
    
    def insert_fill(self, fill: FillRecord):
        """Insert fill record"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO fills
            (fill_id, order_id, client_id, symbol, side, price, size,
             timestamp, trade_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fill.fill_id, fill.order_id, fill.client_id, fill.symbol,
            fill.side, fill.price, fill.size, fill.timestamp, fill.trade_id
        ))
        self.conn.commit()
    
    def query_ticks(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[TickData]:
        """Query historical tick data"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM ticks WHERE symbol = ?"
        params = [symbol]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            TickData(
                timestamp=row["timestamp"],
                symbol=row["symbol"],
                bid=row["bid"],
                ask=row["ask"],
                mid=row["mid"],
                spread=row["spread"],
                bid_size=row["bid_size"],
                ask_size=row["ask_size"],
                last_price=row["last_price"],
                last_size=row["last_size"],
                volume=row["volume"]
            )
            for row in rows
        ]
    
    def query_orders(
        self,
        client_id: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[OrderRecord]:
        """Query historical orders"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM orders WHERE 1=1"
        params = []
        
        if client_id:
            query += " AND client_id = ?"
            params.append(client_id)
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            OrderRecord(
                order_id=row["order_id"],
                client_id=row["client_id"],
                symbol=row["symbol"],
                side=row["side"],
                order_type=row["order_type"],
                price=row["price"],
                size=row["size"],
                timestamp=row["timestamp"],
                status=row["status"],
                filled_size=row["filled_size"],
                avg_fill_price=row["avg_fill_price"]
            )
            for row in rows
        ]
    
    def query_fills(
        self,
        client_id: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[FillRecord]:
        """Query historical fills"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM fills WHERE 1=1"
        params = []
        
        if client_id:
            query += " AND client_id = ?"
            params.append(client_id)
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            FillRecord(
                fill_id=row["fill_id"],
                order_id=row["order_id"],
                client_id=row["client_id"],
                symbol=row["symbol"],
                side=row["side"],
                price=row["price"],
                size=row["size"],
                timestamp=row["timestamp"],
                trade_id=row["trade_id"]
            )
            for row in rows
        ]


class PostgreSQLDatabase(DatabaseInterface):
    """
    PostgreSQL/TimescaleDB implementation (for production)
    Requires: psycopg2 or asyncpg
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "trading",
        user: str = "postgres",
        password: str = ""
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            import psycopg2
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.create_tables()
        except ImportError:
            raise ImportError("psycopg2 required for PostgreSQL. Install: pip install psycopg2-binary")
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create required tables with TimescaleDB hypertable"""
        cursor = self.conn.cursor()
        
        # Create ticks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                timestamp TIMESTAMPTZ NOT NULL,
                symbol TEXT NOT NULL,
                bid DOUBLE PRECISION,
                ask DOUBLE PRECISION,
                mid DOUBLE PRECISION,
                spread DOUBLE PRECISION,
                bid_size DOUBLE PRECISION,
                ask_size DOUBLE PRECISION,
                last_price DOUBLE PRECISION,
                last_size DOUBLE PRECISION,
                volume DOUBLE PRECISION
            )
        """)
        
        # Convert to TimescaleDB hypertable (if TimescaleDB is installed)
        try:
            cursor.execute("""
                SELECT create_hypertable('ticks', 'timestamp', 
                                        if_not_exists => TRUE)
            """)
        except:
            # Not TimescaleDB, just create regular index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticks_time_symbol 
                ON ticks(timestamp, symbol)
            """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                client_id TEXT,
                symbol TEXT,
                side TEXT,
                order_type TEXT,
                price DOUBLE PRECISION,
                size INTEGER,
                timestamp TIMESTAMPTZ,
                status TEXT,
                filled_size INTEGER,
                avg_fill_price DOUBLE PRECISION
            )
        """)
        
        # Fills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fills (
                fill_id TEXT PRIMARY KEY,
                order_id TEXT,
                client_id TEXT,
                symbol TEXT,
                side TEXT,
                price DOUBLE PRECISION,
                size INTEGER,
                timestamp TIMESTAMPTZ,
                trade_id TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_client_time 
            ON orders(client_id, timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fills_order 
            ON fills(order_id)
        """)
        
        self.conn.commit()
    
    def insert_tick(self, tick: TickData):
        """Insert market tick data"""
        from datetime import datetime
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ticks 
            (timestamp, symbol, bid, ask, mid, spread, bid_size, ask_size,
             last_price, last_size, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datetime.fromtimestamp(tick.timestamp), tick.symbol,
            tick.bid, tick.ask, tick.mid, tick.spread,
            tick.bid_size, tick.ask_size, tick.last_price,
            tick.last_size, tick.volume
        ))
        self.conn.commit()
    
    def insert_order(self, order: OrderRecord):
        """Insert order record"""
        from datetime import datetime
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO orders
            (order_id, client_id, symbol, side, order_type, price, size,
             timestamp, status, filled_size, avg_fill_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO UPDATE SET
                status = EXCLUDED.status,
                filled_size = EXCLUDED.filled_size,
                avg_fill_price = EXCLUDED.avg_fill_price
        """, (
            order.order_id, order.client_id, order.symbol, order.side,
            order.order_type, order.price, order.size,
            datetime.fromtimestamp(order.timestamp), order.status,
            order.filled_size, order.avg_fill_price
        ))
        self.conn.commit()
    
    def insert_fill(self, fill: FillRecord):
        """Insert fill record"""
        from datetime import datetime
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO fills
            (fill_id, order_id, client_id, symbol, side, price, size,
             timestamp, trade_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            fill.fill_id, fill.order_id, fill.client_id, fill.symbol,
            fill.side, fill.price, fill.size,
            datetime.fromtimestamp(fill.timestamp), fill.trade_id
        ))
        self.conn.commit()
    
    def query_ticks(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[TickData]:
        """Query historical tick data"""
        from datetime import datetime
        cursor = self.conn.cursor()
        query = "SELECT * FROM ticks WHERE symbol = %s"
        params = [symbol]
        
        if start_time:
            query += " AND timestamp >= %s"
            params.append(datetime.fromtimestamp(start_time))
        if end_time:
            query += " AND timestamp <= %s"
            params.append(datetime.fromtimestamp(end_time))
        
        query += " ORDER BY timestamp"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to TickData objects
        # (Implementation depends on cursor row format)
        return []  # Placeholder
    
    def query_orders(
        self,
        client_id: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[OrderRecord]:
        """Query historical orders"""
        # Similar implementation
        return []
    
    def query_fills(
        self,
        client_id: Optional[str] = None,
        symbol: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[FillRecord]:
        """Query historical fills"""
        # Similar implementation
        return []
