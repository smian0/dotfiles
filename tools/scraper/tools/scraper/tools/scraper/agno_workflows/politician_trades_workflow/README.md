# Politician Trades Workflow

Automated congressional stock trading intelligence using Perplexity Finance and Agno workflows.

## Overview

This workflow analyzes politician stock trades to identify potential trading signals based on committee assignments and insider knowledge. It:

1. **Extracts Recent Trades**: Scrapes Perplexity Finance politicians page for latest congressional stock transactions
2. **Looks Up Committees**: Queries committee assignments for politicians who made significant trades
3. **Synthesizes Intelligence**: Connects trades to committee jurisdiction to identify actionable trading opportunities

## Features

- 🏛️ **Congressional Trade Tracking**: Automated extraction of politician stock transactions
- 🔍 **Committee Analysis**: Maps trades to congressional committee power and jurisdiction
- 📊 **Sector Intelligence**: Identifies which sectors are being favored/avoided by insiders
- 🎯 **Actionable Insights**: Generates trading recommendations based on political positioning
- 📝 **Comprehensive Reports**: Markdown-formatted analysis with executive summaries

## Installation

Requires the scraper_agent.py to be available at:
```
../../../scraper_agent.py
```

Dependencies are managed via uv script metadata (automatically handled).

## Usage

### Full Analysis

Run complete workflow (trades + committees + synthesis):

```bash
./workflow.py analyze
```

Save report to file:

```bash
./workflow.py analyze --output reports/politician_trades_$(date +%Y%m%d).md
```

### Committee Lookup

Look up committees for a specific politician:

```bash
./workflow.py committee "Donald S. Beyer Jr."
```

Save to custom file:

```bash
./workflow.py committee "Marjorie Taylor Greene" --output reports/greene_committees.json
```

### Quick Screenshot

Capture politicians page without analysis:

```bash
./workflow.py quick
```

## Example Use Cases

### Strategy 1: Committee Front-Running

**Goal**: Identify trades by politicians on relevant committees before policy announcements

**Example**:
```bash
# Beyer (Ways & Means Committee) buys GDXJ (gold miners)
# → Ways & Means handles trade policy
# → Watch for trade policy affecting precious metals
./workflow.py committee "Donald S. Beyer Jr."
```

### Strategy 2: Sector Trend Detection

**Goal**: Spot which sectors multiple politicians are entering/exiting

**Example**:
```bash
# Full analysis shows multiple politicians buying tech
# → Early signal of favorable tech regulation
./workflow.py analyze --output reports/tech_sector_$(date +%Y%m%d).md
```

### Strategy 3: Risk Detection

**Goal**: Identify sectors being exited by informed insiders

**Example**:
```bash
# Politicians on banking committees selling financials
# → Warning signal for banking sector
./workflow.py analyze
```

## Workflow Architecture

### Step 1: Extract Recent Trades

- **URL**: `https://www.perplexity.ai/finance/politicians`
- **Method**: Scraper agent with structured JSON extraction
- **Output**: Politician name, ticker, buy/sell, amount, date
- **File**: `/tmp/politician_trades.json`

### Step 2: Lookup Committee Assignments

- **Politicians Analyzed**: Beyer, McClain Delaney, Greene (customizable)
- **Query**: "Which congressional committees is {politician} on?"
- **Output**: Committee names and jurisdictions
- **Files**: `/tmp/{politician}_committees.json`

### Step 3: Synthesize Trading Intelligence

- **Agent**: GLM-4.6 (198K context)
- **Analysis**:
  - Trade patterns and correlations
  - Committee jurisdiction mapping
  - Sector implications
  - Actionable trading insights
  - Risk assessment

## Output Format

### Full Report Structure

```markdown
# Executive Summary
- Key findings
- Most significant trades
- Recommended actions

# Key Trades Analysis
- Politician: Trade details
- Transaction type and size
- Timing considerations

# Committee Jurisdiction Mapping
- Politician → Committees → Jurisdiction
- Correlation to recent trades
- Policy implications

# Sector Implications
- Which sectors are favored
- Which sectors are being exited
- Timing indicators

# Actionable Trading Insights
- Specific ticker recommendations
- Entry/exit strategies
- Risk/reward assessment

# Risk Assessment
- Are these early signals or late?
- Regulatory risk factors
- Market timing considerations
```

## Configuration

### Customizing Politicians

Edit the `lookup_committee_assignments()` function in workflow.py:

```python
politicians = [
    "Donald S. Beyer Jr.",
    "April McClain Delaney",
    "Marjorie Taylor Greene",
    # Add more politicians here
]
```

### Adjusting Timeouts

Scraper commands have 120s timeout. Adjust if needed:

```python
timeout=120,  # Increase for slower networks
```

### Model Configuration

Synthesis uses GLM-4.6 with full 198K context:

```python
model=Ollama(
    id="glm-4.6:cloud",
    options={"num_ctx": 198000}
)
```

Change model for different analysis styles.

## Real-World Example

From our testing, Donald S. Beyer Jr. (Ways & Means Committee, Trade Subcommittee) bought GDXJ (gold miners ETF). This correlation between his committee jurisdiction (international trade policy) and the trade (precious metals) suggests:

- **Potential catalyst**: Trade policy changes affecting gold/commodities
- **Action**: Watch GDXJ and gold sector for policy announcements
- **Risk**: Committee membership doesn't guarantee insider knowledge

## Limitations

- **Not financial advice**: Correlation ≠ causation
- **Timing uncertainty**: Trades are reported with delay (45-day disclosure)
- **Scraping reliability**: Dependent on Perplexity page structure
- **Committee changes**: Politicians may join/leave committees

## Troubleshooting

### Timeout Errors

Increase timeout in scrape commands:
```python
timeout=180,  # 3 minutes instead of 2
```

### Empty Extractions

Check scraper_agent.py is working:
```bash
../../../scraper_agent.py screenshot https://www.perplexity.ai/finance/politicians -o test.png
```

### BlockingIOError

Ensure scraper_agent.py has the TTY detection fix (lines 234-244).

## Directory Structure

```
politician_trades_workflow/
├── workflow.py           # Main workflow script
├── README.md             # This file
└── reports/              # Output directory for saved reports
    └── (generated reports saved here)
```

## Credits

Built with:
- **Agno**: AI agent workflow framework
- **Comet Browser**: Perplexity's Chromium with remote debugging
- **Chrome DevTools MCP**: Browser automation via Model Context Protocol
- **GLM-4.6**: Synthesis and analysis model

---

**Last Updated**: 2025-11-11

**Disclaimer**: This tool is for educational and research purposes. Always verify trades through official congressional disclosure databases (STOCK Act reports). Do not use as sole basis for investment decisions.
