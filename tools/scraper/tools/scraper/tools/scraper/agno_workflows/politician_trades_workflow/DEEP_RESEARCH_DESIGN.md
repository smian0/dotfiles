# Deep Research Enhancement for Congressional Trading Analysis

## Vision

Transform the simple trade extraction workflow into a comprehensive political trading intelligence platform using Perplexity's Deep Research capabilities.

## Current vs Enhanced Capabilities

### Current System (Basic)

```
1. Extract trades from politicians page
2. Look up committee assignments
3. Synthesize with GLM-4.6
```

**Output**: Simple correlation between trades and committee jurisdiction

### Enhanced System (Deep Research)

```
1. Extract recent trades (same as before)
2. Deep Research: Full politician background
3. Deep Research: Pending legislation in committee jurisdiction
4. Deep Research: Historical trade patterns
5. Deep Research: Sector trends and upcoming catalysts
6. Network Analysis: Coordinated trading patterns
7. Advanced Synthesis: Multi-source intelligence report
```

**Output**: Comprehensive trading intelligence with actionable insights

## Proposed Enhancement Phases

### Phase 1: Deep Research Integration

**New Feature**: Multi-step research for each politician

**Implementation**:
```python
def deep_research_politician(politician: str) -> dict:
    """
    Use Perplexity Deep Research to analyze politician comprehensively

    Research Steps:
    1. Trading history (past 12 months)
    2. Committee assignments and jurisdiction
    3. Recent committee activity and hearings
    4. Sponsored/co-sponsored bills
    5. Voting record on sector-relevant legislation
    6. Public statements and policy positions
    """
```

**Scraper Prompt**:
```
Navigate to Perplexity and initiate Deep Research with:
"Analyze {politician}'s congressional trading activity, committee jurisdiction,
recent legislative activity, and public policy positions related to their recent
stock trades in {sectors}. Include pending legislation that could impact these sectors."
```

**Why Deep Research?**
- Multi-step reasoning across sources
- Citation tracking for verification
- More comprehensive than single Q&A
- Connects dots across time and topics

### Phase 2: Legislation Correlation Engine

**New Feature**: Match trades to upcoming legislation

**Research Questions**:
1. "What pending bills are under {committee} jurisdiction?"
2. "What legislation could impact {sector} in the next 6 months?"
3. "Has {politician} sponsored bills affecting {company/sector}?"

**Implementation**:
```python
def correlate_trades_to_legislation(trades: list, committees: dict) -> dict:
    """
    For each trade:
    1. Identify sector/industry
    2. Query pending legislation affecting that sector
    3. Check if politician's committee has jurisdiction
    4. Calculate "insider signal strength"
    """
```

**Example Output**:
```
Trade: Beyer bought GDXJ (gold miners) on Oct 15
Committee: Ways & Means (Trade subcommittee)
Pending Legislation:
  - H.R. 2345: Critical Minerals Security Act (in committee)
  - Trade policy review on rare earth metals (hearing scheduled)
Insider Signal: HIGH (committee jurisdiction + pending action)
```

### Phase 3: Historical Pattern Analysis

**New Feature**: Track politician's trading success rate

**Research Queries**:
```
"What stocks did {politician} buy in the past 12 months and what was
the performance 30/60/90 days after purchase?"

"Has {politician} had a history of well-timed trades before committee votes?"

"What is {politician}'s average holding period and exit timing?"
```

**Implementation**:
```python
def analyze_historical_performance(politician: str) -> dict:
    """
    Track historical trades:
    1. Entry price and date
    2. Exit price and date (if sold)
    3. Performance at 30/60/90 day marks
    4. Correlation with committee events
    5. Win rate and average return
    """
```

**Value**: Identify politicians with "hot hands" vs. noise traders

### Phase 4: Sector Trend Detection

**New Feature**: Aggregate congressional trading by sector

**Analysis**:
```python
def detect_sector_trends(all_trades: list) -> dict:
    """
    Aggregate trades by sector:
    1. Count buy/sell ratio per sector
    2. Identify sectors with unusual activity
    3. Cross-reference with market sentiment
    4. Flag divergences (congress buying, market selling)
    """
```

**Research Queries**:
```
"What are the major catalysts for {sector} in the next quarter?"
"Is congress buying {sector} while the market is selling? Why?"
"What upcoming regulatory changes could impact {sector}?"
```

**Example Output**:
```
Sector: Clean Energy
Congressional Activity: 5 buys, 0 sells (past 30 days)
Market Sentiment: Bearish (sector down 8%)
Divergence: HIGH - Congress buying while market sells
Potential Catalyst:
  - IRA implementation funding (Ways & Means oversight)
  - EPA regulations pending (Energy & Commerce committee)
Signal: Strong contrarian buy indicator
```

