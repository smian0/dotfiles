---
description: Multi-turn agentic research loop for comprehensive stock analysis using Perplexity
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
---

### Round 2: Fundamentals Deep Dive
**Perplexity Query**: "Analyze {SYMBOL}'s financial fundamentals in depth: Provide Q3 2025 earnings breakdown by segment, margin trends, balance sheet strength (debt, cash, FCF), and detailed valuation comparison vs top 3 competitors. Is it overvalued or undervalued?"

**Extract**: Detailed financial metrics, competitive positioning
**Updates**: Fundamentals dimension +30-40%

---
---

### Round 4: Technical & Institutional
**Perplexity Query**: "Analyze {SYMBOL}'s technical setup and institutional positioning: Current price action/trend, key support/resistance levels, recent institutional ownership changes from 13F filings, insider buying/selling patterns, short interest trends, and unusual options activity."

**Extract**: Market structure and positioning data
**Updates**: Technical/Sentiment dimension +30-40%

---
---

### Round 6: Forward Outlook
**Perplexity Query**: "Analyze {SYMBOL}'s forward outlook: Consensus analyst projections for next 2-3 years (revenue/EPS growth), total addressable market size and penetration, key strategic initiatives driving growth, and scenario analysis with price targets for bull/base/bear cases."

**Extract**: Growth projections and upside scenarios
**Updates**: Outlook dimension +40-50%

---
---

### Round 8: Final Validation (if needed)
**Perplexity Query**: "Synthesize the investment thesis for {SYMBOL}: What makes this compelling (bull case), what are the key risks (bear case), and what is the balanced risk/reward assessment? Include confidence level based on data quality."

**Extract**: Investment thesis validation, holistic view
**Updates**: Final completeness check across all dimensions

---
---

*This command implements a quantifiable, iterative research process with clear completeness metrics, termination criteria, and organized file management for daily research tracking.*
