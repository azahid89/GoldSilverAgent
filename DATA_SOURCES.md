# Data Sources Documentation

## Overview

This document details all data sources used by the Gold & Silver Prediction Agent System, organized by commodity and data type.

## Gold Data Sources

### Price Data
| Source | Symbol | Description | Update Frequency |
|--------|--------|-------------|------------------|
| Yahoo Finance | `GC=F` | COMEX Gold Futures | Real-time |
| LBMA | N/A | London Bullion Market Association Spot | Daily (future) |
| Yahoo Finance | `GLD` | SPDR Gold Trust ETF | Real-time |

### Volatility
| Source | Symbol | Description |
|--------|--------|-------------|
| Yahoo Finance | `GVZ` | Gold Volatility Index |

### Macro Drivers
| Source | Symbol | Description |
|--------|--------|-------------|
| FRED | `DGS10` | 10-Year Treasury Rate |
| FRED | `DFII10` | 10-Year TIPS (Real Rates) |
| FRED | `CPIAUCSL` | Consumer Price Index |
| FRED | `PCEPI` | Personal Consumption Expenditures |
| Yahoo Finance | `DX-Y.NYB` | USD Dollar Index (DXY) |
| Yahoo Finance | `VIX` | Volatility Index (Risk Sentiment) |

### ETF Flows
| Source | Symbol | Description |
|--------|--------|-------------|
| Yahoo Finance | `GLD` | SPDR Gold Trust (price/volume proxy) |
| ETF Provider | Direct | Holdings data (future) |
| CFTC | COT Reports | Speculative positioning (future) |

## Silver Data Sources

### Price Data
| Source | Symbol | Description | Update Frequency |
|--------|--------|-------------|------------------|
| Yahoo Finance | `SI=F` | COMEX Silver Futures | Real-time |
| LBMA | N/A | London Bullion Market Association Spot | Daily (future) |
| Yahoo Finance | `SLV` | iShares Silver Trust ETF | Real-time |

### Volatility
| Source | Symbol | Description |
|--------|--------|-------------|
| Yahoo Finance | `SVZ` | Silver Volatility Index |

### Industrial Demand Proxies
| Source | Symbol | Description |
|--------|--------|-------------|
| Yahoo Finance | `HG=F` | Copper Futures (correlation) |
| PMI Data | N/A | Manufacturing PMIs (future) |
| Industry Reports | N/A | Solar production data (future) |
| Trade Data | N/A | China demand signals (future) |

### Macro Drivers
Same as Gold (real rates, USD, inflation, etc.)

### ETF Flows
| Source | Symbol | Description |
|--------|--------|-------------|
| Yahoo Finance | `SLV` | iShares Silver Trust (price/volume proxy) |
| ETF Provider | Direct | Holdings data (future) |
| CFTC | COT Reports | Speculative positioning (future) |

## Data Source Details

### FRED (Federal Reserve Economic Data)
- **API**: https://fred.stlouisfed.org/docs/api/
- **API Key Required**: Yes (free registration)
- **Rate Limits**: 120 requests per minute
- **Data Frequency**: Varies by series (daily, monthly, etc.)
- **Latency**: Usually same-day or next-day

**Key Series**:
- `DGS10`: 10-Year Treasury Constant Maturity Rate (daily)
- `DFII10`: 10-Year Treasury Inflation-Indexed Security (daily)
- `CPIAUCSL`: Consumer Price Index for All Urban Consumers (monthly)
- `PCEPI`: Personal Consumption Expenditures Price Index (monthly)

### Yahoo Finance
- **API**: yfinance Python library
- **API Key Required**: No
- **Rate Limits**: Informal (be respectful)
- **Data Frequency**: Real-time for active markets
- **Latency**: Near real-time

**Key Symbols**:
- `GC=F`: Gold Futures
- `SI=F`: Silver Futures
- `GLD`: Gold ETF
- `SLV`: Silver ETF
- `DX-Y.NYB`: USD Dollar Index
- `VIX`: Volatility Index
- `GVZ`: Gold Volatility Index
- `SVZ`: Silver Volatility Index
- `HG=F`: Copper Futures

### ETF Data (Current Implementation)
Currently uses Yahoo Finance price/volume as proxy for flows.

**Future Enhancements**:
- Direct API access to ETF providers (SPDR, iShares)
- Holdings data from ETF websites
- Flow calculation from NAV changes

### CFTC COT Reports (Future)
- **Source**: Commodity Futures Trading Commission
- **Frequency**: Weekly (Fridays)
- **Data**: Speculative positioning, commercial hedging
- **Access**: Public data, requires parsing

### LBMA (Future)
- **Source**: London Bullion Market Association
- **Frequency**: Daily (AM/PM fixes)
- **Data**: Official spot prices
- **Access**: Via aggregators or direct API (if available)

## Data Quality Considerations

### Reliability
- **FRED**: Highly reliable, official government data
- **Yahoo Finance**: Generally reliable, but unofficial
- **ETF Data**: Proxy method less accurate than direct holdings

### Latency
- **Real-time**: Yahoo Finance (during market hours)
- **Daily**: FRED (next-day for some series)
- **Weekly**: COT reports (Friday releases)

### Missing Data Handling
- System handles missing data gracefully
- Confidence scores adjust based on data availability
- Fallback to available data sources when possible

## API Setup Instructions

### FRED API Key
1. Register at https://fred.stlouisfed.org/
2. Go to "My Account" → "API Keys"
3. Create new API key
4. Copy `env.sample` to `.env` and add: `FRED_API_KEY=your_key_here`

### Yahoo Finance
- No setup required
- Uses yfinance library
- May require internet connection

### OpenAI (Optional)
1. Register at https://platform.openai.com/
2. Create API key
3. Copy `env.sample` to `.env` and add: `OPENAI_API_KEY=your_key_here`
4. System works without it (uses template explanations)

## Data Update Frequency

### Real-time Updates
- Price data (during market hours)
- Volatility indices

### Daily Updates
- FRED economic data (next-day)
- ETF prices/volumes

### Weekly Updates
- COT reports (Fridays)

### Monthly Updates
- CPI, PCE (monthly releases)

## Data Storage

Currently, data is fetched on-demand and not persisted. Future enhancements:
- Caching layer for frequently accessed data
- Historical data storage
- Database for prediction history
- Performance metrics tracking

