"""
Flask API Server for Gold & Silver Agent System
Connects React frontend to Python agents
"""
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from datetime import datetime
import sys
import os
import time
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.ensemble_agent import EnsembleAgent
from reasoning.llm_reasoning import LLMReasoningLayer
from config import PREDICTION_HORIZONS

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize agents (lazy loading)
ensemble_agents = {}
reasoning_layer = None


def get_ensemble_agent(commodity):
    """Get or create ensemble agent for commodity"""
    if commodity not in ensemble_agents:
        ensemble_agents[commodity] = EnsembleAgent(commodity=commodity)
    return ensemble_agents[commodity]


def get_reasoning_layer():
    """Get or create reasoning layer"""
    global reasoning_layer
    if reasoning_layer is None:
        reasoning_layer = LLMReasoningLayer()
    return reasoning_layer


@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get current predictions for both gold and silver"""
    try:
        # Get horizon parameter and ensure it's an integer
        horizon_str = request.args.get('horizon', '90')
        try:
            horizon = int(horizon_str)
        except (ValueError, TypeError):
            horizon = 90  # Default to 90 days
        
        predictions = {}
        
        for commodity in ['gold', 'silver']:
            ensemble = get_ensemble_agent(commodity)
            prediction = ensemble.get_ensemble_prediction(horizon_days=horizon)
            
            # Format for frontend
            predictions[commodity] = {
                'signal': prediction.get('signal', 'neutral'),
                'confidence': prediction.get('confidence', 0.0),
                'drivers': prediction.get('drivers', []),
                'agent_breakdown': prediction.get('agent_breakdown', {}),
                'invalidation_conditions': prediction.get('invalidation_conditions', []),
                'horizon_days': prediction.get('horizon_days', horizon),
                'timestamp': prediction.get('timestamp', datetime.now().isoformat()),
            }
        
        return jsonify(predictions)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predictions/<commodity>', methods=['GET'])
def get_commodity_prediction(commodity):
    """Get prediction for specific commodity"""
    try:
        if commodity not in ['gold', 'silver']:
            return jsonify({'error': 'Invalid commodity'}), 400
        
        # Get horizon parameter and ensure it's an integer
        horizon_str = request.args.get('horizon', '90')
        try:
            horizon = int(horizon_str)
        except (ValueError, TypeError):
            horizon = 90  # Default to 90 days
        
        ensemble = get_ensemble_agent(commodity)
        prediction = ensemble.get_ensemble_prediction(horizon_days=horizon)
        
        # Generate explanation
        reasoning = get_reasoning_layer()
        explanation = reasoning.generate_explanation(prediction)
        
        return jsonify({
            'prediction': {
                'signal': prediction.get('signal', 'neutral'),
                'confidence': prediction.get('confidence', 0.0),
                'drivers': prediction.get('drivers', []),
                'agent_breakdown': prediction.get('agent_breakdown', {}),
                'invalidation_conditions': prediction.get('invalidation_conditions', []),
                'horizon_days': prediction.get('horizon_days', horizon),
            },
            'explanation': explanation,
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and generate responses (streaming)"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        stream = data.get('stream', True)  # Default to streaming
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if stream:
            # Return streaming response
            return Response(
                stream_with_context(generate_streaming_response(message)),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive',
                }
            )
        else:
            # Return regular response
            response = process_chat_message(message)
            return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_streaming_response(message):
    """Generate streaming response with progress updates"""
    try:
        # Send initial "thinking" message
        yield f"data: {json.dumps({'content': 'Analyzing market data... ', 'done': False})}\n\n"
        time.sleep(0.1)
        
        # Process the message to get full response
        full_response = process_chat_message(message)
        
        # Stream the response in chunks for faster display
        chunk_size = 3  # Stream 3 characters at a time for faster response
        for i in range(0, len(full_response), chunk_size):
            chunk = full_response[i:i+chunk_size]
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
            # Faster streaming (0.005 = ~200 chars/sec)
            time.sleep(0.005)
        
        # Send completion signal
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        for char in error_msg:
            yield f"data: {json.dumps({'content': char, 'done': False})}\n\n"
            time.sleep(0.005)
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"


def process_chat_message(message):
    """Process user message and generate intelligent response"""
    message_lower = message.lower()
    
    # Check for price queries FIRST (before prediction queries)
    if any(word in message_lower for word in ['price', 'rate', 'current', 'today', 'today\'s', 'what is']):
        if any(word in message_lower for word in ['gold', 'silver']) or 'price' in message_lower or 'rate' in message_lower:
            return get_price_response(message_lower)
    
    # Check for specific queries
    if any(word in message_lower for word in ['gold', 'silver']):
        # Get predictions
        commodity = 'gold' if 'gold' in message_lower else 'silver'
        if 'silver' in message_lower and 'gold' not in message_lower:
            commodity = 'silver'
        
        horizon = 30  # Default
        if '7' in message or 'week' in message_lower or 'short' in message_lower:
            horizon = 7
        elif '30' in message or 'month' in message_lower or 'medium' in message_lower:
            horizon = 30
        elif '90' in message or 'quarter' in message_lower or 'long' in message_lower:
            horizon = 90
        
        try:
            ensemble = get_ensemble_agent(commodity)
            prediction = ensemble.get_ensemble_prediction(horizon_days=horizon)
            reasoning = get_reasoning_layer()
            explanation = reasoning.generate_explanation(prediction)
            
            response = f"## {commodity.capitalize()} Prediction ({horizon}-day horizon)\n\n"
            response += f"**Signal:** {prediction['signal'].upper()}\n"
            response += f"**Confidence:** {prediction['confidence']:.1f}%\n\n"
            response += f"**Key Drivers:**\n"
            for driver in prediction.get('drivers', [])[:3]:
                response += f"- {driver}\n"
            response += f"\n**Analysis:**\n{explanation.get('reasoning', '')}\n\n"
            
            if explanation.get('risk_factors'):
                response += f"**Risk Factors:**\n"
                for risk in explanation['risk_factors'][:3]:
                    response += f"- {risk}\n"
            
            return response
        
        except Exception as e:
            return f"I encountered an error generating the prediction: {str(e)}"
    
    elif any(word in message_lower for word in ['driver', 'factor', 'why', 'reason']):
        # Explain drivers
        commodity = 'gold' if 'gold' in message_lower else 'silver' if 'silver' in message_lower else 'gold'
        
        try:
            ensemble = get_ensemble_agent(commodity)
            prediction = ensemble.get_ensemble_prediction(horizon_days=30)
            
            response = f"## Key Drivers for {commodity.capitalize()}\n\n"
            response += "The main factors influencing the prediction are:\n\n"
            
            for i, driver in enumerate(prediction.get('drivers', []), 1):
                response += f"{i}. **{driver}**\n"
            
            response += "\n**Agent Breakdown:**\n"
            for agent, data in prediction.get('agent_breakdown', {}).items():
                response += f"- {agent.capitalize()}: {data.get('signal', 'neutral')} "
                response += f"({data.get('confidence', 0):.1f}% confidence)\n"
            
            return response
        
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    elif any(word in message_lower for word in ['help', 'what can', 'how', 'capabilities']):
        return """## How I Can Help

