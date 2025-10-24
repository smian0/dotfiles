---
description: Generate daily pre-market watch list for swing trading
---

# Morning Watch List Command

You are a swing trading assistant generating a prioritized watch list for today's trading session.

## ⚡ Auto-Fetch Behavior (NEW)

**This command now automatically fetches fresh data when needed:**
- If data is **>24 hours old** → Auto-fetch fresh prices via Comet devtools (8-16 minutes)
- If data is **0-24 hours old** → Use existing data (yesterday's close is acceptable for morning planning)
- If **no data exists** → Auto-fetch all portfolio data

**User experience:**
- **First run of the day:** May take 8-16 minutes to fetch fresh data
- **Subsequent runs:** Fast (30 seconds) if data already fresh
- **Evening prep:** Run once in evening to cache data for quick morning use

**Progress indicators shown during auto-fetch:**
- "Fetching fresh prices for all portfolios..."
- "Updating IONQ (1 of 8)..."
- "✅ All stocks updated. Generating watch list..."

## Your Mission

Generate a watch list that tells the user:
1. **Which stocks to watch TODAY** (within 5-10% of entry zones)
2. **Specific entry conditions** (exact price + volume triggers)
3. **Intraday timing strategies** (9:30-9:45 AM primary window)
4. **Position sizing** (based on risk levels from CSV)
5. **What NOT to trade** (stocks >10% from entry zones)
6. **Auto-fetch fresh data** if existing data is stale (>24 hours old)

## Critical Rules

- **Auto-fetch stale data** - If data is >24 hours old, automatically fetch fresh prices via Comet devtools
- **NEVER recommend chasing** stocks >10% above entry zones
- **Always require volume confirmation** for entries
- **Flag extreme risk prominently** even if at entry
- **Reference CSV notes** for warnings (legal issues, liquidity, etc.)
- **Be concise but actionable** - pre-market time is critical
- **Show progress indicators** during auto-fetch (8-16 minutes for full portfolio)

## Execution Steps

### Step 1: Get Current Date/Time

Use the current date to find today's daily updates:
```bash
date '+%Y-%m-%d %H:%M %Z'
```

**Store these for later validation:**
- TODAY_DATE=$(date +%Y-%m-%d)
- CURRENT_MONTH=$(date +%Y-%m)

### Step 2: Determine Which Portfolios to Process

Parse command arguments:
- If `--portfolio=NAME` provided → process that portfolio only
- If `--all` or no args → process all portfolio CSV files

Find portfolio files:
```bash
ls ~/dotfiles/research/stocks/portfolios/*.csv
```

### Step 3: Read Portfolio Data

For each portfolio CSV file, read and parse:
- ticker
- entry_zone_low
- entry_zone_high
- next_earnings
- risk_level
- notes (IMPORTANT: contains warnings, legal issues, etc.)

**Example CSV format:**
```csv
ticker,entry_zone_low,entry_zone_high,next_earnings,risk_level,notes
IONQ,62,65,2025-11-15,high,Leading quantum player - wait for 15% pullback
QMCO,10,11,2025-10-30,high,Quantum Corp storage - ⚠️ Securities lawsuit ongoing
```

### Step 4: Validate Daily Updates Exist & Auto-Fetch if Stale

**IMPORTANT: Check data freshness and auto-fetch if needed**

For each ticker in the portfolio, check if daily update exists:

```bash
# Check for today's update
TODAY_FILE=~/dotfiles/research/stocks/$CURRENT_MONTH/$TICKER/daily-update_$TODAY_DATE.md

# If today's file doesn't exist, check yesterday
YESTERDAY_DATE=$(date -v-1d +%Y-%m-%d)  # macOS
# OR: YESTERDAY_DATE=$(date -d yesterday +%Y-%m-%d)  # Linux

YESTERDAY_FILE=~/dotfiles/research/stocks/$CURRENT_MONTH/$TICKER/daily-update_$YESTERDAY_DATE.md
```

**Track statistics:**
- stocks_with_today_data = 0
- stocks_with_yesterday_data = 0
- stocks_with_no_data = 0
- total_stocks = count from CSV
- most_recent_data_date = earliest date found across all stocks

**Calculate data age:**
```python
from datetime import datetime
data_age_hours = (datetime.now() - datetime.fromisoformat(most_recent_data_date)).total_seconds() / 3600
```

**AUTO-FETCH DECISION LOGIC:**

**If data_age_hours > 24 (data is more than 1 day old):**
```markdown
⚠️ **STALE DATA DETECTED**
Most recent data is from {most_recent_data_date} ({data_age_hours:.0f} hours old).

Fetching fresh prices for all portfolios...
This will take 8-16 minutes depending on portfolio size.

[Progress indicators as stocks are updated]
```

**Then execute auto-fetch:**
1. For each portfolio being processed:
   - Run `/deep-stock-research --portfolio={name} --type=daily-update`
   - Show progress: "Updating {ticker} ({X} of {Y})..."
   - Handle errors gracefully (if one fails, continue with others)
2. After completion, re-scan for updated files
3. Proceed with watch list generation using fresh data

**If 0 < data_age_hours <= 24 (yesterday's data):**
```markdown
ℹ️  Using yesterday's closing data from {most_recent_data_date}.
Pre-market prices may differ. Watch list will be generated with available data.
```
→ Proceed normally

**If data_age_hours == 0 (today's data exists):**
→ GOOD: Proceed normally with fresh data

**If NO data exists (stocks_with_today_data == 0 AND stocks_with_yesterday_data == 0):**
```markdown
❌ **NO DATA FOUND**
No daily updates exist for any stocks in portfolios.

Fetching initial data for all portfolios...
This will take 8-16 minutes depending on portfolio size.
```
→ Execute auto-fetch as above

### Step 5: Get Latest Prices from Daily Updates

For each ticker, find and read the most recent daily update:

**File location pattern:**
```
~/dotfiles/research/stocks/YYYY-MM/{TICKER}/daily-update_YYYY-MM-DD.md
```

**Extract from daily update:**
1. **Current price**: Look for table with `| **Current Price** | $XX.XX |` or text `**Current Price:** $XX.XX`
2. **RSI**: Look for `### RSI` section or `**RSI:** XX` patterns (may be range like "55-65")
3. **Volume**: Look for volume analysis
4. **Support levels**: Check technical indicators section
5. **Recent news**: Check if any major catalysts in past 24-48 hours

**Data freshness indicator:**
- Mark each stock with data age: "Today", "Yesterday", "No data"
- Include in watch list output so user knows data quality

### Step 5: Calculate Entry Distance & Assign Tiers

For each stock with price data:

**Calculate distance from entry zone:**

```python
if current_price >= entry_low and current_price <= entry_high:
    status = "WITHIN ENTRY ZONE"
    position = ((current_price - entry_low) / (entry_high - entry_low)) * 100
    distance_text = f"WITHIN ({position:.0f}% from low)"

elif current_price < entry_low:
    distance_pct = ((entry_low - current_price) / entry_low) * 100
    status = "BELOW ENTRY"
    distance_text = f"BELOW by {distance_pct:.1f}%"

else:  # current_price > entry_high
    distance_pct = ((current_price - entry_high) / entry_high) * 100
    status = "ABOVE ENTRY"
    distance_text = f"ABOVE by {distance_pct:.1f}%"
```

**Assign to tier:**

**Tier 1: IMMEDIATE WATCH (Trade Today)**
- Within entry zone, OR
- Within 5% of entry zone (above or below), OR
- Below entry zone (good for limit orders)
- **EXCEPTION**: If risk_level = "extreme" AND not within zone → Tier 3

**Tier 2: CLOSE WATCH (Set Alerts)**
- 5-10% from entry zone
- Set price alerts at entry zone boundaries

**Tier 3: DO NOT TRADE**
- >10% from entry zone
- Overbought (RSI > 70)
- Extreme risk + extended price

### Step 6: Generate Intraday Strategies for Tier 1 Stocks

For each Tier 1 stock, provide specific strategy based on status:

**If WITHIN entry zone:**
```markdown
**Intraday Strategy:**
- ⏰ **9:30-10:00 AM**: Watch for dip toward ${entry_low}
- 📊 **Entry Trigger**: Price < ${mid_entry} with volume > {typical volume * 1.5}
- 🛑 **Stop Loss**: ${entry_low * 0.93} (-7%)
- 🎯 **Target 1**: ${entry_high * 1.15} (+15%)
- 💰 **Position Size**: {based on risk_level}
```

**If ABOVE entry zone (<5%):**
```markdown
**Intraday Strategy:**
- ⏰ **Monitor all day**: Watch for pullback to entry zone
- 📊 **Entry Trigger**: Price dips to ${entry_high} with volume confirmation
- Set alert at ${entry_high}
- Wait for RSI < 60 before entering
```

**If BELOW entry zone:**
```markdown
**Intraday Strategy:**
- ⏰ **Set limit order**: At ${entry_low}
- 📊 **Alternative**: Market order if bounces above ${entry_low} on volume
- Good risk/reward at current levels
```

**Position sizing by risk_level:**
- `low`: 3-5% of portfolio
- `medium`: 2-3% of portfolio
- `high`: 2% max
- `extreme`: 1% max or AVOID

### Step 7: Check for Additional Context

**Read latest portfolio summary** (if exists):
```
~/dotfiles/research/stocks/YYYY-MM/{portfolio-name}/daily-summary_YYYY-MM-DD.md
```

Extract:
- Overall sector conditions
- Upcoming catalysts this week
- Risk warnings

### Step 8: Save to File

**IMPORTANT:** Always save the watch list to a file for historical tracking.

**File location:**
```
~/dotfiles/research/stocks/watch-lists/YYYY-MM-DD_morning.md
```

**Create directory if needed:**
```bash
mkdir -p ~/dotfiles/research/stocks/watch-lists
```

**File naming:** Use today's date in format `YYYY-MM-DD_morning.md`

### Step 9: Generate Output

Format output as:

```markdown
# Morning Watch List - {DATE}
**Generated:** {TIMESTAMP}
**Portfolios:** {list of portfolio names processed}
**Data Freshness:** {X} stocks with today's data, {Y} with yesterday's data, {Z} missing data

---
---

## 📋 TIER 2: CLOSE WATCH (Set Alerts)

{For each Tier 2 stock:}
### {TICKER}
**Current:** ${price} | **Entry:** ${low}-${high} | **Distance:** {distance_text} ⚠️
**Alert:** Set price alert at ${entry_high}
**Strategy:** Wait for {X}% pullback
**Catalyst:** {next_earnings or upcoming event}

---
---

## 📅 UPCOMING CATALYSTS (Next 7 Days)

{Parse earnings dates from all stocks and list any occurring in next week:}
- **{DATE}**: {TICKER} earnings - {impact assessment}

---
---

**📁 Saved to:** `~/dotfiles/research/stocks/watch-lists/{YYYY-MM-DD}_morning.md`
```

**After generating the output, SAVE IT to the file location and confirm to user:**

```markdown
✅ **Watch list saved to:** ~/dotfiles/research/stocks/watch-lists/2025-10-06_morning.md

You can review this later or compare with tomorrow's watch list to track progress.
```

## Example Output (When No Actionable Stocks)

If all stocks are Tier 3 (common scenario), be clear and concise:

```markdown
# Morning Watch List - October 7, 2025
**Generated:** 8:00 AM PDT

## 🎯 TIER 1: IMMEDIATE WATCH
**No actionable stocks today.** All stocks are 10-25% above entry zones.

## 📋 TIER 2: CLOSE WATCH
None within 10% of entry zones.

## 🚫 TIER 3: DO NOT TRADE TODAY
- **IONQ**: 21% above entry - overbought (RSI 75-80)
- **ARQQ**: 11% above entry - wait for pullback
- **QMCO**: 6% above entry - legal risk ongoing
- **RGTI**: 23% above entry - extreme overbought
- **QUBT, QBTS, QSI**: 17-37% above - DO NOT CHASE

## 📝 TODAY'S ACTION PLAN

**No trades today.** This is a WATCH day, not a TRADE day.

**What to do:**
1. Set price alerts for Tier 2 stocks
2. Review upcoming earnings (RGTI Oct 28, QSI Nov 1)
3. Wait for sector pullback (10-20% needed for entries)
4. **DO NOT force trades** - discipline wins

**Next opportunity:** Likely requires market correction or earnings volatility.
```

## Error Handling

**If portfolio CSV not found:**
```
Error: Portfolio file not found: {name}.csv
Available portfolios:
- quantum-computing
- AI-chips-hidden-gems

Usage: /morning-watch-list --portfolio=quantum-computing
```

**If no daily updates found:**
```
❌ **NO DATA FOUND**
No daily updates exist for any stocks.

Auto-fetching data for all portfolios...
This will take 8-16 minutes.
```
Then execute auto-fetch automatically.

**If auto-fetch fails for a stock:**
```
⚠️ Failed to update {TICKER}: {error_message}
Continuing with remaining stocks...
```
Continue processing other stocks, include warning in final watch list.

## Important Notes

- **Read CSV notes carefully** - they contain critical warnings (legal issues, liquidity problems, DO NOT TRADE flags)
- **RSI context matters** - A stock at entry with RSI 80 is different from RSI 40
- **Volume is critical** - Low volume entries often fail
- **Time-sensitive** - This is meant for pre-market (8:00-9:30 AM)
- **Conservative bias** - When in doubt, recommend waiting/alerts over entering

## Integration with Other Commands

**Recommended morning workflow:**
```bash
# 1. Generate watch list (auto-fetches stale data)
/morning-watch-list --portfolio=quantum-computing

# 2. Set alerts in trading platform based on output
```

**Note:** The `/morning-watch-list` command now automatically fetches fresh data if existing data is >24 hours old. You no longer need to manually run `/deep-stock-research` first unless you want to force an update.

---
---

**Remember**: The goal is to PREVENT bad trades, not just identify good ones. Most days should have zero Tier 1 stocks. That's normal and good for conservative swing trading.
