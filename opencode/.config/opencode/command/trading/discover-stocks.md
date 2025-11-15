---
description: Discover hidden gem stocks in a sector using agentic research loop (Comet/Perplexity MCP)
---

# Discover Hidden Gem Stocks

Use agentic research loop with Perplexity to discover under-the-radar stocks in a specific sector.

## Your Mission

Find 5-10 "hidden gem" stocks in a target sector that meet specific criteria:
1. **Under-the-radar** - Market cap <$5B, low analyst coverage
2. **Growth potential** - Strong fundamentals, emerging catalysts
3. **Investable** - Reasonable liquidity, accessible to retail
4. **Sector fit** - Clear alignment with target sector

## Command Execution

### Step 0: Parse Arguments

```bash
ARGS="$ARGUMENTS"

# Extract --sector flag (required)
if echo "$ARGS" | grep -q -- '--sector='; then
    SECTOR=$(echo "$ARGS" | grep -o -- '--sector=[^ ]*' | cut -d= -f2)
else
    echo "❌ Error: --sector flag required"
    echo "Usage: /discover-stocks --sector=quantum-computing"
    echo "Available sectors: quantum-computing, AI-chips, edge-AI, neuromorphic, photonics"
    exit 1
fi

# Extract --market-cap-max (default: 5B)
if echo "$ARGS" | grep -q -- '--market-cap-max='; then
    MAX_MARKET_CAP=$(echo "$ARGS" | grep -o -- '--market-cap-max=[^ ]*' | cut -d= -f2)
else
    MAX_MARKET_CAP="5B"
fi

# Extract --min-stocks (default: 5)
if echo "$ARGS" | grep -q -- '--min-stocks='; then
    MIN_STOCKS=$(echo "$ARGS" | grep -o -- '--min-stocks=[^ ]*' | cut -d= -f2)
else
    MIN_STOCKS=5
fi

# Get current date for file organization
DISCOVERY_DATE=$(date +%Y-%m-%d)
DISCOVERY_MONTH=$(date +%Y-%m)
```

### Step 1: Verify Comet Browser Running

```bash
# Check if Comet is running on port 9223
if ! ps aux | grep -i "comet.*9223" | grep -v grep > /dev/null; then
    echo "⚠️ Comet Browser not running. Launching..."
    bash ~/dotfiles/scripts/launch-comet.sh
    sleep 5
fi
```

Use `mcp__comet-devtools__list_pages` to verify connection.

### Step 2: Navigate to Perplexity

**URL**: `https://www.perplexity.ai/`

Use these MCP tools in sequence:
1. `mcp__comet-devtools__navigate_page` → Perplexity home
2. `mcp__comet-devtools__wait_for` → Wait for "Ask anything" text
3. `mcp__comet-devtools__take_snapshot` → Get page structure

### Step 3: Multi-Round Discovery Research Loop

Execute 3-5 research rounds to discover and validate hidden gems.

#### Round 1: Broad Discovery Query

**Query Template**:
```
Discover hidden gem stocks in the {SECTOR} sector for October 2025. Find companies with:
- Market cap under ${MAX_MARKET_CAP}
- Low analyst coverage (<10 analysts)
- Strong recent developments or catalysts
- Reasonable trading volume (>100K shares/day)
- NOT well-known large-cap stocks

For each stock, provide: ticker, company name, market cap, brief business description, and why it's interesting.
```

**Interaction**:
1. Take snapshot → Find input field UID
2. `mcp__comet-devtools__fill` → Query
3. `mcp__comet-devtools__click` → Submit button
4. `mcp__comet-devtools__wait_for` → "Share" button (60s timeout)
5. Take snapshot → Extract response

**Extract**:
- List of 5-15 potential stocks
- Basic info (ticker, market cap, business model)
- Initial screening criteria

**Store**: Create initial candidate list with tickers

#### Round 2: Financial Screening

**Query Template**:
```
For these {SECTOR} stocks: {TICKER1}, {TICKER2}, {TICKER3}, {TICKER4}, {TICKER5}

Provide financial screening data (most recent quarter):

**Financial Metrics:**
- Revenue and revenue growth (YoY)
- Gross margin and operating margin
- Cash position and debt levels
- P/S ratio (price-to-sales)
- Analyst coverage count
- Average daily volume

**Customer Concentration & Revenue Quality:**
- Top 5 customer concentration % (if disclosed in 10-K)
- Government contract dependency (% of revenue)
- Recurring revenue % vs one-time sales
- Average contract length/duration
- Customer churn indicators

Flag any with red flags (declining revenue, excessive debt, illiquidity, high customer concentration >50%).
```

