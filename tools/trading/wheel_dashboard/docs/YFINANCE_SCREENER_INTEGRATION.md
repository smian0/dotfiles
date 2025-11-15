# yfinance Screener Integration Strategy

**Last Updated**: 2025-10-26

## Executive Summary

The yfinance library includes a built-in stock screener (`yf.Screener()`) that can **dramatically speed up Stage 1 filtering** for our market-wide discovery scanner. However, it **cannot detect unusual options activity** - that must still be done manually in Stage 2.

## Current vs Optimized Architecture

### Current (Slow)
```
Stage 1: Fetch S&P 500 list from Wikipedia → BROKEN (HTTP 403)
Stage 2: Scan all 500 stocks for options activity → Slow
```

### Optimized (Fast)
```
Stage 1: yfinance screener (fundamentals filter) → <1 second, 50-100 candidates
Stage 2: Scan candidates for options activity → 10-20x faster
```

## What yfinance Screener CAN Do

### ✅ Stock Fundamental Filtering (Fast!)

**Predefined Screeners** (ready-made):
- `most_actives` - Highest volume stocks today
- `day_gainers` - Biggest price gainers
- `day_losers` - Biggest price losers
- `undervalued_large_caps` - Value opportunities
- `undervalued_growth_stocks` - Growth + value
- `aggressive_small_caps` - High-risk/high-reward

**Custom Query Builder** (150+ parameters):
```python
from yfinance import EquityQuery

query = EquityQuery('and', [
    EquityQuery('gt', ['intradaymarketcap', 5000000000]),  # >$5B cap
    EquityQuery('gt', ['avgdailyvol3m', 1000000]),          # High volume
    EquityQuery('lt', ['trailingpe', 50]),                   # Reasonable PE
    EquityQuery('eq', ['sector', 'Technology'])             # Tech sector
])
```

**Available Parameters**:
- Market cap, volume, price changes
- Valuation metrics (PE, PB, PS, PEG)
- Profitability (ROE, ROA, margins)
- Growth metrics (EPS growth, revenue growth)
- Short interest, institutional ownership
- Sector, industry, exchange filters

## What yfinance Screener CANNOT Do

### ❌ Options Activity Detection (Must Build Manually)

**Not available in screener**:
- Unusual options volume
- IV rank/percentile
- Put/Call ratio extremes
- Large open interest changes
- Options flow patterns

**Why**: yfinance options data comes from separate API (`ticker.option_chain()`), not integrated with screener.

**Solution**: Fetch options chains in Stage 2 for screener candidates.

## Recommended Implementation

### Stage 1: Fast Fundamental Filter (yfinance screener)

```python
import yfinance as yf

# Use predefined screener for liquid stocks
screener = yf.Screener()
screener.set_predefined_body('most_actives')
response = screener.response

# Extract symbols (50-100 stocks typically)
candidates = [quote['symbol'] for quote in response['quotes']]

# OR use custom query for specific criteria
from yfinance import EquityQuery

query = EquityQuery('and', [
    # Large/mid cap with high liquidity
    EquityQuery('gt', ['intradaymarketcap', 2000000000]),
    EquityQuery('gt', ['avgdailyvol3m', 1000000]),

    # Profitable companies (for wheel strategy)
    EquityQuery('gt', ['netprofitmargin.lasttwelvemonths', 5]),

    # Reasonable valuation
    EquityQuery('lt', ['trailingpe', 60]),

    # US exchanges
    EquityQuery('is-in', ['exchange', 'NYQ', 'NMS'])
])

screener = yf.Screener()
screener.set_default_body(query)
candidates = [quote['symbol'] for quote in screener.response['quotes']]
```

### Stage 2: Options Activity Analysis (Manual)

```python
from concurrent.futures import ThreadPoolExecutor

def analyze_options_activity(symbol):
    """Your existing logic for unusual activity detection"""
    ticker = yf.Ticker(symbol)

    # Fetch options chain
    chain = ticker.option_chain(ticker.options[0])

    # Calculate Volume/OI ratio, Put/Call ratio, etc.
    # (Your existing code)

    return discovery_score, signals

# Scan candidates in parallel
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(analyze_options_activity, candidates)

# Filter for high scores
opportunities = [r for r in results if r.discovery_score >= 35]
```

## Integration Points

### Option A: Replace Wikipedia Fetching (Quick Win)

**File**: `analyzers/market_discovery.py`

