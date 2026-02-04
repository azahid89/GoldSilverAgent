"""
Dashboard Output Layer
"""
from typing import Dict, Any, List
import json
from datetime import datetime


class Dashboard:
    """Dashboard for displaying predictions and analysis"""
    
    def __init__(self):
        self.predictions = {}
        self.history = []
    
    def update(self, commodity: str, prediction: Dict[str, Any], explanation: Dict[str, Any]):
        """Update dashboard with new prediction"""
        self.predictions[commodity] = {
            "prediction": prediction,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append({
            "commodity": commodity,
            "prediction": prediction,
            "timestamp": datetime.now().isoformat(),
        })
    
    def generate_report(self, commodity: str) -> str:
        """Generate text report for commodity"""
        if commodity not in self.predictions:
            return f"No prediction available for {commodity}"
        
        data = self.predictions[commodity]
        pred = data["prediction"]
        exp = data["explanation"]
        
        report = f"""
{'='*60}
{commodity.upper()} PREDICTION REPORT
{'='*60}
Generated: {data['timestamp']}

PREDICTION SUMMARY
------------------
Directional Bias: {pred.get('signal', 'neutral').upper()}
Confidence: {pred.get('confidence', 0.0):.1f}%
Time Horizon: {pred.get('horizon_days', 7)} days

KEY DRIVERS
-----------
{chr(10).join(f"• {driver}" for driver in pred.get('drivers', []))}

AGENT BREAKDOWN
---------------
"""
        for agent, details in pred.get('agent_breakdown', {}).items():
            report += f"{agent.capitalize()}: {details.get('signal', 'neutral')} "
            report += f"({details.get('confidence', 0.0):.1f}% confidence)\n"
        
        report += f"""
REASONING
---------
{exp.get('reasoning', 'No reasoning available')}

RISK FACTORS
------------
{chr(10).join(f"• {risk}" for risk in exp.get('risk_factors', []))}

SCENARIOS
---------
{chr(10).join(f"• {scenario}" for scenario in exp.get('scenarios', []))}

INVALIDATION CONDITIONS
------------------------
{chr(10).join(f"• {condition}" for condition in pred.get('invalidation_conditions', []))}

{exp.get('disclaimer', '')}
{'='*60}
"""
        return report
    
    def to_json(self) -> str:
        """Export dashboard data as JSON"""
        return json.dumps({
            "predictions": self.predictions,
            "history": self.history[-10:],  # Last 10 predictions
        }, indent=2)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all predictions"""
        summary = {}
        for commodity, data in self.predictions.items():
            pred = data["prediction"]
            summary[commodity] = {
                "signal": pred.get("signal"),
                "confidence": pred.get("confidence"),
                "horizon_days": pred.get("horizon_days"),
            }
        return summary





