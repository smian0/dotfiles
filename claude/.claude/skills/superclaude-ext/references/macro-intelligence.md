# Macro Intelligence Domain Guide

## Overview

The Macro Intelligence domain provides institutional-grade economic analysis, market intelligence, and trading insights across all asset classes.

## Available Agents

### macro-analyst
Elite macro economic intelligence providing executive briefings:
- Federal Reserve and central bank policy analysis
- Economic indicator interpretation
- Risk assessment and tail risk identification
- Cross-asset impact analysis
- Trade idea generation with specific levels

**Signal Strength Rating**: 1-10 scale for all developments
**Time Sensitivity**: Immediate/Today/This Week/Monitor
**Best for**: Trading decisions, risk management, portfolio positioning

### market-analyzer
Cross-asset market analysis across equities, bonds, FX, and commodities:
- Technical analysis with support/resistance levels
- Fundamental drivers and valuations
- Correlation analysis and regime identification
- Inter-market relationships

**Best for**: Market timing, asset allocation, technical setups

### research-assistant
Multi-source research and validation:
- Data collection from multiple sources
- Fact validation and cross-referencing
- Synthesis and report generation
- Confidence scoring

**Best for**: Deep dives, data validation, comprehensive research

## Market Regimes

### Regime Classification
- 🐂 **Risk-On**: Equities up, VIX down, credit spreads tight
- 🐻 **Risk-Off**: Bonds up, USD/JPY down, gold up
- 🦘 **Choppy**: Mixed signals, regime transition
- 🦢 **Black Swan**: Extreme moves, correlation = 1

## Common Use Cases

### Daily Briefing
```
@superclaude-ext/macro-analyst morning macro briefing
```

### Fed Analysis
```
@superclaude-ext/macro-analyst Fed impact on markets with trade ideas
```

### Market Analysis
```
@superclaude-ext/market-analyzer analyze SPY with technical levels
```

### Research Project
```
@superclaude-ext/research-assistant research inflation impact on tech valuations
```

## Key Indicators Tracked

### Economic Indicators
- **Growth**: GDP, PMI, Industrial Production
- **Inflation**: CPI, PPI, PCE, Wage Growth
- **Labor**: NFP, Unemployment, JOLTS
- **Consumer**: Retail Sales, Consumer Confidence
- **Housing**: Starts, Sales, Prices

### Market Indicators
- **Volatility**: VIX, MOVE, Currency vol
- **Yields**: 2Y, 10Y, 30Y, Real yields
- **Spreads**: Credit, Term, TED
- **Positioning**: COT, Fund flows, Put/Call
- **Breadth**: A/D line, New highs/lows

### Central Banks
- **Fed**: FOMC, Dot plot, Balance sheet
- **ECB**: Governing Council, PEPP, TLTROs
- **BoJ**: YCC, ETF purchases, Kuroda-san
- **BoE**: MPC, Bailey guidance
- **PBoC**: RRR, MLF, Yuan fixing

## Trading Framework

### Trade Idea Structure
```
Asset/Strategy: [Specific instrument]
Rationale: [Why now]
Entry: [Specific level]
Target: [Level] ([X]% move)
Stop: [Level] ([X]% risk)
Risk/Reward: [X:X ratio]
Timeframe: [Days/Weeks/Months]
```

### Risk Management Rules
- Maximum 2% portfolio risk per idea
- Minimum 2:1 risk/reward ratio
- Always define stops before entry
- Trail stops on winning positions
- Monitor correlation risk

### Position Sizing
```
Position Size = (Account Risk %) / (Stop Distance %)
```

## Analysis Techniques

### Multi-Timeframe Analysis
- **Intraday**: Immediate opportunities
- **Daily**: Tactical positions
- **Weekly**: Trend confirmation
- **Monthly**: Regime identification

### Technical Indicators
- **Momentum**: RSI, MACD, Stochastics
- **Trend**: Moving averages, ADX, Ichimoku
- **Volume**: OBV, Money flow, Volume profile
- **Volatility**: ATR, Bollinger bands, Keltner

### Fundamental Analysis
- **Valuation**: P/E, P/B, EV/EBITDA
- **Growth**: Revenue, EPS, margins
- **Quality**: ROE, ROIC, Debt/Equity
- **Macro**: Correlations, beta, factor exposure

## Special Scenarios

### FOMC Days
**Pre-Meeting**:
- Position analysis
- Scenario planning
- Risk hedging

**Real-Time**:
- Statement parsing
- Dot plot analysis
- Key phrase detection

**Post-Meeting**:
- Market reaction
- Trade opportunities
- Regime shifts

### Crisis Response
**Monitoring**:
- Correlation breaks
- Funding stress
- Safe haven flows
- Central bank response

**Actions**:
- Increase update frequency
- Focus on liquidity
- Identify dislocations
- Track interventions

### Month/Quarter End
**Effects**:
- Rebalancing flows
- Window dressing
- Pension reallocation
- Index changes
- Option expiry

## Output Formats

### Executive Briefing
```markdown
# Macro Briefing
**Regime**: [Current regime]
**Key Development**: [Most important item]
**Action Required**: [Yes/No]
**Trade Ideas**: [Number]
```

### Detailed Analysis
```markdown
# Comprehensive Analysis
## Critical Developments
## Market Impact
## Trading Opportunities
## Risk Assessment
## Upcoming Catalysts
```

## Best Practices

### For Macro Analysis
1. Specify time horizon (intraday/daily/weekly)
2. Include risk tolerance
3. Mention portfolio context
4. Define success metrics
5. Set alert thresholds

### For Market Analysis
1. Specify assets of interest
2. Include technical/fundamental preference
3. Define position timeframe
4. Mention current positions
5. Set risk parameters

### For Research
1. Define research objectives
2. Specify data sources preferred
3. Include time constraints
4. Mention output format needed
5. Define confidence requirements

## Integration Examples

### Pre-Market Workflow
```
1. @superclaude-ext/macro-analyst overnight developments
2. @superclaude-ext/market-analyzer pre-market levels
3. Generate trading plan
```

### Event Analysis
```
1. @superclaude-ext/research-assistant gather event data
2. @superclaude-ext/macro-analyst impact assessment
3. @superclaude-ext/market-analyzer technical setup
```

## Risk Warnings

### Disclaimers
- Analysis is not personal investment advice
- Past performance doesn't guarantee future results
- All investments carry risk of loss
- Consult qualified advisors for personal situation

### Risk Factors
- Market volatility
- Liquidity risk
- Counterparty risk
- Regulatory changes
- Black swan events

## Advanced Features

### Custom Alerts
Set specific triggers:
```
Alert when VIX > 30
Alert when 10Y > 4.5%
Alert when DXY breaks 106
```

### Portfolio Analysis
Analyze existing positions:
```
@superclaude-ext/macro-analyst analyze portfolio risk given current macro
```

### Scenario Testing
Test multiple scenarios:
```
@superclaude-ext/macro-analyst analyze:
1. Fed pause scenario
2. Recession scenario
3. Soft landing scenario
```