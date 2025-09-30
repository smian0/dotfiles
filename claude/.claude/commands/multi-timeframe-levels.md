---
name: multi-timeframe-levels
description: Analyzes support/resistance levels across daily, 4-hour, and 1-hour timeframes to find high-confidence trading zones where multiple timeframes agree
tools: Task, TodoWrite, Read, Write, Bash
---

# Multi-Timeframe Technical Analysis Command

Perform comprehensive technical analysis across three timeframes (daily, 4-hour, 1-hour) to identify high-probability support and resistance levels where multiple timeframes show confluence.

## Usage

```bash
# Analyze a single ticker
/multi-timeframe-levels SPY

# Analyze multiple tickers
/multi-timeframe-levels SPY QQQ IWM

# With output directory specification
/multi-timeframe-levels SPY --output-dir=/path/to/analysis
```

## What This Command Does

1. **Spawns 3 timeframe analysis agents in parallel** (60 seconds):
   - `daily-chart-agent`: Daily timeframe for swing trading levels
   - `4hour-chart-agent`: 4-hour timeframe for intraday momentum
   - `hourly-chart-agent`: 1-hour timeframe for scalping levels

2. **Synthesizes results** (15 seconds):
   - `confluence-agent`: Identifies where all 3 timeframes agree
   - Creates unified analysis with confluence scores
   - Provides trading strategies for each level

3. **Produces actionable report**:
   - High-confidence support/resistance zones
   - Tier ratings (⭐⭐⭐⭐⭐ = maximum confluence)
   - Entry/exit strategies for different trading styles
   - Risk/reward ratios

**Total Time**: ~75 seconds per ticker

## Command Implementation

When invoked, follow this orchestration workflow:

### Phase 1: Initialization (5-10 seconds)

#### Step 1.1: Parse Input and Validate

Extract ticker symbols from user input:
```
Input: "/multi-timeframe-levels SPY QQQ IWM"
Tickers: ["SPY", "QQQ", "IWM"]
```

**Validation Rules**:
- Ticker symbols must be 1-5 uppercase letters
- Remove duplicates
- Maximum 10 tickers per command (performance limit)
- If no tickers provided, show usage help

**Pre-flight Checks**:
```bash
# Validate ticker format
for ticker in $TICKERS; do
  if ! echo "$ticker" | grep -qE '^[A-Z]{1,5}$'; then
    echo "❌ ERROR: Invalid ticker format: $ticker"
    echo "   Tickers must be 1-5 uppercase letters (e.g., SPY, QQQ, AAPL)"
    exit 1
  fi
done

# Check agent files exist
REQUIRED_AGENTS=("daily-chart-agent" "4hour-chart-agent" "hourly-chart-agent" "confluence-agent")
for agent in "${REQUIRED_AGENTS[@]}"; do
  if [ ! -f "$CLAUDE_DIR/agents/trading/$agent.md" ]; then
    echo "❌ ERROR: Required agent not found: $agent"
    exit 1
  fi
done
```

#### Step 1.2: Setup Output Directory

```bash
# Default output directory
OUTPUT_DIR="${OUTPUT_DIR:-.claude/analysis/multi-timeframe}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create directory structure
mkdir -p "$OUTPUT_DIR/$TIMESTAMP"/{daily,4hour,hourly,confluence}

# Track all output paths
ANALYSIS_MANIFEST="$OUTPUT_DIR/$TIMESTAMP/manifest.txt"
touch "$ANALYSIS_MANIFEST"
```

#### Step 1.3: Initialize TodoWrite

```markdown
TodoWrite([
  {"content": "Validate tickers and setup workspace (~5s)", "status": "in_progress", "activeForm": "Validating tickers"},
  {"content": "Spawn parallel timeframe analysis agents (~60s)", "status": "pending", "activeForm": "Spawning timeframe agents"},
  {"content": "Synthesize confluence analysis (~15s)", "status": "pending", "activeForm": "Synthesizing confluence"},
  {"content": "Generate summary report (~5s)", "status": "pending", "activeForm": "Generating summary"},
  {"content": "Archive results and display paths (~5s)", "status": "pending", "activeForm": "Archiving results"}
])
```

