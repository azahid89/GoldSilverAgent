"""
Flask API Server for Gold & Silver Agent System
Connects React frontend to Python agents
"""
from flask import Flask, request, jsonify, Response, stream_with_context
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from datetime import datetime
import sys
import os
import time
import json
import random
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.ensemble_agent import EnsembleAgent
from reasoning.llm_reasoning import LLMReasoningLayer
from config import PREDICTION_HORIZONS

class UpdatedJSONProvider(DefaultJSONProvider):
    """Custom JSON provider for numpy types (Modern Flask 2.2+)"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.json = UpdatedJSONProvider(app)

# CORS configuration - allow all origins in development, restrict in production
# For production, set ALLOWED_ORIGINS environment variable
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

# Initialize agents (lazy loading)
ensemble_agents = {}
reasoning_layer = None

# Simple conversation context (in production, use Redis or database)
conversation_context = {}


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
        session_id = data.get('session_id', 'default')  # Simple session tracking
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Handle greeting messages
        message_lower = message.lower().strip()
        if any(greeting in message_lower for greeting in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']):
            greeting_response = get_greeting_response()
            if stream:
                return Response(
                    stream_with_context(generate_streaming_response_direct(greeting_response)),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no',
                        'Connection': 'keep-alive',
                    }
                )
            else:
                return jsonify({'response': greeting_response})
        
        if stream:
            # Return streaming response
            return Response(
                stream_with_context(generate_streaming_response(message, session_id)),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive',
                }
            )
        else:
            # Return regular response
            response = process_chat_message(message, session_id)
            return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_streaming_response(message, session_id='default'):
    """Generate streaming response with progress updates"""
    try:
        # Send friendly initial message
        friendly_messages = [
            "Let me look that up for you... ",
            "Great question! Let me check... ",
            "I'm on it! ",
            "Analyzing the latest data... "
        ]
        initial_msg = random.choice(friendly_messages)
        yield f"data: {json.dumps({'content': initial_msg, 'done': False})}\n\n"
        time.sleep(0.1)
        
        # Process the message to get full response
        full_response = process_chat_message(message, session_id)
        
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
        error_msg = get_friendly_error_message(str(e))
        for char in error_msg:
            yield f"data: {json.dumps({'content': char, 'done': False})}\n\n"
            time.sleep(0.005)
        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"


def generate_streaming_response_direct(response_text):
    """Generate streaming response for direct text (like greetings)"""
    chunk_size = 3
    for i in range(0, len(response_text), chunk_size):
        chunk = response_text[i:i+chunk_size]
        yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        time.sleep(0.005)
    yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"


def get_greeting_response():
    """Return a friendly greeting message"""
    return """Hi there! 👋 

I'm your friendly Gold & Silver market assistant! I'm here to help you understand precious metals markets, answer questions, and provide insights.

**What I can help with:**
- Current gold and silver prices
- Market predictions and forecasts
- Understanding market drivers and factors
- General questions about precious metals
- Market analysis and trends

Just ask me anything in natural language - I'll do my best to help! For example:
- "What's the gold price today?"
- "Tell me about silver predictions"
- "How does inflation affect gold?"
- Or anything else you're curious about!

What would you like to know? 😊"""


def process_chat_message(message, session_id='default'):
    """Process user message and generate intelligent response using LLM-based intent classification"""
    try:
        # Check if question is off-topic
        if is_off_topic(message):
            return handle_off_topic_question(message)
        
        reasoning = get_reasoning_layer()
        
        # Get conversation history for context
        conversation_history = conversation_context.get(session_id, [])
        
        # Use LLM to classify intent and route appropriately
        if reasoning.client:
            intent = classify_user_intent(message, reasoning.client, conversation_history)
        else:
            # Fallback to keyword-based classification if LLM unavailable
            intent = classify_intent_keywords(message)
        
        # Update conversation history (keep last 5 messages)
        conversation_history.append({'role': 'user', 'content': message})
        if len(conversation_history) > 10:  # Keep last 5 exchanges (10 messages)
            conversation_history = conversation_history[-10:]
        conversation_context[session_id] = conversation_history
        
        # Route based on intent
        if intent['type'] == 'price_query':
            response = handle_price_query(message, intent)
        elif intent['type'] == 'prediction_query':
            response = handle_prediction_query(message, intent)
        elif intent['type'] == 'driver_analysis':
            response = handle_driver_analysis(message, intent)
        elif intent['type'] == 'help_query':
            response = get_help_response()
        else:
            # General question - use LLM with full context
            response = answer_general_question(message, intent, conversation_history)
        
        # Add response to history
        conversation_history.append({'role': 'assistant', 'content': response})
        conversation_context[session_id] = conversation_history
        
        return response
    
    except Exception as e:
        return get_friendly_error_message(str(e))


def classify_user_intent(message, llm_client, conversation_history=None):
    """Use LLM to classify user intent from natural language"""
    try:
        history_context = ""
        if conversation_history and len(conversation_history) > 0:
            # Include last 2 exchanges for context
            recent_history = conversation_history[-4:] if len(conversation_history) >= 4 else conversation_history
            history_context = "\n\nRecent conversation context:\n"
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')[:100]  # Truncate for context
                history_context += f"{role}: {content}\n"
        
        prompt = f"""Analyze this user question about gold and silver markets and classify the intent.
{history_context}
User Question: "{message}"