I'm your Gold & Silver market analysis agent. Here's what I can do:

**Current Prices:**
- "What's the gold price today?"
- "Current silver rate"
- "Gold price in USD"
- "Show me silver price and week comparison"

**Predictions:**
- Ask: "What's the gold prediction?" or "Show me silver forecast"
- Specify horizon: "Gold 7-day prediction" or "Silver 90-day outlook"

**Analysis:**
- "What are the drivers for gold?"
- "Why is silver bullish/bearish?"
- "Explain the gold prediction"

**General Questions:**
- Ask about market factors, trends, or analysis

**Examples:**
- "What's the gold price today?"
- "Current silver rate with week comparison"
- "What's the 30-day gold prediction?"
- "Explain silver drivers"
- "Show me gold analysis for next week"

Just ask me anything about gold and silver prices, predictions, or market analysis!"""
    
    else:
        # General question - use LLM to answer any gold/silver related question
        return answer_general_question(message)


def answer_general_question(message):
    """Answer any general question about gold and silver using LLM"""
    try:
        reasoning = get_reasoning_layer()
        
        # Get current market context
        context = get_market_context()
        
        # Create prompt for LLM
        prompt = f"""You are a professional commodities analyst specializing in gold and silver markets.

Current Market Context:
{context}

User Question: {message}

