# Gold & Silver Prediction Agent System

A comprehensive multi-agent system for analyzing and predicting gold and silver price movements using macro, market, technical, and fundamental signals.

## System Architecture

```
┌────────────────────────────────────┐
│        Macro Data Agents           │
│ • Fed / Rates Agent                │
│ • Inflation Agent                  │
│ • USD (DXY) Agent                  │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│        Market Data Agents           │
│ • Gold price (spot / futures)       │
│ • Silver price                      │
│ • Volatility (GVZ, SVZ)             │
│ • ETF flows (GLD, SLV)              │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│      Technical Signal Agent         │
│ • RSI / MACD / EMA                  │
│ • Support & resistance              │
│ • Trend strength                    │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│     Fundamental Signal Agent        │
│ • Real rates pressure               │
│ • ETF flow momentum                 │
│ • Inflation surprise index          │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│     Correlation & Spread Agent      │
│ • Gold–Silver ratio                 │
│ • Gold vs USD                       │
│ • Silver vs copper                  │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│     Ensemble Prediction Agent       │
│ • 7-day directional bias            │
│ • 30–90 day regime outlook          │
│ • Confidence score                  │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│        LLM Reasoning Layer          │
│ • "Why this bias?"                  │
│ • Risk factors & invalidation       │
│ • Scenario narratives               │
└──────────────┬─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│          Output Layer               │
│ • Dashboard                         │
│ • Weekly report                     │
│ • Event-based alerts                │
└────────────────────────────────────┘
```

## Key Features

- **Multi-Agent Architecture**: Specialized agents for different signal types
- **Data Integration**: FRED, Yahoo Finance, ETF flows, COT reports
- **Ensemble Predictions**: Combines multiple signals with confidence scoring
- **LLM Reasoning**: Explains predictions and identifies risk factors
- **Legal Safety**: Built-in disclaimers to avoid financial advice liability

## Installation

1. Clone or download this repository

2. **Set up virtual environment** (recommended for modern Python installations):

   **Option A: Automated setup script**
   ```bash
   # First, install python3-venv if needed
   sudo apt install python3.12-venv
   
   # Run the setup script
   ./setup_venv.sh
   # OR
   bash setup_venv.sh
   ```

   **Option B: Manual setup**
   ```bash
   # Install python3-venv if needed
   sudo apt install python3.12-venv
   
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

   **Option C: Use --user flag** (if you can't use venv)
   ```bash
   pip3 install --user -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   # If using venv, activate it first
   source venv/bin/activate
   
   python3 check_dependencies.py
   ```

3. **Set up API keys** (optional but recommended):
```bash
cp env.sample .env
# Edit .env and add your API keys:
# - FRED_API_KEY (get from https://fred.stlouisfed.org/docs/api/api_key.html)
# - OPENAI_API_KEY (optional, for LLM explanations)
```

## Usage

**If using virtual environment:**
```bash
# Activate virtual environment
source venv/bin/activate

# Run the system
python main.py

# Or use the run script
./run.sh
```

**If not using virtual environment:**
```bash
python3 main.py
```

This will:
- Fetch data from all sources
- Run all specialized agents
- Generate ensemble predictions for gold and silver
- Create explanations using LLM reasoning
- Display comprehensive reports
- Export dashboard data to JSON

## System Components

### Agents
- **MacroAgent**: Analyzes Fed policy, rates, inflation, USD strength
- **MarketAgent**: Analyzes price momentum, ETF flows, volatility
- **TechnicalAgent**: Technical indicators (RSI, MACD, EMA, support/resistance)
- **FundamentalAgent**: Deep fundamental analysis (real rates, inflation surprises)
- **CorrelationAgent**: Cross-asset relationships (gold-silver ratio, USD, copper)
- **EnsembleAgent**: Combines all agents with weighted consensus

### Data Sources
- **FRED**: Economic data (rates, inflation)
- **Yahoo Finance**: Market prices, ETFs, volatility
- **ETF Clients**: Flow analysis (GLD, SLV)

### Output
- **Dashboard**: Real-time predictions and agent breakdowns
- **Reports**: Detailed text reports per commodity
- **JSON Export**: Machine-readable prediction data

## Prediction Outputs

For each commodity (gold, silver) and horizon (7D, 30D, 90D):

- **Signal**: Bullish / Neutral / Bearish
- **Confidence**: 0-100% (based on agent agreement and data quality)
- **Key Drivers**: Top 3 factors driving the prediction
- **Invalidation Conditions**: Events that would change the prediction
- **Agent Breakdown**: Individual agent signals and confidences
- **Reasoning**: LLM-generated explanation of "why"
- **Risk Factors**: Top risks to the prediction
- **Scenarios**: Plausible future scenarios

## Documentation

- **SYSTEM_DESIGN.md**: Detailed architecture and design decisions
- **DATA_SOURCES.md**: Complete data source documentation
- **LEGAL_DISCLAIMER.md**: Full legal terms and disclaimers
- **kpis.py**: KPI definitions and evaluation framework

## Legal Disclaimer

**IMPORTANT**: This system provides market analysis and information only. It does NOT constitute financial advice, investment recommendations, or trading signals. See `LEGAL_DISCLAIMER.md` for complete terms.

## KPIs and Evaluation

See `kpis.py` for:
- Directional accuracy metrics
- Confidence calibration
- Performance by commodity and horizon
- Risk-adjusted returns (if used as signals)

## Key Design Principles

1. **Multi-Agent Architecture**: Specialized agents for different signal types
2. **Ensemble Consensus**: Weighted combination of agent signals
3. **Confidence Scoring**: Uncertainty quantification for all predictions
4. **Legal Safety**: Built-in disclaimers and risk warnings
5. **Professional Analysis**: How professionals actually think about gold/silver

## What Moves Gold & Silver

### Gold Drivers
- USD strength (DXY) - negative correlation
- Real interest rates (10Y - inflation) - negative correlation
- Fed policy & forward guidance
- Inflation expectations (CPI, PCE)
- Geopolitical risk
- ETF flows (GLD)
- Central bank buying

### Silver Drivers
- Everything gold has, PLUS:
- Industrial demand (solar, EVs)
- Manufacturing PMIs
- Copper correlation
- China demand signals

The system treats gold and silver as **related but NOT identical** assets.

## Future Enhancements

- Direct LBMA spot price integration
- CFTC COT report parsing
- Central bank buying data
- PMI data for silver industrial demand
- Machine learning model integration
- Real-time alert system
- Interactive web dashboard