Classify the intent into one of these categories:
1. price_query - User wants current prices, rates, or price comparisons
2. prediction_query - User wants predictions, forecasts, outlook, or future price direction
3. driver_analysis - User wants to understand factors, drivers, reasons, or explanations for market movements
4. help_query - User wants help, capabilities, or examples
5. general_question - Any other question about gold/silver markets, history, concepts, comparisons, etc.

Also extract:
- commodity: "gold", "silver", "both", or "none"
- horizon: number of days if mentioned (7, 30, 90), or null
- specific_info: any specific data points requested

Respond in JSON format:
{{
    "type": "intent_category",
    "commodity": "gold|silver|both|none",
    "horizon": number_or_null,
    "specific_info": "any specific data requested",
    "confidence": 0.0-1.0
}}"""

        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intent classification system. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        import json
        result = json.loads(response.choices[0].message.content.strip())
        return result
    
    except Exception as e:
        print(f"Error classifying intent: {e}")
        return classify_intent_keywords(message)


def classify_intent_keywords(message):
    """Fallback keyword-based intent classification"""
    message_lower = message.lower()
    
    # Price queries
    if any(word in message_lower for word in ['price', 'rate', 'current', 'today', 'cost', 'value']):
        commodity = 'both'
        if 'gold' in message_lower:
            commodity = 'gold'
        elif 'silver' in message_lower:
            commodity = 'silver'
        return {'type': 'price_query', 'commodity': commodity, 'horizon': None, 'confidence': 0.8}
    
    # Prediction queries
    if any(word in message_lower for word in ['prediction', 'forecast', 'outlook', 'expect', 'will', 'going to']):
        commodity = 'gold'
        if 'silver' in message_lower and 'gold' not in message_lower:
            commodity = 'silver'
        elif 'silver' in message_lower:
            commodity = 'both'
        
        horizon = 30
        if '7' in message or 'week' in message_lower:
            horizon = 7
        elif '90' in message or 'quarter' in message_lower:
            horizon = 90
        
        return {'type': 'prediction_query', 'commodity': commodity, 'horizon': horizon, 'confidence': 0.8}
    
    # Driver analysis
    if any(word in message_lower for word in ['driver', 'factor', 'why', 'reason', 'cause', 'explain']):
        commodity = 'gold'
        if 'silver' in message_lower and 'gold' not in message_lower:
            commodity = 'silver'
        return {'type': 'driver_analysis', 'commodity': commodity, 'horizon': None, 'confidence': 0.8}
    
    # Help queries
    if any(word in message_lower for word in ['help', 'what can', 'how', 'capabilities', 'examples']):
        return {'type': 'help_query', 'commodity': 'none', 'horizon': None, 'confidence': 0.9}
    
    # Default to general question
    commodity = 'both'
    if 'gold' in message_lower and 'silver' not in message_lower:
        commodity = 'gold'
    elif 'silver' in message_lower and 'gold' not in message_lower:
        commodity = 'silver'
    
    return {'type': 'general_question', 'commodity': commodity, 'horizon': None, 'confidence': 0.7}


def handle_price_query(message, intent):
    """Handle price-related queries"""
    commodity = intent.get('commodity', 'both')
    if commodity == 'none':
        commodity = 'both'
    
    message_lower = message.lower()
    is_gold = commodity in ['gold', 'both']
    is_silver = commodity in ['silver', 'both']
    
    response = get_price_response(message_lower, is_gold, is_silver)
    # Add friendly intro if not already present
    if not response.startswith('Hi') and not response.startswith('Here'):
        response = "Here's the latest price information! 📊\n\n" + response
    return response


def handle_prediction_query(message, intent):
    """Handle prediction-related queries"""
    commodity = intent.get('commodity', 'gold')
    horizon = intent.get('horizon', 30)
    
    if commodity == 'none':
        commodity = 'gold'
    
    # Friendly intro
    intro = f"Great question! Let me analyze the {horizon}-day outlook for you. 📊\n\n"
    
    if commodity == 'both':
        # Handle both commodities
        response = intro
        for comm in ['gold', 'silver']:
            try:
                ensemble = get_ensemble_agent(comm)
                prediction = ensemble.get_ensemble_prediction(horizon_days=horizon)
                reasoning = get_reasoning_layer()
                explanation = reasoning.generate_explanation(prediction)
                
                response += f"## {comm.capitalize()} Prediction ({horizon}-day horizon)\n\n"
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
                response += "\n---\n\n"
            except Exception as e:
                response += f"Sorry, I had trouble generating the {comm} prediction: {str(e)}\n\n"
        
        return response
    else:
        # Single commodity
        try:
            ensemble = get_ensemble_agent(commodity)
            prediction = ensemble.get_ensemble_prediction(horizon_days=horizon)
            reasoning = get_reasoning_layer()
            explanation = reasoning.generate_explanation(prediction)
            
            response = intro + f"## {commodity.capitalize()} Prediction ({horizon}-day horizon)\n\n"
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
            return get_friendly_error_message(str(e))


def handle_driver_analysis(message, intent):
    """Handle driver/factor analysis queries"""
    commodity = intent.get('commodity', 'gold')
    if commodity == 'none':
        commodity = 'gold'
    
    try:
        ensemble = get_ensemble_agent(commodity)
        prediction = ensemble.get_ensemble_prediction(horizon_days=30)
        
        response = f"Great question! Let me break down the key factors affecting {commodity}. 💡\n\n"
        response += f"## Key Drivers for {commodity.capitalize()}\n\n"
        response += "Here are the main factors influencing the current outlook:\n\n"
        
        for i, driver in enumerate(prediction.get('drivers', []), 1):
            response += f"{i}. **{driver}**\n"
        
        response += "\n**Agent Analysis Breakdown:**\n"
        for agent, data in prediction.get('agent_breakdown', {}).items():
            signal_emoji = "📈" if data.get('signal') == 'bullish' else "📉" if data.get('signal') == 'bearish' else "➡️"
            response += f"- {agent.capitalize()}: {signal_emoji} {data.get('signal', 'neutral').upper()} "
            response += f"({data.get('confidence', 0):.1f}% confidence)\n"
        
        return response
    
    except Exception as e:
        return get_friendly_error_message(str(e))


def get_help_response():
    """Return help information"""
    return """## How I Can Help You! 😊

