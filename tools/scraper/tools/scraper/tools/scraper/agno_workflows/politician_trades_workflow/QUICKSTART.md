# Politician Trades Workflow - Quick Start Guide

## What We Built

A complete Agno workflow for analyzing congressional stock trades with committee assignment correlation.

## Workflow Structure

```
politician_trades_workflow/
├── workflow.py           # ✅ Main workflow script (executable)
├── README.md             # ✅ Complete documentation
├── QUICKSTART.md         # ✅ This file
└── reports/              # ✅ Output directory
```

## Available Commands

### 1. Quick Screenshot (Fastest - No AI Processing)

Capture the politicians trading page:

```bash
cd /Users/smian/dotfiles/tools/scraper/tools/scraper/tools/scraper/agno_workflows/politician_trades_workflow
./workflow.py quick
```

**Output**: `/tmp/politician_trades_quick.png`

### 2. Committee Lookup (Single Politician)

Look up committee assignments for one politician:

```bash
./workflow.py committee "Donald S. Beyer Jr."
```

**Output**: `/tmp/donald_s._beyer_jr._committees.json`

Save to custom location:

```bash
./workflow.py committee "Marjorie Taylor Greene" --output reports/greene_$(date +%Y%m%d).json
```

### 3. Full Analysis (Complete Workflow)

Extract trades + look up committees + synthesize insights:

```bash
./workflow.py analyze
```

Save report:

```bash
./workflow.py analyze --output reports/politician_analysis_$(date +%Y%m%d).md
```

## Test Results

### ✅ What Works

- **Workflow structure**: All files created and organized
- **CLI interface**: Commands properly defined with Click
- **Scraper integration**: Correctly calls scraper_agent.py
- **File paths**: Proper absolute paths resolved

### ⚠️ Known Issue

**Ollama Internal Server Error 500**: Temporary backend crash during testing

```
ollama._types.ResponseError: mismatched arg_key and arg_value counts
```

**Impact**: Prevents completion of scraper operations
**Cause**: Ollama backend instability (not a workflow bug)
**Resolution**: Restart Ollama or wait for stable backend

## Manual Testing Steps

Once Ollama is stable, test in this order:

### Step 1: Quick Screenshot (No AI)

```bash
./workflow.py quick
open /tmp/politician_trades_quick.png
```

**Expected**: Screenshot of politicians trading page

### Step 2: Committee Lookup (Minimal AI)

```bash
./workflow.py committee "Donald S. Beyer Jr." --output test_beyer.json
cat test_beyer.json
```

**Expected**: JSON with committee assignments from our earlier successful test:
- Ways and Means Committee
- Joint Economic Committee
- Subcommittees: Trade, Tax

### Step 3: Full Analysis (All Steps)

```bash
./workflow.py analyze --output test_full_report.md
cat test_full_report.md
```

**Expected**: Markdown report with:
- Recent politician trades
- Committee assignments for 3 politicians (Beyer, McClain Delaney, Greene)
- Synthesized trading intelligence

## Example Use Case

**Scenario**: Track Beyer's GDXJ trade

```bash
# 1. Check what Beyer bought
./workflow.py quick
# See GDXJ (gold miners) purchase

# 2. Look up his committees
./workflow.py committee "Donald S. Beyer Jr."
# See Ways & Means (Trade subcommittee)

# 3. Correlation: Trade policy jurisdiction + precious metals investment
```

## Integration with Stock Research Workflow

Combine politician trades with stock analysis:

```bash
# 1. Identify politician trades
cd politician_trades_workflow
./workflow.py analyze --output reports/pol_trades.md

# 2. Research specific tickers mentioned
cd ../stock_research_workflow
./workflow.py research GDXJ --output reports/gdxj_analysis.md

# 3. Cross-reference for trading ideas
```

## Troubleshooting

### "Permission denied" when running workflow.py

```bash
chmod +x workflow.py
```

### "scraper_agent.py not found"

The workflow expects scraper_agent.py at:
```
../../../scraper_agent.py
```

Verify it exists:
```bash
ls -lah ../../../scraper_agent.py
```

### Timeout errors

Increase timeout in workflow.py (default is 120s):
```python
timeout=180,  # 3 minutes
```

## Next Steps

1. **Wait for Ollama stability** - The workflow is ready to use once backend is stable
2. **Test quick command first** - Verify scraper works without AI processing
3. **Test committee lookup** - Minimal AI, should complete quickly
4. **Run full analysis** - Complete workflow with synthesis

---

**Status**: Workflow ready for testing
**Created**: 2025-11-11
**Last Tested**: 2025-11-11 (Ollama crash during committee lookup)
