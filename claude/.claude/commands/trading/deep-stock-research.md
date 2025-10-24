---
description: Multi-turn agentic research loop for comprehensive stock analysis using Perplexity
gitignore: project
---

# Deep Stock Research: Multi-Turn Agentic Loop

Execute a comprehensive, multi-turn research process for stock analysis using Perplexity Assistant.

## Command Execution Logic

**CRITICAL**: Start by parsing arguments from `$ARGUMENTS` to determine workflow.

### Step 0: Parse Arguments and Route Workflow

```bash
# Get current date for all workflows
RESEARCH_DATE=$(date +%Y-%m-%d)
RESEARCH_MONTH=$(date +%Y-%m)

# Parse $ARGUMENTS
ARGS="$ARGUMENTS"

# Extract tickers (everything before first --)
TICKERS_RAW=$(echo "$ARGS" | sed 's/--.*$//' | tr ',' ' ')

# Extract --type flag (default: comprehensive)
if echo "$ARGS" | grep -q -- '--type='; then
    RESEARCH_TYPE=$(echo "$ARGS" | grep -o -- '--type=[^ ]*' | cut -d= -f2)
else
    RESEARCH_TYPE="comprehensive"
fi

# Extract --portfolio flag
if echo "$ARGS" | grep -q -- '--portfolio='; then
    PORTFOLIO_NAME=$(echo "$ARGS" | grep -o -- '--portfolio=[^ ]*' | cut -d= -f2)
else
    PORTFOLIO_NAME=""
fi

# Determine ticker source: command line or CSV file
if [ -n "$PORTFOLIO_NAME" ] && [ -z "$TICKERS_RAW" ]; then
    # Portfolio specified but no explicit tickers → read from CSV
    PORTFOLIO_CSV="$HOME/dotfiles/research/stocks/portfolios/$PORTFOLIO_NAME.csv"

    if [ -f "$PORTFOLIO_CSV" ]; then
        echo "📋 Reading portfolio from: $PORTFOLIO_CSV"

        # Parse CSV (skip header, extract tickers)
        TICKERS=$(tail -n +2 "$PORTFOLIO_CSV" | cut -d, -f1 | tr '\n' ' ')

        # TODO: Parse other columns (entry zones, earnings, risk levels)
        # For now, just extract tickers
    else
        echo "❌ Error: Portfolio CSV not found: $PORTFOLIO_CSV"
        exit 1
    fi
else
    # Use explicit tickers from command line
    TICKERS="$TICKERS_RAW"
fi

# Count stocks
STOCK_COUNT=$(echo "$TICKERS" | wc -w | tr -d ' ')
```

### Step 1: Route to Appropriate Workflow

```
IF $RESEARCH_TYPE == "daily-update":
    → Execute Daily Update Workflow (see below)
    → For each ticker in $TICKERS:
        - Run daily update for individual stock
        - Save audit trail
    → IF $PORTFOLIO_NAME is set AND $STOCK_COUNT > 1:
        - Generate consolidated daily summary
    → Output: Summary of files created

ELSE IF $RESEARCH_TYPE == "swing-trading":
    → Execute Swing Trading Workflow
    → (Not yet implemented - fall back to comprehensive)

ELSE:
    → Execute Comprehensive Research Workflow (default)
    → Continue to "Comprehensive Research" section below
```

**After routing, proceed to the appropriate workflow section below.**

---

## Research Types

This command supports multiple research types:

1. **Comprehensive Research** (default): Multi-turn deep dive across 5 dimensions (6-8 Perplexity queries)
2. **Swing Trading Analysis** (`--type=swing-trading`): Technical analysis focus (3-4 queries)
3. **Daily Update** (`--type=daily-update`): Quick daily technical check (single Perplexity Finance query)
   - Creates individual daily update with audit trail
   - For multi-stock portfolios: Also creates consolidated daily summary

## Process

### Daily Update Workflow (--type=daily-update)

