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
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
NASDAQ_DATA_LINK_API_KEY = os.getenv("NASDAQ_DATA_LINK_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")  # For headlines

# Data Sources
DATA_SOURCES = {
    "gold": {
        "spot": "GC=F",  # COMEX Gold Futures
        "etf": "GLD",
        "volatility": "^GVZ",  # Gold Volatility Index
        "lbma": "GOLDAMGBD228NLBM",  # LBMA Gold Price (FRED)
    },
    "silver": {
        "spot": "SI=F",  # COMEX Silver Futures
        "etf": "SLV",
        "volatility": "^SVZ",  # Silver Volatility Index
        "lbma": "SLVPRUSD",  # LBMA Silver Price (FRED)
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
        "semiconductor_prod": "IPG3344S", # Solar proxy (FRED)
        "auto_prod": "IPG3361T3S", # EV proxy (FRED)
        "central_bank_reserves": "M14062USM027NNBR",  # US Gold Reserves (FRED)
        "china_industrial_output": "PRINTO01CNQ663N", # China Industrial Production (FRED)
    },
    "etf_flows": {
        "gld": "GLD",
        "slv": "SLV",
    },
    "sentiment": {
        "sources": [
            "https://www.reuters.com/arc/outboundfeeds/news-handler/?facetId=commodities&format=xml",
            "https://www.bloomberg.com/feeds/bview/commodities.xml",
        ],
        "keywords": ["gold", "silver", "xau", "xag", "bullion", "precious metals"]
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
    "macro": 0.20,
    "market": 0.15,
    "technical": 0.15,
    "fundamental": 0.20,
    "correlation": 0.15,
    "sentiment": 0.15,
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