Hi! I'm your friendly Gold & Silver market assistant. I'm here to help you understand precious metals markets in a simple, conversational way!

**What I Can Do:**

**💰 Current Prices:**
- "What's the gold price today?"
- "Show me current silver rates"
- "Compare gold and silver prices"
- "How much is gold right now?"

**🔮 Predictions & Forecasts:**
- "What's the gold prediction for next week?"
- "Show me silver forecast for 90 days"
- "What do you think will happen to gold prices?"
- "Will silver go up next month?"

**📊 Market Analysis:**
- "What are the drivers for gold?"
- "Why is silver bullish?"
- "Explain the factors affecting gold prices"
- "What makes gold prices move?"

**💡 General Questions:**
- "What's the difference between gold and silver?"
- "How does inflation affect gold?"
- "What is the gold-silver ratio?"
- "Tell me about central bank gold reserves"
- "How do interest rates impact precious metals?"
- Any other question about gold and silver markets!

**💬 Just Ask Naturally!**

You don't need to use specific keywords - just ask me anything in your own words! For example:
- "What's the gold price today?"
- "What's your prediction for silver next month?"
- "Why might gold go up?"
- "How does the dollar affect precious metals?"
- "What's the relationship between gold and interest rates?"
- "I'm curious about silver - tell me more!"