Provide a comprehensive, professional answer to the user's question about gold and/or silver. 
Be factual, informative, and helpful. If the question relates to current market conditions, 
reference the context provided. If it's a general knowledge question, provide accurate information.

Do NOT provide investment advice. Focus on education and market analysis.

Format your response clearly with sections if needed. Use markdown for formatting."""

        # Use LLM if available
        if reasoning.client:
            try:
                response = reasoning.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional commodities analyst. Provide factual, educational information about gold and silver markets. Do not provide investment advice."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"LLM error: {e}")
                # Fall back to template response
        
        # Fallback: Template-based response for common questions
        return get_template_response(message, context)
    
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try rephrasing your question."


def get_market_context():
    """Get current market context for LLM responses"""
    try:
        from data_sources.yahoo_client import YahooClient
        
        yahoo_client = YahooClient()
        context = []
        
        # Get current prices
        gold_data = yahoo_client.get_gold_price(period="7d")
        silver_data = yahoo_client.get_silver_price(period="7d")
        
        if not gold_data.empty:
            current_gold = float(gold_data["Close"].iloc[-1])
            context.append(f"Gold: ${current_gold:,.2f} USD/oz")
        
        if not silver_data.empty:
            current_silver = float(silver_data["Close"].iloc[-1])
            context.append(f"Silver: ${current_silver:,.2f} USD/oz")
        
        # Add new macro indicators
        try:
            from data_sources.fred_client import FREDClient
            fred_client = FREDClient()
            
            balance_sheet = fred_client.get_fed_balance_sheet(days=60)
            if not balance_sheet.empty and len(balance_sheet) >= 2:
                liq_change = (balance_sheet.iloc[-1] / balance_sheet.iloc[-2] - 1) * 100
                context.append(f"Fed Balance Sheet Change (Weekly): {liq_change:+.2f}%")
            
            yield_curve = fred_client.get_yield_curve(days=7)
            if not yield_curve.empty:
                context.append(f"Yield Curve (10Y-2Y): {yield_curve.iloc[-1]:.2f}")
        except Exception as e:
            print(f"Error adding macro context: {e}")

        # Add Bitcoin as sentiment proxy
        btc_price = yahoo_client.get_current_price("BTC-USD")
        if btc_price:
            context.append(f"Bitcoin: ${btc_price:,.0f} USD")
        
        # Get recent predictions if available
        try:
            gold_ensemble = get_ensemble_agent('gold')
            gold_pred = gold_ensemble.get_ensemble_prediction(horizon_days=30)
            context.append(f"Gold 30-day outlook: {gold_pred.get('signal', 'neutral')} ({gold_pred.get('confidence', 0):.1f}% confidence)")
        except:
            pass
        
        return "\n".join(context) if context else "Market data currently unavailable."
    
    except Exception as e:
        return f"Market context unavailable: {str(e)}"


def get_template_response(message, context):
    """Template-based responses for common questions when LLM unavailable"""
    message_lower = message.lower()
    
    # Common question patterns
    if any(word in message_lower for word in ['what is', 'what are', 'explain', 'tell me about']):
        if 'gold' in message_lower:
            return f"""## About Gold

Gold is a precious metal that has been used as a form of currency and store of value for thousands of years.

**Key Characteristics:**
- Chemical symbol: Au
- Highly malleable and ductile
- Excellent conductor of electricity
- Resistant to corrosion

