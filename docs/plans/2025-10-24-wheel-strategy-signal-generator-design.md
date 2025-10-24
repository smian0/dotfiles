# Wheel Strategy Signal Generator - Institutional Parallel Design

**Date:** 2025-10-24
**Status:** Approved
**Strategy:** Options Wheel (Cash-Secured Puts + Covered Calls)

## Overview

Institutional-grade signal generator for the **Wheel Strategy** - the most reliable and consistent options strategy used by professional traders and market makers. Uses parallel multi-agent processing to screen 100+ stocks in 4-6 minutes, generating ranked trade recommendations with specific strikes and premiums.

## Strategy Background

### The Wheel Strategy

The Wheel is a systematic income-generation strategy combining two phases:

**Phase 1: Cash-Secured Puts**
- Sell out-of-the-money put options on quality stocks
- Collect premium income while waiting to buy at a discount
- If assigned: acquire stock at effective price = strike - premium received

**Phase 2: Covered Calls**
- Once owning stock, sell out-of-the-money call options
- Continue collecting premium income on holdings
- If assigned: sell stock at strike price + all premiums collected

**Why Institutions Love It:**
- Consistent premium income (weekly/monthly)
- Profit in sideways markets (80% of market conditions)
- Forces disciplined entry/exit prices
- Triple income potential with dividend stocks (put premium + call premium + dividends)
- Repeatable, systematic, proven over decades

## Design Decisions

### Stock Selection Criteria: Quality + Dividends

**Rationale:** Conservative institutional approach - only stocks you'd be happy owning long-term.

**Criteria:**
- **Fundamental Quality:** Blue-chip stocks with strong fundamentals, stable businesses
- **Dividend Payers:** Triple income (put premium + call premium + dividends)
- **Liquidity:** Liquid options markets (tight bid/ask spreads, high open interest)
- **Volatility:** Moderate IV (enough premium to make it worthwhile, not meme stocks)

**Example Candidates:** KO, JNJ, PG, WMT, T, PEP - dividend aristocrats

**Rejected Alternatives:**
- High IV / High Premium: Too risky, likely to be assigned at unfavorable prices
- Pure Technical: No fundamental quality filter, could own garbage
- No Dividend Filter: Leaves money on the table for long holds

### Execution Mode: Hybrid Screen + Deep Dive

**Rationale:** Best balance of speed and depth. Quick filter eliminates obvious no-gos, deep analysis only on survivors.

**Two-Phase Approach:**
- Phase 1: Fast filter (IV, dividend yield, liquidity) - 100 stocks in 30s
- Phase 2: Deep analysis (wheel metrics, trade recommendations) - top 10 in 2 min
- Total: ~3-4 minutes for comprehensive screening

### Architecture: Parallel Multi-Agent Processing

**Rationale:** Institutional scalability. Same execution time for 10 stocks or 100 stocks.

**Why Parallel:**
- Sequential: 100 stocks × 2-3 sec/stock = 3-5 minutes just for data fetching
- Parallel: 100 agents × 2-3 sec = 2-3 minutes total (bound by slowest agent)
- Real institutional systems (Goldman, Citadel) use parallel processing for screening

**Rejected Alternatives:**
- Sequential 3-Phase: Too slow for large watchlists (30+ minutes for 100 stocks)
- Simple On-Demand: No screening capability, requires manual ticker input

## Architecture

### 3-Phase Parallel Processing

```
Phase 1: Parallel Ticker Screening (2-3 min)
├─ Input: Watchlist (S&P 100 dividend aristocrats, custom, sector-based)
├─ Launch parallel agents (one per ticker, max 20 concurrent)
├─ Each agent analyzes independently:
│   ├─ Stock fundamentals (price, dividend yield, beta, market cap)
│   ├─ Options chain (30-45 DTE preferred)
│   ├─ Put options (1-2 strikes below current price)
│   ├─ Call options (strikes above breakeven)
│   └─ Returns: ticker, metrics, trade recommendation
└─ Output: Raw results from all agents

Phase 2: Aggregation & Ranking (30 sec)
├─ Collect results from all agents
├─ Calculate wheel attractiveness score:
│   ├─ Premium yield (annualized): 40% weight
│   ├─ Dividend yield: 20% weight
│   ├─ IV Rank: 20% weight
│   ├─ Liquidity: 10% weight
│   └─ Fundamental quality: 10% weight
├─ Normalize scores 0-100
├─ Rank tickers by score
└─ Output: Top 5-10 candidates

Phase 3: Deep Dive Analysis (1-2 min)
├─ Generate detailed analysis for top candidates
├─ Calculate:
│   ├─ Expected annual return
│   ├─ Cost basis reduction
│   ├─ Breakeven points
│   ├─ Greeks (delta for assignment probability)
│   └─ Risk/reward ratios
├─ Produce specific trade recommendations
└─ Output: Ranked report with actionable trades
```