I'm here to help make understanding markets easier and more approachable. What would you like to know? 😊"""


def answer_general_question(message, intent=None, conversation_history=None):
    """Answer any general question about gold and silver using LLM with intelligent data integration"""
    try:
        reasoning = get_reasoning_layer()
        
        # Get comprehensive market context
        context = get_market_context()
        
        # Check if we need to fetch additional data based on the question
        additional_data = fetch_relevant_data(message, intent)
        if additional_data:
            context += f"\n\nAdditional Relevant Data:\n{additional_data}"
        
        # Build conversation context for LLM
        messages = []
        system_message = """You are a friendly, knowledgeable commodities analyst specializing in gold and silver markets. 
You're warm, approachable, and genuinely helpful. You have access to real-time market data and can provide comprehensive, accurate answers.

Your personality:
- Friendly and conversational (like talking to a knowledgeable friend)
- Professional but warm (not robotic or overly formal)
- Enthusiastic about helping people understand markets
- Honest when you don't know something
- Use emojis sparingly but naturally (😊, 📊, 💡, etc.)
- Break down complex concepts simply

IMPORTANT: 
- Do NOT provide investment advice
- Focus on education, market analysis, and factual information
- Be encouraging and supportive
- If asked about something outside gold/silver, politely redirect or explain your focus"""
        
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history if available
        if conversation_history and len(conversation_history) > 0:
            # Include relevant history (last 4 messages = 2 exchanges)
            for msg in conversation_history[-4:]:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role in ['user', 'assistant']:
                    messages.append({"role": role, "content": content})
        
        # Add current question with context
        prompt = f"""Current Market Context:
{context}

User Question: {message}

Please provide a friendly, comprehensive answer. Be conversational and helpful. Use markdown for formatting when helpful."""
        
        messages.append({"role": "user", "content": prompt})

        # Use LLM if available
        if reasoning.client:
            try:
                response = reasoning.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.8,  # Slightly higher for more natural conversation
                    max_tokens=1500
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"LLM error: {e}")
                # Fall back to template response
        
        # Fallback: Template-based response for common questions
        return get_template_response(message, context)
    
    except Exception as e:
        return get_friendly_error_message(str(e))


def is_off_topic(message):
    """Check if question is completely off-topic from gold/silver markets"""
    message_lower = message.lower()
    
    # If it mentions gold or silver, it's on-topic
    if 'gold' in message_lower or 'silver' in message_lower:
        return False
    
    # Check for market-related terms
    market_terms = ['price', 'market', 'commodity', 'precious metal', 'metal', 'investment', 
                   'trading', 'forecast', 'prediction', 'bullion', 'xau', 'xag', 'inflation',
                   'interest rate', 'fed', 'treasury', 'dollar', 'currency', 'economy']
    
    if any(term in message_lower for term in market_terms):
        return False
    
    # Very off-topic questions (weather, sports, etc.)
    off_topic_terms = ['weather', 'sports', 'movie', 'recipe', 'cooking', 'game', 'sport']
    if any(term in message_lower for term in off_topic_terms):
        return True
    
    # If it's a greeting or small talk, it's fine
    greetings = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
    if any(greeting in message_lower for greeting in greetings):
        return False
    
    # Default: assume it might be related (be permissive)
    return False


def handle_off_topic_question(message):
    """Handle off-topic questions in a friendly way"""
    return """I appreciate your question! 😊 

I'm specifically designed to help with questions about **gold and silver markets**. While I'd love to chat about everything, I'm best at helping you understand:
- Gold and silver prices and trends
- Market analysis and predictions
- Factors affecting precious metals
- Market concepts and relationships

If you have a question about gold or silver, I'm here to help! Or if you're curious about how something relates to precious metals markets, feel free to ask - I might be able to make a connection!

What would you like to know about gold or silver? 💡"""


def get_friendly_error_message(error_str):
    """Generate a friendly error message instead of technical error"""
    return f"""Oops! 😅 I ran into a little issue: {error_str}

No worries though - could you try rephrasing your question? Sometimes that helps! 

If you're asking about:
- **Prices**: Try "What's the gold price?" or "Show me silver rates"
- **Predictions**: Try "What's your gold forecast?" or "Silver outlook"
- **General questions**: Just ask naturally!

I'm here to help, so don't hesitate to ask again! 😊"""