**Market Factors:**
- Real interest rates (inverse relationship)
- USD strength (inverse relationship)
- Inflation expectations
- Geopolitical risk
- Central bank demand
- ETF flows

**Current Context:**
{context}

**Uses:**
- Investment/store of value
- Jewelry
- Electronics
- Central bank reserves
- Industrial applications

Would you like more specific information about gold prices, predictions, or market drivers?"""
        
        elif 'silver' in message_lower:
            return f"""## About Silver

Silver is a precious metal with both monetary and industrial value.

**Key Characteristics:**
- Chemical symbol: Ag
- Highest electrical conductivity of any metal
- Highly reflective
- Antibacterial properties

**Market Factors:**
- Industrial demand (solar, electronics, EVs)
- Gold correlation
- USD strength
- Real interest rates
- Manufacturing PMIs
- China demand

**Current Context:**
{context}

**Uses:**
- Investment/store of value
- Industrial applications (solar panels, electronics)
- Jewelry
- Photography
- Medical applications

Would you like more specific information about silver prices, predictions, or market drivers?"""
    
    elif any(word in message_lower for word in ['difference', 'compare', 'vs', 'versus']):
        return f"""## Gold vs Silver Comparison

**Key Differences:**

**Gold:**
- Primarily monetary/investment asset
- Lower industrial demand (~10%)
- More stable prices
- Higher value per ounce
- Stronger safe-haven status

**Silver:**
- Dual role: investment + industrial
- Higher industrial demand (~50%)
- More volatile prices
- Lower value per ounce
- More sensitive to economic cycles

**Current Context:**
{context}

**Gold-Silver Ratio:**
The ratio indicates how many ounces of silver equal one ounce of gold. 
Historically ranges from ~50:1 to ~100:1. Higher ratios suggest silver is relatively cheap.

Would you like current prices, predictions, or more detailed comparison?"""
    
    elif any(word in message_lower for word in ['why', 'reason', 'cause', 'factor']):
        return f"""## Factors Affecting Gold & Silver Prices

**Common Drivers:**

**Macroeconomic:**
- Real interest rates (most important for gold)
- USD strength (DXY)
- Inflation expectations
- Fed policy and forward guidance
- Treasury yields

**Market:**
- ETF flows (GLD, SLV)
- Speculative positioning
- Volatility (GVZ, SVZ)
- Price momentum

**Fundamental:**
- Central bank buying (gold)
- Industrial demand (silver)
- Mining supply
- Geopolitical risk

**Current Context:**
{context}

Would you like to see current predictions or specific driver analysis?"""
    
    # Default response
    return f"""I can help you with questions about gold and silver markets!

**Current Market Context:**
{context}

**I can answer questions about:**
- Current prices and trends
- Market predictions and analysis
- Factors affecting prices
- Gold vs silver comparisons
- Historical context
- Market drivers and dynamics

**Try asking:**
- "What affects gold prices?"
- "Why is silver more volatile?"
- "What's the difference between gold and silver?"
- "Explain the gold-silver ratio"
- Or any other question about gold and silver markets!

