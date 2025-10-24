# Interactive Brokers vs yfinance: Options Screening Data Comparison

**Date:** 2025-10-24
**Purpose:** Evaluate strategic data advantages for options watchlist screening

## Data Point Comparison

### **1. Greeks (Critical for Screening)**

| Metric | yfinance | Interactive Brokers | Strategic Value |
|--------|----------|---------------------|-----------------|
| **Delta** | Black-Scholes estimate | Exchange-calculated real-time | ⭐⭐⭐⭐⭐ Assignment probability |
| **Gamma** | Estimate | Real-time | ⭐⭐⭐⭐ Position risk management |
| **Theta** | Estimate | Real-time | ⭐⭐⭐⭐⭐ Time decay tracking |
| **Vega** | Estimate | Real-time | ⭐⭐⭐⭐ IV sensitivity |
| **Rho** | Estimate | Real-time | ⭐⭐ Interest rate sensitivity |

**Screening Impact:**
- **yfinance:** Estimated delta may be off by 5-10% → assignment probability inaccurate
- **IB:** Real-time delta → precise probability for wheel strategy risk assessment

### **2. Implied Volatility Analysis**

| Data Point | yfinance | IB | Strategic Value |
|------------|----------|-----|-----------------|
| **Current IV** | Yes (delayed) | Real-time | ⭐⭐⭐⭐ |
| **IV Rank** | ❌ No | ✅ Via calculation | ⭐⭐⭐⭐⭐ |
| **IV Percentile** | ❌ No | ✅ Via calculation | ⭐⭐⭐⭐⭐ |
| **Historical IV** | Limited | Complete history | ⭐⭐⭐⭐⭐ |
| **Put/Call IV Skew** | ❌ No | ✅ Yes | ⭐⭐⭐⭐ |
| **Term structure** | ❌ No | ✅ Yes | ⭐⭐⭐ |

**Why IV Rank/Percentile is Critical:**
```
Example: Stock XYZ
- Current IV: 25%
- yfinance: "IV is 25%" (meaningless without context)
- IB with history: "IV Rank: 85th percentile" (HIGH premium environment!)

Screening Decision:
- IV Rank 80-100: SELL premium (great for wheel strategy)
- IV Rank 0-20: AVOID (premiums too low)
- IV Rank 20-80: Conditional (check other factors)
```

### **3. Liquidity Metrics**

| Metric | yfinance | IB | Strategic Value |
|--------|----------|-----|-----------------|
| **Open Interest** | Daily snapshot | Real-time updates | ⭐⭐⭐⭐ |
| **OI Change** | ❌ No | ✅ Yes | ⭐⭐⭐⭐⭐ |
| **Volume** | Daily total | Intraday tracking | ⭐⭐⭐⭐ |
| **Vol/OI Ratio** | Manual calc | Automatic | ⭐⭐⭐⭐ |
| **Bid/Ask Spread** | Snapshot (stale) | Live streaming | ⭐⭐⭐⭐⭐ |
| **Bid/Ask Size** | ❌ No | ✅ Yes | ⭐⭐⭐⭐ |
| **Market depth** | ❌ No | ✅ Yes (Level 2) | ⭐⭐⭐ |

**Screening Impact:**
- **OI Change:** Positive OI change = growing interest (good for wheel)
- **Bid/Ask Size:** Small size = low liquidity (avoid)
- **Vol/OI Ratio > 1:** Unusual activity (potential opportunity or trap)

### **4. Options Chain Coverage**

| Feature | yfinance | IB | Strategic Value |
|---------|----------|-----|-----------------|
| **Strike range** | Limited (ATM ±5-10 strikes) | Full chain (all strikes) | ⭐⭐⭐⭐ |
| **Expirations** | Standard only | Includes weeklies | ⭐⭐⭐⭐⭐ |
| **LEAPS** | Partial | Complete | ⭐⭐⭐ |
| **Mini options** | ❌ No | ✅ Yes | ⭐⭐ |

**Why Weekly Expirations Matter:**
- Wheel strategy can use 7-14 DTE weeklies for higher premium frequency
- yfinance often missing weekly expirations
- IB has complete weekly chain

### **5. Corporate Actions & Events**

| Data | yfinance | IB | Strategic Value |
|------|----------|-----|-----------------|
| **Earnings dates** | Yes (but delayed) | Real-time, accurate | ⭐⭐⭐⭐⭐ |
| **Ex-dividend dates** | Yes | Real-time | ⭐⭐⭐⭐⭐ |
| **Dividend amount** | Yes | Yes | ⭐⭐⭐⭐ |
| **Stock splits** | Yes | Real-time alerts | ⭐⭐⭐ |
| **Special dividends** | Sometimes | Always | ⭐⭐⭐ |