**Mark Step 1.3 complete** after setup.

### Phase 2: Parallel Timeframe Analysis (60 seconds)

For each ticker, spawn 3 analysis agents **in parallel**:

#### Step 2.1: Spawn Daily Chart Agent

```
Task(
  subagent_type="daily-chart-agent",
  description="Analyze daily timeframe for {TICKER}",
  prompt="
You are analyzing {TICKER} on the DAILY timeframe for swing trading levels.

**Your task**:
1. Use mcp__zen__chat with grounded search to get daily chart data for {TICKER}
2. Identify key support and resistance levels (TIER 1-5)
3. Analyze major moving averages (20-day, 50-day, 200-day)
4. Assess overall trend and momentum
5. Output your analysis to: {OUTPUT_DIR}/{TIMESTAMP}/daily/{TICKER}-daily.md

**Time budget**: 45-60 seconds

**Output file**: {OUTPUT_DIR}/{TIMESTAMP}/daily/{TICKER}-daily.md

Follow your agent instructions exactly. Focus on swing trading relevance (multi-day to multi-week holds).
  "
)
```

#### Step 2.2: Spawn 4-Hour Chart Agent

```
Task(
  subagent_type="4hour-chart-agent",
  description="Analyze 4-hour timeframe for {TICKER}",
  prompt="
You are analyzing {TICKER} on the 4-HOUR timeframe for intraday momentum and day trading levels.

**Your task**:
1. Use mcp__zen__chat with grounded search to get 4-hour chart data for {TICKER}
2. Identify intraday support and resistance levels (TIER 1-5)
3. Analyze 20 and 50-period moving averages (4-hour bars)
4. Assess session-based patterns (Asia, Europe, US sessions)
5. Output your analysis to: {OUTPUT_DIR}/{TIMESTAMP}/4hour/{TICKER}-4hour.md

**Time budget**: 45-60 seconds

**Output file**: {OUTPUT_DIR}/{TIMESTAMP}/4hour/{TICKER}-4hour.md

Follow your agent instructions exactly. Focus on day trading relevance (intraday to 2-3 day holds).
  "
)
```

#### Step 2.3: Spawn Hourly Chart Agent

```
Task(
  subagent_type="hourly-chart-agent",
  description="Analyze 1-hour timeframe for {TICKER}",
  prompt="
You are analyzing {TICKER} on the 1-HOUR timeframe for scalping levels and short-term trading.

**Your task**:
1. Use mcp__zen__chat with grounded search to get 1-hour chart data for {TICKER}
2. Identify immediate support and resistance levels (TIER 1-5)
3. Analyze 20 and 50-period moving averages (1-hour bars)
4. Assess opening range and VWAP
5. Output your analysis to: {OUTPUT_DIR}/{TIMESTAMP}/hourly/{TICKER}-hourly.md

**Time budget**: 30-45 seconds

**Output file**: {OUTPUT_DIR}/{TIMESTAMP}/hourly/{TICKER}-hourly.md

Follow your agent instructions exactly. Focus on scalping relevance (minutes to hours holds).
  "
)
```

**CRITICAL**: All 3 agents must spawn **in the same message** using multiple Task calls to achieve parallelism.

**Mark Step 2 complete** after all agents return.

### Phase 3: Confluence Synthesis (15 seconds)

#### Step 3.1: Spawn Confluence Agent

After all 3 timeframe agents complete, spawn the confluence agent:

```
Task(
  subagent_type="confluence-agent",
  description="Synthesize multi-timeframe analysis for {TICKER}",
  prompt="
You are synthesizing multi-timeframe technical analysis for {TICKER}.

**Input files to read**:
- Daily analysis: {OUTPUT_DIR}/{TIMESTAMP}/daily/{TICKER}-daily.md
- 4-Hour analysis: {OUTPUT_DIR}/{TIMESTAMP}/4hour/{TICKER}-4hour.md
- 1-Hour analysis: {OUTPUT_DIR}/{TIMESTAMP}/hourly/{TICKER}-hourly.md

**Your task**:
1. Read all three timeframe analysis files
2. Extract all support and resistance levels from each timeframe
3. Identify confluence zones where 2+ timeframes agree (within $1 or 0.5%)
4. Calculate confluence scores (MAXIMUM/STRONG/MODERATE/WEAK/LOW)
5. Provide trading strategies for each confluence zone
6. Output synthesis to: {OUTPUT_DIR}/{TIMESTAMP}/confluence/{TICKER}-confluence.md

**Time budget**: 45-60 seconds

**Output file**: {OUTPUT_DIR}/{TIMESTAMP}/confluence/{TICKER}-confluence.md

Follow your agent instructions exactly. Focus on identifying high-probability levels where timeframes align.
  "
)
```