def fetch_relevant_data(message, intent=None):
    """Fetch additional relevant data based on the question"""
    message_lower = message.lower()
    additional_data = []
    
    try:
        # Check if question is about specific indicators
        if any(word in message_lower for word in ['interest rate', 'fed', 'treasury', 'yield']):
            from data_sources.fred_client import FREDClient
            fred_client = FREDClient()
            try:
                yield_curve = fred_client.get_yield_curve(days=7)
                if not yield_curve.empty:
                    additional_data.append(f"10Y-2Y Yield Curve: {yield_curve.iloc[-1]:.2f}")
            except:
                pass
        
        if any(word in message_lower for word in ['inflation', 'cpi', 'pce']):
            from data_sources.fred_client import FREDClient
            fred_client = FREDClient()
            try:
                # Add inflation context if available
                additional_data.append("Inflation data available in market context")
            except:
                pass
        
        if any(word in message_lower for word in ['etf', 'flow', 'demand']):
            # ETF flow data would be here
            additional_data.append("ETF flow data considered in market context")
        
        if any(word in message_lower for word in ['correlation', 'relationship', 'compare', 'vs']):
            # Add correlation data
            try:
                from data_sources.yahoo_client import YahooClient
                yahoo_client = YahooClient()
                gold_data = yahoo_client.get_gold_price(period="30d")
                silver_data = yahoo_client.get_silver_price(period="30d")
                if not gold_data.empty and not silver_data.empty:
                    gold_price = float(gold_data["Close"].iloc[-1])
                    silver_price = float(silver_data["Close"].iloc[-1])
                    ratio = gold_price / silver_price
                    additional_data.append(f"Current Gold-Silver Ratio: {ratio:.2f}:1")
            except:
                pass
        
    except Exception as e:
        print(f"Error fetching additional data: {e}")
    
    return "\n".join(additional_data) if additional_data else None


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
        
        # Add COT and Reserves context
        try:
            from data_sources.nasdaq_client import NasdaqClient
            nasdaq_client = NasdaqClient()
            gold_cot = nasdaq_client.get_gold_cot()
            if not gold_cot.empty and "Noncommercial Long" in gold_cot.columns:
                net_pos = gold_cot["Noncommercial Long"].iloc[-1] - gold_cot["Noncommercial Short"].iloc[-1]
                context.append(f"Gold Net Institutional Position: {net_pos:,.0f} contracts")
            
            reserves = fred_client.get_gold_reserves(days=365)
            if not reserves.empty:
                context.append(f"Latest Central Bank Gold Reserves: {reserves.iloc[-1]:,.2f} Fine Troy Oz")
            
            # Silver industrial proxies
            semi_prod = fred_client.get_semiconductor_production(days=180)
            if not semi_prod.empty:
                trend = (semi_prod.iloc[-1] / semi_prod.iloc[-3] - 1) * 100 if len(semi_prod) >= 3 else 0
                context.append(f"Solar/Semiconductor Production Trend: {trend:+.2f}%")
        except Exception as e:
            print(f"Error adding advanced context: {e}")
        
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


def get_price_response(message_lower, is_gold=True, is_silver=True):
    """Generate response for price queries"""
    from data_sources.yahoo_client import YahooClient
    
    yahoo_client = YahooClient()
    
    response = "## Current Prices & Week Comparison\n\n"
    
    # Determine which commodity to show
    show_both = is_gold and is_silver
    gold_data = None
    silver_data = None
    current_gold = None
    current_silver = None
    
    try:
        if is_gold or show_both:
            gold_data = yahoo_client.get_gold_price(period="14d")
            if not gold_data.empty:
                current_gold = float(gold_data["Close"].iloc[-1])
                week_ago_gold = float(gold_data["Close"].iloc[-7]) if len(gold_data) >= 7 else current_gold
                gold_change = ((current_gold / week_ago_gold) - 1) * 100
                gold_change_abs = current_gold - week_ago_gold
                
                change_symbol = "📈" if gold_change >= 0 else "📉"
                
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
        
        if show_both and gold_data is not None and silver_data is not None and not gold_data.empty and not silver_data.empty and current_gold and current_silver:
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