**Purpose**: Quick daily technical check and price action update for swing trading decisions.

**Implementation**:

#### Step 1: Verify Comet Browser Running

```bash
# Check if Comet is running on port 9223
if ! ps aux | grep -i "comet.*9223" | grep -v grep > /dev/null; then
    echo "⚠️ Comet Browser not running. Launching..."
    bash ~/dotfiles/scripts/launch-comet.sh
    sleep 5
fi
```

#### Step 2: Loop Through Each Stock

```bash
for TICKER in $TICKERS; do
    echo "📊 Processing daily update for $TICKER..."

    # Create directory structure
    STOCK_DIR="$HOME/dotfiles/research/stocks/$RESEARCH_MONTH/$TICKER"
    RAW_DATA_DIR="$STOCK_DIR/raw-data/$RESEARCH_DATE"
    mkdir -p "$RAW_DATA_DIR"

    # Read stock-specific configuration from CLAUDE.md if exists
    # (Entry zones, earnings dates, etc.)

    # Execute daily update for this stock (detailed steps below)

done
```

#### Step 3: For Each Stock - Execute Daily Update

**A. Navigate to Perplexity Finance Page**

Use `mcp__comet-devtools__navigate_page`:
```
URL: https://www.perplexity.ai/finance/{TICKER}
```

Wait for page load, then take snapshot to get current page state.

**B. Formulate Query**

Based on stock-specific data (read from `CLAUDE.md` in stock research workflow):
```
Query Template:
"Provide detailed swing trading analysis for {TICKER}: (1) Current RSI (14-day) and MACD readings, (2) Moving averages (50-day, 200-day), (3) Support and resistance levels, (4) Is the ${ENTRY_ZONE_LOW}-${ENTRY_ZONE_HIGH} entry zone likely to be tested?, (5) Next earnings date and any upcoming catalysts, (6) Volume analysis - sustainability of recent upward move."
```

**C. Fill Query and Submit**

1. Take snapshot to get input field UID
2. Use `mcp__comet-devtools__fill` with query
3. Use `mcp__comet-devtools__click` on submit button
4. Wait for response completion (look for "Share" button appearing)

**D. Extract Response**

1. Take final snapshot
2. Extract all response text from StaticText elements
3. Extract sources from citation links
4. Extract price data from Finance Widget

**E. Save Audit Trail**

Create 3 files in `$RAW_DATA_DIR`:

1. **01-query.md**: Save query text with parameters
2. **02-perplexity-response.md**: Save raw response with sources
3. **metadata.json**: Session data (UIDs, timestamps, sources, technical indicators)

**F. Generate Daily Update File**

Using Bash `cat` with heredoc (not Write tool to avoid read requirement):
- File: `$STOCK_DIR/daily-update_$RESEARCH_DATE.md`
- Use template from `~/dotfiles/research/stocks/CLAUDE.md`
- Include audit trail footer linking to raw-data files

#### Step 4: Generate Consolidated Summary (If Multi-Stock Portfolio)

```bash
if [ -n "$PORTFOLIO_NAME" ] && [ "$STOCK_COUNT" -gt 1 ]; then
    echo "📋 Generating consolidated portfolio summary..."

    PORTFOLIO_DIR="$HOME/dotfiles/research/stocks/$RESEARCH_MONTH/$PORTFOLIO_NAME"
    mkdir -p "$PORTFOLIO_DIR"

    # Read all individual daily updates
    # Aggregate data into portfolio overview table
    # Generate consolidated summary using template

    SUMMARY_FILE="$PORTFOLIO_DIR/daily-summary_$RESEARCH_DATE.md"

    # Use Bash cat with heredoc to create consolidated summary
    # Include:
    # - Portfolio overview table (all stocks)
    # - Action items ranked by priority
    # - Risk warnings
    # - Upcoming events calendar
    # - Links to individual daily updates
fi
```

#### Step 5: Output Summary