**Screening Impact:**
```
Critical for Wheel Strategy:
❌ Selling puts before earnings = High risk (IV crush after)
✅ Selling puts AFTER earnings = Lower IV, safer entry
✅ Knowing ex-div date = Avoid early assignment risk

Example:
- Stock XYZ earnings: 2025-11-01
- yfinance: Might show stale date (2024 Q4)
- IB: Shows correct upcoming date with countdown
- Decision: Skip selling puts until Nov 2nd
```

### **6. Advanced Screening Metrics**

| Metric | yfinance | IB | How to Calculate |
|--------|----------|-----|------------------|
| **Put/Call Ratio** | ❌ No | ✅ Via volume data | ⭐⭐⭐⭐ |
| **Implied Move** | ❌ No | ✅ Via straddle price | ⭐⭐⭐⭐ |
| **Probability ITM** | ❌ No | ✅ Via delta | ⭐⭐⭐⭐⭐ |
| **Max Pain** | ❌ No | ✅ Calculate from OI | ⭐⭐⭐ |
| **Skew Index** | ❌ No | ✅ Calculate | ⭐⭐⭐⭐ |

### **7. Historical Data Access**

| Data | yfinance | IB | Strategic Value |
|------|----------|-----|-----------------|
| **Historical options prices** | Very limited | Complete (years) | ⭐⭐⭐⭐⭐ |
| **IV history** | ❌ No | ✅ Yes | ⭐⭐⭐⭐⭐ |
| **OI history** | ❌ No | ✅ Yes | ⭐⭐⭐⭐ |
| **Volume history** | ❌ No | ✅ Yes | ⭐⭐⭐⭐ |

**Why Historical Data Matters:**
- **IV Rank calculation:** Need 52-week IV range
- **Backtesting:** Test wheel strategy on historical data
- **Pattern recognition:** Identify seasonal IV patterns

## Strategic Screening Enhancements with IB

### **Enhancement 1: IV Rank-Based Screening**

```python
# With IB historical data
def calculate_iv_rank(current_iv, iv_history_52w):
    """
    IV Rank = (Current IV - Min IV) / (Max IV - Min IV) * 100

    80-100: High premium environment (SELL)
    20-80: Normal
    0-20: Low premium (AVOID selling)
    """
    min_iv = min(iv_history_52w)
    max_iv = max(iv_history_52w)
    return (current_iv - min_iv) / (max_iv - min_iv) * 100

# Screening filter
if iv_rank >= 80:
    status = "EXCELLENT - High premium environment"
elif iv_rank >= 50:
    status = "GOOD - Above average premiums"
else:
    status = "SKIP - Premiums too low"
```

### **Enhancement 2: Earnings-Aware Screening**

```python
# With IB earnings calendar
def is_safe_to_sell_puts(ticker, dte):
    """Avoid selling puts within 7 days before earnings"""
    days_to_earnings = get_days_to_earnings(ticker)  # IB provides this

    if days_to_earnings < 7:
        return False, "Earnings too close"

    if dte > days_to_earnings:
        return False, "Expiration after earnings"

    return True, "Safe window"

# Filter watchlist
for ticker in watchlist:
    safe, reason = is_safe_to_sell_puts(ticker, 30)
    if not safe:
        skip_ticker(ticker, reason)
```

### **Enhancement 3: Liquidity Quality Score**

```python
# With IB real-time data
def calculate_liquidity_score(option_data):
    """
    Better liquidity assessment than simple OI threshold
    """
    oi = option_data['open_interest']
    volume = option_data['volume']
    spread_pct = option_data['bid_ask_spread_pct']
    bid_size = option_data['bid_size']
    ask_size = option_data['ask_size']

    # Multi-factor liquidity score
    oi_score = min(oi / 1000, 1.0) * 40  # Max 40 points
    vol_score = min(volume / 100, 1.0) * 20  # Max 20 points
    spread_score = max(0, (1 - spread_pct / 30)) * 30  # Max 30 points
    size_score = min((bid_size + ask_size) / 200, 1.0) * 10  # Max 10 points

    total_score = oi_score + vol_score + spread_score + size_score

    if total_score >= 80:
        return "Excellent", total_score
    elif total_score >= 60:
        return "Good", total_score
    elif total_score >= 40:
        return "Fair", total_score
    else:
        return "Poor", total_score
```

### **Enhancement 4: OI Change Detection**