**Total Execution Time:** 4-6 minutes for 100 stocks

## Components

### Component 1: Watchlist Manager

**Responsibilities:**
- Maintain curated lists of wheel-friendly stocks
- Validate tickers have liquid options markets
- Support custom watchlists and imports

**Pre-configured Lists:**
- S&P 100 dividend aristocrats (25-year+ dividend growth)
- High-yield blue chips (4%+ dividend yield)
- Sector rotations (defensive, cyclical)
- Custom user lists

**Validation:**
- Ticker exists and has options
- Minimum option volume/open interest thresholds
- Options available at 30-45 DTE range

### Component 2: Parallel Ticker Analyzer

**Responsibilities:**
- Spawn independent agents for each ticker
- Coordinate parallel execution with concurrency limits
- Aggregate results and handle failures

**Agent Workflow (per ticker):**

```
1. Fetch Stock Data (yfinance get_ticker_info)
   - Current price, dividend yield, beta, market cap
   - Validate: dividend > 0%, market cap > $10B

2. Get Options Expirations (yfinance get_options_dates)
   - Target: 30-45 days to expiration
   - Select nearest expiration in range

3. Analyze Put Options (yfinance get_options_chain)
   - Strikes: 1-2 below current price (~2-5% OTM)
   - Metrics: premium, bid/ask spread, open interest, IV
   - Calculate: annualized premium yield, probability of assignment

4. Check Call Options (for covered call phase)
   - Strikes: above put breakeven price
   - Metrics: premium yield if assigned

5. Return Structured Data:
   {
     "ticker": "KO",
     "current_price": 62.50,
     "dividend_yield": 3.2,
     "recommended_put": {
       "strike": 60,
       "premium": 1.20,
       "expiration": "2025-12-20",
       "annualized_yield": 14.2,
       "assignment_prob": 0.15
     },
     "metrics": {
       "score": 85,
       "breakeven": 58.80,
       "max_loss_if_assigned": "Limited to breakeven"
     }
   }
```

**Parallelization:**
- Max 20 concurrent agents (API rate limit protection)
- Timeout: 30 seconds per agent
- Failed agents don't block others
- Batch processing for 100+ stock lists

### Component 3: Scoring Engine

**Weighted Scoring Algorithm:**

```python
def calculate_wheel_score(ticker_data):
    # Premium Yield (40%) - Most important
    premium_score = normalize(ticker_data.annualized_premium_yield, 0, 30)

    # Dividend Yield (20%) - Triple income factor
    dividend_score = normalize(ticker_data.dividend_yield, 0, 8)

    # IV Rank (20%) - High IV = more premium
    iv_score = normalize(ticker_data.iv_rank, 0, 100)

    # Liquidity (10%) - Tight spreads, high OI
    liquidity_score = (
        0.5 * normalize(ticker_data.open_interest, 0, 10000) +
        0.5 * (1 - ticker_data.bid_ask_spread_pct / 5)  # Penalize wide spreads
    )

    # Fundamental Quality (10%) - Avoid value traps
    quality_score = (
        0.4 * (1 if ticker_data.dividend_growth_years >= 25 else 0) +
        0.3 * normalize(ticker_data.market_cap, 10B, 500B) +
        0.3 * (1 if ticker_data.beta < 1.2 else 0)
    )

    # Weighted sum
    total_score = (
        0.40 * premium_score +
        0.20 * dividend_score +
        0.20 * iv_score +
        0.10 * liquidity_score +
        0.10 * quality_score
    )

    return total_score * 100  # Scale to 0-100
```

**Ranking:**
- Sort by score descending
- Filter top 5-10 for detailed analysis
- Flag any quality issues (low liquidity, high beta)

### Component 4: Report Generator

**Output Format: Ranked Markdown Table**

```markdown
# Wheel Strategy Opportunities - 2025-10-24

## Top 10 Candidates (from 100 stocks screened)

| Rank | Ticker | Score | Trade | Premium | Annual Return | Dividend | Risk Level |
|------|--------|-------|-------|---------|---------------|----------|------------|
| 1 | KO | 92 | Sell Dec 20 $60 Put | $1.20 | 14.2% + 3.2% div | 3.2% | Low |
| 2 | JNJ | 89 | Sell Dec 20 $155 Put | $3.50 | 13.8% + 2.9% div | 2.9% | Low |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Detailed Analysis

### #1: Coca-Cola (KO) - Score: 92

**Trade Recommendation:**
- Sell KO Dec 20 2025 $60 Put for $1.20
- Current Price: $62.50
- Effective Cost if Assigned: $58.80 ($60 - $1.20)

**Return Analysis:**
- Premium Income: $120 per contract (44 days)
- Annualized Premium Yield: 14.2%
- Dividend Yield: 3.2%
- **Total Annual Return: 17.4%** (if not assigned)
- **Breakeven Price: $58.80** (6% downside protection)

**Risk Assessment:**
- Assignment Probability: 15% (delta = 0.15)
- If assigned: Own KO at 6% discount to current price
- Quality: Dividend aristocrat (62-year streak)
- Beta: 0.65 (defensive)
- Risk Level: **Low**

**Covered Call Plan (if assigned):**
- Sell KO Jan 17 2026 $65 Call for ~$2.00
- Additional 20% annualized return
- Continue collecting $0.50/quarter dividend
```