```
✅ Daily Update Complete!

Files Created:
- {TICKER1}/daily-update_{DATE}.md (with audit trail)
- {TICKER2}/daily-update_{DATE}.md (with audit trail)
- ...
- {PORTFOLIO}/daily-summary_{DATE}.md (consolidated)

Quick Summary:
| Stock | Price | Entry Zone | Status | Action |
|-------|-------|------------|--------|--------|
| LSCC  | $XX   | $XX-XX     | ❌ Above | WAIT  |
...

Highest Priority: {STOCK} - {REASON}
```

**See**: `~/dotfiles/research/stocks/CLAUDE.md` for detailed templates and workflow.

---

### Comprehensive Research (Default)

You will conduct iterative research across 5 dimensions: **Fundamentals**, **Catalysts**, **Technical/Sentiment**, **Risks**, and **Outlook**.

### Workflow:

1. **Initialize**: Navigate to Perplexity Assistant at https://www.perplexity.ai/sidecar?copilot=true

2. **Initial Query**: Start with broad overview question

3. **Multi-Turn Loop** (6-8 iterations):
   - Analyze previous response for completeness
   - Identify highest-priority knowledge gap
   - Ask targeted follow-up question
   - Extract and synthesize findings
   - Track completeness across dimensions

4. **Synthesis**: Generate comprehensive markdown report

## Completeness Tracking

Track research completeness for each dimension (0-100%):

### Fundamentals (Target: 75%+)
- [ ] Revenue & earnings data
- [ ] Profit margins & trends
- [ ] Valuation metrics vs peers
- [ ] Balance sheet health
- [ ] Competitive position & market share

### Catalysts (Target: 75%+)
- [ ] Recent news (past 30 days)
- [ ] Analyst ratings & price targets
- [ ] M&A / partnerships
- [ ] Upcoming events / earnings dates
- [ ] Management / insider activity

### Technical & Sentiment (Target: 75%+)
- [ ] Price action & chart patterns
- [ ] Institutional ownership changes
- [ ] Insider trading patterns
- [ ] Short interest data
- [ ] Options activity

### Risks (Target: 75%+)
- [ ] Regulatory risks
- [ ] Competitive threats
- [ ] Execution risks
- [ ] Bear case arguments
- [ ] Macro / industry headwinds

### Outlook (Target: 75%+)
- [ ] Growth projections (2-3 years)
- [ ] TAM & market opportunity
- [ ] Strategic initiatives
- [ ] Scenario analysis (bull/base/bear)
- [ ] Long-term thesis

## Research Execution Workflow

### Step 1: Launch Browser & Navigate to Perplexity

**CRITICAL**: Use Comet Browser with `comet-devtools` MCP for all automation.

```bash
# Ensure Comet Browser is running on port 9223
# If not running, launch with:
bash ~/dotfiles/scripts/launch-comet.sh 9223 no
```

**Browser Automation**:
1. Use `mcp__comet-devtools__list_pages` to check browser state
2. Use `mcp__comet-devtools__navigate_page` to go to: `https://www.perplexity.ai/`
3. Wait for page load with `mcp__comet-devtools__wait_for` (text: "Ask anything")

### Step 2: Execute Research Rounds

For each research round (1-8):

#### A. Enter Query in Perplexity
1. **Take Snapshot**: `mcp__comet-devtools__take_snapshot` to identify input field
2. **Fill Query**: Use `mcp__comet-devtools__fill` with the research question
3. **Submit**: `mcp__comet-devtools__click` on submit button OR press Enter key
4. **Wait for Response**: `mcp__comet-devtools__wait_for` until streaming completes (look for "Related" section or "Sources" appearing)

#### B. Extract Response
1. **Take Snapshot**: `mcp__comet-devtools__take_snapshot` to capture full response
2. **Parse Content**: Extract all StaticText elements containing the answer
3. **Parse Sources**: Extract source URLs from the "Sources" section (look for numbered citations)
4. **Save Findings**: Store response text and source URLs in research state

