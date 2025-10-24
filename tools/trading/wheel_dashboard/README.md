# Wheel Strategy Dashboard 🎯

Real-time options screening dashboard for the Wheel Strategy with institutional-grade analysis and actionable alerts.

## Features

### 🚀 Core Capabilities
- **Real-time Options Analysis** - Live data from yfinance with 5-minute caching
- **Market Hours Detection** - Automatic detection of NYSE trading hours
- **Parallel Screening** - Analyze multiple tickers simultaneously
- **Institutional Scoring** - Weighted algorithm (40% premium, 20% dividend, 20% IV, 10% liquidity, 10% quality)
- **Smart Alerts** - Notifications when opportunities meet your criteria
- **Auto-refresh** - Optional auto-refresh during market hours
- **Interactive Dashboard** - Sort, filter, and drill down into opportunities

### 📊 Analysis Features
- Optimal put strike selection (2-5% OTM)
- Annualized premium yield calculation
- Breakeven and downside protection metrics
- Liquidity analysis (open interest, bid/ask spreads)
- Risk assessment (beta, market cap, dividend quality)
- Trade execution checklist

### 🎨 UI Components
- **Market Status Widget** - Real-time market open/close indicator
- **Alert Panel** - High-score opportunities with expandable details
- **Summary Table** - Top 10 opportunities with key metrics
- **Score Gauge** - Visual score representation (0-100)
- **Detailed View** - Per-ticker deep dive analysis
- **Execution Checklist** - Pre-trade verification steps

## Quick Start

### Installation

```bash
# Navigate to dashboard directory
cd ~/dotfiles/tools/trading/wheel_dashboard

# Install dependencies
pip install -r requirements.txt
```

### Launch Dashboard

```bash
# Run Streamlit app
streamlit run wheel_app.py

# Or with custom port
streamlit run wheel_app.py --server.port 8502
```

The dashboard will open in your browser at `http://localhost:8501`

## Usage Guide

### 1. Select Watchlist
Choose from pre-configured watchlists:
- **S&P 100 Dividend Aristocrats** - 20 quality dividend stocks
- **Dividend Kings** - Ultra-reliable dividend growers
- **Low Beta Blue Chips** - Defensive, stable stocks
- **Test Portfolio** - KO, JNJ, PG for quick testing

### 2. Configure Filters

**Options Filters:**
- **Min DTE** - Minimum days to expiration (default: 30)
- **Max DTE** - Maximum days to expiration (default: 45)

**Alert Thresholds:**
- **Min Score** - Minimum wheel score for alerts (default: 35)
- **Min Premium Yield** - Minimum annualized yield % (default: 8%)

### 3. Review Opportunities

**Summary Table:**
- Sorted by score (highest first)
- Color-coded: Green (60+), Yellow (35-59), Gray (<35)
- Shows: Price, Trade, Premium, Yields, Liquidity

**Alert Panel:**
- Highlights opportunities meeting alert criteria
- Shows specific reasons (high score, high premium, excellent liquidity)
- Expandable cards with detailed metrics

### 4. Detailed Analysis

Select any ticker for:
- Visual score gauge
- Complete fundamental data
- Recommended trade details
- Breakeven analysis
- Liquidity metrics
- Risk assessment

### 5. Execute Trades

Use the **Execution Checklist** to verify:
- [ ] Sufficient cash to secure put ($strike × 100)
- [ ] Earnings date checked
- [ ] Bid/ask spread acceptable
- [ ] Limit order at mid-price planned
- [ ] Position sizing appropriate (<10% portfolio)
- [ ] Comfortable owning stock at strike

### 6. Auto-Refresh (Optional)

During market hours:
1. Enable "Auto-refresh" checkbox
2. Set refresh interval (30-300 seconds)
3. Dashboard updates automatically

## Scoring Algorithm

### Institutional Weighted Scoring (0-100)

```python
Score = (
    40% × Premium Yield Score +
    20% × Dividend Yield Score +
    20% × IV Score +
    10% × Liquidity Score +
    10% × Quality Score
)
```

**Component Normalization:**
- **Premium Yield:** 30% annual = 100% score
- **Dividend Yield:** 8% annual = 100% score
- **Implied Volatility:** 50% IV = 100% score
- **Liquidity:** 10,000 OI + tight spread = 100% score
- **Quality:** Beta < 1.2 = 100% score

### Score Interpretation

| Score | Rating | Action |
|-------|--------|--------|
| 60-100 | Excellent | Strong candidate, execute if criteria met |
| 35-59 | Good | Review carefully, good fundamentals |
| 0-34 | Fair | Pass unless specific strategy need |

## Alert System

### Default Thresholds
- **Min Score:** 35.0
- **Min Premium Yield:** 8.0%
- **Max Spread:** 30.0%
- **Min Open Interest:** 50 contracts

### Alert Triggers
Alerts fire when opportunities meet ANY of:
1. Score ≥ threshold
2. Premium yield ≥ threshold
3. Excellent liquidity (tight spread + high OI)

