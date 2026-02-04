"""
Nasdaq Data Link (formerly Quandl) Client
"""
from typing import Dict, Optional, Any
import pandas as pd
try:
    import nasdaq_data_link
except ImportError:
    nasdaq_data_link = None
import os

from config import NASDAQ_DATA_LINK_API_KEY
from utils.cache import cache

class NasdaqClient:
    """Client for fetching Nasdaq Data Link data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or NASDAQ_DATA_LINK_API_KEY
        if nasdaq_data_link and self.api_key:
            nasdaq_data_link.read_config().set_api_key(self.api_key)
        elif not self.api_key:
            print("Warning: Nasdaq Data Link API key not found. Set NASDAQ_DATA_LINK_API_KEY in .env")
            
    def get_data(self, dataset: str, cache_ttl: int = 86400) -> pd.DataFrame:
        """Generic method to fetch data from Nasdaq Data Link"""
        if not nasdaq_data_link or not self.api_key:
            return pd.DataFrame()
            
        cache_key = f"nasdaq_{dataset.replace('/', '_')}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            data = nasdaq_data_link.get(dataset)
            cache.set(cache_key, data, ttl_seconds=cache_ttl)
            return data
        except Exception as e:
            print(f"Nasdaq Data Link error for {dataset}: {e}")
            return pd.DataFrame()

    def get_gold_cot(self) -> pd.DataFrame:
        """
        Get Gold Commitment of Traders (COT) report
        CFTC/067651_F_ALL - Gold COMEX (Legacy Format)
        """
        return self.get_data("CFTC/067651_F_ALL")

    def get_silver_cot(self) -> pd.DataFrame:
        """
        Get Silver Commitment of Traders (COT) report
        CFTC/084691_F_ALL - Silver COMEX (Legacy Format)
        """
        return self.get_data("CFTC/084691_F_ALL")

    def get_lbma_gold(self) -> pd.DataFrame:
        """Get LBMA Gold Price"""
        return self.get_data("LBMA/GOLD")

    def get_lbma_silver(self) -> pd.DataFrame:
        """Get LBMA Silver Price"""
        return self.get_data("LBMA/SILVER")
