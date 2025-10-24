# CLAUDE.md - Stock Research Workflow

This file provides instructions for Claude Code when working with stock research in this directory.

## Directory Structure

```
~/dotfiles/research/stocks/
├── YYYY-MM/                    # Month folders (e.g., 2025-10/)
│   ├── {STOCK-NAME}/          # Stock-specific folders (LSCC, AMBA, BRCHF, GSIT)
│   │   ├── daily-update_YYYY-MM-DD.md
│   │   ├── comprehensive-research_YYYY-MM-DD.md
│   │   ├── swing-trading-analysis_YYYY-MM-DD.md
│   │   ├── raw-data/          # Audit trail files
│   │   │   └── YYYY-MM-DD/
│   │   │       ├── 01-query.md
│   │   │       ├── 02-perplexity-response.md
│   │   │       └── metadata.json
│   │   └── CLAUDE.md          # Stock-specific notes
│   └── {SECTOR-NAME}/         # Sector/theme folders
│       ├── daily-summary_YYYY-MM-DD.md
│       └── investment-summary_YYYY-MM-DD.md
├── portfolios/                # Portfolio configuration files
│   ├── README.md             # CSV format documentation
│   └── {PORTFOLIO-NAME}.csv  # Stock list with entry zones, risk levels
├── README.md                 # User-facing documentation
└── CLAUDE.md                 # This file - AI workflow instructions
```

## Daily Update Workflow

### Quick Start: Running Daily Updates

**For portfolio-based tracking (RECOMMENDED):**

```bash
# Read tickers from CSV portfolio file
/deep-stock-research --portfolio=AI-chips-hidden-gems --type=daily-update

# CSV file location: ~/dotfiles/research/stocks/portfolios/AI-chips-hidden-gems.csv
# Contains: LSCC, AMBA, BRCHF, GSIT with entry zones, risk levels, notes
```

**For individual stocks:**

```bash
# Single stock daily update
/deep-stock-research LSCC --type=daily-update

# Multiple stocks with explicit tickers
/deep-stock-research LSCC,AMBA --type=daily-update --portfolio=AI-chips-hidden-gems
```

### Portfolio Configuration Files

**Location**: `~/dotfiles/research/stocks/portfolios/{portfolio-name}.csv`

**Format**:
```csv
ticker,entry_zone_low,entry_zone_high,next_earnings,risk_level,notes
LSCC,66,68,2025-11-03,medium,A+ leadership
AMBA,80,82,2025-11-25,medium,Automotive ADAS
```

**Benefits**:
- ✅ DRY: Stock parameters in one place
- ✅ Version control: Track entry zone changes in git
- ✅ Risk management: Explicit risk levels guide position sizing
- ✅ Easy updates: Edit CSV, not command syntax

**See**: `~/dotfiles/research/stocks/portfolios/README.md` for full CSV format documentation

### Manual Daily Update Process

#### Step 1: Check Current Research Context

```bash
# Read the most recent research for the stock
ls ~/dotfiles/research/stocks/2025-10/<STOCK-NAME>/

# Review latest daily update or investment summary
```

#### Step 2: Ensure Comet Browser is Running with Remote Debugging

**CRITICAL: Comet must be running with remote debugging on port 9223**

**Check if Comet is running:**
```bash
ps aux | grep -i "comet" | grep -i "9223" | grep -v grep
```

**If not running, launch Comet with debugging:**
```bash
# Option 1: Use launch script
~/dotfiles/scripts/launch-comet-debug.sh

# Option 2: Manual launch
open -a "Comet" --args --remote-debugging-port=9223 "--remote-allow-origins=*" "--user-data-dir=$HOME/Library/Application Support/Comet"
```

**Wait 3-5 seconds for Comet to fully start before using MCP tools.**

#### Step 3: Navigate to Perplexity Using Comet MCP

Use MCP comet-devtools to interact with Perplexity Assistant:

```javascript
// 1. List available pages
await mcp__comet-devtools__list_pages()

// 2. If Perplexity not open, create new page
await mcp__comet-devtools__new_page("https://www.perplexity.ai/")

// 3. Take snapshot to see page structure
await mcp__comet-devtools__take_snapshot()

// 4. Find input field UID from snapshot (usually a textbox with "Ask anything" placeholder)
// Fill with daily update query
await mcp__comet-devtools__fill(uid, query)

// 5. Find and click submit button UID
await mcp__comet-devtools__click(submitButtonUid)

// 6. Wait for response to complete (look for "Share Link" button appearing)
await mcp__comet-devtools__wait_for("Share Link", 60000)

// 7. Take new snapshot to extract response data
await mcp__comet-devtools__take_snapshot()
```

**Important Notes:**
- Always take a fresh snapshot before filling - UIDs change between page loads
- Wait for "Share Link" button to confirm response is complete
- For long responses, may need multiple wait_for calls to ensure all data loads
- If page becomes unresponsive, refresh and retry

#### Step 4: Craft Daily Update Query

**Template Query:**
```
Latest update on [COMPANY NAME] ([TICKER]) for [TODAY'S DATE]:
(1) Current stock price and today's intraday price action,
(2) Any news or developments in past 24-48 hours,
(3) Has price reached the $[ENTRY-LOW]-[ENTRY-HIGH] entry zone yet?
(4) Updated RSI and MACD readings if available,
(5) Any changes to earnings date (currently [NEXT-EARNINGS-DATE]) or new catalysts scheduled.
```

**Example for LSCC:**
```
Latest update on Lattice Semiconductor (LSCC) for October 5, 2025:
(1) Current stock price and today's intraday price action,
(2) Any news or developments in past 24-48 hours,
(3) Has price reached the $66-68 entry zone yet?
(4) Updated RSI and MACD readings if available,
(5) Any changes to earnings date (currently Nov 3) or new catalysts scheduled.
```

#### Step 5: Extract Key Data from Perplexity Response

**What to Extract:**
- ✅ Current price and after-hours price
- ✅ Intraday price action and week range
- ✅ Recent news (24-48 hours)
- ✅ Entry zone status (has target been reached?)
- ✅ RSI reading (14-day)
- ✅ MACD status (bullish/bearish/neutral)
- ✅ Moving averages (50-day, 200-day)
- ✅ Bollinger Bands status
- ✅ Volume analysis
- ✅ Upcoming earnings date
- ✅ New catalysts

#### Step 6: Save Raw Data for Audit Trail (NEW)

**Purpose:** Preserve the raw query and Perplexity response for full auditability and transparency.

**Process:**

1. **Create date-specific folder:**
   ```bash
   mkdir -p ~/dotfiles/research/stocks/YYYY-MM/<STOCK-NAME>/raw-data/YYYY-MM-DD
   ```

2. **Save query** as `01-query.md`:
   - Full query text sent to Perplexity
   - Entry zone parameters used
   - Earnings dates referenced
   - Timestamp of query submission
   - Use template: `~/dotfiles/research/stocks/templates/raw-data/01-query.md`

3. **Extract and save Perplexity response** as `02-perplexity-response.md`:
   - From the snapshot, extract all text from Perplexity's response
   - Include summary section if provided
   - List all sources cited by Perplexity
   - Add extraction metadata (method, UIDs, timestamps)
   - Use template: `~/dotfiles/research/stocks/templates/raw-data/02-perplexity-response.md`

4. **Generate metadata.json:**
   - Session info (date, timestamp, session ID, Claude version)
   - Stock info (ticker, entry zone, earnings date)
   - Perplexity session details (URL, UIDs used, response detection method)
   - MCP tools invoked
   - Data sources cited
   - Processing timestamps
   - File references linking all artifacts
   - Use template: `~/dotfiles/research/stocks/templates/raw-data/metadata.json`

5. **(Optional) Save snapshots:**
   - `03-snapshot-pre.json` - Page state before query
   - `04-snapshot-post.json` - Page state after response
   - Skip these to save space unless debugging specific issues