**Extract**:
- Financial metrics table
- Red flags
- Ranking by financial health

**Update Candidate List**:
- Remove stocks with critical red flags
- Rank by financial attractiveness
- Keep top 8-10 candidates

#### Round 3: Catalyst & Momentum Analysis

**Query Template**:
```
For these {SECTOR} stocks: {TOP_8_TICKERS}

Analyze recent catalysts and momentum (past 90 days):
- Recent news, partnerships, product launches
- Insider buying/selling activity
- Price action and technical momentum
- Upcoming events (earnings, conferences, product releases)
- Analyst rating changes

Rank by strength of near-term catalysts and momentum.
```

**Extract**:
- Catalyst summary for each stock
- Momentum assessment
- Upcoming event calendar

**Update Candidate List**:
- Score each stock on catalyst strength (1-10)
- Re-rank combining financial health + catalysts
- Narrow to top 5-7 stocks

#### Round 4: Leadership & Governance Analysis

**Query Template**:
```
For these top {SECTOR} stocks: {TOP_5_TICKERS}

Analyze leadership quality and corporate governance:

For each company, provide:

**Leadership Team:**
- CEO/Founder backgrounds (education, previous companies, notable achievements)
- Technical cofounder credentials (if applicable)
- Years of relevant industry experience
- Track record of successful exits or IPOs

**Board of Directors:**
- Notable board members (industry veterans, former executives)
- Board diversity and expertise
- Independent directors vs. insider ratio
- Advisory board composition

**Capital Allocation Track Record:**
- ROIC (Return on Invested Capital) trend (past 3 years)
- M&A history: accretive or dilutive deals?
- Share buyback timing (smart vs poor allocation)
- Cash deployment efficiency
- Cash conversion cycle trend

**Company Location:**
- Headquarters location (city, state)
- Proximity to talent hubs (Silicon Valley, Boston, etc.)
- R&D facility locations
- Manufacturing/operations presence

Rate leadership quality (1-10) based on track record, credentials, and capital allocation discipline.
```

**Extract**:
- Cofounder/CEO backgrounds
- Board member quality score
- Capital allocation track record
- ROIC trends and M&A success
- Location advantages/disadvantages
- Leadership caliber rating

**Analysis Guidance**:
- **Top-tier founders**: PhD from top-10 school, prior exits >$100M, published research
- **Strong boards**: Former CEOs of Fortune 500, industry pioneers, deep domain expertise
- **Smart capital allocators**: ROIC >15%, accretive M&A, buybacks at low valuations
- **Red flags**: Declining ROIC, dilutive M&A, buybacks at peak prices, poor cash conversion
- **Strategic locations**: Bay Area, Boston, Austin, Seattle = talent access; secondary markets = cost advantage

**Update Candidate List**:
- Add leadership scores
- Note any red flags (inexperienced CEOs, weak boards, remote location without clear advantage)

#### Round 5: Insider Trading & Institutional Ownership Analysis

**Query Template**:
```
For these top {SECTOR} stocks: {TOP_5_TICKERS}

Analyze insider trading patterns and institutional ownership:

**Insider Trading (Past 90 Days):**
- Recent insider transactions: buying or selling?
- Insider cluster buying (multiple executives buying simultaneously)?
- Significant Form 4 filings
- C-suite vs board member activity
- Size of transactions relative to holdings

**Institutional Ownership:**
- Top 5 institutional holders and % ownership
- Recent 13F changes (Q-over-Q): accumulation or distribution?
- Notable hedge funds entering or exiting positions
- Institutional ownership % trend (increasing/decreasing)
- Smart money signals (Tiger Global, Baillie Gifford, ARK, etc.)

**Compensation Alignment:**
- Executive stock-based compensation vs cash ratio
- Insider ownership % (skin in the game)
- Recent executive stock option grants

Flag any red flags: heavy insider selling, institutional exodus, misaligned compensation.
```

**Extract**:
- Insider buying/selling patterns
- Cluster buying signals
- Institutional accumulation/distribution
- Smart money positioning
- Ownership alignment scores

**Analysis Guidance**:
- **Bullish signals**: Insider cluster buying, institutional accumulation, high insider ownership %
- **Bearish signals**: Heavy insider selling, institutional exits, low stock-based comp
- **Smart money**: Track funds with strong track records (Tiger Global, Coatue, ARK for growth)

