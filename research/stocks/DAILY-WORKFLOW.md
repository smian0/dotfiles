# Daily Trading Workflow

Complete checklist for running the morning watch list system every trading day.

---

## ⏰ Timeline

### Evening Before (4:00-6:00 PM ET) - OPTIONAL
**Purpose:** Get tomorrow's watch list ready with today's closing prices

```bash
# Run daily updates after market close
/deep-stock-research --portfolio=quantum-computing --type=daily-update
/deep-stock-research --portfolio=AI-chips-hidden-gems --type=daily-update
```

**Time:** 16-20 minutes total
**Benefit:** Tomorrow morning you can skip updates and just generate watch list (2 minutes vs 20 minutes)

---

### Morning (7:00-8:00 AM ET) - REFRESH DATA
**Purpose:** Get latest pre-market prices if market moving overnight

**Option A: Used yesterday's evening data (FASTER - 2 minutes)**
```bash
# Just generate watch list
/morning-watch-list

# If it warns "data from yesterday", check:
# - Did anything significant happen overnight? (check news)
# - Are there major pre-market moves? (check portfolio tickers)
# - If YES to either: Run Option B
# - If NO: Yesterday's close is fine for planning
```

**Option B: Get fresh pre-market data (THOROUGH - 20 minutes)**
```bash
# Update all portfolios
/deep-stock-research --portfolio=quantum-computing --type=daily-update
/deep-stock-research --portfolio=AI-chips-hidden-gems --type=daily-update

# Generate watch list
/morning-watch-list
```

---

### Morning (8:00-9:00 AM ET) - REVIEW & PREPARE
**Purpose:** Set alerts, plan entries, prepare orders

**1. Review Watch List**
```bash
cat ~/dotfiles/research/stocks/watch-lists/$(date +%Y-%m-%d)_morning.md
```

**2. Check Data Freshness**
Look at top of watch list file:
- **"X stocks with today's data"** - How many have fresh data?
- If < 50%, consider running updates

**3. Tier 1 Stocks (Trade Today)**
- [ ] For each Tier 1 stock:
  - [ ] Set limit orders at entry zone prices
  - [ ] Set stop losses
  - [ ] Calculate position size (2-3% max)
  - [ ] Prepare trading platform

**4. Tier 2 Stocks (Set Alerts)**
- [ ] For each Tier 2 stock:
  - [ ] Set price alerts at entry zone high
  - [ ] Set alerts at mid-entry zone
  - [ ] Note earnings dates

**5. Review Warnings**
- [ ] Read all ⚠️ warnings in watch list
- [ ] Note legal risks (e.g., QMCO lawsuit)
- [ ] Check extreme risk stocks (DO NOT TRADE)

---

### Market Open (9:30-9:45 AM ET) - EXECUTE
**Purpose:** Primary entry window for Tier 1 stocks

**Pre-Market (9:15-9:30 AM)**
- [ ] Check pre-market prices for Tier 1 stocks
- [ ] Confirm volume is building (>50% avg pre-market)
- [ ] Review any overnight news

**Opening 15 Minutes (9:30-9:45 AM)**
- [ ] Watch Tier 1 stocks for dips INTO entry zones
- [ ] Require volume confirmation (>1.5x average)
- [ ] Execute limit orders if price/volume conditions met
- [ ] **DO NOT chase if price moves away from entry**

**If No Tier 1 Stocks:**
- [ ] Confirm this is a WATCH day, not TRADE day
- [ ] Set alerts for Tier 2 stocks
- [ ] Review plan but DO NOT force trades

---

### During Market (9:45 AM - 4:00 PM) - MONITOR
**Purpose:** Watch alerts, no active trading unless Tier 1 triggered

**Mid-Morning (10:00-11:00 AM)**
- [ ] Check if any Tier 2 alerts triggered
- [ ] If alert triggered: Wait for volume confirmation
- [ ] Secondary entry window (less reliable than 9:30-9:45)

**Lunch (11:00 AM - 2:00 PM)**
- [ ] Avoid entries (low volume period)
- [ ] Only monitor existing positions

**Power Hour (3:00-4:00 PM)**
- [ ] Third entry window (if Tier 1 stock still actionable)
- [ ] Prefer morning entries over power hour

