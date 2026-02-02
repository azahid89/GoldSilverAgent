"""
Base Agent Class - Foundation for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd


class BaseAgent(ABC):
    """Base class for all prediction agents"""
    
    def __init__(self, name: str, commodity: str = "both"):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            commodity: "gold", "silver", or "both"
        """
        self.name = name
        self.commodity = commodity
        self.last_update = None
        self.data_cache = {}
        
    @abstractmethod
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch required data for this agent"""
        pass
    
    @abstractmethod
    def analyze(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform analysis and return signal
        
        Returns:
            {
                "signal": "bullish" | "neutral" | "bearish",
                "confidence": float (0-100),
                "drivers": List[str],
                "metadata": Dict
            }
        """
        pass
    
    def get_prediction(self, horizon_days: int = 7) -> Dict[str, Any]:
        """
        Get prediction for specified horizon
        
        Args:
            horizon_days: Prediction horizon in days
            
        Returns:
            Prediction dictionary with signal, confidence, drivers
        """
        # Ensure horizon_days is an integer
        try:
            horizon_days = int(horizon_days)
        except (ValueError, TypeError):
            horizon_days = 7  # Default to 7 days if conversion fails
        
        data = self.fetch_data()
        analysis = self.analyze(data)
        
        # Adjust confidence based on horizon
        adjusted_confidence = self._adjust_confidence_for_horizon(
            analysis["confidence"], 
            horizon_days
        )
        
        return {
            "agent": self.name,
            "commodity": self.commodity,
            "horizon_days": horizon_days,
            "signal": analysis["signal"],
            "confidence": adjusted_confidence,
            "drivers": analysis["drivers"],
            "metadata": analysis.get("metadata", {}),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _adjust_confidence_for_horizon(self, base_confidence: float, horizon_days: int) -> float:
        """
        Adjust confidence based on prediction horizon
        Longer horizons = lower confidence
        """
        # Ensure horizon_days is an integer
        try:
            horizon_days = int(horizon_days)
        except (ValueError, TypeError):
            horizon_days = 7  # Default to 7 days if conversion fails
        
        if horizon_days <= 7:
            multiplier = 1.0
        elif horizon_days <= 30:
            multiplier = 0.9
        elif horizon_days <= 90:
            multiplier = 0.75
        else:
            multiplier = 0.6
            
        return min(100, base_confidence * multiplier)
    
    def _normalize_signal(self, value: float, bullish_threshold: float = 0.5, 
                         bearish_threshold: float = -0.5) -> str:
        """Convert numeric signal to categorical"""
        if value >= bullish_threshold:
            return "bullish"
        elif value <= bearish_threshold:
            return "bearish"
        else:
            return "neutral"
    
    def update_cache(self, key: str, value: Any):
        """Update data cache"""
        self.data_cache[key] = value
        self.last_update = datetime.now()
    
    def get_cache(self, key: str) -> Any:
        """Get cached data"""
        return self.data_cache.get(key)