**Update Candidate List**:
- Add insider sentiment scores
- Flag stocks with insider cluster buying (strong buy signal)
- Note institutional accumulation patterns

#### Round 6: Patent & R&D Productivity Analysis

**Query Template**:
```
For these top {SECTOR} stocks: {TOP_5_TICKERS}

Analyze innovation strength and R&D efficiency:

**Patent Analysis:**
- Recent patent filings (past 12-18 months)
- Key patents filed and technology areas covered
- Patent citation quality (forward citations by others)
- Patent breadth (claims coverage, competitive moat)
- Patent velocity trend (accelerating or decelerating)

**R&D Productivity:**
- R&D spending as % of revenue
- R&D spending trend (increasing/decreasing)
- R&D efficiency vs sector peers
- Patents per $M of R&D spending
- Technology roadmap indicators from filings

**Competitive Moat:**
- Patent portfolio strength vs competitors
- Barriers to entry from IP
- Key patent expirations creating risks
- Freedom to operate analysis

Rate innovation strength (1-10) based on patent velocity, quality, and R&D efficiency.
```

**Extract**:
- Patent filing velocity
- Key patents and technology areas
- R&D efficiency metrics
- Competitive moat strength
- Innovation ratings (1-10)

**Analysis Guidance**:
- **Strong innovators**: Accelerating patent velocity, high citation quality, R&D <20% revenue
- **Patent moats**: Broad claims, technology領域 dominance, competitor citations
- **Red flags**: Declining patent filings, high R&D burn with no patents, key expirations

**Update Candidate List**:
- Add innovation strength scores
- Prioritize stocks with accelerating patent velocity
- Note competitive moat indicators

#### Round 7: Risk Assessment

**Query Template**:
```
For these top {SECTOR} stocks: {TOP_5_TICKERS}

Provide risk assessment for each:
- Competitive threats
- Regulatory risks
- Financial risks (burn rate, liquidity)
- Execution risks (leadership, operational)
- Market risks (sector headwinds)

Rate overall risk level (low/medium/high) and explain.
```

**Extract**:
- Risk summary per stock
- Risk level rating
- Bear case points

**Finalize Candidate List**:
- Assign risk levels
- Balance risk vs. reward vs. leadership quality
- Select final 5-6 stocks

#### Round 8: Entry Zone & Valuation (Optional)

**Query Template**:
```
For these final {SECTOR} hidden gems: {FINAL_TICKERS}

Provide technical and valuation analysis:
- Current price and 52-week range
- Key support levels
- Fair value estimate vs. current price
- Conservative entry zone recommendation

Help determine attractive entry points for swing trading.
```

**Extract**:
- Current prices
- Support levels
- Entry zone recommendations

### Step 4: Deep Dive on Top Candidates

For the top 3-5 stocks identified, run comprehensive research:

```bash
for TICKER in $TOP_CANDIDATES; do
    echo "📊 Running comprehensive research on $TICKER..."

    # Leverage existing /deep-stock-research command
    /deep-stock-research $TICKER --type=comprehensive

    # This creates:
    # ~/dotfiles/research/stocks/YYYY-MM/$TICKER/comprehensive-research_YYYY-MM-DD.md
done
```

### Step 5: Generate Discovery Report

**File Location**:
```
~/dotfiles/research/stocks/YYYY-MM/discoveries/{SECTOR}-hidden-gems_YYYY-MM-DD.md
```

**Example**: `~/dotfiles/research/stocks/2025-10/discoveries/quantum-computing-hidden-gems_2025-10-06.md`

**Report Structure**:

```markdown
# {SECTOR} Hidden Gems Discovery Report
**Date:** {DATE}
**Sector:** {SECTOR}
**Market Cap Limit:** <${MAX_MARKET_CAP}
**Stocks Analyzed:** {TOTAL_SCREENED}
**Final Recommendations:** {FINAL_COUNT}

---
---

## 📊 Final Recommendations

### Tier 1: High Conviction (Buy)
{For each Tier 1 stock:}

#### {TICKER} - {COMPANY NAME}
**Market Cap:** ${XXX}M | **Price:** ${XX.XX} | **Analyst Coverage:** {X} analysts

**Why It's a Hidden Gem:**
- {Reason 1 - catalyst or competitive advantage}
- {Reason 2 - financial strength}
- {Reason 3 - growth potential}

**Financials:**
- Revenue (TTM): ${XXX}M (+XX% YoY)
- Gross Margin: XX%
- Cash: ${XX}M | Debt: ${XX}M
- P/S Ratio: X.XX

**Recent Catalysts:**
- {Catalyst 1}
- {Catalyst 2}

**Leadership & Governance:**
- **CEO/Founders:** {Name} - {Background summary} | Leadership Score: {X}/10
- **Notable Board Members:** {Key board members with credentials}
- **Capital Allocation:** ROIC: {X}% | M&A Track Record: {Accretive/Dilutive} | {Key insight}
- **Location:** {City, State} - {Advantage: talent hub / cost efficiency / industry cluster}

**Insider Trading & Ownership:**
- **Insider Activity (90d):** {Buying/Selling/Neutral} | Cluster Buying: {Yes/No}
- **Top Institutional Holders:** {Fund 1}, {Fund 2} - {X}% ownership
- **Institutional Trend:** {Accumulation/Distribution/Stable}
- **Smart Money:** {Notable hedge funds accumulating or exiting}

**Innovation & IP Strength:**
- **Patent Velocity:** {X} patents filed (past 12mo) | Trend: {Accelerating/Stable/Declining}
- **R&D Efficiency:** {X}% of revenue | Patents per $M R&D: {X}
- **Competitive Moat:** {Strong/Medium/Weak} - {Key patents or technology areas}
- **Innovation Rating:** {X}/10

**Entry Strategy:**
- **Recommended Entry Zone:** ${XX}-${XX}
- **Current Status:** {Above/Below/At entry}
- **Risk Level:** {Low/Medium/High}
- **Position Size:** {X}% max

**Risks:**
- {Risk 1}
- {Risk 2}

**Next Steps:**
1. {Action 1}
2. {Action 2}

**Comprehensive Research:** [Link to full report](../{TICKER}/comprehensive-research_{DATE}.md)

---
---

### Tier 3: Pass (Not Recommended)
{Brief reasons why these didn't make the cut}

---
---

## 🔍 Comparison Matrix

| Stock | Mkt Cap | P/S | Rev Growth | Margin | Risk | Catalyst Score | Overall |
|-------|---------|-----|------------|--------|------|----------------|---------|
| **TICKER1** | ${XXX}M | X.X | +XX% | XX% | Med | 8/10 | ⭐⭐⭐⭐⭐ |
| **TICKER2** | ${XXX}M | X.X | +XX% | XX% | High | 7/10 | ⭐⭐⭐⭐ |

---
---

## 💡 Portfolio Construction Recommendation

**Diversification Strategy:**
- Allocate XX% to Tier 1 stocks
- Position sizing based on risk levels
- Entry timing based on entry zones

**Example Portfolio (${PORTFOLIO_SIZE} portfolio):**
- {TICKER1}: ${AMOUNT} ({X}%) - Entry at ${XX}-${XX}
- {TICKER2}: ${AMOUNT} ({X}%) - Entry at ${XX}-${XX}

---
---

## 📝 Next Steps for Investor

1. **Review comprehensive research** for each Tier 1 stock
2. **Set price alerts** at recommended entry zones
3. **Monitor upcoming catalysts** (earnings, events)
4. **Verify financials** via company investor relations
5. **Start with small positions** (1-2% max per stock)
6. **Create portfolio CSV** if adopting multiple stocks

---
---

## 📋 Audit Trail

**Discovery Process:**
- **Research Rounds:** {NUMBER}
- **Total Stocks Screened:** {NUMBER}
- **Final Recommendations:** {NUMBER}
- **Research Duration:** {TIME}
- **Data Sources:** Perplexity AI (company filings, financial news, market data)

**Raw Research Data:** Available in `./raw-discovery/YYYY-MM-DD/` directory

### Audit Trail Directory Structure

```
~/dotfiles/research/stocks/YYYY-MM/{SECTOR}-discoveries/
├── {SECTOR}-hidden-gems_YYYY-MM-DD.md          # Final discovery report
├── raw-discovery/
│   └── YYYY-MM-DD/                             # Date-specific session
│       ├── 00-session-metadata.json            # Discovery session metadata
│       ├── 01-round1-broad-discovery.md        # Round 1: Initial candidates
│       ├── 02-round2-financial-screening.md    # Round 2: Financial + customer concentration
│       ├── 03-round3-catalyst-analysis.md      # Round 3: Catalysts & momentum
│       ├── 04-round4-leadership-analysis.md    # Round 4: Leadership + capital allocation
│       ├── 05-round5-insider-ownership.md      # Round 5: Insider trading + institutions
│       ├── 06-round6-patent-rd-analysis.md     # Round 6: Patents + R&D productivity
│       ├── 07-round7-risk-assessment.md        # Round 7: Risk analysis
│       ├── 08-round8-entry-valuation.md        # Round 8: Entry zones (optional)
│       └── 99-final-candidate-list.json        # Final stock selections + scores
└── README.md                                   # Discovery methodology notes
```

### Per-Round File Structure

Each round file (`01-round1-*.md` through `08-round8-*.md`) contains:

```markdown
# Round {N}: {Round Name}
**Date:** YYYY-MM-DD HH:MM
**Perplexity Session:** https://www.perplexity.ai/...

