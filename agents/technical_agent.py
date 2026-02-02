"""
Technical Signal Agent - RSI, MACD, EMA, Support/Resistance
"""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .base_agent import BaseAgent
from data_sources.yahoo_client import YahooClient


class TechnicalAgent(BaseAgent):
    """Agent for technical analysis signals"""
    
    def __init__(self, commodity: str = "gold"):
        super().__init__("TechnicalAgent", commodity)
        self.yahoo_client = YahooClient()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not rsi.empty else 50.0
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD"""
        if len(prices) < slow + signal:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd": float(macd_line.iloc[-1]),
            "signal": float(signal_line.iloc[-1]),
            "histogram": float(histogram.iloc[-1])
        }
    
    def _calculate_ema(self, prices: pd.Series, period: int = 50) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return float(prices.iloc[-1])
        return float(prices.ewm(span=period, adjust=False).mean().iloc[-1])
    
    def _identify_support_resistance(self, prices: pd.Series, window: int = 20) -> Dict[str, float]:
        """Identify support and resistance levels"""
        if len(prices) < window:
            current = float(prices.iloc[-1])
            return {"support": current * 0.95, "resistance": current * 1.05}
        
        recent = prices.tail(window)
        support = float(recent.min())
        resistance = float(recent.max())
        current = float(prices.iloc[-1])
        
        # Distance to support/resistance
        dist_to_support = ((current - support) / support) * 100
        dist_to_resistance = ((resistance - current) / current) * 100
        
        return {
            "support": support,
            "resistance": resistance,
            "current": current,
            "dist_to_support": dist_to_support,
            "dist_to_resistance": dist_to_resistance
        }
    
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch price data for technical analysis"""
        if self.commodity == "gold":
            price_data = self.yahoo_client.get_gold_price(period="6mo")
        elif self.commodity == "silver":
            price_data = self.yahoo_client.get_silver_price(period="6mo")
        else:
            return {}
        
        if price_data.empty:
            return {}
        
        prices = price_data["Close"]
        
        data = {
            "prices": prices,
            "current_price": float(prices.iloc[-1]),
        }
        
        # Calculate indicators
        data["rsi"] = self._calculate_rsi(prices)
        data["macd"] = self._calculate_macd(prices)
        data["ema_50"] = self._calculate_ema(prices, period=50)
        data["ema_200"] = self._calculate_ema(prices, period=200) if len(prices) >= 200 else data["current_price"]
        data["support_resistance"] = self._identify_support_resistance(prices)
        
        return data
    
    def analyze(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze technical signals"""
        if data is None:
            data = self.fetch_data()
        
        if not data or "prices" not in data:
            return {
                "signal": "neutral",
                "confidence": 0.0,
                "drivers": [],
                "metadata": {}
            }
        
        signals = []
        drivers = []
        confidence_factors = []
        
        # RSI analysis
        rsi = data.get("rsi", 50.0)
        if rsi < 30:
            signals.append(0.7)  # Oversold = bullish
            drivers.append("RSI oversold")
            confidence_factors.append(0.25)
        elif rsi > 70:
            signals.append(-0.7)  # Overbought = bearish
            drivers.append("RSI overbought")
            confidence_factors.append(0.25)
        elif 40 < rsi < 60:
            signals.append(0.0)  # Neutral
            confidence_factors.append(0.1)
        
        # MACD analysis
        macd_data = data.get("macd", {})
        histogram = macd_data.get("histogram", 0.0)
        if histogram > 0:
            signals.append(0.5)  # Bullish momentum
            drivers.append("MACD bullish crossover")
            confidence_factors.append(0.2)
        elif histogram < 0:
            signals.append(-0.5)  # Bearish momentum
            drivers.append("MACD bearish crossover")
            confidence_factors.append(0.2)
        
        # EMA trend analysis
        current = data["current_price"]
        ema_50 = data.get("ema_50", current)
        ema_200 = data.get("ema_200", current)
        
        if current > ema_50 > ema_200:
            signals.append(0.6)  # Strong uptrend
            drivers.append("Price above key EMAs (bullish trend)")
            confidence_factors.append(0.25)
        elif current < ema_50 < ema_200:
            signals.append(-0.6)  # Strong downtrend
            drivers.append("Price below key EMAs (bearish trend)")
            confidence_factors.append(0.25)
        elif current > ema_50:
            signals.append(0.3)  # Mild bullish
            confidence_factors.append(0.15)
        else:
            signals.append(-0.3)  # Mild bearish
            confidence_factors.append(0.15)
        
        # Support/Resistance analysis
        sr = data.get("support_resistance", {})
        dist_to_support = sr.get("dist_to_support", 0)
        dist_to_resistance = sr.get("dist_to_resistance", 0)
        
        if dist_to_support < 2:
            signals.append(0.4)  # Near support = potential bounce
            drivers.append("Near support level")
            confidence_factors.append(0.15)
        elif dist_to_resistance < 2:
            signals.append(-0.4)  # Near resistance = potential rejection
            drivers.append("Near resistance level")
            confidence_factors.append(0.15)
        
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
        confidence = base_confidence * 0.9  # Technical analysis typically lower confidence
        
        return {
            "signal": signal,
            "confidence": confidence,
            "drivers": drivers[:3],
            "metadata": {
                "weighted_signal": weighted_signal,
                "rsi": rsi,
                "macd_histogram": histogram,
                "price_vs_ema50": ((current / ema_50) - 1) * 100 if ema_50 > 0 else 0,
            }
        }

