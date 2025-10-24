---
title: Multi-Timeframe Trading Analysis
description: Orchestrate parallel trading analysis for confluence levels using direct MCP tool access
category: trading
---

# Trading Analysis Command

You orchestrate complete multi-timeframe trading workflows using direct MCP tool access (bypassing Task system limitations).

**Your job**: Take symbol from $ARGUMENTS → deliver synchronized confluence analysis with real market data.

## Critical Architecture Note

**Direct MCP Tool Access Required**: Trading agents require Zen MCP server access which doesn't work through Task system orchestration. Use direct parallel `chat` tool calls instead of Task() invocations.

## Workflow Execution

### Step 0: Get Current Date/Time (ALWAYS DO THIS FIRST)

```bash
date "+%Y-%m-%d %H:%M:%S %Z"
```

Trading analysis requires real-time market data context.

### Step 1: Initialize Analysis Environment

```bash
# Set variables
SYMBOL="${ARGUMENTS:-SPY}"
DATE=$(date +%Y-%m-%d_%H%M%S)
ANALYSIS_DIR="$(pwd)/.claude/analysis/multi-timeframe/$DATE"
mkdir -p "$ANALYSIS_DIR"/{daily,4hour,hourly,confluence}

echo "📊 Starting multi-timeframe analysis for $SYMBOL"
echo "📁 Analysis directory: $ANALYSIS_DIR"
```

### Step 2: Execute Parallel Timeframe Analysis

**CRITICAL**: Launch all timeframe analyses in parallel using direct `chat` tool calls (single message, multiple calls):

```
chat prompt="You are a daily-chart-agent specialist. Analyze $SYMBOL daily chart with current market data as of $(date '+%Y-%m-%d'). Provide: 1) Key support/resistance levels, 2) Trend analysis, 3) Volume profile analysis, 4) Key price targets. Use actual current market data, not hypothetical prices. Base analysis on real market conditions." model="glm-4.5" reasoning_mode="hybrid" > "$ANALYSIS_DIR/daily/$SYMBOL-daily-analysis.md" &

chat prompt="You are a 4hour-chart-agent specialist. Analyze $SYMBOL 4-hour chart for intraday levels with current market data. Focus on: 1) Confluence zones with daily levels, 2) Intraday support/resistance, 3) Momentum patterns, 4) Risk-reward entry zones. Use actual current market data synchronized with daily timeframe." model="glm-4.5" reasoning_mode="hybrid" > "$ANALYSIS_DIR/4hour/$SYMBOL-4hour-analysis.md" &

chat prompt="You are an hourly-chart-agent specialist. Analyze $SYMBOL 1-hour chart for short-term patterns with current market data. Identify: 1) Scalping opportunities, 2) Short-term reversals, 3) Momentum entry points, 4) Alignment with higher timeframes. Use actual current market data." model="glm-4.5" reasoning_mode="hybrid" > "$ANALYSIS_DIR/hourly/$SYMBOL-hourly-analysis.md" &

# Wait for all parallel analyses to complete
wait
```

### Step 3: Verify Fundamental Data (CRITICAL)

```bash
echo "🔍 Verifying current fundamental data for $SYMBOL analysis..."

# Use chat tool with web search capabilities for macroeconomic verification
chat prompt="You are a fundamental data verification specialist. For $SYMBOL analysis, search and verify current macroeconomic data as of $(date '+%Y-%m-%d'):

REQUIRED DATA VERIFICATION:
- Current Fed funds rate and recent policy changes (if applicable)
- Latest CPI/inflation data and trends
- Current interest rate environment and yield curve data
- Recent economic data releases relevant to $SYMBOL
- Any recent policy announcements that could impact markets

For each data point, provide:
1. Current value with date
2. Recent trend/change
3. Source verification
4. Implication for $SYMBOL analysis

This verification ensures our technical analysis is grounded in accurate fundamental context." model="glm-4.5" reasoning_mode="hybrid" > "$ANALYSIS_DIR/fundamental-verification.md"

echo "✅ Fundamental data verification completed"
```

### Step 4: Quality Validation

