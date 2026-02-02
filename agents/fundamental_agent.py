"""
Fundamental Signal Agent - Real Rates, ETF Flows, Inflation Surprises
"""
from typing import Dict, Any, Optional
import numpy as np

from .base_agent import BaseAgent
from data_sources.fred_client import FREDClient
from data_sources.etf_client import ETFClient


class FundamentalAgent(BaseAgent):
    """Agent for fundamental analysis"""
    
    def __init__(self, commodity: str = "gold"):
        super().__init__("FundamentalAgent", commodity)
        self.fred_client = FREDClient()
        self.etf_client = ETFClient()
    
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch fundamental data"""
        data = {}
        
        # Real rates
        real_rate = self.fred_client.calculate_real_rates()
        data["real_rate"] = real_rate
        
        # Treasury rates trend
        treasury_10y = self.fred_client.get_10y_treasury(days=90)
        if not treasury_10y.empty and len(treasury_10y) >= 30:
            data["treasury_trend"] = float(
                (treasury_10y.iloc[-1] / treasury_10y.iloc[-30] - 1) * 100
            )
        
        # Inflation data (optimized - 6 months is enough)
        cpi = self.fred_client.get_cpi(days=180)
        if not cpi.empty and len(cpi) >= 12:
            latest_cpi = cpi.iloc[-1]
            year_ago_cpi = cpi.iloc[-12]
            data["inflation_yoy"] = float(((latest_cpi / year_ago_cpi) - 1) * 100)
            
            # Calculate inflation surprise (vs 2% target)
            data["inflation_surprise"] = data["inflation_yoy"] - 2.0
        
        # ETF flows
        if self.commodity == "gold":
            etf_data = self.etf_client.get_etf_data("gold")
        elif self.commodity == "silver":
            etf_data = self.etf_client.get_etf_data("silver")
        else:
            etf_data = {}
        
        if etf_data:
            data["etf_flow_momentum"] = etf_data.get("flow_momentum", 0.0)
            data["etf_price_change"] = etf_data.get("price_change_30d", 0.0)
        
        return data
    
    def analyze(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze fundamental signals"""
        if data is None:
            data = self.fetch_data()
        
        signals = []
        drivers = []
        confidence_factors = []
        
        # Real rates pressure (most important for gold)
        if data.get("real_rate") is not None:
            real_rate = data["real_rate"]
            # Negative real rates are very bullish for gold
            if real_rate < -1.0:
                signals.append(1.0)  # Very bullish
                drivers.append("Strongly negative real rates")
                confidence_factors.append(0.35)
            elif real_rate < 0:
                signals.append(0.8)  # Bullish
                drivers.append("Negative real rates")
                confidence_factors.append(0.3)
            elif real_rate < 1.0:
                signals.append(0.3)  # Mildly bullish
                confidence_factors.append(0.2)
            elif real_rate > 2.5:
                signals.append(-0.8)  # Bearish
                drivers.append("High real rates pressure")
                confidence_factors.append(0.3)
            else:
                signals.append(0.0)
                confidence_factors.append(0.15)
        
        # Treasury trend
        if "treasury_trend" in data:
            treasury_trend = data["treasury_trend"]
            if treasury_trend < -0.5:
                signals.append(0.6)  # Falling rates = bullish
                drivers.append("Falling Treasury yields")
                confidence_factors.append(0.2)
            elif treasury_trend > 0.5:
                signals.append(-0.6)  # Rising rates = bearish
                drivers.append("Rising Treasury yields")
                confidence_factors.append(0.2)
        
        # Inflation surprise
        if "inflation_surprise" in data:
            inflation_surprise = data["inflation_surprise"]
            if inflation_surprise > 1.0:
                signals.append(0.5)  # High inflation = bullish for gold
                drivers.append("Elevated inflation")
                confidence_factors.append(0.2)
            elif inflation_surprise < -0.5:
                signals.append(-0.3)  # Low inflation = slightly bearish
                confidence_factors.append(0.15)
        
        # ETF flow momentum
        if "etf_flow_momentum" in data:
            flow_momentum = data["etf_flow_momentum"]
            if flow_momentum > 5:
                signals.append(0.7)  # Strong inflows
                drivers.append("Strong ETF inflows")
                confidence_factors.append(0.25)
            elif flow_momentum < -5:
                signals.append(-0.7)  # Strong outflows
                drivers.append("ETF outflows")
                confidence_factors.append(0.25)
            elif flow_momentum > 2:
                signals.append(0.4)
                confidence_factors.append(0.15)
            elif flow_momentum < -2:
                signals.append(-0.4)
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
        data_quality = min(1.0, len([k for k in data.keys() if data.get(k) is not None]) / 5.0)
        confidence = base_confidence * data_quality
        
        return {
            "signal": signal,
            "confidence": confidence,
            "drivers": drivers[:3],
            "metadata": {
                "weighted_signal": weighted_signal,
                "real_rate": data.get("real_rate"),
                "inflation_surprise": data.get("inflation_surprise"),
                "etf_momentum": data.get("etf_flow_momentum"),
            }
        }

