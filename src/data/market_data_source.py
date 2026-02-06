"""
Market Data Sources: Yahoo Finance, Alpha Vantage, etc.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd
import time
from datetime import datetime, timedelta


class MarketDataSource(ABC):
    """Base class for market data sources"""
    
    @abstractmethod
    def get_latest_quote(self, symbol: str) -> Dict:
        """Get latest quote (bid, ask, last, volume)"""
        pass
    
    @abstractmethod
    def get_historical_ticks(self, symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
        """Get historical tick data"""
        pass


class YahooFinanceSource(MarketDataSource):
    """
    Yahoo Finance data source using yfinance library
    """
    
    def __init__(self):
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            raise ImportError("yfinance not installed. Install with: pip install yfinance")
    
    def get_latest_quote(self, symbol: str) -> Dict:
        """Get latest quote from Yahoo Finance"""
        try:
            ticker = self.yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            hist = ticker.history(period="1d", interval="1m")
            if len(hist) > 0:
                last_price = float(hist["Close"].iloc[-1])
                volume = int(hist["Volume"].iloc[-1])
            else:
                last_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
                volume = info.get("volume", 0)
            
            # Estimate bid/ask from last price (Yahoo doesn't provide real-time L2)
            spread_pct = 0.001  # Assume 0.1% spread
            bid = last_price * (1 - spread_pct / 2)
            ask = last_price * (1 + spread_pct / 2)
            
            return {
                "symbol": symbol,
                "last_price": last_price,
                "bid": bid,
                "ask": ask,
                "mid": last_price,
                "spread": ask - bid,
                "volume": volume,
                "timestamp": time.time()
            }
        except Exception as e:
            raise Exception(f"Error fetching Yahoo Finance data for {symbol}: {e}")
    
    def get_historical_ticks(self, symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
        """Get historical tick data (converted from minute bars)"""
        try:
            ticker = self.yf.Ticker(symbol)
            
            # Get minute bars
            hist = ticker.history(start=start, end=end, interval="1m")
            
            if len(hist) == 0:
                return pd.DataFrame(columns=["timestamp", "price", "size", "side"])
            
            # Convert to tick format
            ticks = []
            for idx, row in hist.iterrows():
                # Create buy/sell ticks based on price movement
                price = float(row["Close"])
                volume = int(row["Volume"])
                
                # Distribute volume across ticks
                num_ticks = min(volume // 100, 10)  # Max 10 ticks per minute
                for i in range(num_ticks):
                    # Determine side based on price change
                    if i == 0 and len(ticks) > 0:
                        side = "buy" if price > ticks[-1]["price"] else "sell"
                    else:
                        side = "buy" if i % 2 == 0 else "sell"
                    
                    ticks.append({
                        "timestamp": idx.timestamp(),
                        "price": price + (i * 0.01),  # Small variation
                        "size": max(100, volume // num_ticks),
                        "side": side
                    })
            
            return pd.DataFrame(ticks)
        except Exception as e:
            raise Exception(f"Error fetching historical data for {symbol}: {e}")


class AlphaVantageSource(MarketDataSource):
    """
    Alpha Vantage data source
    Requires API key (free tier available)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo"  # Demo key for testing
        self.base_url = "https://www.alphavantage.co/query"
        import requests
        self.requests = requests
    
    def get_latest_quote(self, symbol: str) -> Dict:
        """Get latest quote from Alpha Vantage"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = self.requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "Global Quote" not in data:
                raise Exception(f"Alpha Vantage API error: {data}")
            
            quote = data["Global Quote"]
            
            last_price = float(quote.get("05. price", 0))
            bid = float(quote.get("03. high", last_price))  # Use high as proxy
            ask = float(quote.get("04. low", last_price))   # Use low as proxy
            
            return {
                "symbol": symbol,
                "last_price": last_price,
                "bid": bid,
                "ask": ask,
                "mid": last_price,
                "spread": abs(ask - bid),
                "volume": int(quote.get("06. volume", 0)),
                "timestamp": time.time()
            }
        except Exception as e:
            raise Exception(f"Error fetching Alpha Vantage data for {symbol}: {e}")
    
    def get_historical_ticks(self, symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
        """Get historical data (intraday)"""
        try:
            # Alpha Vantage intraday endpoint
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": "1min",
                "apikey": self.api_key,
                "outputsize": "full"
            }
            
            response = self.requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if "Time Series (1min)" not in data:
                raise Exception(f"Alpha Vantage API error: {data}")
            
            time_series = data["Time Series (1min)"]
            
            ticks = []
            for timestamp_str, values in time_series.items():
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                if start <= dt <= end:
                    price = float(values["4. close"])
                    volume = int(values["5. volume"])
                    
                    ticks.append({
                        "timestamp": dt.timestamp(),
                        "price": price,
                        "size": volume,
                        "side": "buy"  # Default, would need trade data for accuracy
                    })
            
            return pd.DataFrame(ticks).sort_values("timestamp")
        except Exception as e:
            raise Exception(f"Error fetching historical data for {symbol}: {e}")


class SyntheticSource(MarketDataSource):
    """
    Synthetic data source (fallback/default)
    """
    
    def __init__(self, base_price: float = 100.0, volatility: float = 0.02):
        self.base_price = base_price
        self.volatility = volatility
        self.current_price = base_price
        import random
        self.random = random
    
    def get_latest_quote(self, symbol: str) -> Dict:
        """Generate synthetic quote"""
        # Random walk
        self.current_price += self.random.gauss(0, self.volatility)
        
        spread = 0.02
        bid = self.current_price - spread / 2
        ask = self.current_price + spread / 2
        
        return {
            "symbol": symbol,
            "last_price": self.current_price,
            "bid": bid,
            "ask": ask,
            "mid": self.current_price,
            "spread": spread,
            "volume": self.random.randint(100, 1000),
            "timestamp": time.time()
        }
    
    def get_historical_ticks(self, symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
        """Generate synthetic historical ticks"""
        from ..backtest.replay import generate_synthetic_ticks
        
        duration = (end - start).total_seconds()
        n_ticks = int(duration / 60)  # ~1 tick per minute
        
        return generate_synthetic_ticks(
            n_ticks=n_ticks,
            initial_price=self.base_price,
            volatility=self.volatility
        )


def create_data_source(source_type: str = "synthetic", **kwargs) -> MarketDataSource:
    """
    Factory function to create data source
    
    Args:
        source_type: "yahoo", "alphavantage", or "synthetic"
        **kwargs: Source-specific parameters (api_key, base_price, etc.)
    
    Returns:
        MarketDataSource instance
    """
    if source_type.lower() == "yahoo":
        return YahooFinanceSource()
    elif source_type.lower() == "alphavantage":
        api_key = kwargs.get("api_key")
        return AlphaVantageSource(api_key=api_key)
    elif source_type.lower() == "synthetic":
        base_price = kwargs.get("base_price", 100.0)
        volatility = kwargs.get("volatility", 0.02)
        return SyntheticSource(base_price=base_price, volatility=volatility)
    else:
        raise ValueError(f"Unknown data source type: {source_type}")
