"""
LLM Reasoning Layer - Explains predictions and generates narratives
"""
from typing import Dict, Any, Optional, List
import os
from config import OPENAI_API_KEY, LEGAL_DISCLAIMER

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. LLM reasoning will use template-based explanations.")


class LLMReasoningLayer:
    """LLM layer for generating explanations and narratives"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def generate_explanation(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation for prediction
        
        Args:
            prediction: Ensemble prediction dictionary
            
        Returns:
            Explanation with reasoning, scenarios, and risk factors
        """
        if self.client:
            return self._generate_llm_explanation(prediction)
        else:
            return self._generate_template_explanation(prediction)
    
    def _generate_llm_explanation(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation using LLM"""
        try:
            commodity = prediction.get("commodity", "gold").capitalize()
            signal = prediction.get("signal", "neutral").capitalize()
            confidence = prediction.get("confidence", 0.0)
            drivers = prediction.get("drivers", [])
            horizon = prediction.get("horizon_days", 7)
            invalidation = prediction.get("invalidation_conditions", [])
            
            prompt = f"""You are a professional commodities analyst explaining a {commodity} price prediction.

Prediction Summary:
- Directional Bias: {signal}
- Confidence: {confidence:.1f}%
- Time Horizon: {horizon} days
- Key Drivers: {', '.join(drivers)}

Agent Breakdown:
{self._format_agent_breakdown(prediction.get('agent_breakdown', {}))}

Provide a concise, professional explanation that:
1. Explains WHY this bias exists (2-3 sentences)
2. Identifies the top 3 risk factors that could invalidate this view
3. Describes 2-3 plausible scenarios for the next {horizon} days

Be factual, avoid hype, and emphasize uncertainty. Do NOT provide investment advice.

Format your response as:
WHY: [explanation]
RISKS: [risk factors]
SCENARIOS: [scenarios]"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional commodities analyst. Provide factual, balanced analysis without investment advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            explanation_text = response.choices[0].message.content
            
            # Parse explanation
            reasoning = self._parse_explanation(explanation_text)
            
            return {
                "reasoning": reasoning.get("why", ""),
                "risk_factors": reasoning.get("risks", invalidation),
                "scenarios": reasoning.get("scenarios", []),
                "full_explanation": explanation_text,
                "disclaimer": LEGAL_DISCLAIMER,
            }
            
        except Exception as e:
            print(f"Error generating LLM explanation: {e}")
            return self._generate_template_explanation(prediction)
    
    def _generate_template_explanation(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate template-based explanation when LLM unavailable"""
        commodity = prediction.get("commodity", "gold").capitalize()
        signal = prediction.get("signal", "neutral").capitalize()
        confidence = prediction.get("confidence", 0.0)
        drivers = prediction.get("drivers", [])
        invalidation = prediction.get("invalidation_conditions", [])
        
        # Template reasoning
        if signal == "Bullish":
            reasoning = f"The {commodity} market shows {signal.lower()} signals with {confidence:.1f}% confidence. "
            reasoning += f"Key factors include: {', '.join(drivers[:3])}. "
            reasoning += "This suggests potential upward price pressure over the prediction horizon."
        elif signal == "Bearish":
            reasoning = f"The {commodity} market shows {signal.lower()} signals with {confidence:.1f}% confidence. "
            reasoning += f"Key factors include: {', '.join(drivers[:3])}. "
            reasoning += "This suggests potential downward price pressure over the prediction horizon."
        else:
            reasoning = f"The {commodity} market shows mixed signals with {confidence:.1f}% confidence. "
            reasoning += "Conflicting factors suggest a neutral outlook with limited directional bias."
        
        scenarios = [
            f"Base case: {signal.lower()} bias continues with moderate price movement",
            f"Bull case: Stronger than expected drivers lead to amplified {signal.lower()} move",
            f"Bear case: Invalidation conditions trigger reversal from current {signal.lower()} bias"
        ]
        
        return {
            "reasoning": reasoning,
            "risk_factors": invalidation[:3],
            "scenarios": scenarios,
            "full_explanation": reasoning,
            "disclaimer": LEGAL_DISCLAIMER,
        }
    
    def _format_agent_breakdown(self, breakdown: Dict[str, Any]) -> str:
        """Format agent breakdown for LLM prompt"""
        lines = []
        for agent, data in breakdown.items():
            signal = data.get("signal", "neutral")
            conf = data.get("confidence", 0.0)
            lines.append(f"- {agent}: {signal} ({conf:.1f}% confidence)")
        return "\n".join(lines)
    
    def _parse_explanation(self, text: str) -> Dict[str, List[str]]:
        """Parse LLM explanation into structured format"""
        result = {
            "why": "",
            "risks": [],
            "scenarios": []
        }
        
        # Simple parsing (can be improved)
        lines = text.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("WHY:"):
                current_section = "why"
                result["why"] = line.replace("WHY:", "").strip()
            elif line.startswith("RISKS:"):
                current_section = "risks"
            elif line.startswith("SCENARIOS:"):
                current_section = "scenarios"
            elif line and current_section:
                if current_section == "risks":
                    result["risks"].append(line.lstrip("- ").strip())
                elif current_section == "scenarios":
                    result["scenarios"].append(line.lstrip("- ").strip())
                elif current_section == "why" and not result["why"]:
                    result["why"] = line
        
        return result





