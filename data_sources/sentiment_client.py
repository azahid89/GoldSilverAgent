"""
Sentiment Client for News and Social Signals
"""
from typing import Dict, List, Any, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

from config import DATA_SOURCES
from utils.cache import cache

class SentimentClient:
    """Client for aggregating and analyzing market sentiment"""
    
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.sources = DATA_SOURCES.get("sentiment", {}).get("sources", [])
        self.keywords = DATA_SOURCES.get("sentiment", {}).get("keywords", [])
        
    def fetch_rss_headlines(self) -> List[Dict[str, Any]]:
        """Fetch headlines from configured RSS feeds"""
        all_headlines = []
        
        for url in self.sources:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    headline = {
                        "title": entry.title,
                        "link": entry.link,
                        "summary": getattr(entry, "summary", ""),
                        "published": getattr(entry, "published", ""),
                        "source": url.split("//")[1].split("/")[0]
                    }
                    all_headlines.append(headline)
            except Exception as e:
                print(f"Error fetching RSS from {url}: {e}")
                
        return all_headlines

    def filter_headlines(self, headlines: List[Dict[str, Any]], commodity: str = "gold") -> List[Dict[str, Any]]:
        """Filter headlines by keywords related to the commodity"""
        relevant_keywords = [commodity.lower(), "bullion", "precious metals", "central bank"]
        if commodity.lower() == "gold":
            relevant_keywords.append("xau")
        elif commodity.lower() == "silver":
            relevant_keywords.extend(["xag", "solar", "photovoltaic", "ev", "semiconductor", "industrial demand"])
            
        filtered = []
        for h in headlines:
            text = f"{h['title']} {h['summary']}".lower()
            if any(kw in text for kw in relevant_keywords):
                filtered.append(h)
        return filtered

    def analyze_sentiment(self, text: str) -> float:
        """Calculate sentiment score (range -1 to 1)"""
        scores = self.sia.polarity_scores(text)
        return scores["compound"]

    def get_market_sentiment(self, commodity: str = "gold") -> Dict[str, Any]:
        """Aggregate sentiment for a commodity"""
        cache_key = f"sentiment_agg_{commodity}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        headlines = self.fetch_rss_headlines()
        relevant = self.filter_headlines(headlines, commodity)
        
        if not relevant:
            return {"score": 0, "count": 0, "sentiment": "neutral"}
            
        scores = []
        for h in relevant:
            score = self.analyze_sentiment(f"{h['title']} {h['summary']}")
            scores.append(score)
            
        avg_score = sum(scores) / len(scores)
        
        result = {
            "score": avg_score,
            "count": len(relevant),
            "sentiment": "bullish" if avg_score > 0.1 else "bearish" if avg_score < -0.1 else "neutral",
            "top_headlines": [h["title"] for h in relevant[:5]]
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, result, ttl_seconds=900)
        return result
