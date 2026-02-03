"""
ETF Flow and Holdings Client
"""
from typing import Dict, Optional
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from config import DATA_SOURCES


class ETFClient:
    """Client for ETF holdings and flow analysis"""
    
    def __init__(self):
        self.cache = {}
    
    def get_etf_holdings(self, symbol: str, days: int = 90) -> pd.DataFrame:
        """
        Get ETF price data (proxy for holdings/flows)
        In production, would fetch actual holdings from ETF provider
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=f"{max(days, 90)}d")
            return data
        except Exception as e:
            print(f"Error fetching ETF {symbol}: {e}")
            return pd.DataFrame()
    
    def get_gld_flow_momentum(self, days: int = 30) -> float:
        """
        Calculate GLD flow momentum
        Positive = inflows (bullish for gold)
        """
        data = self.get_etf_holdings("GLD", days=days + 10)
        if data.empty or len(data) < days:
            return 0.0
        
        # Use volume as proxy for flow activity
        recent_volume = data["Volume"].tail(days).mean()
        older_volume = data["Volume"].head(len(data) - days).mean() if len(data) > days else recent_volume
        
        # Price momentum
        price_change = (data["Close"].iloc[-1] / data["Close"].iloc[-days] - 1) * 100
        
        # Combined momentum signal
        volume_momentum = (recent_volume / older_volume - 1) if older_volume > 0 else 0
        momentum = (price_change * 0.7) + (volume_momentum * 30 * 0.3)
        
        return momentum
    
    def get_slv_flow_momentum(self, days: int = 30) -> float:
        """Calculate SLV flow momentum"""
        data = self.get_etf_holdings("SLV", days=days + 10)
        if data.empty or len(data) < days:
            return 0.0
        
        recent_volume = data["Volume"].tail(days).mean()
        older_volume = data["Volume"].head(len(data) - days).mean() if len(data) > days else recent_volume
        
        price_change = (data["Close"].iloc[-1] / data["Close"].iloc[-days] - 1) * 100
        
        volume_momentum = (recent_volume / older_volume - 1) if older_volume > 0 else 0
        momentum = (price_change * 0.7) + (volume_momentum * 30 * 0.3)
        
        return momentum
    
    def get_etf_data(self, commodity: str) -> Dict:
        """Get comprehensive ETF data for commodity"""
        if commodity.lower() == "gold":
            symbol = "GLD"
            momentum = self.get_gld_flow_momentum()
        elif commodity.lower() == "silver":
            symbol = "SLV"
            momentum = self.get_slv_flow_momentum()
        else:
            return {}
        
        data = self.get_etf_holdings(symbol, days=90)
        if data.empty:
            return {}
        
        return {
            "symbol": symbol,
            "current_price": float(data["Close"].iloc[-1]),
            "flow_momentum": momentum,
            "volume_30d_avg": float(data["Volume"].tail(30).mean()),
            "price_change_30d": float((data["Close"].iloc[-1] / data["Close"].iloc[-30] - 1) * 100),
        }



