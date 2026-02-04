"""
Verification script for Gold & Silver Agent data sources and agents
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_sources.fred_client import FREDClient
from data_sources.yahoo_client import YahooClient
from data_sources.alpha_vantage_client import AlphaVantageClient
from data_sources.nasdaq_client import NasdaqClient
from data_sources.sentiment_client import SentimentClient

from agents.macro_agent import MacroAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.ensemble_agent import EnsembleAgent

def test_clients():
    print("--- Testing Data Clients ---")
    
    # 1. FRED
    print("\nTesting FRED Client...")
    fred = FREDClient()
    try:
        reserves = fred.get_gold_reserves(days=365)
        print(f"✅ FRED: Fetched {len(reserves)} points of Gold Reserves")
    except Exception as e:
        print(f"❌ FRED Error: {e}")

    # 2. Alpha Vantage
    print("\nTesting Alpha Vantage Client...")
    av = AlphaVantageClient()
    try:
        gold_daily = av.get_gold_daily()
        if not gold_daily.empty:
            print(f"✅ Alpha Vantage: Fetched {len(gold_daily)} days of Gold OHLC")
        else:
            print("⚠️ Alpha Vantage: Returned empty data (Check API Key/Limit)")
    except Exception as e:
        print(f"❌ Alpha Vantage Error: {e}")

    # 3. Nasdaq Data Link
    print("\nTesting Nasdaq Data Link Client...")
    nasdaq = NasdaqClient()
    try:
        gold_cot = nasdaq.get_gold_cot()
        if not gold_cot.empty:
            print(f"✅ Nasdaq: Fetched {len(gold_cot)} COT reports")
        else:
            print("⚠️ Nasdaq: Returned empty data (Check API Key/Subscription)")
    except Exception as e:
        print(f"❌ Nasdaq Error: {e}")

    # 4. Sentiment Client
    print("\nTesting Sentiment Client...")
    sentiment = SentimentClient()
    try:
        gold_sent = sentiment.get_market_sentiment("gold")
        print(f"✅ Sentiment: Score={gold_sent.get('score', 0):.2f}, Count={gold_sent.get('count', 0)}")
    except Exception as e:
        print(f"❌ Sentiment Error: {e}")

def test_agents():
    print("\n--- Testing Agents ---")
    
    # 1. MacroAgent
    print("\nTesting MacroAgent...")
    try:
        macro = MacroAgent(commodity="gold")
        pred = macro.get_prediction(horizon_days=7)
        print(f"✅ MacroAgent: Signal={pred['signal']}, Confidence={pred['confidence']:.1f}%")
        print(f"   Drivers: {pred['drivers']}")
    except Exception as e:
        print(f"❌ MacroAgent Error: {e}")

    # 2. FundamentalAgent
    print("\nTesting FundamentalAgent...")
    try:
        fund = FundamentalAgent(commodity="gold")
        pred = fund.get_prediction(horizon_days=7)
        print(f"✅ FundamentalAgent: Signal={pred['signal']}, Confidence={pred['confidence']:.1f}%")
    except Exception as e:
        print(f"❌ FundamentalAgent Error: {e}")

    # 3. SentimentAgent
    print("\nTesting SentimentAgent...")
    try:
        sent = SentimentAgent(commodity="gold")
        pred = sent.get_prediction(horizon_days=7)
        print(f"✅ SentimentAgent: Signal={pred['signal']}, Confidence={pred['confidence']:.1f}%")
    except Exception as e:
        print(f"❌ SentimentAgent Error: {e}")

    # 4. EnsembleAgent
    print("\nTesting EnsembleAgent...")
    try:
        ensemble = EnsembleAgent(commodity="gold")
        pred = ensemble.get_ensemble_prediction(horizon_days=30)
        print(f"✅ EnsembleAgent (GOLD): Signal={pred['signal']}, Confidence={pred['confidence']:.1f}%")
        print(f"   Top Drivers: {pred['drivers']}")
    except Exception as e:
        print(f"❌ EnsembleAgent Error: {e}")

if __name__ == "__main__":
    test_clients()
    test_agents()
    print("\n--- Verification Complete ---")
