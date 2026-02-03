"""
Correlation & Spread Agent - Gold-Silver Ratio, Cross-Asset Correlations
"""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .base_agent import BaseAgent
from data_sources.yahoo_client import YahooClient


class CorrelationAgent(BaseAgent):
    """Agent for analyzing correlations and spreads"""
    
    def __init__(self, commodity: str = "both"):
        super().__init__("CorrelationAgent", commodity)
        self.yahoo_client = YahooClient()
    
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch data for correlation analysis"""
        data = {}
        
        # Gold and Silver prices
        gold_data = self.yahoo_client.get_gold_price(period="90d")
        silver_data = self.yahoo_client.get_silver_price(period="90d")
        
        if not gold_data.empty and not silver_data.empty:
            gold_prices = gold_data["Close"]
            silver_prices = silver_data["Close"]
            
            # Align dates
            common_dates = gold_prices.index.intersection(silver_prices.index)
            if len(common_dates) > 0:
                gold_aligned = gold_prices.loc[common_dates]
                silver_aligned = silver_prices.loc[common_dates]
                
                # Gold-Silver ratio
                ratio = gold_aligned / silver_aligned
                data["gs_ratio"] = float(ratio.iloc[-1])
                data["gs_ratio_30d_avg"] = float(ratio.tail(30).mean())
                data["gs_ratio_change"] = float(
                    (ratio.iloc[-1] / ratio.iloc[-30] - 1) * 100
                ) if len(ratio) >= 30 else 0.0
                
                # Correlation
                if len(gold_aligned) >= 30:
                    correlation = gold_aligned.tail(30).corr(silver_aligned.tail(30))
                    data["gs_correlation"] = float(correlation)
        
        # USD correlation
        dxy_data = self.yahoo_client.get_dxy(period="90d")
        if not gold_data.empty and not dxy_data.empty:
            gold_prices = gold_data["Close"]
            dxy_prices = dxy_data["Close"]
            
            common_dates = gold_prices.index.intersection(dxy_prices.index)
            if len(common_dates) >= 30:
                gold_aligned = gold_prices.loc[common_dates].tail(30)
                dxy_aligned = dxy_prices.loc[common_dates].tail(30)
                correlation = gold_aligned.corr(dxy_aligned)
                data["gold_dxy_correlation"] = float(correlation)
        
        # Silver-Copper correlation (industrial demand proxy)
        copper_data = self.yahoo_client.get_copper_price(period="90d")
        if not silver_data.empty and not copper_data.empty:
            silver_prices = silver_data["Close"]
            copper_prices = copper_data["Close"]
            
            common_dates = silver_prices.index.intersection(copper_prices.index)
            if len(common_dates) >= 30:
                silver_aligned = silver_prices.loc[common_dates].tail(30)
                copper_aligned = copper_prices.loc[common_dates].tail(30)
                correlation = silver_aligned.corr(copper_aligned)
                data["silver_copper_correlation"] = float(correlation)
        
        return data
    
    def analyze(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze correlation signals"""
        if data is None:
            data = self.fetch_data()
        
        signals = []
        drivers = []
        confidence_factors = []
        
        # Gold-Silver ratio analysis
        if "gs_ratio" in data and "gs_ratio_30d_avg" in data:
            ratio = data["gs_ratio"]
            ratio_avg = data["gs_ratio_30d_avg"]
            
            # Historical range: ~50-100, average ~70-80
            # High ratio (>85) = silver relatively cheap = potential silver catch-up
            # Low ratio (<65) = gold relatively cheap = potential gold catch-up
            
            if ratio > 85:
                # Silver may be undervalued relative to gold
                if self.commodity == "silver":
                    signals.append(0.6)  # Bullish for silver
                    drivers.append("Gold-Silver ratio elevated (silver catch-up potential)")
                    confidence_factors.append(0.3)
                elif self.commodity == "gold":
                    signals.append(-0.3)  # Slightly bearish for gold
                    confidence_factors.append(0.15)
            elif ratio < 65:
                # Gold may be undervalued relative to silver
                if self.commodity == "gold":
                    signals.append(0.6)  # Bullish for gold
                    drivers.append("Gold-Silver ratio low (gold catch-up potential)")
                    confidence_factors.append(0.3)
                elif self.commodity == "silver":
                    signals.append(-0.3)  # Slightly bearish for silver
                    confidence_factors.append(0.15)
            
            # Ratio momentum
            if "gs_ratio_change" in data:
                ratio_change = data["gs_ratio_change"]
                if abs(ratio_change) > 5:
                    if ratio_change > 0 and self.commodity == "silver":
                        signals.append(0.4)  # Ratio expanding = silver lagging = catch-up
                        drivers.append("Gold-Silver ratio expanding")
                        confidence_factors.append(0.2)
                    elif ratio_change < 0 and self.commodity == "gold":
                        signals.append(0.4)  # Ratio contracting = gold lagging = catch-up
                        drivers.append("Gold-Silver ratio contracting")
                        confidence_factors.append(0.2)
        
        # USD correlation (negative correlation expected)
        if "gold_dxy_correlation" in data:
            correlation = data["gold_dxy_correlation"]
            # If correlation becomes less negative or positive, it's unusual
            if correlation > -0.3:
                signals.append(-0.3)  # Weakening negative correlation
                drivers.append("Weakening gold-USD negative correlation")
                confidence_factors.append(0.15)
        
        # Silver-Copper correlation (positive correlation expected for industrial demand)
        if "silver_copper_correlation" in data and self.commodity == "silver":
            correlation = data["silver_copper_correlation"]
            if correlation > 0.7:
                signals.append(0.3)  # Strong industrial demand signal
                drivers.append("Strong silver-copper correlation (industrial demand)")
                confidence_factors.append(0.2)
            elif correlation < 0.3:
                signals.append(-0.2)  # Weak industrial demand
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
        data_quality = min(1.0, len([k for k in data.keys() if data.get(k) is not None]) / 4.0)
        confidence = base_confidence * data_quality * 0.8  # Correlation signals typically lower confidence
        
        return {
            "signal": signal,
            "confidence": confidence,
            "drivers": drivers[:3],
            "metadata": {
                "weighted_signal": weighted_signal,
                "gs_ratio": data.get("gs_ratio"),
                "gs_ratio_change": data.get("gs_ratio_change"),
                "gold_dxy_correlation": data.get("gold_dxy_correlation"),
            }
        }