**Mark Step 3 complete** after confluence agent returns.

### Phase 4: Summary Report Generation (5 seconds)

#### Step 4.1: Create Executive Summary

Generate a quick-reference summary for the user:

```markdown
# Multi-Timeframe Analysis Summary - {TICKER}

**Analysis Timestamp**: {TIMESTAMP}
**Timeframes Analyzed**: Daily, 4-Hour, 1-Hour

## Quick Reference

| Confluence Level | Price | Type | Score | Distance |
|------------------|-------|------|-------|----------|
| MAXIMUM ⭐⭐⭐⭐⭐ | $XXX.XX | Resistance | 95 | +2.5% |
| STRONG ⭐⭐⭐⭐ | $XXX.XX | Support | 82 | -1.8% |
| ... | ... | ... | ... | ... |

## Next Steps

1. **Review full analysis**: See `{TICKER}-confluence.md` for detailed trading strategies
2. **Check individual timeframes**:
   - Daily: `{TICKER}-daily.md` (swing trading context)
   - 4-Hour: `{TICKER}-4hour.md` (intraday momentum)
   - 1-Hour: `{TICKER}-hourly.md` (scalping levels)
3. **Validate levels**: Cross-reference with your own charts
4. **Plan trades**: Use confluence zones for entries/exits

## Files Generated

- Daily Analysis: {OUTPUT_DIR}/{TIMESTAMP}/daily/{TICKER}-daily.md
- 4-Hour Analysis: {OUTPUT_DIR}/{TIMESTAMP}/4hour/{TICKER}-4hour.md
- 1-Hour Analysis: {OUTPUT_DIR}/{TIMESTAMP}/hourly/{TICKER}-hourly.md
- Confluence Synthesis: {OUTPUT_DIR}/{TIMESTAMP}/confluence/{TICKER}-confluence.md
- This Summary: {OUTPUT_DIR}/{TIMESTAMP}/{TICKER}-SUMMARY.md
```

Write this summary to: `{OUTPUT_DIR}/{TIMESTAMP}/{TICKER}-SUMMARY.md`

#### Step 4.2: Update Manifest

```bash
# Add to manifest
echo "{TICKER}: {OUTPUT_DIR}/{TIMESTAMP}/{TICKER}-SUMMARY.md" >> "$ANALYSIS_MANIFEST"
```

**Mark Step 4 complete**.

### Phase 5: Archiving and Display (5 seconds)

#### Step 5.1: Validate Output Files

```bash
# Check all expected files were created
EXPECTED_FILES=(
  "$OUTPUT_DIR/$TIMESTAMP/daily/{TICKER}-daily.md"
  "$OUTPUT_DIR/$TIMESTAMP/4hour/{TICKER}-4hour.md"
  "$OUTPUT_DIR/$TIMESTAMP/hourly/{TICKER}-hourly.md"
  "$OUTPUT_DIR/$TIMESTAMP/confluence/{TICKER}-confluence.md"
  "$OUTPUT_DIR/$TIMESTAMP/{TICKER}-SUMMARY.md"
)

MISSING_FILES=0
for file in "${EXPECTED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "⚠️  WARNING: Expected file not created: $file"
    MISSING_FILES=$((MISSING_FILES + 1))
  fi
done

if [ "$MISSING_FILES" -gt 0 ]; then
  echo "❌ Analysis incomplete: $MISSING_FILES file(s) missing"
  echo "   Check agent logs for errors"
fi
```

#### Step 5.2: Display Results to User

