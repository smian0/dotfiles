---
title: Wheel Strategy Signal Generator
description: Scan quality dividend stocks for optimal wheel strategy opportunities using parallel multi-agent analysis. Institutional-grade screening with ranked trade recommendations.
category: trading
---

# Wheel Strategy Signal Generator

Generate ranked wheel strategy trade recommendations using parallel analysis of quality dividend-paying stocks.

## Strategy Overview

**The Wheel Strategy**: Institutional favorite for consistent premium income
- Phase 1: Sell cash-secured puts → Collect premium while waiting to buy at discount
- Phase 2: Sell covered calls on assigned stock → Continue collecting premiums
- Triple income potential: Put premiums + Call premiums + Dividends

**Why Institutions Love It:**
- Consistent income in sideways markets (80% of conditions)
- Forced disciplined entry/exit prices
- Proven over decades
- Scales to any capital size

## Command Usage

```
/trading:wheel-scan <watchlist|tickers>
```

**Arguments:**
- `sp100-dividends` - S&P 100 dividend aristocrats (pre-configured)
- `"TICKER1 TICKER2 ..."` - Custom space-separated tickers (quoted)

**Examples:**
```
/trading:wheel-scan sp100-dividends
/trading:wheel-scan "KO JNJ PG WMT T"
/trading:wheel-scan "AAPL MSFT GOOGL"
```

## Execution Workflow

### Pre-configured Watchlists

**sp100-dividends** (S&P 100 Dividend Aristocrats - 25+ year dividend growth):
```
KO JNJ PG WMT T PEP CL MMM CAT XOM CVX
JNJ ABT MDT TMO LLY UNH
WBA WMT HD LOW TGT
PFE MRK BMY ABBV AMGN GILD
NEE DUK SO D AEP
```

(Use subset for faster testing, or all for comprehensive scan)

### Phase 1: Parallel Ticker Screening (2-3 min)

**Objective:** Analyze each ticker independently for wheel viability

**For each ticker, launch parallel agent using Task tool:**

```
Task(
  subagent_type="general-purpose",
  description=f"Analyze {ticker} for wheel strategy",
  prompt=f'''
Analyze {ticker} for Wheel Strategy suitability:

1. Get stock fundamentals (yfinance get_ticker_info):
   - Current price, dividend yield, beta, market cap
   - Verify: dividend > 0%, market cap > $10B, quality stock

2. Get options expirations (yfinance get_options_dates):
   - Target: 30-45 DTE (days to expiration)
   - Select nearest expiration in 30-45 day range

3. Analyze put options (yfinance get_options_chain):
   - Focus on strikes 2-5% below current price (slight OTM)
   - Get: premium, bid/ask spread, volume, open interest, IV
   - Format: calls only, summary mode, JSON format

4. Calculate metrics:
   ```python
   strike = current_price * 0.95  # 5% below
   premium_yield_annual = (premium / strike) * (365 / days_to_expiration) * 100
   assignment_delta = 0.15-0.25 range ideal (15-25% probability)
   breakeven = strike - premium
   ```

5. Return structured JSON:
   ```json
   {{
     "ticker": "{ticker}",
     "current_price": <float>,
     "dividend_yield": <float>,
     "beta": <float>,
     "recommended_put": {{
       "strike": <float>,
       "premium": <float>,
       "expiration": "YYYY-MM-DD",
       "annualized_yield": <float>,
       "bid_ask_spread_pct": <float>,
       "open_interest": <int>,
       "implied_volatility": <float>
     }},
     "metrics": {{
       "breakeven": <float>,
       "downside_protection_pct": <float>
     }}
   }}
   ```

If ticker invalid or no options: Return {{"error": "reason"}}
  '''
)
```

**Parallelization:**
- Launch max 20 concurrent agents (API rate limit protection)
- Each agent timeout: 30 seconds
- Failed agents don't block others
- For 100+ tickers: batch in groups of 20

