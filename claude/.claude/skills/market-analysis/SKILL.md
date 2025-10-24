---
name: market-analysis
description: Generate market analysis reports with parameterized types (overview, hidden, sector, technical) using parallel research and grounded citations
tags: [markets, analysis, research, trading]
---

# Market Analysis

Generate professional market analysis reports with 100% grounded citations across multiple report types.

## Available Report Types

- **`overview`** - Daily market overview (stocks, crypto, macro, sentiment)
- **`hidden`** - Hidden opportunities and structural risks (penny stocks, whales, anomalies)
- **`sector`** - Sector rotation analysis (performance, patterns, catalysts)
- **`technical`** - Technical analysis and price action (levels, breakouts, momentum)

See [Report Type Specifications](./references/report-types.md) for detailed angle configurations.

## How to Use

### Step 1: Parse Report Type

Extract `report_type` from the input prompt. Valid types: `overview`, `hidden`, `sector`, `technical`.

If not specified, default to `overview`.

### Step 2: Execute Parallel Research

Launch research agents for all angles in a **single message** (parallel execution).

**For `overview` type** (4 angles):

```
Task(subagent_type="research-web-researcher", description="Stock market overview",
  prompt="Research today's stock market. Find 12+ sources on S&P 500, Nasdaq, Dow, sectors, breadth, movers. Save to market-overview-stocks-$(date +%Y-%m-%d).md")

Task(subagent_type="research-web-researcher", description="Crypto markets",
  prompt="Research crypto. Find 12+ sources on BTC, ETH, altcoins, whale activity, ETF flows. Save to market-overview-crypto-$(date +%Y-%m-%d).md")

Task(subagent_type="research-web-researcher", description="Macro drivers",
  prompt="Research macro. Find 12+ sources on Fed policy, economic data, bond yields, geopolitical events. Save to market-overview-macro-$(date +%Y-%m-%d).md")

Task(subagent_type="research-web-researcher", description="Market sentiment",
  prompt="Research sentiment. Find 12+ sources on VIX, breadth divergences, fund flows, options positioning. Save to market-overview-sentiment-$(date +%Y-%m-%d).md")
```

**For `hidden` type** (6 angles):

```
Task(subagent_type="research-web-researcher", description="Penny stocks",
  prompt="Research unusual penny stock moves. Find 10+ sources on stocks up 50%+, meme rallies, volume spikes. Save to market-hidden-penny-$(date +%Y-%m-%d).md")

Task(subagent_type="research-web-researcher", description="Whale positioning",
  prompt="Research whale activity. Find 10+ sources on crypto whale positions, large shorts/longs, smart money divergence. Save to market-hidden-whales-$(date +%Y-%m-%d).md")

Task(subagent_type="research-web-researcher", description="Market structure",
  prompt="Research structure anomalies. Find 10+ sources on breadth divergences, leadership concentration, small-cap gaps. Save to market-hidden-structure-$(date +%Y-%m-%d).md")

Task(subagent_type="research-web-researcher", description="Emerging markets",
  prompt="Research EM stress. Find 10+ sources on currency depreciation, capital flight, contagion risks. Save to market-hidden-em-$(date +%Y-%m-%d).md")

Task(subagent_type="research-web-researcher", description="Altcoins/DeFi",
  prompt="Research altcoin moves. Find 10+ sources on tokens up 20%+, new listings, whale accumulation. Save to market-hidden-altcoins-$(date +%Y-%m-%d).md")

Task(subagent_type="research-web-researcher", description="Hidden catalysts",
  prompt="Research under-reported news. Find 10+ sources on regulatory impacts, technical breaks, rebalancing. Save to market-hidden-catalysts-$(date +%Y-%m-%d).md")
```

**For `sector` and `technical` types:** See [Report Type Specifications](./references/report-types.md) for angle prompts.

### Step 3: Synthesize Report

After all research completes, create the final report and **output to stdout**:

**IMPORTANT: Output the report directly to stdout, do NOT attempt to write files.**

Create a comprehensive markdown report with:
- Executive summary
- Sections for each research angle (stocks, crypto, macro, sentiment)
- Footnote citations `[^1]`, `[^2]` for ALL factual claims
- References section at bottom: `[^1]: [domain](url): "verbatim quote"`

**Print the entire report to stdout so the caller can redirect it to a file if needed.**

### Step 4: Usage Pattern

When invoking this skill:

```bash
# Direct stdout (for viewing)
oc run --model "..." "Generate market overview report for today"

# Redirect to file (for saving)
oc run --model "..." "Generate market overview report for today" > market-analysis-$(date +%Y-%m-%d).md

# Or save to specific location
cd /Users/smian/dotfiles/docs/plans/
oc run --model "..." "Generate market overview report for today" > market-analysis-$(date +%Y-%m-%d).md
```

## Quality Standards

- ✅ **100% Citation Coverage** - Every claim sourced with URL and verbatim quote
- ✅ **Footnote Format** - `[^1]`, `[^2]` with references section
- ✅ **12+ Sources** per research angle minimum
- ✅ **Parallel Execution** - All research angles run simultaneously
- ✅ **Consistent Structure** - Same quality across all report types

## Usage Examples

Direct invocation:
```
@market-analysis report_type: overview
@market-analysis report_type: hidden
```

From commands:
```bash
/market-overview        # Calls skill with report_type: overview
/under-radar-markets    # Calls skill with report_type: hidden
```

## Adding New Report Types

1. Add angle specifications to `references/report-types.md`
2. Add Task() execution code to Step 2 above
3. Update synthesis instructions in Step 3 if needed