#### C. Analyze Completeness & Gap Identification

**CRITICAL: This is the intelligent feedback loop. You MUST perform this analysis after EVERY round.**

1. **Extract Key Findings**: Summarize what specific data points were gathered from this round's Perplexity response
   - List concrete facts, numbers, dates, quotes
   - Note which dimension(s) this data addresses

2. **Update Dimension Scores** (0-100% each):
   - **Fundamentals**: Do we have revenue breakdown, margins, cash flow, debt, competitive valuation comparison?
   - **Catalysts**: Do we have upcoming events, recent analyst actions with dates/firms/targets, M&A news, insider activity?
   - **Technical/Sentiment**: Do we have institutional changes, short interest, options data, price levels?
   - **Risks**: Do we have regulatory, competitive, execution, valuation, macro risks identified?
   - **Outlook**: Do we have 2026-2027 projections, TAM analysis, strategic initiatives, scenarios?

   Assign percentage based on checklist coverage:
   - 0-25%: Minimal data, major gaps
   - 25-50%: Some data, significant gaps remain
   - 50-75%: Good data, minor gaps
   - 75-100%: Comprehensive coverage, ready for report

3. **Calculate Overall Completeness**: Average of all 5 dimension scores

4. **Identify Biggest Gap**: Which dimension has the LOWEST score? What specific data is missing?

5. **Decide Next Action**:
   - If ALL dimensions ≥75%: Proceed to report generation
   - If round ≥8: Proceed to report generation (max iterations reached)
   - If any dimension <75% AND round <8: Continue to next round targeting lowest dimension

#### D. Formulate Next Query (Adaptive)

**DO NOT blindly follow the round templates below. Instead:**

1. **Review dimension scores** from Step C
2. **Identify the lowest-completeness dimension** (<75%)
3. **List specific missing data points** for that dimension
4. **Construct a targeted query** that fills those exact gaps

**Example**:
- If Fundamentals = 45% (missing: cash flow details, working capital, detailed segment margins)
- Then query: "For {SYMBOL}, provide detailed cash flow statement (operating, investing, financing), working capital metrics, and profit margins broken down by each business segment for Q2-Q3 2025"

**Use the templates below as GUIDES, not scripts. Adapt them based on actual gaps identified.**

---

### Round 1: Broad Overview
**Perplexity Query**: "Provide comprehensive overview of {SYMBOL}: business model, recent Q3 2025 financial performance, valuation metrics, major recent news, and current market sentiment. Include analyst consensus and key risks."

**Extract**: Basic facts across all dimensions
**Updates**: All dimensions get initial 15-25% completeness

---

### Round 2: Fundamentals Deep Dive
**Perplexity Query**: "Analyze {SYMBOL}'s financial fundamentals in depth: Provide Q3 2025 earnings breakdown by segment, margin trends, balance sheet strength (debt, cash, FCF), and detailed valuation comparison vs top 3 competitors. Is it overvalued or undervalued?"

**Extract**: Detailed financial metrics, competitive positioning
**Updates**: Fundamentals dimension +30-40%

---

### Round 3: Recent Catalysts
**Perplexity Query**: "What are the most significant catalysts affecting {SYMBOL} in September-October 2025? Include: recent news/announcements, analyst rating changes, M&A or partnership activity, upcoming earnings/product launches, and management/insider trading activity."

**Extract**: Time-sensitive events and sentiment shifts
**Updates**: Catalysts dimension +35-45%

---

### Round 4: Technical & Institutional
**Perplexity Query**: "Analyze {SYMBOL}'s technical setup and institutional positioning: Current price action/trend, key support/resistance levels, recent institutional ownership changes from 13F filings, insider buying/selling patterns, short interest trends, and unusual options activity."

**Extract**: Market structure and positioning data
**Updates**: Technical/Sentiment dimension +30-40%