**Agent Management:**
```python
from concurrent.futures import wait, FIRST_COMPLETED
agents = []
results = []

for ticker in tickers[:20]:  # First batch
    agent = Task(...)
    agents.append(agent)

# Wait for completion
while agents:
    done, agents = wait(agents, return_when=FIRST_COMPLETED)
    for agent in done:
        try:
            result = agent.result()  # Get result
            results.append(result)
        except Exception as e:
            # Log failure, continue with others
            results.append({"ticker": ticker, "error": str(e)})
```

### Phase 2: Aggregation & Ranking (30 sec)

**Objective:** Score and rank candidates by wheel attractiveness

**Weighted Scoring Algorithm:**

```python
def calculate_wheel_score(ticker_data):
    # Extract data
    premium_yield = ticker_data['recommended_put']['annualized_yield']
    dividend_yield = ticker_data['dividend_yield']
    iv = ticker_data['recommended_put']['implied_volatility']
    open_interest = ticker_data['recommended_put']['open_interest']
    spread_pct = ticker_data['recommended_put']['bid_ask_spread_pct']
    beta = ticker_data['beta']

    # Normalize each component 0-1
    premium_score = min(premium_yield / 30, 1.0)  # 30% annual = perfect
    dividend_score = min(dividend_yield / 8, 1.0)  # 8% div = perfect
    iv_score = min(iv / 0.50, 1.0)  # 50% IV = perfect
    liquidity_score = min(open_interest / 10000, 1.0) * (1 - min(spread_pct / 5, 1.0))
    quality_score = 1.0 if beta < 1.2 else 0.5

    # Weighted sum
    total_score = (
        0.40 * premium_score +    # Premium yield most important
        0.20 * dividend_score +   # Dividend income
        0.20 * iv_score +         # IV for premium generation
        0.10 * liquidity_score +  # Tight spreads, high OI
        0.10 * quality_score      # Quality/low volatility
    )

    return total_score * 100  # Scale to 0-100
```

**Ranking:**
1. Calculate score for each valid result (skip errors)
2. Sort by score descending
3. Take top 5-10 for detailed analysis
4. Flag quality issues (low liquidity, high beta, wide spreads)

### Phase 3: Deep Dive Analysis & Reporting (1-2 min)

**Objective:** Generate actionable trade recommendations with risk analysis

**For top 5-10 candidates, create detailed report:**