---

### After Market Close (4:00-6:00 PM) - REVIEW
**Purpose:** Analyze day, prepare for tomorrow

**1. Trade Journal**
If you made trades today:
- [ ] Log entry price, time, size
- [ ] Note why entry criteria were met
- [ ] Document stop loss and targets
- [ ] Screenshot watch list for reference

**2. Alert Review**
- [ ] Which alerts triggered?
- [ ] Did you execute or pass? Why?
- [ ] Were entry criteria met?

**3. Next Day Prep (OPTIONAL)**
- [ ] Run evening daily updates (see Evening Before section)
- [ ] Review upcoming earnings (next 7 days)
- [ ] Check if any stocks approached entry zones

**4. Weekly Review (Fridays only)**
- [ ] Compare Mon-Fri watch lists
- [ ] Track which stocks moved toward/away from entry
- [ ] Review discipline: Did you follow the plan?

---

## 🚨 Red Flags - Stop and Reassess

**STOP if you find yourself:**
- [ ] Chasing prices above entry zones
- [ ] Trading Tier 3 stocks "because they're moving"
- [ ] Ignoring warnings in watch list
- [ ] Forcing trades when watch list says "No trades today"
- [ ] Entering without volume confirmation
- [ ] Skipping stop losses
- [ ] Position sizing >3% per stock

**If any red flags:** Close trading platform, walk away, review watch list again

---

## ⏱️ Time Commitment

**Minimum (Using Evening Data):**
- Morning: 5 minutes (generate watch list + review)
- Market open: 15 minutes (execute or confirm no trades)
- **Total: 20 minutes/day**

**Thorough (Fresh Morning Data):**
- Morning: 25 minutes (updates + watch list + review)
- Market open: 15 minutes (execute or confirm no trades)
- **Total: 40 minutes/day**

**With Evening Prep:**
- Evening: 20 minutes (updates for next day)
- Morning: 5 minutes (generate watch list + review)
- Market open: 15 minutes (execute or confirm no trades)
- **Total: 40 minutes split across 2 sessions**

---

## 📋 Weekly Checklist (Every Monday)

- [ ] Review previous week's watch lists
- [ ] Check earnings calendar for upcoming week
- [ ] Update portfolio CSVs if entry zones changed
- [ ] Review sector trends from portfolio summaries
- [ ] Adjust alerts if entry zones moved

---

## 🎯 Success Metrics

**Good discipline indicators:**
- 80-90% of days have zero Tier 1 stocks (this is NORMAL)
- You pass on Tier 2/3 stocks consistently
- Alerts are set but rarely trigger
- When trades execute, they follow the plan exactly
- Position sizes stay at 2-3% max

**Bad discipline indicators:**
- Trading every day (forcing trades)
- Chasing Tier 3 stocks
- Ignoring watch list recommendations
- Position sizes >3%
- Not using stop losses

---

## 🔄 Common Scenarios

### Scenario: All Tier 3 (Most Common)
**Action:** Set alerts for Tier 2, no trades today
**Time:** 5 minutes
**Outcome:** Zero trades (this is SUCCESS)

### Scenario: One Tier 1 Stock
**Action:** Prepare limit order, execute 9:30-9:45 AM if conditions met
**Time:** 20 minutes
**Outcome:** Either entry or pass (both are valid)

### Scenario: Multiple Tier 1 Stocks (Rare)
**Action:** Prioritize by risk level, enter max 2 stocks same day
**Time:** 30 minutes
**Outcome:** Portfolio diversification

### Scenario: Data is Stale
**Action:** Run daily updates OR acknowledge data age and proceed
**Time:** +15 minutes if updating
**Outcome:** Current data for better decisions

---

## 📝 Tips for Consistency

**1. Same Time Every Day**
Run morning watch list at same time (7:30-8:00 AM best)

**2. Evening Prep Saves Time**
Running updates after market close means faster mornings

**3. Accept Zero Trades**
Most days should have no actionable stocks - this is the system working

**4. Trust the Tiers**
If it says Tier 3 / DO NOT TRADE, believe it

**5. Volume is Critical**
No volume confirmation = no entry (even if price is perfect)

---

**Last Updated:** October 6, 2025
**System Version:** 1.0
