"""
FRED (Federal Reserve Economic Data) Client
"""
from typing import Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
try:
    from fredapi import Fred
except ImportError:
    Fred = None

from config import FRED_API_KEY
from utils.cache import cache


class FREDClient:
    """Client for fetching FRED economic data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or FRED_API_KEY
        if Fred and self.api_key:
            self.client = Fred(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: FRED client not initialized. Set FRED_API_KEY in .env")
    
    def get_10y_treasury(self, days: int = 365) -> pd.Series:
        """Get 10-Year Treasury Rate (with caching)"""
        if not self.client:
            return pd.Series()
        
        cache_key = f"fred_dgs10_{days}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = self.client.get_series("DGS10", start=start_date, end=end_date)
            # Cache for 5 minutes
            cache.set(cache_key, data, ttl_seconds=300)
            return data
        except Exception as e:
            print(f"Error fetching 10Y Treasury: {e}")
            # Cache empty result for 1 minute
            cache.set(cache_key, pd.Series(), ttl_seconds=60)
            return pd.Series()
    
    def get_tips(self, days: int = 365) -> pd.Series:
        """Get 10-Year TIPS (Real Rates proxy)"""
        if not self.client:
            return pd.Series()
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = self.client.get_series("DFII10", start=start_date, end=end_date)
            return data
        except Exception as e:
            print(f"Error fetching TIPS: {e}")
            return pd.Series()
    
    def get_cpi(self, days: int = 365) -> pd.Series:
        """Get Consumer Price Index (with caching)"""
        if not self.client:
            return pd.Series()
        
        cache_key = f"fred_cpi_{days}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = self.client.get_series("CPIAUCSL", start=start_date, end=end_date)
            # Cache for 1 hour (CPI updates monthly)
            cache.set(cache_key, data, ttl_seconds=3600)
            return data
        except Exception as e:
            print(f"Error fetching CPI: {e}")
            cache.set(cache_key, pd.Series(), ttl_seconds=60)
            return pd.Series()
    
    def get_pce(self, days: int = 365) -> pd.Series:
        """Get Personal Consumption Expenditures Price Index"""
        if not self.client:
            return pd.Series()
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = self.client.get_series("PCEPI", start=start_date, end=end_date)
            return data
        except Exception as e:
            print(f"Error fetching PCE: {e}")
            return pd.Series()
    
    def get_series(self, series_id: str, days: int = 365, cache_ttl: int = 3600) -> pd.Series:
        """Generic method to fetch any FRED series with caching"""
        if not self.client:
            return pd.Series()
        
        cache_key = f"fred_{series_id}_{days}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
            
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = self.client.get_series(series_id, start=start_date, end=end_date)
            cache.set(cache_key, data, ttl_seconds=cache_ttl)
            return data
        except Exception as e:
            print(f"Error fetching FRED series {series_id}: {e}")
            cache.set(cache_key, pd.Series(), ttl_seconds=60)
            return pd.Series()

    def get_fed_balance_sheet(self, days: int = 730) -> pd.Series:
        """Get Fed Total Assets (WALCL)"""
        return self.get_series("WALCL", days=days, cache_ttl=86400)  # Weekly data

    def get_m2_money_supply(self, days: int = 730) -> pd.Series:
        """Get M2 Money Stock (M2SL)"""
        return self.get_series("M2SL", days=days, cache_ttl=86400)  # Monthly data

    def get_yield_curve(self, days: int = 365) -> pd.Series:
        """Get 10Y-2Y Treasury Yield Spread (T10Y2Y)"""
        return self.get_series("T10Y2Y", days=days, cache_ttl=3600)  # Daily data

    def get_industrial_production(self, days: int = 730) -> pd.Series:
        """Get Industrial Production (IPMAN)"""
        return self.get_series("IPMAN", days=days, cache_ttl=86400)  # Monthly data

    def calculate_real_rates(self) -> float:
        """
        Calculate real interest rates (10Y Treasury - Inflation)
        Returns latest real rate estimate (optimized)
        """
        try:
            # Use shorter periods for faster calculation
            treasury_10y = self.get_10y_treasury(days=30)
            cpi = self.get_cpi(days=180)  # 6 months is enough for YoY calculation
            
            if treasury_10y.empty or cpi.empty:
                return None
            
            # Calculate YoY inflation
            latest_cpi = cpi.iloc[-1]
            year_ago_cpi = cpi.iloc[-12] if len(cpi) >= 12 else cpi.iloc[0]
            inflation = ((latest_cpi / year_ago_cpi) - 1) * 100
            
            # Real rate = Nominal rate - Inflation
            nominal_rate = treasury_10y.iloc[-1]
            real_rate = nominal_rate - inflation
            
            return real_rate
        except Exception as e:
            print(f"Error calculating real rates: {e}")
            return None

