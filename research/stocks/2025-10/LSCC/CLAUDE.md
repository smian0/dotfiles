# CLAUDE.md - LSCC Stock-Specific Notes

**For general workflow instructions, see:** [../../../CLAUDE.md](../../../CLAUDE.md)

This file contains LSCC-specific trading parameters and context.

## Quick Reference

### Daily Update Query Template

```
Latest update on Lattice Semiconductor (LSCC) for [TODAY'S DATE]:
(1) Current stock price and today's intraday price action,
(2) Any news or developments in past 24-48 hours,
(3) Has price reached the $66-68 entry zone yet?
(4) Updated RSI and MACD readings if available,
(5) Any changes to earnings date (currently Nov 3) or new catalysts scheduled.
```

## LSCC Trading Parameters

```markdown
# LSCC Daily Update - [DATE]

## 📊 Price Action Summary
- Last Close, After-Hours, Week Range
- Entry Zone Status (TARGET: $66-68)

## 📰 Recent News & Developments (Past 48 Hours)
- Company announcements
- Analyst actions
- Technical alerts

## 📈 Technical Indicators Update
- RSI (14-Day)
- MACD
- Moving Averages
- Bollinger Bands
- Volume Analysis

## 🎯 Trading Levels Update
- Support Levels
- Resistance Levels
- Entry Strategy Status

## 📅 Upcoming Catalysts
- Earnings date
- Known catalysts

## 🎬 Action Items & Recommendations
- For conservative swing traders
- Risk assessment
- Stop-loss levels

## 📝 Summary & Key Takeaways
- TLDR
- What changed vs. last analysis
- What stayed the same
- Next steps
```

## Key Information to Track

### Price Levels
- **Target Entry Zone:** $66-68 (conservative swing entry)
- **Current Resistance:** $74.90, $80, $90
- **Key Support:** $64.64 (50-day MA), $54.89 (200-day MA)

### Technical Indicators
- **RSI Target:** Watch for oversold (<30) or neutral (40-60) for entry
- **MACD:** Monitor for bullish crossovers
- **Bollinger Bands:** Squeezes indicate upcoming volatility

### Fundamental Data
- **Next Earnings:** November 3, 2025
- **Expected Q3 Revenue:** $133M midpoint
- **Expected Q3 EPS:** $0.28
- **Valuation Concerns:** Trading at 20x sales, 52x P/E

### Trading Strategy
- **Entry:** Wait for pullback to $66-68
- **Position Size:** 50% at $66-68, 50% if breaks $74.90 on volume
- **Take Profit:** 50% at $80, trail stop for remainder to $90
- **Stop Loss:** $66.75 (moderate) or $63 (conservative)

## File Organization

### Current Files in This Directory
- `investment-summary_2025-10-05.md` - Comprehensive analysis (all 4 stocks)
- `swing-trading-analysis_2025-10-05.md` - Technical analysis (all 4 stocks)
- `daily-update_YYYY-MM-DD.md` - Daily updates (LSCC only)
- `CLAUDE.md` - This file

### Naming Convention
- Daily updates: `daily-update_YYYY-MM-DD.md`
- Comprehensive research: `comprehensive-research_YYYY-MM-DD.md`
- Swing trading analysis: `swing-trading-analysis_YYYY-MM-DD.md`

## Automation Triggers

### When to Create Daily Update
1. **Daily:** Before market open (to review previous day)
2. **After major news:** Company announcements, earnings, etc.
3. **Price alerts:** If price approaches $68
4. **Weekly minimum:** Even if no major changes

### When to Update Investment Summary
1. **Weekly:** Sunday evening or Monday morning
2. **After earnings:** Within 24 hours of Q3 report (Nov 3)
3. **Major catalyst events:** New partnerships, product launches
4. **Quarterly:** Comprehensive review every 3 months

## MCP Tools Used

### comet-devtools (Port 9223)
- `take_snapshot` - Capture current page state
- `fill` - Fill input fields with queries
- `click` - Submit forms
- `wait_for` - Wait for specific text/elements

### Example Workflow
```javascript
// 1. Take snapshot
await mcp__comet-devtools__take_snapshot()

// 2. Fill query
await mcp__comet-devtools__fill(uid, query)

// 3. Submit
await mcp__comet-devtools__click(submitButton)

// 4. Wait for response
await mcp__comet-devtools__wait_for("Latest Update")
```

## Research Context

### Related Stocks Being Tracked
1. **LSCC** - Lattice Semiconductor (this directory)
2. **AMBA** - Ambarella
3. **BRCHF** - BrainChip Holdings
4. **GSIT** - GSI Technology

All part of "AI Chips Hidden Gems" research theme.

### Leadership Quality (LSCC)
- **CEO:** Dr. Ford Tamer
- **Background:** Ex-Inphi CEO, ex-Broadcom, MIT PhD
- **Grade:** A+ (top-tier semiconductor executive)

## Perplexity Search Tips

### Effective Query Structure
1. **Date:** Always include specific date
2. **Ticker:** Use both company name and ticker
3. **Specifics:** Ask for exact metrics (RSI, MACD, price levels)
4. **Time Range:** Specify 24-48 hours for daily updates
5. **Context:** Reference previous key levels ($66-68 entry zone)

### What to Ask For
- ✅ Current price and intraday action
- ✅ Recent news (24-48 hours)
- ✅ Technical indicator updates (RSI, MACD)
- ✅ Earnings date confirmation
- ✅ Entry zone status (specific price levels)

### What NOT to Ask For
- ❌ Investment advice
- ❌ "Should I buy/sell" questions
- ❌ Predictions of future price
- ❌ Overly broad queries

## Cross-References

### Main Research Directory
- [Research Stocks README](../../README.md)
- [AI Chips Hidden Gems Summary](../AI-chips-hidden-gems/investment-summary_2025-10-05.md)

### Deep Stock Research Command
- Location: `~/.claude/commands/deep-stock-research.md`
- Usage: `/deep-stock-research <TICKER> [--type=TYPE]`

## Notes for Future Sessions

### Session Continuity
- Always read this CLAUDE.md file when resuming LSCC research
- Check most recent `daily-update_*.md` for latest data
- Reference `investment-summary_*.md` for comprehensive context

### Important Reminders
- **Entry zone:** $66-68 (do NOT chase price above this)
- **Earnings:** Nov 3, 2025 (NOT Nov 4)
- **Valuation:** High (20x sales) - requires pullback for good risk/reward
- **Strategy:** Conservative swing trading, NOT day trading

---

**Last Updated:** October 5, 2025
**Next Review:** Daily until entry zone reached or earnings (Nov 3)
