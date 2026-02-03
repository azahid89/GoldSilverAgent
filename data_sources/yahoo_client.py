"""
Yahoo Finance Client for market data
"""
from typing import Dict, Optional, List
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import os
import sys
from contextlib import contextmanager
import hashlib

from config import DATA_SOURCES
from utils.cache import cache

# Suppress yfinance warnings for missing/delisted symbols
warnings.filterwarnings('ignore', category=FutureWarning)


@contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output"""
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


class YahooClient:
    """Client for fetching Yahoo Finance data"""
    
    def __init__(self):
        self.cache = {}
    
    def get_price_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get price data for a symbol (with caching)"""
        # Create cache key
        cache_key = f"yahoo_{symbol}_{period}_{interval}"
        
        # Check cache first
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            # Suppress yfinance stderr output (warnings about missing symbols)
            with suppress_stderr():
                ticker = yf.Ticker(symbol)
                # Try to get data, some symbols may not be available
                # Use shorter timeout by limiting data period
                data = ticker.history(period=period, interval=interval)
            
            # Check if data is empty (symbol might not exist or be delisted)
            if data.empty:
                # Cache empty result for shorter time
                cache.set(cache_key, pd.DataFrame(), ttl_seconds=60)
                return pd.DataFrame()
            
            # Cache successful result
            cache.set(cache_key, data, ttl_seconds=300)  # 5 minutes
            return data
        except Exception:
            # Cache error for short time to avoid repeated failures
            cache.set(cache_key, pd.DataFrame(), ttl_seconds=60)
            return pd.DataFrame()
    
    def get_gold_price(self, period: str = "1y") -> pd.DataFrame:
        """Get gold futures price"""
        return self.get_price_data(DATA_SOURCES["gold"]["spot"], period=period)
    
    def get_silver_price(self, period: str = "1y") -> pd.DataFrame:
        """Get silver futures price"""
        return self.get_price_data(DATA_SOURCES["silver"]["spot"], period=period)
    
    def get_dxy(self, period: str = "1y") -> pd.DataFrame:
        """Get USD Dollar Index"""
        return self.get_price_data(DATA_SOURCES["macro"]["dxy"], period=period)
    
    def get_vix(self, period: str = "1y") -> pd.DataFrame:
        """Get VIX - tries multiple symbol variations"""
        symbols = ["^VIX", "VIX", "VIX.X"]  # Try different variations
        for symbol in symbols:
            data = self.get_price_data(symbol, period=period)
            if not data.empty:
                return data
        return pd.DataFrame()  # Return empty if none work
    
    def get_gold_volatility(self, period: str = "1y") -> pd.DataFrame:
        """Get Gold Volatility Index (GVZ) - tries multiple symbol variations"""
        symbols = ["^GVZ", "GVZ", DATA_SOURCES["gold"]["volatility"]]  # Try different variations
        for symbol in symbols:
            data = self.get_price_data(symbol, period=period)
            if not data.empty:
                return data
        return pd.DataFrame()  # Return empty if none work (volatility indices may not be available)
    
    def get_silver_volatility(self, period: str = "1y") -> pd.DataFrame:
        """Get Silver Volatility Index (SVZ) - tries multiple symbol variations"""
        symbols = ["^SVZ", "SVZ", DATA_SOURCES["silver"]["volatility"]]  # Try different variations
        for symbol in symbols:
            data = self.get_price_data(symbol, period=period)
            if not data.empty:
                return data
        return pd.DataFrame()  # Return empty if none work (volatility indices may not be available)
    
    def get_copper_price(self, period: str = "1y") -> pd.DataFrame:
        """Get copper futures price"""
        return self.get_price_data(DATA_SOURCES["macro"]["copper"], period=period)
    
    def get_platinum_price(self, period: str = "1y") -> pd.DataFrame:
        """Get platinum futures price"""
        return self.get_price_data(DATA_SOURCES["macro"]["platinum"], period=period)
    
    def get_palladium_price(self, period: str = "1y") -> pd.DataFrame:
        """Get palladium futures price"""
        return self.get_price_data(DATA_SOURCES["macro"]["palladium"], period=period)
    
    def get_bitcoin_price(self, period: str = "1y") -> pd.DataFrame:
        """Get bitcoin price"""
        return self.get_price_data(DATA_SOURCES["macro"]["bitcoin"], period=period)
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current/latest price"""
        data = self.get_price_data(symbol, period="5d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
        return None
    
    def get_returns(self, symbol: str, days: int = 30) -> pd.Series:
        """Get returns over specified days"""
        data = self.get_price_data(symbol, period=f"{max(days, 60)}d")
        if not data.empty:
            returns = data["Close"].pct_change().dropna()
            return returns.tail(days)
        return pd.Series()