### Customization
Adjust thresholds in sidebar to match your strategy:
- Conservative: Min score 50, Min premium 6%
- Aggressive: Min score 30, Min premium 10%
- Liquidity-focused: Lower score threshold, raise OI requirement

## Watchlist Customization

### Add Custom Watchlist

Edit `wheel_app.py`:

```python
WATCHLISTS = {
    "Your Custom List": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META"
    ],
    # ... existing watchlists
}
```

### Pre-configured Lists

**S&P 100 Dividend Aristocrats:**
KO, JNJ, PG, WMT, T, PEP, CL, MMM, CAT, XOM, CVX, ABT, MDT, TMO, LLY, UNH, WBA, HD, LOW, TGT

**Dividend Kings:**
KO, JNJ, PG, CL, EMR, GPC, HRL, SJW

**Low Beta Blue Chips:**
KO, JNJ, PG, WMT, PEP, MCD, NEE, DUK

## Market Hours

### NYSE Hours (Eastern Time)
- **Market Open:** 9:30 AM ET
- **Market Close:** 4:00 PM ET
- **Trading Days:** Monday - Friday (excluding holidays)

### Dashboard Indicators
- 🟢 **Market OPEN** - Active trading hours
- 🔴 **Market CLOSED** - After hours or weekend
- **Next Open** - Countdown to next trading session

## Data & Caching

### Data Sources
- **Stock Fundamentals:** yfinance `Ticker.info`
- **Options Chains:** yfinance `Ticker.option_chain()`
- **Expirations:** yfinance `Ticker.options`

### Cache Strategy
- **TTL:** 5 minutes (300 seconds)
- **Auto-clear:** On manual refresh button
- **Rationale:** Balance between data freshness and API limits

### Rate Limits
yfinance has informal rate limits (~2,000 requests/hour). Dashboard respects this via:
- 5-minute caching
- Parallel fetching (not sequential hammering)
- Progress indicators for user awareness

## Performance

### Timing Benchmarks
- **3 tickers:** ~5-10 seconds
- **10 tickers:** ~15-25 seconds
- **20 tickers:** ~30-45 seconds

### Optimization Tips
1. **Use smaller watchlists** during market hours
2. **Increase cache TTL** if data staleness acceptable
3. **Disable auto-refresh** when not actively monitoring
4. **Use Test Portfolio** for quick validation

## Troubleshooting

### "No valid opportunities found"
**Cause:** DTE range too restrictive or tickers lack options
**Fix:** Widen DTE range (7-90 days) or change watchlist

### "Error fetching {ticker}"
**Cause:** Ticker delisted, invalid, or yfinance API issue
**Fix:** Remove ticker from watchlist or retry

### Dashboard slow to load
**Cause:** Large watchlist + cold cache
**Fix:** Use smaller watchlist or wait for initial cache population

### Auto-refresh not working
**Cause:** Market closed or checkbox disabled
**Fix:** Verify market hours, enable checkbox, check interval setting

## Advanced Usage

### Running on Custom Port

```bash
streamlit run wheel_app.py --server.port 8502
```

### Headless Deployment

```bash
# Run in background
nohup streamlit run wheel_app.py --server.headless true &

# Check logs
tail -f nohup.out
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY wheel_app.py .

EXPOSE 8501
CMD ["streamlit", "run", "wheel_app.py", "--server.headless", "true"]
```

Build and run:
```bash
docker build -t wheel-dashboard .
docker run -p 8501:8501 wheel-dashboard
```

## Integration with MCP

### Using with yfinance MCP Server

The dashboard can also leverage the yfinance MCP server if available:

```python
# In future enhancement:
# Replace yfinance direct calls with MCP tool calls
# mcp__yfinance__get_ticker_info(ticker)
# mcp__yfinance__get_options_chain(ticker, expiration)
```

This would enable:
- Centralized data caching
- Unified error handling
- Rate limit coordination across tools

## Roadmap

### v1.1 (Next Release)
- [ ] Earnings calendar integration
- [ ] Historical performance tracking
- [ ] Portfolio position tracking
- [ ] Export to CSV/JSON
- [ ] Telegram/Slack alerts

### v2.0 (Future)
- [ ] Backtesting engine
- [ ] Machine learning assignment prediction
- [ ] Multi-strategy support (iron condors, spreads)
- [ ] Broker integration (read-only positions)

## License

Part of the dotfiles repository. See repository LICENSE.

## Disclaimer

**This tool is for educational and informational purposes only.**

- Not financial advice
- Options trading involves significant risk
- Past performance doesn't guarantee future results
- Consult a financial advisor before trading
- Author not responsible for trading losses

## Support

For issues or questions:
1. Check troubleshooting section
2. Review design doc: `docs/plans/2025-10-24-wheel-strategy-signal-generator-design.md`
3. File issue in dotfiles repository

---

**Last Updated:** 2025-10-24