### Phase 5: Network Analysis

**New Feature**: Detect coordinated trading patterns

**Implementation**:
```python
def detect_coordinated_trades(trades: list) -> dict:
    """
    Find patterns:
    1. Multiple politicians buying same stock within 7 days
    2. Same committee members trading same sector
    3. Party-based clustering (Dems vs Reps)
    4. Spouse trades (coordination signal)
    """
```

**Research Queries**:
```
"Did multiple members of {committee} trade {stock/sector} recently?"
"What information might have been shared in recent {committee} hearings?"
"Are there patterns of coordinated purchases before policy announcements?"
```

**Example Output**:
```
Coordinated Trade Alert:
- Greene (Oversight) bought COIN on Nov 1
- Sherman (Financial Services) bought COIN on Nov 3
- Davidson (Financial Services) bought COIN on Nov 5
Pattern: 3 crypto-related committee members within 5 days
Research Finding: SEC crypto regulation hearing scheduled Nov 15
Signal: Strong insider positioning before announcement
```

### Phase 6: Advanced Synthesis Agent

**Enhanced Agent with Multi-Source Context**:

```python
synthesizer = Agent(
    name="Advanced Political Trading Intelligence",
    model=Ollama(
        id="glm-4.6:cloud",
        options={"num_ctx": 198000}
    ),
    instructions=[
        "You are an elite political trading intelligence analyst.",
        "Synthesize multi-source research into actionable trading intelligence.",

        "Required Analysis Sections:",
        "1. Executive Summary - Key findings and recommended actions",
        "2. High-Confidence Signals - Trades with strong insider indicators",
        "3. Sector Analysis - Aggregate trends and divergences",
        "4. Legislation Impact - Upcoming policy catalysts",
        "5. Historical Context - Track record of these politicians",
        "6. Network Effects - Coordinated trading patterns",
        "7. Risk Assessment - False signals and timing risks",
        "8. Action Plan - Specific trades with entry/exit strategies",

        "For each trade signal:",
        "- Insider Signal Strength: Low/Medium/High/Very High",
        "- Confidence Level: 1-10",
        "- Time Horizon: Days/Weeks/Months",
        "- Risk Factors: What could go wrong",
        "- Validation Steps: How to verify the signal",

        "Use citation-backed analysis only. Mark speculation clearly.",
        "Prioritize quality over quantity - focus on high-confidence signals.",
    ],
)
```

## Enhanced Workflow Architecture

```
┌─────────────────────────────────────────────────┐
│  Step 1: Extract Recent Trades                 │
│  - Scrape politicians page                     │
│  - Parse trades (who, what, when)              │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 2: Deep Research - Politicians           │
│  For each politician:                          │
│  - Trading history and patterns                │
│  - Committee jurisdiction                      │
│  - Recent legislative activity                 │
│  - Policy positions                            │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 3: Deep Research - Legislation           │
│  For each committee:                           │
│  - Pending bills                               │
│  - Scheduled hearings                          │
│  - Recent votes                                │
│  - Upcoming policy decisions                   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 4: Deep Research - Sector Analysis       │
│  For each traded sector:                       │
│  - Market sentiment                            │
│  - Upcoming catalysts                          │
│  - Regulatory changes                          │
│  - Industry trends                             │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 5: Historical Pattern Analysis           │
│  - Past trade performance                      │
│  - Politician "hot hands" identification       │
│  - Success rate metrics                        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 6: Network Analysis                      │
│  - Detect coordinated trades                   │
│  - Committee clustering                        │
│  - Party-based patterns                        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Step 7: Advanced Synthesis                    │
│  - Multi-source intelligence report            │
│  - High-confidence signals prioritized         │
│  - Actionable trade recommendations            │
│  - Risk assessment and validation              │
└─────────────────────────────────────────────────┘
```

## Implementation Strategy

### Option A: Enhanced Single Workflow

Extend `politician_trades_workflow/workflow.py` with additional steps:

```python
politician_deep_research_workflow = Workflow(
    name="Deep Political Trading Intelligence",
    steps=[
        Step(name="Extract Recent Trades", ...),
        Step(name="Deep Research Politicians", ...),
        Step(name="Deep Research Legislation", ...),
        Step(name="Deep Research Sectors", ...),
        Step(name="Analyze Historical Patterns", ...),
        Step(name="Detect Network Patterns", ...),
        Step(name="Synthesize Intelligence Report", ...),
    ],
)
```

### Option B: Modular Multi-Workflow System

Create specialized sub-workflows:

