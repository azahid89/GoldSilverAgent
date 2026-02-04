"""
Sentiment Agent - Processes news and social signals
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from agents.base_agent import BaseAgent
from data_sources.sentiment_client import SentimentClient
from data_sources.alpha_vantage_client import AlphaVantageClient

class SentimentAgent(BaseAgent):
    """Agent that analyzes market sentiment from news and social data"""
    
    def __init__(self, commodity: str = "both"):
        super().__init__(name="SentimentAgent", commodity=commodity)
        self.sentiment_client = SentimentClient()
        self.av_client = AlphaVantageClient()
        
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch news and sentiment data"""
        data = {}
        commodities = ["gold", "silver"] if self.commodity == "both" else [self.commodity]
        
        for comm in commodities:
            data[comm] = {
                "rss": self.sentiment_client.get_market_sentiment(comm),
                "alpha_vantage": self.av_client.get_sentiment(tickers="GLD" if comm == "gold" else "SLV")
            }
        return data
        
    def analyze(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze sentiment data and return signals"""
        if not data:
            data = self.fetch_data()
            
        commodities = ["gold", "silver"] if self.commodity == "both" else [self.commodity]
        
        # Consolidation logic
        comm = commodities[0] # Simplification for single commodity analysis
        comm_data = data.get(comm, {})
        
        rss_sentiment = comm_data.get("rss", {})
        av_sentiment_data = comm_data.get("alpha_vantage", {})
        
        rss_score = rss_sentiment.get("score", 0)
        
        # Extract Alpha Vantage sentiment score if available
        av_score = 0
        if "feed" in av_sentiment_data:
            scores = []
            for item in av_sentiment_data["feed"][:10]:
                scores.append(float(item.get("overall_sentiment_score", 0)))
            if scores:
                av_score = sum(scores) / len(scores)
        
        # Weighted score (RSS 60%, AV 40%)
        composite_score = (rss_score * 0.6) + (av_score * 0.4)
        
        signal = self._normalize_signal(composite_score, bullish_threshold=0.1, bearish_threshold=-0.1)
        confidence = min(80, max(20, abs(composite_score) * 100))
        
        drivers = []
        if rss_sentiment.get("count", 0) > 0:
            drivers.append(f"Aggregated {rss_sentiment['count']} headlines (score: {rss_score:.2f})")
        if av_score != 0:
            drivers.append(f"Alpha Vantage sentiment score: {av_score:.2f}")
            
        # Add top headlines as drivers if bullish/bearish
        if signal != "neutral":
            top_headlines = rss_sentiment.get("top_headlines", [])
            for h in top_headlines[:2]:
                drivers.append(f"Headline: {h[:50]}...")
                
        return {
            "signal": signal,
            "confidence": confidence,
            "drivers": drivers,
            "metadata": {
                "composite_score": composite_score,
                "rss_score": rss_score,
                "av_score": av_score,
                "headline_count": rss_sentiment.get("count", 0)
            }
        }