---

### Round 5: Risk Assessment
**Perplexity Query**: "Provide comprehensive risk analysis for {SYMBOL}: Regulatory risks, competitive threats from emerging players/technologies, execution risks, the detailed bear case (why it could fail), and macro/industry headwinds. What are the 3 biggest risks to the investment thesis?"

**Extract**: Downside scenarios and concerns
**Updates**: Risks dimension +40-50%

---

### Round 6: Forward Outlook
**Perplexity Query**: "Analyze {SYMBOL}'s forward outlook: Consensus analyst projections for next 2-3 years (revenue/EPS growth), total addressable market size and penetration, key strategic initiatives driving growth, and scenario analysis with price targets for bull/base/bear cases."

**Extract**: Growth projections and upside scenarios
**Updates**: Outlook dimension +40-50%

---

### Round 7: Gap Fill (Adaptive)
**Assessment**: Review all 5 dimensions. Identify which has lowest completeness.

**Perplexity Query Templates**:
- **If Fundamentals <75%**: "For {SYMBOL}, provide missing financial data: [list specific gaps like balance sheet ratios, cash flow details, segment margins]"
- **If Catalysts <75%**: "What recent developments for {SYMBOL} haven't been covered: [list gaps like M&A rumors, product delays, management changes]"
- **If Technical <75%**: "Provide detailed technical and ownership analysis for {SYMBOL}: [list gaps like short interest, options flow, institutional changes]"
- **If Risks <75%**: "What additional risks should investors consider for {SYMBOL}: [list gaps like regulatory, litigation, execution risks]"
- **If Outlook <75%**: "Provide detailed forward projections for {SYMBOL}: [list gaps like segment forecasts, TAM analysis, strategic roadmap]"

**Extract**: Targeted gap-fill data
**Updates**: Lowest dimension +20-30%

---

### Round 8: Final Validation (if needed)
**Perplexity Query**: "Synthesize the investment thesis for {SYMBOL}: What makes this compelling (bull case), what are the key risks (bear case), and what is the balanced risk/reward assessment? Include confidence level based on data quality."

**Extract**: Investment thesis validation, holistic view
**Updates**: Final completeness check across all dimensions

---

## Response Extraction Strategy

After each Perplexity response completes:

### 1. Snapshot Capture
```javascript
mcp__comet-devtools__take_snapshot()
```

### 2. Content Extraction
Parse snapshot for:
- **Answer Text**: All StaticText elements in main content area (exclude UI elements like "Ask anything", "Related", etc.)
- **Source Citations**: Links in "Sources" section (usually numbered [1], [2], etc.)
- **Follow-up Suggestions**: "Related" questions (optional, can inform next round)

### 3. Data Storage
Store in research state object:
```javascript
{
  round: 1-8,
  dimension: "fundamentals|catalysts|technical|risks|outlook",
  query: "exact query sent to Perplexity",
  response: "extracted answer text",
  sources: ["url1", "url2", ...],
  completeness_update: {
    fundamentals: 25,  // 0-100%
    catalysts: 15,
    technical: 10,
    risks: 20,
    outlook: 15
  }
}
```

### 4. Completeness Calculation
Update cumulative scores:
```javascript
total_completeness = {
  fundamentals: round1_score + round2_score + ...,
  catalysts: round1_score + round3_score + ...,
  technical: round1_score + round4_score + ...,
  risks: round1_score + round5_score + ...,
  outlook: round1_score + round6_score + ...
}
```

### 5. Next Round Decision
```javascript
if (all dimensions >= 75% || round >= 8 || diminishing_returns) {
  proceed_to_report_generation()
} else {
  identify_lowest_dimension()
  formulate_next_query()
  execute_next_round()
}
```

## Report Generation

After achieving 75%+ across all dimensions, generate markdown report with:

