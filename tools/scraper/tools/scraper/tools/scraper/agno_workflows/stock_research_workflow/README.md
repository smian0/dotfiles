# Stock Research Workflow

Automated stock research using Perplexity Finance via your Comet browser scraper agent.

## Overview

This Agno workflow automates the manual stock research process you performed with AAPL:
1. **Navigate** to Perplexity Finance page for any stock ticker
2. **Extract** recent developments and news
3. **Ask** analytical questions to Perplexity
4. **Synthesize** findings into a comprehensive investment report

## Features

- **Repeatable for any stock**: Just provide a ticker symbol (AAPL, TSLA, NVDA, etc.)
- **Two modes**: Full research or quick screenshot
- **Automated questioning**: Asks key analytical questions automatically
- **AI synthesis**: GLM-4.6 cloud model synthesizes findings into professional report
- **File export**: Save reports to markdown files

## Installation

Dependencies are managed automatically by `uv`. The workflow requires:
- Python 3.12+
- Agno framework (from local installation)
- Your scraper_agent.py (Comet browser integration)

## Usage

### Full Research (Recommended)

Run complete research with developments + Q&A + synthesis:

```bash
# Basic research
./workflow.py research AAPL

# Save report to file
./workflow.py research TSLA --output tsla_report.md
./workflow.py research NVDA -o nvda_analysis.md
```

**What happens:**
1. Screenshots Perplexity Finance page for the ticker
2. Asks 3 analytical questions:
   - Is there an obvious buy signal?
   - What are the key risks and opportunities?
   - How does current valuation compare to historical averages?
3. Synthesizes all findings into comprehensive report with:
   - Executive Summary
   - Recent Developments Analysis
   - Key Findings from Q&A
   - Investment Thesis
   - Risk Assessment
   - Buy/Hold/Sell Recommendation

**Execution time:** ~5-10 minutes (depending on Perplexity response times)

### Quick Mode

Capture screenshot only (no questions, no synthesis):

```bash
./workflow.py quick AAPL
```

**What happens:**
- Takes screenshot of Perplexity Finance page
- Saves to `/tmp/perplexity_<ticker>_quick.png`
- Displays URL for manual viewing

**Execution time:** ~30-60 seconds

### Help

```bash
# Main help
./workflow.py --help

# Command-specific help
./workflow.py research --help
./workflow.py quick --help
```

## Architecture

### Workflow Steps

**Step 1: Fetch Recent Developments** (Custom Executor)
- Calls `scraper_agent.py screenshot` command
- Navigates to `https://www.perplexity.ai/finance/<TICKER>`
- Captures page screenshot

**Step 2: Query Analytical Insights** (Custom Executor)
- Calls `scraper_agent.py scrape` command for each question
- Interacts with Perplexity's finance Q&A interface
- Extracts responses as JSON

**Step 3: Synthesize Research Report** (Agent)
- GLM-4.6 cloud model (198K context window)
- Reviews all gathered data
- Generates professional investment report

### Integration with Scraper Agent

The workflow calls your existing `scraper_agent.py`:

```python
# Screenshot command
scraper_agent.py screenshot https://www.perplexity.ai/finance/AAPL -o /tmp/aapl.png

# Scrape command with Q&A
scraper_agent.py scrape https://www.perplexity.ai/finance/AAPL \
  --prompt "Find the search box, type 'Is there a buy signal?' and extract response" \
  -o /tmp/aapl_analysis.json
```

**No modifications needed** to your scraper agent - it works as-is!

## Example Output

```markdown
# AAPL - Investment Research Report

## Executive Summary
Apple Inc. (AAPL) demonstrates strong fundamentals with...

## Recent Developments
- Q4 earnings beat expectations
- New AI features announced
- Services revenue growth accelerating

## Perplexity Analysis

### Buy Signal Assessment
✅ Multiple technical indicators suggest...

### Risk/Opportunity Analysis
Key opportunities:
- AI integration in iOS 18
- Services margin expansion
- India market growth

Key risks:
- Regulatory pressure in EU
- iPhone sales plateau
- China competition

### Valuation Analysis
Current P/E: 28.5x
Historical average: 24.2x
Assessment: Moderately expensive but justified by...

## Investment Thesis
Strong buy for long-term investors based on...

## Risk Assessment
Risk Score: Moderate (6/10)

## Recommendation
**BUY** - Price target: $XXX
Hold period: 12-18 months
```

