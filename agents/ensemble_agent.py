"""
Ensemble Prediction Agent - Combines all agent signals
"""
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

from .base_agent import BaseAgent
from .macro_agent import MacroAgent
from .market_agent import MarketAgent
from .technical_agent import TechnicalAgent
from .fundamental_agent import FundamentalAgent
from .correlation_agent import CorrelationAgent
from config import AGENT_WEIGHTS


class EnsembleAgent:
    """Ensemble agent that combines predictions from all specialized agents"""
    
    def __init__(self, commodity: str = "gold"):
        self.commodity = commodity
        self.agents = {
            "macro": MacroAgent(commodity="both"),
            "market": MarketAgent(commodity=commodity),
            "technical": TechnicalAgent(commodity=commodity),
            "fundamental": FundamentalAgent(commodity=commodity),
            "correlation": CorrelationAgent(commodity="both"),
        }
        self.weights = AGENT_WEIGHTS
    
    def get_ensemble_prediction(self, horizon_days: int = 7) -> Dict[str, Any]:
        """
        Get ensemble prediction combining all agents
        
        Args:
            horizon_days: Prediction horizon
            
        Returns:
            Ensemble prediction with signal, confidence, drivers, invalidation conditions
        """
        # Ensure horizon_days is an integer
        try:
            horizon_days = int(horizon_days)
        except (ValueError, TypeError):
            horizon_days = 7  # Default to 7 days if conversion fails
        
        agent_predictions = {}
        
        # Get predictions from all agents (run in parallel for speed)
        import concurrent.futures
        
        def get_agent_prediction(agent_name, agent):
            try:
                return agent_name, agent.get_prediction(horizon_days=horizon_days)
            except Exception as e:
                print(f"Error getting prediction from {agent_name}: {e}")
                return agent_name, None
        
        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(get_agent_prediction, name, agent): name
                for name, agent in self.agents.items()
            }
            
            for future in concurrent.futures.as_completed(futures):
                agent_name, pred = future.result()
                if pred is not None:
                    agent_predictions[agent_name] = pred
        
        if not agent_predictions:
            return {
                "commodity": self.commodity,
                "horizon_days": horizon_days,
                "signal": "neutral",
                "confidence": 0.0,
                "drivers": [],
                "invalidation_conditions": [],
                "agent_breakdown": {},
                "timestamp": datetime.now().isoformat(),
            }
        
        # Convert signals to numeric for weighted averaging
        signal_map = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}
        
        weighted_signal = 0.0
        total_weight = 0.0
        all_drivers = []
        agent_breakdown = {}
        
        for agent_name, pred in agent_predictions.items():
            signal_numeric = signal_map.get(pred["signal"], 0.0)
            confidence = pred.get("confidence", 0.0)
            weight = self.weights.get(agent_name, 0.1)
            
            # Weight by agent weight and confidence
            effective_weight = weight * (confidence / 100.0)
            weighted_signal += signal_numeric * effective_weight
            total_weight += effective_weight
            
            all_drivers.extend(pred.get("drivers", []))
            agent_breakdown[agent_name] = {
                "signal": pred["signal"],
                "confidence": confidence,
                "drivers": pred.get("drivers", []),
            }
        
        # Normalize weighted signal
        if total_weight > 0:
            normalized_signal = weighted_signal / total_weight
        else:
            normalized_signal = 0.0
        
        # Convert back to categorical
        if normalized_signal >= 0.3:
            ensemble_signal = "bullish"
        elif normalized_signal <= -0.3:
            ensemble_signal = "bearish"
        else:
            ensemble_signal = "neutral"
        
        # Calculate ensemble confidence
        # Based on agreement between agents and individual confidences
        signal_values = [signal_map.get(pred["signal"], 0.0) for pred in agent_predictions.values()]
        agreement = 1.0 - (np.std(signal_values) / 2.0)  # Higher agreement = higher confidence
        
        avg_confidence = np.mean([pred.get("confidence", 0.0) for pred in agent_predictions.values()])
        ensemble_confidence = avg_confidence * (0.5 + 0.5 * agreement)
        ensemble_confidence = min(100, max(0, ensemble_confidence))
        
        # Get top drivers (most mentioned)
        driver_counts = {}
        for driver in all_drivers:
            driver_counts[driver] = driver_counts.get(driver, 0) + 1
        top_drivers = sorted(driver_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_drivers_list = [driver for driver, _ in top_drivers]
        
        # Generate invalidation conditions
        invalidation_conditions = self._generate_invalidation_conditions(
            agent_predictions, ensemble_signal
        )
        
        return {
            "commodity": self.commodity,
            "horizon_days": horizon_days,
            "signal": ensemble_signal,
            "confidence": float(ensemble_confidence),
            "drivers": top_drivers_list,
            "invalidation_conditions": invalidation_conditions,
            "agent_breakdown": agent_breakdown,
            "weighted_signal": float(normalized_signal),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_invalidation_conditions(self, agent_predictions: Dict, signal: str) -> List[str]:
        """Generate conditions that would invalidate the prediction"""
        conditions = []
        
        # Check for conflicting signals
        signals = [pred["signal"] for pred in agent_predictions.values()]
        if len(set(signals)) > 1:
            conditions.append("Significant disagreement among agents")
        
        # Macro invalidation
        if "macro" in agent_predictions:
            macro_pred = agent_predictions["macro"]
            if macro_pred["signal"] != signal:
                conditions.append("Surprise Fed policy shift")
                conditions.append("Unexpected inflation data")
        
        # Market invalidation
        if "market" in agent_predictions:
            market_pred = agent_predictions["market"]
            if market_pred["signal"] != signal:
                conditions.append("Sudden ETF flow reversal")
                conditions.append("Unusual volatility spike")
        
        # Technical invalidation
        if "technical" in agent_predictions:
            conditions.append("Break of key support/resistance levels")
        
        # Fundamental invalidation
        if "fundamental" in agent_predictions:
            conditions.append("Real rates move opposite to prediction")
            conditions.append("Central bank policy surprise")
        
        # General conditions
        conditions.append("Major geopolitical event")
        conditions.append("Market structure change")
        
        return conditions[:5]  # Top 5 conditions