## Query Sent to Perplexity

```
[Exact query text sent]
```

## Perplexity Response (Raw)

[Complete unmodified response from Perplexity]

### Sources Cited by Perplexity
1. source1.com - Article title
2. source2.com - Article title
...

## Extracted Data

**Stocks Analyzed:** {LIST}
**Data Points Extracted:**
- {Key metric 1}: {value}
- {Key metric 2}: {value}

## Candidate List After This Round

| Ticker | Status | Score | Notes |
|--------|--------|-------|-------|
| TICK1  | Advanced | 8/10  | {reason} |
| TICK2  | Eliminated | N/A  | {red flag} |

**Stocks Advancing:** {LIST}
**Stocks Eliminated:** {LIST} (reasons: {reasons})
```

### Session Metadata (`00-session-metadata.json`)

```json
{
  "session_info": {
    "date": "2025-10-06",
    "timestamp": "2025-10-06T14:30:00-07:00",
    "session_id": "quantum-discovery-2025-10-06",
    "claude_version": "claude-sonnet-4-5-20250929",
    "command_version": "v2.1-hedge-fund-grade"
  },
  "discovery_parameters": {
    "sector": "quantum-computing",
    "market_cap_max": "5B",
    "market_cap_min": "100M",
    "min_stocks_target": 5,
    "analyst_coverage_max": 10,
    "volume_min": "100K shares/day"
  },
  "research_rounds_completed": {
    "round1_broad_discovery": true,
    "round2_financial_screening": true,
    "round3_catalyst_analysis": true,
    "round4_leadership_analysis": true,
    "round5_insider_ownership": true,
    "round6_patent_rd_analysis": true,
    "round7_risk_assessment": true,
    "round8_entry_valuation": false
  },
  "perplexity_sessions": [
    {
      "round": 1,
      "url": "https://www.perplexity.ai/...",
      "query_timestamp": "2025-10-06T14:32:00-07:00",
      "response_timestamp": "2025-10-06T14:35:30-07:00",
      "pro_search": true,
      "sources_count": 23
    }
  ],
  "candidate_progression": {
    "round1_initial": 12,
    "round2_after_financial": 8,
    "round3_after_catalyst": 6,
    "round4_after_leadership": 6,
    "round5_after_insider": 5,
    "round6_after_patent": 5,
    "round7_final": 4
  },
  "final_recommendations": {
    "tier1_high_conviction": ["FORM", "SKYT"],
    "tier2_moderate_conviction": ["FEIM"],
    "tier3_speculative": ["MVIS"]
  },
  "mcp_tools_used": [
    "mcp__comet-devtools__navigate_page",
    "mcp__comet-devtools__take_snapshot",
    "mcp__comet-devtools__fill",
    "mcp__comet-devtools__click",
    "mcp__comet-devtools__wait_for",
    "mcp__comet-devtools__evaluate_script"
  ],
  "total_research_duration_minutes": 145,
  "files_generated": {
    "round_files": 8,
    "final_report": "{SECTOR}-hidden-gems_2025-10-06.md",
    "portfolio_csv": "quantum-new-discoveries-2025-10-06.csv"
  }
}
```

### Why This Audit Trail Matters

**Transparency:**
- Clear separation between Perplexity's raw output and Claude's synthesis
- Each round independently auditable

**Reproducibility:**
- Exact queries preserved for future runs
- Source citations traceable to originals

**Debugging:**
- Identify which round produced questionable data
- Tweak specific rounds without re-running entire discovery

**Compliance:**
- Full data lineage from sources → Perplexity → extraction → final report
- Verifiable research methodology

**Continuous Improvement:**
- Review round effectiveness (which rounds eliminated most stocks?)
- A/B test different query formulations
- Track Perplexity source quality over time

---
---

**Remember**: The goal is to find **investable** hidden gems, not just obscure stocks. Quality > quantity.