```markdown
✅ **Multi-Timeframe Analysis Complete for {TICKER}**

📊 **Analysis Summary**: `{OUTPUT_DIR}/{TIMESTAMP}/{TICKER}-SUMMARY.md`

📁 **Detailed Reports**:
- **Confluence Analysis**: `{OUTPUT_DIR}/{TIMESTAMP}/confluence/{TICKER}-confluence.md` ⭐ START HERE
- **Daily Chart**: `{OUTPUT_DIR}/{TIMESTAMP}/daily/{TICKER}-daily.md`
- **4-Hour Chart**: `{OUTPUT_DIR}/{TIMESTAMP}/4hour/{TICKER}-4hour.md`
- **1-Hour Chart**: `{OUTPUT_DIR}/{TIMESTAMP}/hourly/{TICKER}-hourly.md`

💡 **Recommended Reading Order**:
1. Start with confluence analysis for high-probability levels
2. Drill into specific timeframes based on your trading style:
   - Swing trading → Daily chart
   - Day trading → 4-Hour chart
   - Scalping → 1-Hour chart

⏱️ **Analysis Time**: ~75 seconds
```

**Mark Step 5 complete**.

## Multi-Ticker Workflow

If multiple tickers provided (e.g., `/multi-timeframe-levels SPY QQQ IWM`):

1. **Process tickers sequentially** (not in parallel):
   - Reason: Each ticker spawns 3 parallel agents = 3 concurrent tasks
   - Running multiple tickers in parallel = 3N concurrent tasks (too many)
   - Sequential processing keeps parallelism manageable

2. **Create separate output directories per ticker**:
   ```
   .claude/analysis/multi-timeframe/20250930_143022/
   ├── SPY/
   │   ├── daily/
   │   ├── 4hour/
   │   ├── hourly/
   │   ├── confluence/
   │   └── SPY-SUMMARY.md
   ├── QQQ/
   │   └── ...
   └── manifest.txt
   ```

3. **Update progress for each ticker**:
   ```
   ✅ SPY analysis complete (75s)
   🔄 Analyzing QQQ... (2/3)
   ⏳ IWM pending (3/3)
   ```

4. **Final summary across all tickers**:
   ```markdown
   ## Multi-Ticker Analysis Complete

   Analyzed: SPY, QQQ, IWM
   Total time: 225 seconds (~3.75 minutes)

   **Quick Access**:
   - SPY: {OUTPUT_DIR}/{TIMESTAMP}/SPY/SPY-SUMMARY.md
   - QQQ: {OUTPUT_DIR}/{TIMESTAMP}/QQQ/QQQ-SUMMARY.md
   - IWM: {OUTPUT_DIR}/{TIMESTAMP}/IWM/IWM-SUMMARY.md

   **Manifest**: {OUTPUT_DIR}/{TIMESTAMP}/manifest.txt
   ```

## Error Handling

### Pre-flight Errors

**Invalid ticker format**:
```bash
if [[ ! "$TICKER" =~ ^[A-Z]{1,5}$ ]]; then
  echo "❌ ERROR: Invalid ticker '$TICKER'"
  echo "   Expected: 1-5 uppercase letters (e.g., SPY, AAPL, TSLA)"
  exit 1
fi
```

**Too many tickers**:
```bash
if [ "${#TICKERS[@]}" -gt 10 ]; then
  echo "❌ ERROR: Too many tickers (${#TICKERS[@]})"
  echo "   Maximum: 10 tickers per command"
  echo "   Suggestion: Split into multiple commands"
  exit 1
fi
```

**Missing agents**:
```bash
for agent in daily-chart-agent 4hour-chart-agent hourly-chart-agent confluence-agent; do
  if [ ! -f "$CLAUDE_DIR/agents/trading/$agent.md" ]; then
    echo "❌ ERROR: Required agent missing: $agent"
    echo "   Expected: $CLAUDE_DIR/agents/trading/$agent.md"
    exit 1
  fi
done
```

### In-flight Errors

**Agent timeout** (if agent takes >90 seconds):
```
⚠️  WARNING: {agent} for {TICKER} exceeded time budget (>90s)
   Continuing with available data...
```

**Agent failure** (if Task returns error):
```
❌ ERROR: {agent} failed for {TICKER}
   Error: {error_message}
   Skipping {TICKER} analysis
```