**Why This Matters:**
- **Transparency:** Clear separation between Perplexity's raw output and Claude's synthesis
- **Verifiability:** Anyone can compare raw response vs final analysis
- **Reproducibility:** Exact query and response preserved for future reference
- **Debugging:** Identify if issues stem from query, Perplexity, or Claude interpretation

**Example File Locations:**
```
~/dotfiles/research/stocks/2025-10/LSCC/
├── raw-data/
│   ├── 2025-10-06/
│   │   ├── 01-query.md
│   │   ├── 02-perplexity-response.md
│   │   └── metadata.json
│   └── README.md
└── daily-update_2025-10-06.md
```

#### Step 7: Create Individual Daily Update Files

**File Location:**
```
~/dotfiles/research/stocks/YYYY-MM/<STOCK-NAME>/daily-update_YYYY-MM-DD.md
```

**Use Standard Template** (see Individual Daily Update Template below)

#### Step 8: Create Consolidated Daily Summary (Multi-Stock)

**IMPORTANT:** When running daily updates for multiple stocks (e.g., AI Chips Hidden Gems portfolio), create a consolidated summary file that aggregates key information across all stocks.

**File Location:**
```
~/dotfiles/research/stocks/YYYY-MM/<PORTFOLIO-NAME>/daily-summary_YYYY-MM-DD.md
```

**Example:** `~/dotfiles/research/stocks/2025-10/AI-chips-hidden-gems/daily-summary_2025-10-06.md`

**Required Sections:**
1. **Portfolio Overview Table** - All stocks with current price, entry zone, status, RSI
2. **Today's Action Items** - Immediate opportunities and high-priority alerts
3. **Technical Summary by Stock** - Concise overview of each stock
4. **Portfolio Strategy & Priorities** - Ranking by entry probability
5. **Upcoming Events Calendar** - All earnings dates and catalysts
6. **Market Context** - Sector trends and macro considerations
7. **Summary & Recommendations** - TLDR and what to do right now
8. **Individual Stock Reports** - Links to detailed daily updates

**Use Standard Template** (see Consolidated Daily Summary Template below)

### Daily Update Template