If you have a specific question, feel free to ask!"""


def get_price_response(message_lower):
    """Generate response for price queries"""
    from data_sources.yahoo_client import YahooClient
    
    yahoo_client = YahooClient()
    
    response = "## Current Prices & Week Comparison\n\n"
    
    # Determine which commodity
    is_gold = 'gold' in message_lower
    is_silver = 'silver' in message_lower
    show_both = not is_gold and not is_silver
    
    try:
        if is_gold or show_both:
            gold_data = yahoo_client.get_gold_price(period="14d")
            if not gold_data.empty:
                current_gold = float(gold_data["Close"].iloc[-1])
                week_ago_gold = float(gold_data["Close"].iloc[-7]) if len(gold_data) >= 7 else current_gold
                gold_change = ((current_gold / week_ago_gold) - 1) * 100
                gold_change_abs = current_gold - week_ago_gold
                
                change_symbol = "📈" if gold_change >= 0 else "📉"
                change_color = "up" if gold_change >= 0 else "down"
                
                response += f"### 🏅 Gold\n"
                response += f"**Current Price:** ${current_gold:,.2f} USD per ounce\n"
                response += f"**Week Ago:** ${week_ago_gold:,.2f} USD\n"
                response += f"**Change:** {change_symbol} ${abs(gold_change_abs):,.2f} ({abs(gold_change):.2f}%)\n"
                response += f"**Trend:** {'Up' if gold_change >= 0 else 'Down'} from last week\n\n"
        
        if is_silver or show_both:
            silver_data = yahoo_client.get_silver_price(period="14d")
            if not silver_data.empty:
                current_silver = float(silver_data["Close"].iloc[-1])
                week_ago_silver = float(silver_data["Close"].iloc[-7]) if len(silver_data) >= 7 else current_silver
                silver_change = ((current_silver / week_ago_silver) - 1) * 100
                silver_change_abs = current_silver - week_ago_silver
                
                change_symbol = "📈" if silver_change >= 0 else "📉"
                
                response += f"### 🥈 Silver\n"
                response += f"**Current Price:** ${current_silver:,.2f} USD per ounce\n"
                response += f"**Week Ago:** ${week_ago_silver:,.2f} USD\n"
                response += f"**Change:** {change_symbol} ${abs(silver_change_abs):,.2f} ({abs(silver_change):.2f}%)\n"
                response += f"**Trend:** {'Up' if silver_change >= 0 else 'Down'} from last week\n\n"
        
        if show_both and not gold_data.empty and not silver_data.empty:
            # Gold-Silver ratio
            gs_ratio = current_gold / current_silver
            response += f"### 📊 Gold-Silver Ratio\n"
            response += f"**Current Ratio:** {gs_ratio:.2f}:1\n"
            response += f"*(1 ounce of gold = {gs_ratio:.2f} ounces of silver)*\n\n"
        
        response += "*Prices are based on COMEX futures and may vary slightly from spot prices.*"
        
        return response
    
    except Exception as e:
        return f"I encountered an error fetching current prices: {str(e)}. Please try again."


@app.route('/api/prices', methods=['GET'])
def get_current_prices():
    """Get current gold and silver prices with week comparison"""
    try:
        from data_sources.yahoo_client import YahooClient
        
        yahoo_client = YahooClient()
        
        # Get current prices
        gold_data = yahoo_client.get_gold_price(period="14d")  # 2 weeks for comparison
        silver_data = yahoo_client.get_silver_price(period="14d")
        
        prices = {}
        
        if not gold_data.empty:
            current_gold = float(gold_data["Close"].iloc[-1])
            week_ago_gold = float(gold_data["Close"].iloc[-7]) if len(gold_data) >= 7 else current_gold
            gold_change = ((current_gold / week_ago_gold) - 1) * 100
            
            prices['gold'] = {
                'current': current_gold,
                'week_ago': week_ago_gold,
                'change_percent': round(gold_change, 2),
                'change_absolute': round(current_gold - week_ago_gold, 2),
                'currency': 'USD',
                'unit': 'per ounce'
            }
        
        if not silver_data.empty:
            current_silver = float(silver_data["Close"].iloc[-1])
            week_ago_silver = float(silver_data["Close"].iloc[-7]) if len(silver_data) >= 7 else current_silver
            silver_change = ((current_silver / week_ago_silver) - 1) * 100
            
            prices['silver'] = {
                'current': current_silver,
                'week_ago': week_ago_silver,
                'change_percent': round(silver_change, 2),
                'change_absolute': round(current_silver - week_ago_silver, 2),
                'currency': 'USD',
                'unit': 'per ounce'
            }
        
        return jsonify(prices)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    print("="*60)
    print("Gold & Silver Agent API Server")
    print("="*60)
    print("Starting server on http://localhost:5000")
    print("Frontend should be running on http://localhost:3000")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