```
politician_trades_workflow/
├── workflow.py                    # Main orchestrator
├── modules/
│   ├── deep_research.py          # Perplexity Deep Research integration
│   ├── legislation_tracker.py    # Bill/hearing correlation
│   ├── historical_analyzer.py    # Performance tracking
│   ├── network_detector.py       # Coordinated trade patterns
│   └── sector_analyzer.py        # Aggregate sector trends
└── reports/
    ├── daily_intelligence.md     # Daily brief
    └── deep_dive_{politician}.md # Individual deep dives
```

## Perplexity UI Features to Leverage

### 1. Deep Research Mode

**Access**: Click "Deep Research" button on Perplexity main page

**Scraper Implementation**:
```python
prompt = """
1. Navigate to https://www.perplexity.ai
2. Click on "Deep Research" mode
3. Enter query: "{research_question}"
4. Wait for multi-step research to complete
5. Extract final report with citations
"""
```

### 2. Focus Modes

**Academic Focus**: For legislative analysis
**Writing Focus**: For synthesizing reports
**General**: For broad market research

### 3. Collections

Create persistent research collections:
- "Congressional Trading - Nov 2025"
- "Committee Legislation Tracker"
- "Sector Catalysts"

**Benefit**: Accumulate context over time

### 4. Follow-Up Questions

Deep Research allows iterative refinement:
```
Initial: "Analyze Beyer's GDXJ purchase"
Follow-up 1: "What pending trade policy affects gold miners?"
Follow-up 2: "Historical gold miner performance during trade policy changes?"
```

## Example Enhanced Output

### Current Output (Basic)

```markdown
# Politician Trades Analysis

## Donald S. Beyer Jr.
- Trade: GDXJ buy
- Committee: Ways & Means (Trade)
- Correlation: Trade jurisdiction → gold miners
```

### Enhanced Output (Deep Research)

```markdown
# Political Trading Intelligence Report
**Generated**: 2025-11-11
**Confidence**: High (8/10)

## Executive Summary

**High-Priority Signal**: Rep. Donald S. Beyer Jr. (D-VA-8) purchased GDXJ
(VanEck Gold Miners ETF) on Oct 15, 2025, two weeks before Ways & Means
Trade Subcommittee hearing on Critical Minerals Security.

**Insider Signal Strength**: VERY HIGH
- Committee jurisdiction alignment ✓
- Pending legislation affecting sector ✓
- Historical timing success ✓
- No coordinated trades (unique positioning) ✓

---

## Deep Research Findings

### Politician Background

**Rep. Donald S. Beyer Jr.**
- Committee: Ways & Means (Chair, Trade Subcommittee)
- Trading History: 12 trades in 2025, 67% profitable (30-day returns)
- Avg Holding Period: 45 days
- Specialization: Trade policy, tariffs, critical minerals

**Recent Committee Activity**:
- Nov 5: Hearing on "Critical Minerals Supply Chain Security"
- Oct 20: Closed session on China trade restrictions
- Oct 15: **GDXJ purchase** (same day as closed session)

**Key Insight**: Trade occurred immediately after closed-door session on
China critical minerals policy.

---

### Legislation Analysis

**Pending Bills** (Deep Research: 15 sources):

1. **H.R. 2345 - Critical Minerals Security Act**
   - Status: In Ways & Means Committee
   - Next Action: Markup scheduled Nov 18
   - Impact: Subsidies for domestic gold/rare earth mining
   - **Perplexity Citation**: [Congressional Record Nov 2025](...)

2. **Executive Order - China Rare Earth Import Restrictions**
   - Status: Under review
   - Expected: Dec 2025
   - Impact: Force domestic gold miner investment
   - **Perplexity Citation**: [Federal Register Filing](...)

**Catalyst Timeline**:
- Nov 18: Committee markup (GDXJ-positive)
- Dec 15: Expected executive order (GDXJ-positive)
- Q1 2026: Bill passage likely (GDXJ-positive)

---

### Sector Analysis

**Gold Miners ETF (GDXJ)**
- Market Sentiment: Bearish (-5% past month)
- Congressional Activity: 1 buy, 0 sells (only Beyer)
- **Divergence**: Congress buying while market sells

**Upcoming Catalysts** (Deep Research: 23 sources):
- Critical minerals subsidies (bullish)
- China import restrictions (bullish)
- Fed rate cuts Q1 2026 (bullish for gold)

**Historical Performance**:
- Post-legislation: +18% avg (past 3 instances)
- Time to peak: 60-90 days
- Volatility: High (±12%)

---

### Historical Pattern Analysis

**Beyer's Track Record**:
```
Trade Date    Ticker    Entry    30-Day Return    Committee Event
-----------------------------------------------------------------
2025-08-10    NVDA      $450     +15%            AI regulation hearing
2025-06-22    TSM       $145     +8%             Chips Act funding
2025-04-15    LMT       $420     -3%             Defense budget (miss)
2025-02-28    COIN      $180     +22%            SEC crypto hearing
```

**Success Rate**: 75% (9/12 trades positive)
**Avg Return**: +11% (30-day)
**Best Trades**: Before committee hearings
**Worst Trades**: After public announcements

**Pattern**: Beyer's best trades come 1-3 weeks before major committee action

---

### Network Analysis

**Coordinated Trades**: None detected
- No other Ways & Means members bought GDXJ
- No Energy & Commerce members (mining jurisdiction)
- No spouse trades in gold sector

**Interpretation**: Unique positioning = higher alpha potential
(No dilution from copycat trades)

---

### Risk Assessment

**Risks** (Confidence Impact):
1. ❌ Legislation could stall (Medium risk)
   - Mitigation: Strong bipartisan support

2. ❌ Gold price macro weakness (Medium risk)
   - Mitigation: Fed rate cut catalyst

3. ❌ GDXJ China exposure (Low risk)
   - Mitigation: Shift to domestic miners helps ETF

4. ❌ Ethics investigation timing (Low risk)
   - Mitigation: STOCK Act compliance observed

**Overall Risk**: Medium (acceptable for signal strength)

---

## Action Plan

### Recommended Trade

**Ticker**: GDXJ (VanEck Gold Miners ETF)
**Action**: BUY
**Confidence**: 8/10
**Time Horizon**: 60-90 days

**Entry Strategy**:
- Current Price: $32.50
- Target Entry: $31.50-$32.00 (on dip)
- Position Size: 2-3% of portfolio

**Exit Strategy**:
- Target 1: $36.00 (+11%, take 50%)
- Target 2: $38.50 (+18%, take 50%)
- Stop Loss: $29.00 (-8%)

**Catalysts to Watch**:
- Nov 18: Committee markup (expected positive)
- Dec 15: Executive order announcement
- Jan 2026: Bill passage vote

**Validation Steps**:
1. Monitor committee hearing transcripts
2. Track other Ways & Means trades
3. Watch for Beyer's next trade (confirmation/exit signal)
4. Check GDXJ inflows (institutional confirmation)

---

## Additional Opportunities

### Secondary Signals (Medium Confidence)

**None detected** - Beyer's trade is isolated, suggesting early positioning

### Watchlist (Low Confidence - Monitor Only)

- **REMX** (Rare Earth ETF): Same thesis, higher beta
- **GDX** (Large cap gold miners): Lower beta, safer
- **Individual miners**: SLW, GOLD, NEM (higher risk)

---

## Sources

**Deep Research Citations**: 47 sources consulted
- Congressional Record: 12 sources
- Federal Register: 5 sources
- Market Data: 18 sources
- Historical Analysis: 8 sources
- News Coverage: 4 sources

**Perplexity Deep Research Report**: [Full Report](...)

---

**Disclaimer**: Not financial advice. For research purposes only.
**Next Update**: Nov 12, 2025 (daily intelligence brief)
```

