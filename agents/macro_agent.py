"""
Macro Data Agent - Fed, Rates, Inflation, USD
"""
from typing import Dict, Any, Optional
import numpy as np

from .base_agent import BaseAgent
from data_sources.fred_client import FREDClient
from data_sources.yahoo_client import YahooClient


class MacroAgent(BaseAgent):
    """Agent for analyzing macroeconomic drivers"""
    
    def __init__(self, commodity: str = "both"):
        super().__init__("MacroAgent", commodity)
        self.fred_client = FREDClient()
        self.yahoo_client = YahooClient()
    
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch macro economic data"""
        data = {}
        
        # Real rates
        real_rate = self.fred_client.calculate_real_rates()
        data["real_rate"] = real_rate
        
        # 10Y Treasury
        treasury_10y = self.fred_client.get_10y_treasury(days=90)
        if not treasury_10y.empty:
            data["treasury_10y"] = float(treasury_10y.iloc[-1])
            data["treasury_10y_change"] = float(
                (treasury_10y.iloc[-1] / treasury_10y.iloc[-30] - 1) * 100
            ) if len(treasury_10y) >= 30 else 0.0
        
        # USD Strength (DXY)
        dxy_data = self.yahoo_client.get_dxy(period="90d")
        if not dxy_data.empty:
            data["dxy"] = float(dxy_data["Close"].iloc[-1])
            data["dxy_change_30d"] = float(
                (dxy_data["Close"].iloc[-1] / dxy_data["Close"].iloc[-30] - 1) * 100
            ) if len(dxy_data) >= 30 else 0.0
        
        # Inflation (use shorter period - we only need recent data)
        cpi = self.fred_client.get_cpi(days=180)  # 6 months instead of 1 year
        if not cpi.empty and len(cpi) >= 12:
            latest_cpi = cpi.iloc[-1]
            year_ago_cpi = cpi.iloc[-12]
            data["inflation_yoy"] = float(((latest_cpi / year_ago_cpi) - 1) * 100)
        
        # VIX (risk sentiment)
        vix_data = self.yahoo_client.get_vix(period="30d")
        if not vix_data.empty:
            data["vix"] = float(vix_data["Close"].iloc[-1])

        # Fed Balance Sheet (liquidity)
        balance_sheet = self.fred_client.get_fed_balance_sheet(days=90)
        if not balance_sheet.empty and len(balance_sheet) >= 4:
            # Weekly data, look at 4-week change
            data["fed_liquidity_change"] = float(
                (balance_sheet.iloc[-1] / balance_sheet.iloc[-4] - 1) * 100
            )

        # Yield Curve (economic outlook)
        yield_curve = self.fred_client.get_yield_curve(days=30)
        if not yield_curve.empty:
            data["yield_curve"] = float(yield_curve.iloc[-1])

        # Industrial Production (for silver industrial demand)
        ind_prod = self.fred_client.get_industrial_production(days=365)
        if not ind_prod.empty and len(ind_prod) >= 3:
            # Monthly data, look at 3-month trend
            data["industrial_production_trend"] = float(
                (ind_prod.iloc[-1] / ind_prod.iloc[-3] - 1) * 100
            )
        
        return data
    
    def analyze(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze macro signals for gold/silver"""
        if data is None:
            data = self.fetch_data()
        
        signals = []
        drivers = []
        confidence_factors = []
        
        # Real rates analysis (negative correlation with gold)
        if data.get("real_rate") is not None:
            real_rate = data["real_rate"]
            # Lower real rates = bullish for gold
            if real_rate < 0:
                signals.append(1.0)  # Strong bullish
                drivers.append("Negative real rates supportive")
                confidence_factors.append(0.3)
            elif real_rate < 1.0:
                signals.append(0.5)  # Mild bullish
                drivers.append("Low real rates")
                confidence_factors.append(0.2)
            elif real_rate > 2.0:
                signals.append(-0.5)  # Bearish
                drivers.append("High real rates pressure")
                confidence_factors.append(0.2)
            else:
                signals.append(0.0)  # Neutral
                confidence_factors.append(0.1)
        
        # USD strength (negative correlation)
        if "dxy_change_30d" in data:
            dxy_change = data["dxy_change_30d"]
            if dxy_change < -2:
                signals.append(0.8)  # Bullish (weak USD)
                drivers.append("Weakening USD")
                confidence_factors.append(0.25)
            elif dxy_change > 2:
                signals.append(-0.8)  # Bearish (strong USD)
                drivers.append("Strengthening USD")
                confidence_factors.append(0.25)
            else:
                signals.append(0.0)
                confidence_factors.append(0.1)
        
        # Treasury rates change
        if "treasury_10y_change" in data:
            treasury_change = data["treasury_10y_change"]
            if treasury_change < -0.5:
                signals.append(0.6)  # Falling rates = bullish
                drivers.append("Falling Treasury yields")
                confidence_factors.append(0.2)
            elif treasury_change > 0.5:
                signals.append(-0.6)  # Rising rates = bearish
                drivers.append("Rising Treasury yields")
                confidence_factors.append(0.2)
        
        # Risk sentiment (VIX)
        if "vix" in data:
            vix = data["vix"]
            if vix > 25:
                signals.append(0.5)  # High fear = safe haven demand
                drivers.append("Elevated risk sentiment")
                confidence_factors.append(0.15)
            elif vix < 15:
                signals.append(-0.2)  # Low fear = less safe haven demand
                confidence_factors.append(0.1)

        # Fed Liquidity (positive correlation with assets)
        if "fed_liquidity_change" in data:
            liq_change = data["fed_liquidity_change"]
            if liq_change > 0.1:  # Expansion
                signals.append(0.5)
                drivers.append("Fed balance sheet expansion")
                confidence_factors.append(0.15)
            elif liq_change < -0.1:  # Contraction
                signals.append(-0.5)
                drivers.append("Fed balance sheet contraction")
                confidence_factors.append(0.15)

        # Yield Curve (recession signal)
        if "yield_curve" in data:
            yc = data["yield_curve"]
            if yc < 0:  # Inversion
                signals.append(0.4)
                drivers.append("Yield curve inversion (macro risk)")
                confidence_factors.append(0.1)

        # Industrial Production (Specific to Silver)
        if self.commodity == "silver" and "industrial_production_trend" in data:
            ip_trend = data["industrial_production_trend"]
            if ip_trend > 1.0:
                signals.append(0.6)
                drivers.append("Strong industrial production (silver demand)")
                confidence_factors.append(0.2)
            elif ip_trend < -1.0:
                signals.append(-0.6)
                drivers.append("Weak industrial production")
                confidence_factors.append(0.2)
        
        # Calculate weighted signal
        if signals:
            total_weight = sum(confidence_factors)
            if total_weight > 0:
                weighted_signal = sum(s * w for s, w in zip(signals, confidence_factors)) / total_weight
            else:
                weighted_signal = 0.0
        else:
            weighted_signal = 0.0
        
        # Convert to categorical
        signal = self._normalize_signal(weighted_signal, bullish_threshold=0.3, bearish_threshold=-0.3)
        
        # Confidence based on data quality and signal strength
        base_confidence = min(100, abs(weighted_signal) * 100)
        data_quality = min(1.0, len([k for k in data.keys() if data[k] is not None]) / 7.0) # increased total metrics
        confidence = base_confidence * data_quality
        
        return {
            "signal": signal,
            "confidence": confidence,
            "drivers": drivers[:3],  # Top 3 drivers
            "metadata": {
                "weighted_signal": weighted_signal,
                "real_rate": data.get("real_rate"),
                "dxy_change": data.get("dxy_change_30d"),
            }
        }

