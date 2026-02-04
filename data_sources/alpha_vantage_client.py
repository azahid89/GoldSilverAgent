"""
Alpha Vantage Client for market data
"""
from typing import Dict, Optional, Any
import pandas as pd
import requests
from datetime import datetime, timedelta
import os

from config import ALPHA_VANTAGE_API_KEY
from utils.cache import cache

class AlphaVantageClient:
    """Client for fetching Alpha Vantage data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        
        if not self.api_key:
            print("Warning: Alpha Vantage API key not found. Set ALPHA_VANTAGE_API_KEY in .env")
    
    def get_fx_ohlc(self, from_symbol: str, to_symbol: str = "USD") -> pd.DataFrame:
        """Get daily FX OHLC data (XAU and XAG are treated as FX)"""
        if not self.api_key:
            return pd.DataFrame()
            
        cache_key = f"av_fx_{from_symbol}_{to_symbol}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            params = {
                "function": "FX_DAILY",
                "from_symbol": from_symbol,
                "to_symbol": to_symbol,
                "outputsize": "compact",
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            time_series_key = "Time Series FX (Daily)"
            if time_series_key not in data:
                print(f"Error fetching Alpha Vantage FX data: {data.get('Error Message', data.get('Note', 'Unknown error'))}")
                return pd.DataFrame()
                
            df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
            df.index = pd.to_datetime(df.index)
            df.columns = [c.split('. ')[1] for c in df.columns]
            df = df.apply(pd.to_numeric)
            df.sort_index(inplace=True)
            
            # Simple column mapping to match expected format
            if 'close' in df.columns:
                df['value'] = df['close']
            
            # Cache for 1 day
            cache.set(cache_key, df, ttl_seconds=86400)
            return df
        except Exception as e:
            print(f"Alpha Vantage FX fetch error: {e}")
            return pd.DataFrame()

    def get_gold_daily(self) -> pd.DataFrame:
        """Get daily Gold price from Alpha Vantage"""
        return self.get_fx_ohlc("XAU")

    def get_silver_daily(self) -> pd.DataFrame:
        """Get daily Silver price from Alpha Vantage"""
        return self.get_fx_ohlc("XAG")
    
    def get_sentiment(self, tickers: str = "GLD,SLV") -> Dict[str, Any]:
        """Get news sentiment for specific tickers (GLD/SLV are better for news volume)"""
        if not self.api_key:
            return {}
            
        cache_key = f"av_sentiment_{tickers}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
            
        try:
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": tickers,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            # Cache for 1 hour
            cache.set(cache_key, data, ttl_seconds=3600)
            return data
        except Exception as e:
            print(f"Alpha Vantage sentiment error: {e}")
            return {}