## Technical Implementation Notes

### Scraper Enhancements Needed

1. **Deep Research Mode Detection**
   ```python
   # Detect and wait for Deep Research completion
   snapshot = await chrome_tools.take_snapshot()
   if "Research in progress" in snapshot:
       await chrome_tools.wait_for("Research complete")
   ```

2. **Citation Extraction**
   ```python
   # Extract sources with URLs
   prompt = "Find all cited sources and extract [Title, URL, Quote]"
   ```

3. **Multi-Step Research Tracking**
   ```python
   # Track research progress
   steps = await extract_research_steps()
   # ["Analyzing legislation...", "Reviewing historical data...", "Synthesizing findings..."]
   ```

### Workflow Execution Time

**Current Basic Workflow**: ~5-10 minutes
- Step 1: Extract trades (2 min)
- Step 2: Committee lookup (2 min)
- Step 3: Synthesis (1 min)

**Enhanced Deep Research Workflow**: ~30-45 minutes
- Step 1: Extract trades (2 min)
- Step 2: Deep research politicians (10 min)
- Step 3: Deep research legislation (10 min)
- Step 4: Deep research sectors (10 min)
- Step 5: Historical analysis (5 min)
- Step 6: Network analysis (3 min)
- Step 7: Advanced synthesis (5 min)

**Trade-off**: 6x slower, but 10x more actionable intelligence

## Next Steps

1. **Proof of Concept**: Build Deep Research integration for single politician
2. **Validate Output**: Compare basic vs enhanced analysis quality
3. **Optimize Speed**: Parallel research where possible
4. **Build Dashboard**: Real-time tracking UI
5. **Automate Monitoring**: Daily runs with alerts

---

**Status**: Design proposal - ready for implementation
**Priority**: High - significantly increases trading signal quality
**Effort**: Medium - 2-3 days for full implementation
