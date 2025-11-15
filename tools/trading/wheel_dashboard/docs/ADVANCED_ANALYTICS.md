# Advanced Analytics Page - User Guide

## Overview

The Advanced Analytics page provides deep-dive options analysis with Open Interest (OI) heatmaps, volume comparison, max pain calculation, and put/call ratio analysis.

**Access**: Navigate to the "📊 Advanced Analytics" page in the sidebar

**Data Source**: Yahoo Finance (no IB connection required for this page)

---

## 🎯 Features

### 1. **OI Heatmaps** (Tab 1)

**What it shows**: Open Interest intensity across all strikes and expirations

**How to read**:
- **Bright colors** = High OI = Better liquidity
- **Dark colors** = Low OI = Poor liquidity
- **Red dashed line** = Current stock price

**For Wheel Strategy**:
- Look for bright zones 2-5% below current price
- These are your best targets (liquid + OTM)
- Avoid dark zones (hard to enter/exit)

**Example**:
```
Strike $68: Dark (OI: 50) → Skip
Strike $69: Medium (OI: 500) → Consider
Strike $70: Bright (OI: 2,000) → Excellent
```

---

### 2. **Volume vs OI** (Tab 2)

**What it shows**: Today's volume (bars) vs existing positions (line)

**How to interpret**:
- **High OI + Low Volume** = Stable positions (institutions holding)
- **High Volume + Low OI** = New activity (opportunity or risk)
- **High both** = Very active strike (excellent liquidity)
- **Low both** = Avoid (illiquid)

**For Wheel Strategy**:
- Target strikes with high OI (stable liquidity)
- Spikes in volume can signal unusual activity

**Strike Distribution Charts**:
- Visualize OI concentration
- Look for clusters (support/resistance levels)

---

### 3. **Max Pain** (Tab 3)

**Theory**: Market makers have incentive to push stock toward the strike where most options expire worthless (minimizes their payout).

**What it calculates**:
- For each strike, sum of ITM put value + ITM call value
- Max pain = strike with MINIMUM total pain

**How to use for Wheel**:

**Scenario 1: Max Pain Below Current Price**
```
Current: $70
Max Pain: $68
Distance: -2.9%

Interpretation: ⚠️ Downward pressure expected
Action: Sell puts at $66 or lower (safer)
```

**Scenario 2: Max Pain Above Current Price**
```
Current: $70
Max Pain: $72
Distance: +2.9%

Interpretation: 📈 Upward pull expected
Action: Can sell puts closer to current price
```

**Scenario 3: Max Pain Near Current**
```
Current: $70
Max Pain: $70.50
Distance: +0.7%

Interpretation: ✅ Range-bound expected
Action: Optimal conditions for wheel
```

**Important Notes**:
- Max pain is a **magnet, not a guarantee**
- Works best in final 7 DTE (expiration week)
- Combines well with IV Rank from main dashboard

---

### 4. **Put/Call Ratios** (Tab 4)

**What it shows**: Put OI / Call OI at each strike

**How to interpret**:
- **Ratio > 1.0 (Red)**: More puts than calls (bearish sentiment or hedging)
- **Ratio < 1.0 (Green)**: More calls than puts (bullish sentiment)
- **Very high ratio**: Potential support level (institutions protecting downside)

**For Wheel Strategy**:

**High Put OI Strikes** (Top 10 table):
- These often act as support levels
- Institutions are hedging/protecting at these strikes
- Selling puts BELOW these strikes = safer (extra cushion)

**Example**:
```
Strike $68: P/C Ratio 3.5 (Put OI: 3,500, Call OI: 1,000)
Strike $70: P/C Ratio 1.2 (Put OI: 1,200, Call OI: 1,000)
Strike $72: P/C Ratio 0.8 (Put OI: 800, Call OI: 1,000)

Interpretation:
- $68 has heavy put hedging (strong support)
- Selling $66 puts = very safe (below support)
- Selling $69 puts = moderate risk
```

---

## 🔄 Workflow: Main Dashboard + Advanced Analytics

### **Step 1: Screen on Main Dashboard**
1. Use IV Rank filter (> 50)
2. Exclude earnings (< 10 days)
3. Get top 5-10 opportunities

### **Step 2: Deep Dive on Advanced Analytics**
1. Check **OI Heatmap**: Verify target strike has good liquidity
2. Check **Max Pain**: Understand directional bias
3. Check **P/C Ratio**: Identify support levels
4. Refine strike selection

### **Step 3: Execute Trade**
1. Return to main dashboard
2. Review execution checklist
3. Place trade with confidence

---

## 📊 Example Analysis: KO (Coca-Cola)

### Main Dashboard:
```
IV Rank: 65/100 (NORMAL)
Earnings: 45 days (SAFE)
Recommended: Sell $68 Put @ $0.85 (12% annual yield)
```

### Advanced Analytics:

**OI Heatmap**:
- $68 strike: High OI (2,000+) ✅ Liquid
- $67 strike: Medium OI (500) 🟡 Acceptable
- $66 strike: Low OI (100) ❌ Avoid

**Max Pain**:
- Current: $69.71
- Max Pain: $69.50
- Distance: -0.3% ✅ Nearly neutral

**Put/Call Ratio**:
- $68: Ratio 2.1 (heavy put hedging - support level)
- $67: Ratio 3.5 (very heavy - strong support)

**Decision**:
- Sell $68 Put (original recommendation) ✅
- Good liquidity, near max pain, above support
- OR sell $67 Put if want extra safety (below strong support)

---

## ⚙️ Configuration

**Max Expirations Slider**:
- Default: 6 expirations
- Increase to 12 for longer-term view
- Decrease to 3 for faster loading

**Refresh Button**:
- Clears cache and reloads data
- Use if market moved significantly

---

## 🎯 Best Practices

### **DO**:
- Use OI heatmaps to identify liquid strikes
- Use max pain to understand directional bias
- Use P/C ratios to find institutional support
- Combine with IV Rank from main dashboard

### **DON'T**:
- Rely on max pain alone (it's a magnet, not destiny)
- Trade strikes with very low OI (even if good premium)
- Ignore volume spikes (could signal unusual activity)
- Over-complicate analysis (wheel strategy wins through consistency)

---

## 🚀 Quick Reference

| Analysis | Best For | Time Frame |
|----------|----------|------------|
| **OI Heatmap** | Liquidity check | Any |
| **Volume vs OI** | Entry timing | Daily |
| **Max Pain** | Directional bias | Last 7 DTE |
| **P/C Ratio** | Support levels | Any |

---

## 📝 Notes

- Advanced Analytics uses **yfinance only** (no IB required)
- OI and volume data refreshes every 5 minutes
- All charts are interactive (zoom, pan, hover for details)
- Export data via browser save/screenshot if needed

---

**Last Updated**: 2025-10-24
