"""
Key Performance Indicators (KPIs) for Prediction Quality Evaluation
"""
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class KPIEvaluator:
    """Evaluates prediction quality using various KPIs"""
    
    def __init__(self):
        self.predictions_history = []
        self.actual_prices = []
    
    def record_prediction(self, prediction: Dict[str, Any], actual_price: Optional[float] = None):
        """Record a prediction for later evaluation"""
        self.predictions_history.append({
            "timestamp": datetime.now(),
            "commodity": prediction.get("commodity"),
            "signal": prediction.get("signal"),
            "confidence": prediction.get("confidence"),
            "horizon_days": prediction.get("horizon_days"),
            "actual_price": actual_price,
        })
    
    def calculate_directional_accuracy(self, horizon_days: int = 7, lookback_days: int = 90) -> Dict[str, float]:
        """
        Calculate directional accuracy (did price move in predicted direction?)
        
        Returns:
            {
                "accuracy": float (0-100),
                "bullish_accuracy": float,
                "bearish_accuracy": float,
                "neutral_accuracy": float,
                "sample_size": int
            }
        """
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        relevant_preds = [
            p for p in self.predictions_history
            if p["timestamp"] >= cutoff_date and p["horizon_days"] == horizon_days
        ]
        
        if not relevant_preds:
            return {
                "accuracy": 0.0,
                "bullish_accuracy": 0.0,
                "bearish_accuracy": 0.0,
                "neutral_accuracy": 0.0,
                "sample_size": 0,
            }
        
        # For now, return placeholder (would need actual price data)
        # In production, would compare predicted direction with actual price movement
        return {
            "accuracy": 0.0,  # Placeholder
            "bullish_accuracy": 0.0,
            "bearish_accuracy": 0.0,
            "neutral_accuracy": 0.0,
            "sample_size": len(relevant_preds),
        }
    
    def calculate_confidence_calibration(self) -> Dict[str, Any]:
        """
        Calculate confidence calibration
        (Are high-confidence predictions more accurate?)
        
        Returns:
            {
                "calibration_score": float,
                "bins": List[Dict]  # Confidence bins with actual accuracy
            }
        """
        # Placeholder - would need actual outcomes
        return {
            "calibration_score": 0.0,
            "bins": [],
        }
    
    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio of predictions (if treating as signals)"""
        if len(returns) == 0:
            return 0.0
        return float(np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0.0
    
    def get_kpi_summary(self) -> Dict[str, Any]:
        """Get summary of all KPIs"""
        return {
            "directional_accuracy_7d": self.calculate_directional_accuracy(horizon_days=7),
            "directional_accuracy_30d": self.calculate_directional_accuracy(horizon_days=30),
            "directional_accuracy_90d": self.calculate_directional_accuracy(horizon_days=90),
            "confidence_calibration": self.calculate_confidence_calibration(),
            "total_predictions": len(self.predictions_history),
        }


# KPI Definitions Document
KPI_DEFINITIONS = """
KEY PERFORMANCE INDICATORS (KPIs) FOR PREDICTION QUALITY

1. DIRECTIONAL ACCURACY
   - Definition: Percentage of predictions where actual price moved in predicted direction
   - Calculation: (Correct predictions / Total predictions) * 100
   - Targets:
     * 7-day: >55% (better than random)
     * 30-day: >60%
     * 90-day: >65%
   - Breakdown by signal type (bullish/bearish/neutral)

2. CONFIDENCE CALIBRATION
   - Definition: Correlation between confidence scores and actual accuracy
   - Calculation: Group predictions by confidence bins, measure accuracy per bin
   - Target: High-confidence predictions should be more accurate
   - Ideal: 80% confidence predictions should be correct ~80% of the time

3. MAGNITUDE ACCURACY (Optional)
   - Definition: How well predictions capture price movement magnitude
   - Calculation: Compare predicted vs actual percentage moves
   - Metric: Mean Absolute Error (MAE) or Root Mean Squared Error (RMSE)

4. SHARPE RATIO (If used as trading signals)
   - Definition: Risk-adjusted return of following predictions
   - Calculation: (Mean return / Std dev of returns) * sqrt(252)
   - Target: >1.0 (positive risk-adjusted returns)

5. HIT RATE BY COMMODITY
   - Gold vs Silver prediction accuracy
   - Identifies if system is better at one commodity

6. INVALIDATION RATE
   - Definition: Percentage of predictions invalidated by stated conditions
   - Tracks whether risk management is effective

7. CONSENSUS STRENGTH
   - Definition: Correlation between agent agreement and prediction accuracy
   - Higher agreement should correlate with higher accuracy

8. HORIZON PERFORMANCE
   - Compare accuracy across different time horizons
   - Identifies optimal prediction horizon

EVALUATION FREQUENCY
- Daily: Track all predictions
- Weekly: Calculate rolling 7-day accuracy
- Monthly: Full KPI report with calibration analysis
"""