```python
# With IB daily OI tracking
def detect_oi_anomalies(ticker, strike, expiration):
    """
    Positive OI change = New positions opening (bullish sign for puts)
    Negative OI change = Positions closing (bearish sign)
    """
    oi_today = get_current_oi(ticker, strike, expiration)
    oi_yesterday = get_historical_oi(ticker, strike, expiration, days_ago=1)

    oi_change = oi_today - oi_yesterday
    oi_change_pct = (oi_change / oi_yesterday * 100) if oi_yesterday > 0 else 0

    if oi_change_pct > 50:
        return "🚨 ALERT: +50% OI increase - Strong buying interest"
    elif oi_change_pct > 20:
        return "✅ Good: Growing open interest"
    elif oi_change_pct < -20:
        return "⚠️ Warning: Declining open interest"
    else:
        return "Stable"
```

### **Enhancement 5: Put/Call Skew Analysis**

```python
# With IB full options chain
def analyze_iv_skew(ticker, expiration, current_price):
    """
    Put skew > Call skew = Market fears downside (good for wheel puts)
    """
    # Get ATM puts and calls
    atm_put_iv = get_option_iv(ticker, current_price, expiration, 'PUT')
    atm_call_iv = get_option_iv(ticker, current_price, expiration, 'CALL')

    # Get OTM (10% below for puts, 10% above for calls)
    otm_put_iv = get_option_iv(ticker, current_price * 0.90, expiration, 'PUT')
    otm_call_iv = get_option_iv(ticker, current_price * 1.10, expiration, 'CALL')

    put_skew = otm_put_iv - atm_put_iv
    call_skew = otm_call_iv - atm_call_iv

    if put_skew > call_skew:
        return "📈 Put skew elevated - Better premiums on puts (GOOD for wheel)"
    else:
        return "📉 Call skew elevated - Puts less attractive"
```

## Summary: IB Strategic Data Advantages

### **Most Valuable for Options Screening:**

1. **IV Rank/Percentile** ⭐⭐⭐⭐⭐
   - **Critical** for timing premium selling
   - yfinance: Cannot calculate (no historical IV)
   - IB: Full IV history → precise IV rank

2. **Earnings Calendar** ⭐⭐⭐⭐⭐
   - **Critical** for avoiding IV crush
   - yfinance: Stale or missing
   - IB: Real-time, accurate

3. **OI Change Tracking** ⭐⭐⭐⭐⭐
   - **Critical** for liquidity validation
   - yfinance: Only daily snapshot
   - IB: Track daily changes

4. **Real-time Greeks** ⭐⭐⭐⭐⭐
   - **Critical** for assignment probability
   - yfinance: Estimates (inaccurate)
   - IB: Exchange-calculated (precise)

5. **Weekly Expirations** ⭐⭐⭐⭐⭐
   - **Critical** for high-frequency wheel
   - yfinance: Often missing
   - IB: Complete weekly chains

6. **Bid/Ask Dynamics** ⭐⭐⭐⭐
   - **Important** for entry timing
   - yfinance: Stale snapshots
   - IB: Live streaming

7. **IV Skew Analysis** ⭐⭐⭐⭐
   - **Important** for strategy selection
   - yfinance: Cannot calculate
   - IB: Full chain analysis

### **Less Critical (Nice to Have):**

- Put/Call ratio ⭐⭐⭐
- Max pain ⭐⭐⭐
- Market depth ⭐⭐
- Rho (interest rate sensitivity) ⭐⭐

## Recommendation

### **Use IB for Screening If:**
✅ You want IV Rank-based filtering (game-changer)
✅ You need accurate earnings dates (critical for wheel)
✅ You trade weekly expirations (higher frequency)
✅ You want precise assignment probabilities (real Greeks)
✅ You track OI changes for liquidity validation

### **Stick with yfinance If:**
✅ You only screen monthly expirations
✅ You manually check earnings calendars
✅ You're okay with estimated Greeks (±5-10% error)
✅ You don't need IV rank calculations

## Implementation Priority

**Phase 1: Critical Data (Do First)**
1. IV Rank calculation (needs historical IV from IB)
2. Earnings calendar integration
3. Weekly expiration support
4. Real-time Greeks

**Phase 2: Enhanced Filtering**
5. OI change tracking
6. Liquidity quality score
7. IV skew analysis

**Phase 3: Advanced Analytics**
8. Put/call ratio
9. Implied move calculations
10. Max pain analysis

---

**Conclusion:** For serious options screening, IB provides **5 critical data points** that yfinance cannot match:
1. IV Rank (historical IV needed)
2. Accurate earnings dates
3. OI change detection
4. Real-time Greeks
5. Complete weekly chains

These are **strategic advantages**, not just execution conveniences.