```markdown
# <TICKER> Daily Update - <DATE>

**Last Updated:** <DATE>

## 📊 Price Action Summary

| Metric | Value | Change |
|--------|-------|--------|
| **Last Close** | $XX.XX | ±X.XX% |
| **After-Hours** | $XX.XX | ±X.XX% |
| **Week Range** | $XX.XX - $XX.XX | - |
| **52-Week Range** | $XX.XX - $XX.XX | - |
| **Volume** | XXM | Above/Below average |

### Intraday Assessment
- **Price Status:** Above/Below/At entry zone
- **Lowest Close (Last Week):** $XX.XX
- **Trend:** [Description]
- **Entry Zone Status:** ✅/❌ [Status]

## 📰 Recent News & Developments (Past 48 Hours)

### Company-Specific News
- [News items or "No major announcements"]

### Market Sentiment
- [Analyst actions, ratings changes]

### Technical Alert
- [Any significant technical events]

## 📈 Technical Indicators Update

### RSI (14-Day)
- **Current:** XX.X
- **Status:** Oversold/Neutral/Overbought
- **Previous:** XX.X

### MACD
- **Status:** Bullish/Bearish/Neutral
- **Details:** [Description]

### Moving Averages
| MA | Value | Status |
|----|-------|--------|
| **50-Day SMA** | $XX.XX | Support/Resistance |
| **200-Day SMA** | $XX.XX | Support/Resistance |

### Bollinger Bands
- **Status:** [Squeezing/Expanding/etc]
- **Implication:** [What it means]

### Volume Analysis
- **Recent:** [Description]
- **Trend:** [Description]

## 🎯 Trading Levels Update

### Support Levels
1. **Primary:** $XX-XX (TARGET ENTRY ZONE)
2. **50-Day MA:** $XX.XX
3. **200-Day MA:** $XX.XX

### Resistance Levels
1. **Near-term:** $XX.XX
2. **Target 1:** $XX.XX
3. **Target 2:** $XX.XX

### Entry Strategy Status
- **Conservative Entry:** ✅/❌ Status
- **Action:** [What to do]

## 📅 Upcoming Catalysts

### Earnings Date
- **Next Report:** [Date]
- **Expected EPS:** $X.XX
- **Expected Revenue:** $XXM

### Known Catalysts
1. [Catalyst 1]
2. [Catalyst 2]

## 🎬 Action Items & Recommendations

### For Conservative Swing Traders
1. [Action item 1]
2. [Action item 2]

### Risk Assessment
- **Short-term:** [Assessment]
- **Daily Trend:** [Assessment]
- **Long-term Trend:** [Assessment]

## 📝 Summary & Key Takeaways

**TLDR:** [One-sentence summary]

### What Changed vs. Last Analysis
- [Change 1]
- [Change 2]

### What Stayed the Same
- [Constant 1]
- [Constant 2]

### Next Steps
1. [Step 1]
2. [Step 2]

---

**Previous Research:**
- [Links to related files]

---

## 📋 Audit Trail

**Raw Data Location:** `./raw-data/YYYY-MM-DD/`

- **Query Used:** [01-query.md](./raw-data/YYYY-MM-DD/01-query.md)
- **Perplexity Response:** [02-perplexity-response.md](./raw-data/YYYY-MM-DD/02-perplexity-response.md)
- **Session Metadata:** [metadata.json](./raw-data/YYYY-MM-DD/metadata.json)

**Purpose:** This audit trail preserves the raw query sent to Perplexity and the unmodified response received. Compare these files against the analysis above to distinguish between Perplexity's output and Claude's synthesis.

**Data Sources:**
- Perplexity Finance ([TICKER] page)
- Technical analysis via Perplexity (sources listed in 02-perplexity-response.md)
- Real-time price data as of [DATE TIME]
```

### Consolidated Daily Summary Template (Multi-Stock)

```markdown
# <PORTFOLIO-NAME> - Daily Summary
## <DATE>

**Last Updated:** <DATE>, <TIME>

---

## 📊 Portfolio Overview

| Stock | Current Price | Change | Entry Zone | Status | RSI (14d) | Next Catalyst |
|-------|--------------|--------|------------|--------|-----------|---------------|
| **STOCK1** | $XX.XX | ±X.XX% | $XX-XX | ✅/❌ | XX | Event Date |
| **STOCK2** | $XX.XX | ±X.XX% | $XX-XX | ✅/❌ | XX ⚠️ | Event Date |

### Key Symbols
- ✅ = At or below entry zone (ready to enter with confirmation)
- ❌ = Above entry zone (wait for pullback)
- ⚠️ = Warning/Alert condition

---

## 🎯 Today's Action Items

### Immediate Opportunities
[List stocks at entry zones or "NONE"]

### High-Priority Alerts to Set
1. **STOCK - PRIORITY LEVEL**
   - Set alert at **$XX.XX** (level description)
   - **Reason:** [Why this alert matters]
   - **Event Risk:** [Any upcoming catalysts]

---

## 📈 Technical Summary by Stock

### STOCK1 - Company Name
**Price:** $XX.XX (±X.XX%) | **Entry:** $XX-XX | **Status:** ✅/❌

**Key Points:**
- [Bullet point 1]
- [Bullet point 2]

**Action:** [What to do]

**Support Levels:** [List]
**Resistance Levels:** [List]

---

## 🎬 Portfolio Strategy & Priorities

### Ranking by Entry Probability (Next 2-4 Weeks)

1. **STOCK1** - XX% probability of hitting entry zone
   - [Reasoning]
   - Strategy: [Position sizing, stops]

2. **STOCK2** - XX% probability
   - [Reasoning]
   - Strategy: [Position sizing, stops]

### Risk Warnings

**⚠️ STOCK - Risk Level:**
- [Risk description]
- [Action recommendation]

---

## 📅 Upcoming Events Calendar

| Date | Stock | Event | Impact |
|------|-------|-------|--------|
| **Date** | TICKER | Event description | Impact level |

---

## 📊 Market Context

**Overall Sector:**
- [Sector performance summary]
- [Key trends]

**Macro Considerations:**
- [Macro factors affecting portfolio]

---

## 📝 Summary & Recommendations

### TLDR
[One-paragraph summary of portfolio status and key actions]

### What to Do Right Now

1. **Set Price Alerts:** [List]
2. **Prepare Entry Plans:** [List]
3. **Monitor Daily:** [What to watch]
4. **Avoid:** [What NOT to do]

---

## 📋 Individual Stock Reports

For detailed analysis of each stock, see individual daily updates:

- [STOCK1 Daily Update](../STOCK1/daily-update_YYYY-MM-DD.md)
- [STOCK2 Daily Update](../STOCK2/daily-update_YYYY-MM-DD.md)

**Audit Trails:** Each stock has complete raw data in `./raw-data/YYYY-MM-DD/` directories.

---

## 🔄 Change Log vs Previous Analysis

### New Information
- [What's new since last update]

### Status Changes
- [Any changes in priorities or recommendations]

---

**Last Updated:** <DATE>, <TIME>
**Next Update:** <DATE> (or sooner if significant moves occur)
```

