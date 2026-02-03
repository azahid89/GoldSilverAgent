"""
Configuration file for Gold & Silver Agent System
"""
import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, will use system environment variables only
    pass

# API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Data Sources
DATA_SOURCES = {
    "gold": {
        "spot": "GC=F",  # COMEX Gold Futures
        "etf": "GLD",
        "volatility": "^GVZ",  # Gold Volatility Index (may not be available)
    },
    "silver": {
        "spot": "SI=F",  # COMEX Silver Futures
        "etf": "SLV",
        "volatility": "^SVZ",  # Silver Volatility Index (may not be available)
    },
    "macro": {
        "dxy": "DX-Y.NYB",  # USD Dollar Index
        "dgs10": "DGS10",  # 10-Year Treasury Rate (FRED)
        "tips": "DFII10",  # 10-Year TIPS (FRED)
        "cpi": "CPIAUCSL",  # CPI (FRED)
        "pce": "PCEPI",  # PCE Price Index (FRED)
        "vix": "^VIX",  # VIX (CBOE Volatility Index)
        "copper": "HG=F",  # Copper Futures
        "platinum": "PL=F",  # Platinum Futures
        "palladium": "PA=F",  # Palladium Futures
        "bitcoin": "BTC-USD",  # Bitcoin
        "fed_balance_sheet": "WALCL",  # Fed Balance Sheet (FRED)
        "money_supply": "M2SL",  # M2 Money Supply (FRED)
        "yield_curve": "T10Y2Y",  # 10Y-2Y Spread (FRED)
        "industrial_production": "IPMAN",  # Industrial Production (FRED)
    },
    "etf_flows": {
        "gld": "GLD",
        "slv": "SLV",
    }
}

# Prediction Horizons
PREDICTION_HORIZONS = {
    "short_term": 7,  # days
    "medium_term": 30,  # days
    "long_term": 90,  # days
}

# Agent Weights (for ensemble)
AGENT_WEIGHTS = {
    "macro": 0.25,
    "market": 0.20,
    "technical": 0.15,
    "fundamental": 0.20,
    "correlation": 0.20,
}

# Confidence Thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 70,
    "medium": 50,
    "low": 30,
}

# Legal Disclaimer
LEGAL_DISCLAIMER = """
⚠️ IMPORTANT LEGAL DISCLAIMER ⚠️

This system provides market analysis, data aggregation, and informational content only.
It does NOT constitute:
- Financial advice
- Investment recommendations
- Trading signals
- Professional investment guidance

All predictions and analyses are for informational purposes only.
Users should consult with licensed financial advisors before making any investment decisions.
The system operators assume no liability for any trading or investment decisions made based on this information.

See LEGAL_DISCLAIMER.md for complete terms.
"""

