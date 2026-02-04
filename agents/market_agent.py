"""
Market Data Agent - Price, Volatility, ETF Flows
"""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .base_agent import BaseAgent
from data_sources.yahoo_client import YahooClient
from data_sources.etf_client import ETFClient


class MarketAgent(BaseAgent):
    """Agent for analyzing market data and flows"""
    
    def __init__(self, commodity: str = "gold"):
        super().__init__("MarketAgent", commodity)
        self.yahoo_client = YahooClient()
        self.etf_client = ETFClient()
    
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch market data"""
        data = {}
        
        if self.commodity == "gold":
            price_data = self.yahoo_client.get_gold_price(period="90d")
            vol_data = self.yahoo_client.get_gold_volatility(period="90d")
            etf_data = self.etf_client.get_etf_data("gold")
        elif self.commodity == "silver":
            price_data = self.yahoo_client.get_silver_price(period="90d")
            vol_data = self.yahoo_client.get_silver_volatility(period="90d")
            etf_data = self.etf_client.get_etf_data("silver")
        else:
            return data
        
        if not price_data.empty:
            data["current_price"] = float(price_data["Close"].iloc[-1])
            data["price_7d_change"] = float(
                (price_data["Close"].iloc[-1] / price_data["Close"].iloc[-7] - 1) * 100
            ) if len(price_data) >= 7 else 0.0
            data["price_30d_change"] = float(
                (price_data["Close"].iloc[-1] / price_data["Close"].iloc[-30] - 1) * 100
            ) if len(price_data) >= 30 else 0.0
            data["volume_30d_avg"] = float(price_data["Volume"].tail(30).mean())
        
        if not vol_data.empty:
            data["volatility"] = float(vol_data["Close"].iloc[-1])
            data["volatility_30d_avg"] = float(vol_data["Close"].tail(30).mean())
        
        if etf_data:
            data["etf_flow_momentum"] = etf_data.get("flow_momentum", 0.0)
            data["etf_price_change"] = etf_data.get("price_change_30d", 0.0)
        
        return data
    
    def analyze(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze market signals"""
        if data is None:
            data = self.fetch_data()
        
        if not data:
            return {
                "signal": "neutral",
                "confidence": 0.0,
                "drivers": [],
                "metadata": {}
            }
        
        signals = []
        drivers = []
        confidence_factors = []
        
        # Price momentum
        if "price_7d_change" in data:
            price_change_7d = data["price_7d_change"]
            if price_change_7d > 2:
                signals.append(0.7)
                drivers.append("Strong 7-day price momentum")
                confidence_factors.append(0.3)
            elif price_change_7d < -2:
                signals.append(-0.7)
                drivers.append("Weak 7-day price momentum")
                confidence_factors.append(0.3)
        
        if "price_30d_change" in data:
            price_change_30d = data["price_30d_change"]
            if price_change_30d > 5:
                signals.append(0.8)
                drivers.append("Strong 30-day uptrend")
                confidence_factors.append(0.25)
            elif price_change_30d < -5:
                signals.append(-0.8)
                drivers.append("Weak 30-day downtrend")
                confidence_factors.append(0.25)
        
        # ETF flow momentum
        if "etf_flow_momentum" in data:
            flow_momentum = data["etf_flow_momentum"]
            if flow_momentum > 3:
                signals.append(0.6)
                drivers.append("Strong ETF inflows")
                confidence_factors.append(0.25)
            elif flow_momentum < -3:
                signals.append(-0.6)
                drivers.append("ETF outflows")
                confidence_factors.append(0.25)
        
        # Volatility analysis
        if "volatility" in data and "volatility_30d_avg" in data:
            vol = data["volatility"]
            vol_avg = data["volatility_30d_avg"]
            if vol > vol_avg * 1.2:
                # High volatility can indicate uncertainty (neutral to slightly bearish)
                signals.append(-0.2)
                confidence_factors.append(0.1)
            elif vol < vol_avg * 0.8:
                # Low volatility can indicate stability (slightly bullish)
                signals.append(0.2)
                confidence_factors.append(0.1)
        
        # Calculate weighted signal
        if signals:
            total_weight = sum(confidence_factors) if confidence_factors else 1.0
            if total_weight > 0:
                weighted_signal = sum(s * w for s, w in zip(signals, confidence_factors)) / total_weight
            else:
                weighted_signal = 0.0
        else:
            weighted_signal = 0.0
        
        signal = self._normalize_signal(weighted_signal, bullish_threshold=0.3, bearish_threshold=-0.3)
        
        base_confidence = min(100, abs(weighted_signal) * 100)
        data_quality = min(1.0, len([k for k in data.keys() if data.get(k) is not None]) / 6.0)
        confidence = base_confidence * data_quality
        
        return {
            "signal": signal,
            "confidence": confidence,
            "drivers": drivers[:3],
            "metadata": {
                "weighted_signal": weighted_signal,
                "price_change_7d": data.get("price_7d_change"),
                "price_change_30d": data.get("price_30d_change"),
                "etf_momentum": data.get("etf_flow_momentum"),
            }
        }