## Stock-Specific Information

### Currently Tracked Stocks (AI Chips Hidden Gems)

#### 1. LSCC - Lattice Semiconductor
- **Target Entry:** $66-68
- **Next Earnings:** Nov 3, 2025
- **Leadership:** A+ (Dr. Ford Tamer, ex-Inphi CEO)
- **Key Levels:** Resistance $74.90/$80/$90, Support $64.64/$54.89

#### 2. AMBA - Ambarella
- **Target Entry:** $80-82
- **Key Levels:** Resistance $90/$95/$108, Support $75.12/$65.48

#### 3. BRCHF - BrainChip Holdings
- **Target Entry:** $0.155 (volume confirmation)
- **Key Levels:** Resistance $0.167/$0.173/$0.18, Support $0.150
- **Risk:** Very High (microcap, illiquid)

#### 4. GSIT - GSI Technology
- **Target Entry:** $4.10-4.60
- **Key Levels:** Resistance $5.24/$5.49/$5.74, Support $3.98/$3.51
- **Risk:** High (momentum-driven, overbought)

## File Naming Conventions

### Daily Updates (Individual Stock)
```
daily-update_YYYY-MM-DD.md
```
Example: `daily-update_2025-10-05.md`
Location: `~/dotfiles/research/stocks/YYYY-MM/<STOCK-NAME>/`

### Daily Summary (Multi-Stock Portfolio)
```
daily-summary_YYYY-MM-DD.md
```
Example: `daily-summary_2025-10-06.md`
Location: `~/dotfiles/research/stocks/YYYY-MM/<PORTFOLIO-NAME>/`
**Purpose:** Consolidated view of all stocks in portfolio with comparative analysis

### Comprehensive Research
```
comprehensive-research_YYYY-MM-DD.md
```

### Swing Trading Analysis
```
swing-trading-analysis_YYYY-MM-DD.md
```

### Investment Summaries (Multi-Stock)
```
investment-summary_YYYY-MM-DD.md
```
**Note:** This is different from daily-summary - investment summaries are comprehensive research reports

## MCP Tools Reference

### comet-devtools (Port 9223 - Comet Browser)

**Key Functions:**
```javascript
// Navigation and page inspection
mcp__comet-devtools__list_pages()
mcp__comet-devtools__select_page(pageIdx)
mcp__comet-devtools__navigate_page(url)
mcp__comet-devtools__take_snapshot()

// Interaction
mcp__comet-devtools__fill(uid, value)
mcp__comet-devtools__click(uid)
mcp__comet-devtools__wait_for(text, timeout)

// Data extraction
mcp__comet-devtools__evaluate_script(function)
```