```bash
# Verify all analyses completed successfully
if [[ ! -f "$ANALYSIS_DIR/daily/$SYMBOL-daily-analysis.md" ]] ||
   [[ ! -f "$ANALYSIS_DIR/4hour/$SYMBOL-4hour-analysis.md" ]] ||
   [[ ! -f "$ANALYSIS_DIR/hourly/$SYMBOL-hourly-analysis.md" ]] ||
   [[ ! -f "$ANALYSIS_DIR/fundamental-verification.md" ]]; then
    echo "❌ Error: One or more analysis components failed"
    exit 1
fi

echo "✅ All timeframe analyses and fundamental verification completed successfully"
```

### Step 5: Confluence Synthesis

```
chat prompt="You are a confluence-agent specialist. Create comprehensive confluence analysis from these synchronized timeframe analyses for $SYMBOL:

FUNDAMENTAL VERIFICATION:
$(cat "$ANALYSIS_DIR/fundamental-verification.md")

DAILY ANALYSIS:
$(cat "$ANALYSIS_DIR/daily/$SYMBOL-daily-analysis.md")

4-HOUR ANALYSIS:
$(cat "$ANALYSIS_DIR/4hour/$SYMBOL-4hour-analysis.md")

1-HOUR ANALYSIS:
$(cat "$ANALYSIS_DIR/hourly/$SYMBOL-hourly-analysis.md")

SYNTHESIS REQUIREMENTS:
1. **Integrate fundamental verification** - Ground technical analysis in verified macro data
2. Identify high-confidence confluence zones (3+ timeframes aligned)
3. Highlight medium-confidence zones (2 timeframes aligned)
4. Provide risk-reward scenarios for each key level
5. Suggest optimal entry strategies based on timeframe alignment and fundamental context
6. Highlight any conflicting signals between timeframes and fundamental data
7. Provide actionable trading plan with specific price levels and fundamental rationale

CRITICAL INTEGRATION:
- Ensure fundamental verification data is incorporated into market assessment
- Cross-reference technical levels with verified macroeconomic context
- Highlight any discrepancies between technical patterns and fundamental drivers
- Adjust trading recommendations based on verified fundamental environment
- Note confidence level adjustments based on fundamental data quality

IMPORTANT: Verify that all timeframes use synchronized price data. If you find price discrepancies, prioritize the most recent data and note any inconsistencies." model="glm-4.5" reasoning_mode="hybrid" > "$ANALYSIS_DIR/confluence/$SYMBOL-confluence-analysis.md"
```

### Step 6: Output Results Summary

```bash
echo "🎯 Multi-timeframe confluence analysis complete!"
echo ""
echo "📊 Results Summary:"
echo "   Daily Analysis:       $ANALYSIS_DIR/daily/$SYMBOL-daily-analysis.md"
echo "   4-Hour Analysis:      $ANALYSIS_DIR/4hour/$SYMBOL-4hour-analysis.md"
echo "   1-Hour Analysis:      $ANALYSIS_DIR/hourly/$SYMBOL-hourly-analysis.md"
echo "   Fundamental Verify:   $ANALYSIS_DIR/fundamental-verification.md"
echo "   Confluence:           $ANALYSIS_DIR/confluence/$SYMBOL-confluence-analysis.md"
echo ""
echo "📈 Quick confluence preview:"
echo "---"
head -20 "$ANALYSIS_DIR/confluence/$SYMBOL-confluence-analysis.md"
echo "---"
echo "📁 Full analysis available in: $ANALYSIS_DIR/"
```

## Usage Examples

```bash
/trading-analysis              # Default SPY analysis
/trading-analysis SPY          # SPY multi-timeframe analysis
/trading-analysis QQQ          # QQQ analysis
/trading-analysis AAPL         # Apple analysis
```

## Technical Architecture

- **Direct MCP Access**: Bypasses Task system limitations
- **GLM-4.5 Optimization**: Leverages 90.6% tool calling success rate
- **Parallel Execution**: All timeframes analyzed simultaneously
- **Data Synchronization**: Uses real market data from GLM-4.5
- **Hot Configuration**: Edit this file for immediate workflow changes