### Structure:
```markdown
# Deep Stock Research: {SYMBOL}

## Executive Summary
- Quick facts (market cap, P/E, revenue, EPS)
- Key highlights
- Investment recommendation
- Confidence level

## Fundamental Analysis
- Financial metrics table
- Business model breakdown
- Competitive position

## Catalysts & Events
- Recent developments
- Analyst activity
- Upcoming events
- Strategic moves

## Technical & Sentiment
- Price action analysis
- Institutional positioning
- Insider activity
- Short interest

## Risk Assessment
- Risk categories (regulatory, competitive, execution, valuation, macro)
- Bear case summary

## Forward Outlook
- Growth projections
- Market opportunity
- Strategic initiatives
- Scenario analysis

## Investment Thesis
- Bull case (3-5 points)
- Bear case (3-5 points)
- Risk/reward assessment
- Confidence score

## Sources & Methodology
- Source bibliography
- Research metadata
```

## Quality Standards

### Source Requirements:
- Minimum 3 independent sources per dimension
- Prefer: Company filings, financial news, analyst reports, market data
- Avoid: Single-source claims, promotional content

### Recency Requirements:
- Prefer data from past 30 days
- Maximum 90 days old
- Mark older data as "historical context"

### Confidence Scoring:
- **Very High (90-100%)**: Multiple recent sources agree
- **High (75-89%)**: Good sources, minor gaps
- **Moderate (60-74%)**: Some contradictions or gaps
- **Low (40-59%)**: Significant missing data
- **Very Low (<40%)**: Insufficient for recommendation

## Termination Conditions

Stop research loop when:
1. All dimensions ≥ 75% complete, OR
2. 8 iterations reached (max), OR
3. Diminishing returns (new info < 10% per iteration)

## File Organization & Directory Structure

**CRITICAL**: All research reports MUST be saved to the structured directory system in `~/dotfiles/research/stocks/`.

### Directory Structure

```
~/dotfiles/research/stocks/
├── YYYY-MM/                    # Month folder (e.g., 2025-10/)
│   ├── {STOCK-NAME}/          # Stock-specific folder (e.g., AMD/, NVDA/)
│   │   ├── {type}_YYYY-MM-DD.md           # Research report
│   │   ├── swing-trading-analysis_YYYY-MM-DD.md
│   │   ├── fundamentals-deep-dive_YYYY-MM-DD.md
│   │   └── catalyst-tracker_YYYY-MM-DD.md
│   └── {SECTOR-NAME}/         # Sector/theme folder (e.g., AI-chips-hidden-gems/)
│       └── {type}_YYYY-MM-DD.md
├── archive/                   # Older research (>3 months)
│   └── YYYY-MM/
├── templates/                 # Report templates
│   ├── fundamental-analysis-template.md
│   ├── swing-trading-template.md
│   └── comprehensive-research-template.md
└── README.md                  # Directory structure explanation
```

### Naming Conventions

**File Names:**
- Format: `{analysis-type}_{YYYY-MM-DD}.md`
- Examples:
  - `comprehensive-research_2025-10-05.md` - Full deep research
  - `swing-trading-analysis_2025-10-05.md` - Technical/entry point analysis
  - `fundamentals-deep-dive_2025-10-05.md` - Financial analysis focus
  - `catalyst-tracker_2025-10-05.md` - News/events tracking
  - `risk-assessment_2025-10-05.md` - Risk-focused analysis

**Directory Names:**
- Stock-specific: Use ticker OR full name in kebab-case (e.g., `AMD/`, `NVIDIA/`, `Meta-Platforms/`)
- Sector/theme: Use descriptive kebab-case (e.g., `AI-chips-hidden-gems/`, `semiconductor-sector/`, `cloud-infrastructure/`)

### File Organization Workflow

**When completing research:**