```markdown
# Wheel Strategy Opportunities - {DATE}

## Screening Summary
- **Tickers Analyzed:** {total_count}
- **Valid Candidates:** {valid_count}
- **Top Recommendations:** {top_count}
- **Execution Time:** {duration}

---

## Top 10 Ranked Opportunities

| Rank | Ticker | Score | Trade Recommendation | Premium | Annual Return | Dividend | Risk |
|------|--------|-------|---------------------|---------|---------------|----------|------|
| 1 | {ticker} | {score} | Sell {exp} ${strike} Put | ${prem} | {ann_yield}% + {div}% div | {div}% | {risk} |
| ... | ... | ... | ... | ... | ... | ... | ... |

---

## Detailed Analysis

### #1: {Company Name} ({TICKER}) - Score: {score}/100

**📊 Trade Recommendation:**
- **Action:** Sell {TICKER} {expiration_date} ${strike} Put
- **Premium:** ${premium} per contract
- **Current Stock Price:** ${current_price}
- **Effective Cost if Assigned:** ${breakeven} (${strike} - ${premium})

**💰 Return Analysis:**
- **Premium Income:** ${premium_total} per contract ({DTE} days)
- **Annualized Premium Yield:** {annual_yield}%
- **Dividend Yield:** {div_yield}%
- **Total Annual Return:** {total_return}% (if not assigned)
- **Breakeven Price:** ${breakeven} ({downside_pct}% downside protection)

**📈 Options Metrics:**
- **Implied Volatility:** {iv}% (IV Rank: {iv_rank})
- **Open Interest:** {oi} contracts (Excellent liquidity)
- **Bid/Ask Spread:** ${bid}-${ask} ({spread_pct}% spread)
- **Assignment Probability:** ~{delta * 100}% (Delta: {delta})

**⚠️ Risk Assessment:**
- **If Assigned:** Own {TICKER} at {downside_pct}% discount to current price
- **Quality Metrics:**
  - Dividend Aristocrat: {years}-year streak
  - Beta: {beta} ({risk_level} volatility)
  - Market Cap: ${market_cap}B
- **Maximum Loss:** Limited to breakeven price (${breakeven})
- **Risk Level:** **{RISK_LEVEL}** (Low/Medium/High)

**🔄 Covered Call Plan (if assigned):**
- Sell {TICKER} {next_exp} ${call_strike} Call for ~${call_premium}
- Additional {call_annual_yield}% annualized return
- Continue collecting ${dividend_per_quarter}/quarter dividend
- **Wheel Cycle Total Return:** {cycle_return}%

**💡 Trade Rationale:**
{1-2 sentence explanation of why this is a good wheel candidate}

---

### #2: ... (repeat for top 5-10)

---

## Execution Checklist

Before placing trades:
- [ ] Verify account has cash to secure puts (strike × 100 × contracts)
- [ ] Check earnings dates - avoid selling puts just before earnings
- [ ] Confirm bid/ask spreads are reasonable (< 5% of premium)
- [ ] Set limit orders between bid/ask (don't use market orders)
- [ ] Review position sizing (don't allocate > 10% per ticker)
- [ ] Happy to own stock at strike price? (Quality check)

## Risk Warnings

⚠️ **Assignment Risk:** You may be assigned and forced to buy stock at strike price
⚠️ **Capital Requirement:** Each put requires strike × 100 in cash
⚠️ **Opportunity Cost:** Capital locked up if not assigned
⚠️ **Market Risk:** Stock can drop below breakeven (limited but real downside)

## Next Steps

1. **Review Recommendations:** Verify each ticker meets your criteria
2. **Check Earnings Dates:** Avoid surprises (use yfinance get_ticker_info)
3. **Place Limit Orders:** Enter orders at mid-price or better
4. **Track Positions:** Monitor for assignment, consider rolling if needed
5. **Prepare for Assignment:** If assigned, immediately plan covered call

## Resources

- Design Document: `docs/plans/2025-10-24-wheel-strategy-signal-generator-design.md`
- yfinance MCP Tools: All 8 tools available (stock + options data)
- Position Tracking: (Future enhancement - track active wheels)
```

## Error Handling

**Ticker-Level Failures (Graceful Degradation):**
- Invalid ticker → Skip, note in report
- No options available → Skip, note reason
- API timeout → Retry once, then skip
- Missing dividend → Still analyze, score lower

**System-Level Failures:**
- All agents fail → Report error, check yfinance MCP connection
- Empty watchlist → Clear error message with examples
- yfinance MCP unavailable → Cannot proceed, suggest restart

**Partial Results Acceptable:**
- 80/100 tickers succeed → Generate report with 80
- Show failed tickers in report summary
- Don't block on individual failures

## Performance Optimization

**For Large Watchlists (100+ tickers):**
```python
# Batch processing
batch_size = 20
for i in range(0, len(tickers), batch_size):
    batch = tickers[i:i+batch_size]
    # Launch batch
    # Wait for completion
    # Collect results
    # Continue to next batch
```

**Caching (5 minute TTL):**
- Stock fundamentals can be reused across multiple scans
- Options chains refresh each scan (more volatile)

**Estimated Timing:**
- 10 stocks: < 2 minutes
- 50 stocks: 3-4 minutes
- 100 stocks: 5-6 minutes

## Success Criteria

✅ **Functional Requirements:**
- Screen 100 stocks in < 6 minutes
- Rank by institutional criteria
- Generate specific trade recommendations
- Calculate returns and risk metrics
- Handle failures gracefully

✅ **Quality Requirements:**
- Top 10 are wheel-viable (quality stocks, reasonable premiums)
- Trade recommendations are executable (liquid options)
- Risk assessment is conservative
- Easy to understand for beginners, rigorous for pros

## Future Enhancements

**Phase 2 (Post-MVP):**
- Position tracking (monitor active wheels, cumulative returns)
- Alert system (notify when setups meet criteria)
- Backtesting (historical analysis)

**Phase 3 (Advanced):**
- ML-based assignment prediction
- Market regime detection (adjust criteria based on VIX)
- Tax optimization (wash sale awareness)