**Partial failure** (if 1-2 agents succeed but not all):
```
⚠️  WARNING: Only {N}/3 timeframe agents completed for {TICKER}
   Proceeding with partial analysis (confluence may be limited)
```

### Post-flight Errors

**Missing output files**:
```bash
if [ ! -f "$OUTPUT_DIR/$TIMESTAMP/confluence/{TICKER}-confluence.md" ]; then
  echo "❌ ERROR: Confluence analysis not generated for {TICKER}"
  echo "   Check if all 3 timeframe agents completed successfully"
  echo "   Available files:"
  ls -la "$OUTPUT_DIR/$TIMESTAMP/"*"/{TICKER}"*
fi
```

**File system errors**:
```bash
if [ ! -w "$OUTPUT_DIR" ]; then
  echo "❌ ERROR: Cannot write to output directory: $OUTPUT_DIR"
  echo "   Check permissions: ls -la $(dirname $OUTPUT_DIR)"
  exit 1
fi
```

## Performance Benchmarks

| Tickers | Parallel Agents | Total Time | Breakdown |
|---------|-----------------|------------|-----------|
| 1 | 3 | ~75s | 5s init + 60s parallel + 15s synthesis + 5s archive |
| 3 | 3 (per ticker) | ~225s | 5s + (3 × 75s) |
| 5 | 3 (per ticker) | ~375s | 5s + (5 × 75s) |
| 10 | 3 (per ticker) | ~750s | 5s + (10 × 75s) |

**vs. Sequential (no parallelism)**:
- 1 ticker: 180s (2.4x slower)
- 3 tickers: 540s (2.4x slower)

## Key Principles

1. **Parallel Execution**: All 3 timeframe agents spawn simultaneously per ticker
2. **Sequential Tickers**: Process tickers one at a time to avoid overwhelming system
3. **Fail-Fast**: Validate inputs before spawning expensive agents
4. **Graceful Degradation**: Continue with partial results if 1-2 agents fail
5. **Clear Communication**: Show progress, timings, file paths throughout
6. **Confluence Priority**: Emphasize confluence analysis as primary output
7. **Time Budget Awareness**: All agents have 30-60s budgets, total ~75s per ticker

## Example Output

```
/multi-timeframe-levels SPY

✅ Validated ticker: SPY
📁 Output directory: .claude/analysis/multi-timeframe/20250930_143022

🔄 Spawning parallel timeframe analysis agents...
   ├─ daily-chart-agent (45-60s)
   ├─ 4hour-chart-agent (45-60s)
   └─ hourly-chart-agent (30-45s)

⏱️  Waiting for agents to complete... (est. 60s)

✅ Daily analysis complete (52s)
✅ 4-Hour analysis complete (58s)
✅ 1-Hour analysis complete (41s)

🔄 Synthesizing confluence analysis...
   └─ confluence-agent (45-60s)

✅ Confluence analysis complete (48s)

📊 Generating summary report...

✅ **Multi-Timeframe Analysis Complete for SPY**

📊 **Analysis Summary**: .claude/analysis/multi-timeframe/20250930_143022/SPY-SUMMARY.md

📁 **Detailed Reports**:
- **Confluence Analysis**: .claude/analysis/multi-timeframe/20250930_143022/confluence/SPY-confluence.md ⭐ START HERE
- **Daily Chart**: .claude/analysis/multi-timeframe/20250930_143022/daily/SPY-daily.md
- **4-Hour Chart**: .claude/analysis/multi-timeframe/20250930_143022/4hour/SPY-4hour.md
- **1-Hour Chart**: .claude/analysis/multi-timeframe/20250930_143022/hourly/SPY-hourly.md

⏱️ **Total Analysis Time**: 73 seconds
```

## Future Enhancements

Potential improvements (not implemented yet):
- **Caching**: Cache recent analyses (< 1 hour old) to avoid re-analysis
- **Real-time updates**: Subscribe to price updates and re-run when levels tested
- **Backtesting**: Validate confluence zones against historical price action
- **Alerts**: Set alerts when price approaches confluence zones
- **Portfolio view**: Analyze entire portfolio at once with correlation matrix
- **Options integration**: Add options Greeks and levels relevant to options traders