## Implementation Plan

### Tools & Technologies

**Primary:**
- workflow-orchestrator skill (for generating the multi-phase workflow)
- yfinance MCP server (all 8 tools: stock data + options)
- Task tool (for spawning parallel agents)

**Output Format:**
- Pattern B: Slash command `/trading:wheel-scan <watchlist>`
- Reusable, parameterized, easy to invoke
- Can also generate Pattern A (skill) if needed for frequent use

### Error Handling

**Ticker-Level Failures (Graceful Degradation):**
- No options available → Skip ticker, log reason
- Invalid ticker → Skip with warning in report
- API rate limits → Retry with exponential backoff (1s, 2s, 4s), then skip
- Missing fundamentals → Use partial data, flag in report
- No dividend → Still analyze, score lower on dividend component

**System-Level Failures (Fail Fast):**
- Workflow orchestrator errors → Stop process, clear error message
- All agents fail → Report issue, suggest checking yfinance MCP connection
- Empty watchlist → User error with examples
- yfinance MCP unavailable → Cannot proceed, clear diagnostic

**Performance Optimization:**
- Limit concurrent agents to 20 (avoid API rate limits)
- Batch larger watchlists: Run 20, wait, run next 20
- Cache stock fundamentals for 5 minutes (multiple scans)
- Reuse options chain data within same scan

### Testing Strategy

**Unit Tests:**
- Single ticker analysis agent (KO)
- Scoring algorithm with known inputs
- Watchlist validation

**Integration Tests:**
- 3-ticker parallel run (KO, JNJ, PG)
- Agent failure handling (invalid ticker)
- Scoring and ranking with mixed quality stocks

**End-to-End Test:**
- Full workflow with 10-stock subset of S&P 100 dividend aristocrats
- Validate all phases complete
- Verify report format and content
- Timing: should complete in < 2 minutes for 10 stocks

**Validation Criteria:**
- Known good candidates (KO, JNJ) rank in top 5
- Known bad candidates (meme stocks, no dividends) filtered out
- Scores correlate with manual analysis
- Trade recommendations are actionable (specific strikes, expirations)

## Success Criteria

**Functional:**
- ✅ Screen 100 stocks in < 6 minutes
- ✅ Rank candidates by institutional criteria
- ✅ Generate specific trade recommendations (strike, expiration, premium)
- ✅ Calculate expected returns and risk metrics
- ✅ Handle failures gracefully (partial results acceptable)

**Quality:**
- ✅ Top 10 recommendations are wheel-viable (quality stocks, reasonable premiums)
- ✅ Scoring algorithm correlates with manual analysis
- ✅ Trade recommendations are executable (liquid options, reasonable spreads)
- ✅ Risk assessment is conservative and realistic

**Performance:**
- ✅ 4-6 minutes for 100 stocks (parallel execution)
- ✅ < 2 minutes for 10 stocks
- ✅ < 30 seconds per agent (with timeout)

**Usability:**
- ✅ Simple invocation: `/trading:wheel-scan sp100-dividends`
- ✅ Clear, actionable report format
- ✅ Easy to understand for options beginners
- ✅ Institutional-grade rigor for experienced traders

## Future Enhancements

**Phase 2 (Post-MVP):**
- Position tracking: Monitor active wheel positions, calculate cumulative returns
- Alert system: Notify when setups meet criteria (IV spike, earnings cleared)
- Backtesting: Historical analysis of wheel strategy on top candidates
- Portfolio integration: Track cost basis adjustments across multiple wheel cycles

**Phase 3 (Advanced):**
- Machine learning: Predict assignment probability beyond simple delta
- Market regime detection: Adjust criteria based on VIX, market conditions
- Execution integration: Auto-generate orders for review (not auto-execute)
- Tax optimization: Wash sale awareness, long-term vs short-term gains

## References

- yfinance MCP implementation: `mcp_servers/yfinance/yfinance_mcp.py`
- workflow-orchestrator skill: `.claude/skills/workflow-orchestrator/`
- Options APIs design: `docs/plans/2025-10-24-yfinance-options-apis-design.md`
- Wheel strategy primer: https://www.investopedia.com/wheel-strategy (external)