```python
def _get_sp500_tickers(self) -> List[str]:
    """Fetch S&P 500 tickers using yfinance screener instead of Wikipedia"""
    try:
        import yfinance as yf

        # Use yfinance custom query for S&P 500-like stocks
        from yfinance import EquityQuery

        query = EquityQuery('and', [
            EquityQuery('gt', ['intradaymarketcap', 10000000000]),  # >$10B (large cap)
            EquityQuery('gt', ['avgdailyvol3m', 500000]),            # Liquid
            EquityQuery('is-in', ['exchange', 'NYQ', 'NMS'])        # NYSE/NASDAQ
        ])

        screener = yf.Screener()
        screener.set_default_body(query)
        quotes = screener.response['quotes']

        return [q['symbol'] for q in quotes[:500]]  # Top 500 by market cap

    except Exception as e:
        logger.error(f"yfinance screener failed: {e}")
        # Fallback to hardcoded list
        return FALLBACK_TICKERS
```

### Option B: Add New Screener Presets (Better UX)

**File**: `config/scan_presets.py`

```python
YFINANCE_SCREENER_PRESETS = {
    'yf_most_actives': {
        'name': '🔥 Most Active (yfinance)',
        'description': 'Highest volume stocks today - fast screener',
        'screener_type': 'predefined',
        'screener_body': 'most_actives',
        'expected_premium': '2-4% monthly',
        'risk_profile': 'MEDIUM'
    },

    'yf_day_gainers': {
        'name': '📈 Today\'s Gainers (yfinance)',
        'description': 'Stocks with momentum - scan for continuation',
        'screener_type': 'predefined',
        'screener_body': 'day_gainers',
        'expected_premium': '3-5% monthly',
        'risk_profile': 'HIGH'
    },

    'yf_undervalued_large_caps': {
        'name': '💎 Undervalued Large Caps (yfinance)',
        'description': 'Value opportunities in established companies',
        'screener_type': 'predefined',
        'screener_body': 'undervalued_large_caps',
        'expected_premium': '1-2% monthly',
        'risk_profile': 'LOW'
    }
}
```

### Option C: Hybrid Mode (Best Performance)

Combine predefined ticker lists with yfinance screener:

```python
def get_scan_universe(preset_name):
    """Get ticker list from preset or yfinance screener"""

    # Predefined presets (instant, reliable)
    if preset_name in SCAN_PRESETS:
        return SCAN_PRESETS[preset_name]['tickers']

    # yfinance screener presets (fast, dynamic)
    if preset_name in YFINANCE_SCREENER_PRESETS:
        config = YFINANCE_SCREENER_PRESETS[preset_name]

        screener = yf.Screener()
        if config['screener_type'] == 'predefined':
            screener.set_predefined_body(config['screener_body'])
        else:
            screener.set_default_body(config['custom_query'])

        return [q['symbol'] for q in screener.response['quotes']]

    # Fallback
    raise ValueError(f"Unknown preset: {preset_name}")
```

## Performance Impact

### Before (Wikipedia + Full Scan)
```
Wikipedia fetch: 2-5 seconds (often fails with HTTP 403)
S&P 500 scan: 500 stocks × 0.5s = 250 seconds (4+ minutes)
Total: ~4-5 minutes (when Wikipedia works)
```

### After (yfinance screener + Targeted Scan)
```
yfinance screener: <1 second (50-100 candidates)
Targeted scan: 100 stocks × 0.5s = 50 seconds
Total: ~50 seconds (5-6x faster)
```

## Data Quality Notes

### ✅ Good Enough for Screening
- Stock prices: 15-minute delayed (acceptable for wheel strategy)
- Volume data: Reliable
- Fundamental metrics: Daily updates (sufficient)

### ⚠️ Known Limitations
- **Options IV**: Unreliable (use IB data when available)
- **No real-time**: 15-minute delay
- **No SLA**: Unofficial API, can break
- **Rate limiting**: Undocumented throttling

### 🎯 Best Practice
1. Use yfinance screener for Stage 1 filtering (fast, good enough)
2. Use your manual options analysis for Stage 2 (unusual activity)
3. Validate high-conviction signals with IB data before execution

## Implementation Priority

### Phase 1: Quick Wins (1-2 hours)
1. ✅ Lower default Min Discovery Score from 60 → 35 (fixes "0 results")
2. 🔄 Replace Wikipedia fetch with yfinance screener (fixes HTTP 403)
3. ✅ Add "most_actives" to scan presets dropdown

### Phase 2: Enhanced UX (2-4 hours)
1. Add 3-5 yfinance screener presets to dropdown
2. Show "Stage 1: Filtered to X candidates" progress indicator
3. Cache screener results for 5-15 minutes

### Phase 3: Advanced (Future)
1. Allow users to create custom yfinance queries in UI
2. Combine multiple screeners (e.g., "most_actives" + "high institutional ownership")
3. Historical tracking of which screener presets find best opportunities

## Code Examples

See research report for full implementation examples:
- `YFINANCE_SCREENER_RESEARCH_2025-10-26.md`

## Next Steps

1. **Immediate**: Change default Min Score to 35 (1 line change)
2. **Quick win**: Add yfinance screener to replace Wikipedia (30 minutes)
3. **Test**: Verify scan works with multiple scenarios
4. **Document**: Update user-facing help text with new screener options
