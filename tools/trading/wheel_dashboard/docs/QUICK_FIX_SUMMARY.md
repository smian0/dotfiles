# Market-Wide Discovery Scanner - Quick Fix Summary

**Date**: 2025-10-26
**Issue**: Scanner returning "0 hidden gems" - confusing UX

## Root Causes Identified

### 1. Wikipedia Blocking S&P 500 Fetching
- **Error**: `HTTP 403: Forbidden` when fetching ticker list
- **Impact**: S&P 500 option scans 0 stocks → always returns 0 results
- **Solution**: Use scan presets (hardcoded ticker lists) or yfinance screener API

### 2. Min Discovery Score Too High
- **Default**: 60 (only finds exceptional opportunities)
- **Reality**: Most good opportunities score 35-60
- **Impact**: Even with working presets, users see "0 results"
- **Solution**: Lower default to 35

## What Actually Works Right Now

Your background scans with **Min Score 35** found **40+ opportunities**:

### Top 5 Perfect Scores (100/100)
1. **WMT** - 59,999 OI, P/C 0.37, Positive news
2. **MRK** - 31,107 OI, Healthcare leader
3. **KO** - 31,868 OI, Strong catalyst (+25pts)
4. **CSCO** - 29,611 OI, **Huge news boost (+90pts)**
5. **ADBE** - 21,732 OI, Tech momentum

### Strong Candidates (60-100)
NVDA (74.2), JNJ (77.6), VZ (81.5), TMO (94.0), IBM (96.9), NEE (99.6), TXN (100), ORCL (100), and 30+ more

## yfinance Screener Discovery

### Key Finding
yfinance HAS a built-in stock screener API that can replace Wikipedia fetching:

```python
import yfinance as yf

# Predefined screeners (instant)
screener = yf.Screener()
screener.set_predefined_body('most_actives')  # or 'day_gainers', 'undervalued_large_caps'
candidates = [q['symbol'] for q in screener.response['quotes']]

# Custom queries (150+ parameters)
from yfinance import EquityQuery
query = EquityQuery('and', [
    EquityQuery('gt', ['intradaymarketcap', 5000000000]),  # >$5B cap
    EquityQuery('gt', ['avgdailyvol3m', 1000000])           # High volume
])
```

### What It Can Do
✅ Fast fundamental filtering (market cap, volume, PE ratio, sector)
✅ Predefined screeners ready to use
✅ Custom queries with 150+ parameters

### What It CANNOT Do
❌ Unusual options activity (must build manually)
❌ IV rank/percentile detection
❌ Options flow analysis

**Conclusion**: Use yfinance for Stage 1 (fast fundamental filter), keep your manual options analysis for Stage 2 (unusual activity)

## Immediate Actions

### Phase 1: Quick Fixes (Complete in 10 minutes)

#### Fix #1: Lower Default Min Score
**File**: Look for slider default in Streamlit Discover page
**Change**: `value=60` → `value=35`
**Impact**: Users immediately see results instead of confusion

#### Fix #2: Add yfinance Screener Option (Future)
**File**: `config/scan_presets.py`
**Add**: New preset using `yf.Screener().set_predefined_body('most_actives')`
**Impact**: Fast, reliable alternative to Wikipedia S&P 500

### Recommended Architecture

```
┌─────────────────────────────────────────────┐
│    2-Stage Discovery Scanner                │
├─────────────────────────────────────────────┤
│                                              │
│  Stage 1: Fast Fundamental Filter           │
│  ├─ Option A: Scan Presets (instant)       │
│  ├─ Option B: yfinance screener (<1s)      │
│  └─ Returns: 50-100 candidates              │
│                                              │
│  Stage 2: Options Activity Analysis         │
│  ├─ Your existing unusual activity code     │
│  ├─ Calculate Vol/OI, Put/Call ratios       │
│  └─ Returns: 10-20 opportunities            │
│                                              │
└─────────────────────────────────────────────┘
```

## Performance Gains

### Before (Wikipedia + Full Scan)
- Wikipedia: 2-5s (often fails)
- S&P 500 scan: 500 stocks × 0.5s = 250s
- **Total: 4-5 minutes (when it works)**

### After (yfinance + Targeted Scan)
- yfinance screener: <1s
- Targeted scan: 100 stocks × 0.5s = 50s
- **Total: ~50 seconds (5-6x faster)**

## User Instructions (What to Tell Users)

### Current Workaround
1. **Use Scan Presets** (not S&P 500 option)
   - Conservative Wheel, Mega Cap Tech, High Premium Tech, etc.

2. **Lower Min Discovery Score to 35-40**
   - Default 60 is too strict
   - 35-40 finds good opportunities

3. **Expected Results**
   - Score 35-50: Many opportunities (some noise)
   - Score 50-70: Very good opportunities
   - Score 70-100: Exceptional opportunities (rare)

### What Each Parameter Does

| Parameter | Purpose | Recommendation |
|-----------|---------|----------------|
| **Scan Strategy** | Which stocks to scan | Use presets (not S&P 500!) |
| **Min Discovery Score** | Quality threshold | **35-40** for balanced results |
| **Max Results** | Display limit | 20 (default is fine) |
| **Prefer Small/Mid Caps** | Higher risk/reward | Check for aggressive strategies |
| **Prefer Low Analyst Coverage** | Find hidden gems | Check for undiscovered stocks |

## Next Steps

1. ✅ Document yfinance screener integration strategy (DONE)
2. 🔄 Change default Min Score to 35 (IN PROGRESS)
3. ⏳ Test with multiple scan scenarios
4. ⏳ Add yfinance screener presets (Phase 2)

## Files Created/Updated

- `docs/YFINANCE_SCREENER_INTEGRATION.md` - Full integration guide
- `docs/QUICK_FIX_SUMMARY.md` - This file
- Next: Update Streamlit Discover page with new default

## Key Takeaway

Your scanner logic is **correct** - you have to build unusual options activity detection manually because yfinance doesn't provide it. The fixes are simple:

1. **Lower default Min Score to 35** (stops "0 results" confusion)
2. **Use scan presets** (reliable, instant ticker lists)
3. **(Future) Add yfinance screener** (fast Stage 1 filter, replaces Wikipedia)

The 40+ opportunities from your background scans prove the scanner works when configured correctly!