**Common Workflow:**
1. Take snapshot to see page structure
2. Identify input field UID from snapshot
3. Fill input with query
4. Click submit button
5. Wait for response text
6. Take new snapshot to extract data

### web-search-prime (Alternative to Perplexity)

For quick fact-checking without browser:
```javascript
mcp__web-search-prime__webSearchPrime({
  search_query: "LSCC stock price latest",
  location: "us",
  count: 10
})
```

## Automation Best Practices

### When to Create Daily Updates

**Daily Triggers:**
1. Before market open (review previous day)
2. After market close (if significant moves)
3. After major news/announcements

**Event-Based Triggers:**
1. Price approaches entry zone (within 5%)
2. Earnings reports
3. Analyst rating changes
4. Major company announcements

**Minimum Frequency:**
- Weekly updates even if no major changes
- More frequent as entry zone approaches
- Daily during earnings season

### When to Update Investment Summaries

1. **Weekly:** Sunday evening or Monday morning
2. **After Earnings:** Within 24 hours of quarterly reports
3. **Major Catalysts:** New products, partnerships, leadership changes
4. **Quarterly:** Comprehensive review every 3 months
5. **Strategy Changes:** When entry/exit levels need adjustment

## Cross-References

### Key Command Files
- `/deep-stock-research`: `~/.claude/commands/deep-stock-research.md`
- Multi-timeframe analysis: `~/.claude/commands/trading-analysis.md`

### Related Documentation
- [Research Stocks README](./README.md) - User-facing guide
- [Deep Stock Research Command](~/.claude/commands/deep-stock-research.md)

## Common Issues & Solutions

### Issue: Perplexity Input Field UID Changes
**Solution:** Always take fresh snapshot before filling. UIDs change between page loads.

### Issue: Response Timeout
**Solution:** Increase timeout to 60000ms (60 seconds) for complex queries.

### Issue: Incomplete Response
**Solution:** Wait for "Share Link" button to appear, indicating response is complete.

### Issue: Price Data Delayed
**Solution:** Note that free data is typically 15-20 minutes delayed. After-hours prices may be more current.

## Trading Strategy Guidelines

### Conservative Swing Trading (Primary Strategy)

**Entry Criteria:**
- ✅ Price at or below entry zone
- ✅ RSI < 50 (neutral or oversold preferred)
- ✅ Volume confirmation on breakout
- ✅ Above 50-day MA (uptrend intact)

**Position Sizing:**
- 50% at entry zone low
- 50% on breakout confirmation (volume + resistance break)

**Exit Strategy:**
- Take 50% profit at Target 1
- Trail stop for remainder to Target 2
- Stop loss below entry zone

**Risk Management:**
- Maximum 2% account risk per position
- Set alerts at entry zones
- Never chase price above entry zone

## Notes for Future Sessions

### Session Continuity Checklist
1. ✅ Read this CLAUDE.md file
2. ✅ Check most recent daily updates for each stock
3. ✅ Review investment summary for comprehensive context
4. ✅ Verify earnings dates haven't changed
5. ✅ Check if entry zones have been reached

### Critical Reminders
- **DO NOT chase prices** above entry zones
- **Entry zones are hard limits** for conservative strategy
- **Valuation matters** - all 4 stocks trading at premium multiples
- **Risk increases** with microcaps (BRCHF, GSIT)
- **Always confirm** earnings dates (they can change)

### Research Quality Standards
- **Verify facts** - Don't state without confirmation
- **Express uncertainty** - Use "appears", "likely" when unsure
- **Break down complexity** - Multi-step analysis for complex tasks
- **Reference sources** - Note where data came from (Perplexity, Yahoo Finance, etc.)

---

**Last Updated:** October 5, 2025
**Next Review:** When adding new stocks or updating workflow