## Customization

### Modify Questions

Edit `query_perplexity_analysis()` function in `workflow.py`:

```python
questions = [
    "Your custom question 1?",
    "Your custom question 2?",
    "Your custom question 3?",
]
```

### Change Synthesis Model

Edit the `synthesizer` agent configuration:

```python
synthesizer = Agent(
    model=Ollama(
        id="gpt-oss:120b-cloud",  # Use different model
        options={"num_ctx": 120000}
    ),
    # ... rest of config
)
```

### Adjust Timeouts

```python
# In fetch_stock_developments():
timeout=60,  # Screenshot timeout (seconds)

# In query_perplexity_analysis():
timeout=120,  # Q&A timeout (seconds)
```

## Troubleshooting

### "scraper_agent.py not found"

The workflow expects scraper_agent.py at:
```
tools/scraper/tools/scraper/tools/scraper/scraper_agent.py
```

If different location, update `SCRAPER_AGENT` constant in workflow.py.

### "Comet is not running"

Start Comet browser before running workflow:
```bash
# Your scraper agent handles this automatically
# But if issues, manually start Comet:
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9223
```

### "Question timeout"

Perplexity may take longer to respond. Increase timeout:
```python
timeout=180,  # Increase from 120s to 180s
```

### Workflow takes too long

Use quick mode for faster results:
```bash
./workflow.py quick AAPL
```

Or reduce number of questions in `query_perplexity_analysis()`.

## File Locations

```
agno_workflows/stock_research_workflow/
├── workflow.py              # Main workflow script
├── README.md               # This file
└── reports/                # Output reports (auto-created)
    ├── tsla_report.md
    └── nvda_analysis.md

/tmp/
├── perplexity_aapl_developments.png    # Screenshots
├── aapl_analysis_1.json                # Q&A responses
├── aapl_analysis_2.json
└── aapl_analysis_3.json
```

## Examples

### Research multiple stocks

```bash
for ticker in AAPL MSFT GOOGL TSLA; do
    ./workflow.py research $ticker -o "reports/${ticker}_$(date +%Y%m%d).md"
done
```

### Quick comparison

```bash
./workflow.py quick AAPL
./workflow.py quick TSLA
open /tmp/perplexity_aapl_quick.png /tmp/perplexity_tsla_quick.png
```

### Monitor a watchlist

```bash
# Create watchlist file
echo -e "AAPL\nTSLA\nNVDA" > watchlist.txt

# Research all tickers
while read ticker; do
    echo "Researching $ticker..."
    ./workflow.py research $ticker -o "reports/${ticker}_daily.md"
done < watchlist.txt
```

## Technical Details

**Dependencies:**
- agno (local editable install from github-smian0/agno-ck)
- click (CLI framework)
- ollama (model provider)
- fastapi, sqlalchemy (required by agno)

**Models used:**
- GLM-4.6 cloud (198K context) for synthesis
- Qwen3 VL (via scraper agent) for screenshot analysis

**Execution flow:**
1. Parse ticker from command
2. Execute Step 1 (screenshot)
3. Execute Step 2 (Q&A loop)
4. Execute Step 3 (AI synthesis)
5. Display and optionally save report

## Next Steps

1. **Add more questions**: Edit `questions` list in `query_perplexity_analysis()`
2. **Customize report format**: Modify synthesizer instructions
3. **Integrate with other tools**: Use workflow output in trading system
4. **Add caching**: Cache Perplexity responses to avoid re-fetching
5. **Parallel research**: Research multiple stocks concurrently

## Credits

Built with:
- **Agno Framework**: Multi-agent workflow orchestration
- **Your Scraper Agent**: Comet browser automation
- **Perplexity Finance**: Real-time stock data and AI analysis

Last Updated: 2025-11-11