1. **Determine Current Date**: Use `date +%Y-%m-%d` to get today's date
2. **Create Month Folder** (if doesn't exist):
   ```bash
   mkdir -p ~/dotfiles/research/stocks/$(date +%Y-%m)
   ```
3. **Create Stock/Sector Folder**:
   ```bash
   mkdir -p ~/dotfiles/research/stocks/$(date +%Y-%m)/{STOCK-NAME}
   ```
4. **Save Report** with proper naming:
   ```bash
   # Example for AMD comprehensive research
   ~/dotfiles/research/stocks/2025-10/AMD/comprehensive-research_2025-10-05.md

   # Example for AI chip sector swing trading
   ~/dotfiles/research/stocks/2025-10/AI-chips-hidden-gems/swing-trading-analysis_2025-10-05.md
   ```

### Cross-Referencing Previous Research

**IMPORTANT**: Before starting new research on a stock, CHECK for existing research:

```bash
# List all previous research for a stock
ls -lh ~/dotfiles/research/stocks/*/AMD/

# Find all swing trading analyses
find ~/dotfiles/research/stocks -name "swing-trading-analysis_*.md"

# Search for specific stock across all months
find ~/dotfiles/research/stocks -type d -name "NVDA"
```

**In Report Header**, include reference to previous research if exists:
```markdown
**Previous Research:**
- [AMD Comprehensive Research - Oct 5](../AMD/comprehensive-research_2025-10-05.md)
- [AI Chips Sector Analysis - Sep 28](../../2025-09/AI-chips-sector/sector-overview_2025-09-28.md)
```

### Research Continuity

**When updating existing research:**
- Create NEW file with current date (don't overwrite)
- Add "Update Notes" section referencing previous report
- Keep old reports for historical tracking

**Archive Policy:**
- Move reports >3 months old to `archive/YYYY-MM/` directory
- Keep latest report in main directory for quick access

## Example Usage

```
/deep-stock-research NVDA

→ Executes 6-8 iteration research loop
→ Generates comprehensive report
→ Saves to: ~/dotfiles/research/stocks/2025-10/NVDA/comprehensive-research_2025-10-05.md
→ Checks for previous NVDA research and cross-references if found
```

```
/deep-stock-research LSCC --type=swing-trading

→ Focused swing trading technical analysis
→ Saves to: ~/dotfiles/research/stocks/2025-10/LSCC/swing-trading-analysis_2025-10-05.md
```

```
/deep-stock-research LSCC --type=daily-update

→ Quick daily technical update (single query to Perplexity Finance)
→ Saves to: ~/dotfiles/research/stocks/2025-10/LSCC/daily-update_2025-10-06.md
→ Also creates audit trail: ./raw-data/2025-10-06/ (query, response, metadata)
```

```
/deep-stock-research LSCC,AMBA,BRCHF,GSIT --type=daily-update --portfolio=AI-chips-hidden-gems

→ Daily updates for multiple stocks in a portfolio
→ Creates individual daily updates for each stock (with audit trails)
→ ALSO creates consolidated summary: ~/dotfiles/research/stocks/2025-10/AI-chips-hidden-gems/daily-summary_2025-10-06.md
→ Consolidated summary includes: portfolio overview, action items, priorities, risk warnings
```

## Notes

- **CRITICAL**: Use `comet-devtools` MCP for all browser automation (configured for Comet Browser on port 9223)
- Perplexity Assistant URL: `https://www.perplexity.ai/`
- Track state between iterations in conversation (maintain completeness scores, collected findings)
- Save intermediate findings to avoid data loss if session interrupts
- Take screenshots (`mcp__comet-devtools__take_screenshot`) for debugging if snapshot parsing fails
- Be patient - each Perplexity query takes 30-60 seconds to stream complete response
- **DO NOT use web-search-prime or other search tools** - only Perplexity via browser automation
- **ALWAYS check for previous research** before starting new analysis - reference it in your report
- **Use structured directory** - never save to root dotfiles directory

---

*This command implements a quantifiable, iterative research process with clear completeness metrics, termination criteria, and organized file management for daily research tracking.*
