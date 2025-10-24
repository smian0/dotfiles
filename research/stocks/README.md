# Stock Research Archive

Organized repository for daily stock research, technical analysis, and investment tracking.

---

## Quick Start

```bash
# RECOMMENDED MORNING ROUTINE (Before 9:30 AM ET)

# 1. Update prices first (8-16 minutes for both portfolios)
/deep-stock-research --portfolio=quantum-computing --type=daily-update
/deep-stock-research --portfolio=AI-chips-hidden-gems --type=daily-update

# 2. Generate watch list with fresh data
/morning-watch-list

# 3. Review watch list
cat ~/dotfiles/research/stocks/watch-lists/$(date +%Y-%m-%d)_morning.md

# Alternative: Use yesterday's data (if ran updates after market close)
/morning-watch-list  # Will warn if data is stale
```

**Other Commands:**
```bash
# Discover hidden gem stocks in a sector
/discover-stocks --sector=quantum-computing

# View research for specific stock
ls -lh ~/dotfiles/research/stocks/*/IONQ/

# Find latest analyses
find ~/dotfiles/research/stocks -name "daily-update_*.md" | sort -r | head -5
```

---

## Directory Structure

```
~/dotfiles/research/stocks/
├── YYYY-MM/{STOCK}/           # Stock-specific (IONQ/, AMD/, etc)
│   ├── daily-update_YYYY-MM-DD.md
│   ├── comprehensive-research_YYYY-MM-DD.md
│   └── raw-data/YYYY-MM-DD/   # Audit trail (query, response, metadata)
├── YYYY-MM/{PORTFOLIO}/       # Portfolio summaries (quantum-computing/, etc)
│   └── daily-summary_YYYY-MM-DD.md
├── YYYY-MM/discoveries/       # Stock discovery reports (NEW)
│   └── {sector}-hidden-gems_YYYY-MM-DD.md
├── portfolios/                # CSV configs (tickers, entry zones, risk)
├── watch-lists/               # Morning watch lists (auto-saved)
│   └── YYYY-MM-DD_morning.md
└── archive/                   # Research >3 months old
```

---

## File Naming

| Type | Format | Purpose |
|------|--------|---------|
| Daily update | `daily-update_YYYY-MM-DD.md` | Single stock analysis |
| Daily summary | `daily-summary_YYYY-MM-DD.md` | Portfolio overview |
| Comprehensive | `comprehensive-research_YYYY-MM-DD.md` | Deep dive research |
| Swing trading | `swing-trading-analysis_YYYY-MM-DD.md` | Entry/exit points |

**Key Rule:** Never overwrite files - create new dated versions to preserve history.

---

## Workflow

### 1. Portfolio Configuration

Create CSV in `portfolios/` directory:

```csv
ticker,entry_zone_low,entry_zone_high,next_earnings,risk_level,notes
IONQ,62,65,2025-11-15,high,Leading quantum player
QMCO,10,11,2025-10-30,high,Not pure quantum play
```

### 2. Run Daily Updates

```bash
# Entire portfolio
/deep-stock-research --portfolio=quantum-computing --type=daily-update

# Single stock
/deep-stock-research IONQ --type=daily-update
```

### 3. Files Created

**Individual stocks:** `YYYY-MM/IONQ/daily-update_YYYY-MM-DD.md`
**Portfolio summary:** `YYYY-MM/quantum-computing/daily-summary_YYYY-MM-DD.md`
**Audit trail:** `YYYY-MM/IONQ/raw-data/YYYY-MM-DD/` (query, response, metadata)

### 4. Cross-Reference Previous Research

In report headers, link to related files:

```markdown
**Previous Research:**
- [IONQ Daily - Oct 5](../IONQ/daily-update_2025-10-05.md)
- [Portfolio Summary - Oct 5](../quantum-computing/daily-summary_2025-10-05.md)
```

---

## Quality Standards

### Source Requirements
- **Minimum:** 3 independent sources
- **Preferred:** Company filings, Bloomberg, Reuters, WSJ, analyst reports
- **Avoid:** Single-source claims, outdated data (>90 days)

### Data Recency
- **Optimal:** <30 days
- **Acceptable:** <90 days (mark as historical)
- **Outdated:** >90 days (trends only)

---

## Common Commands

```bash
# View today's watch list
cat ~/dotfiles/research/stocks/watch-lists/$(date +%Y-%m-%d)_morning.md

# Compare watch lists over time
diff ~/dotfiles/research/stocks/watch-lists/2025-10-06_morning.md \
     ~/dotfiles/research/stocks/watch-lists/2025-10-07_morning.md

# Find latest analysis for stock
find ~/dotfiles/research/stocks -path "*/IONQ/daily-update_*.md" | sort -r | head -1

# Compare entry zones over time
grep "Entry Zone:" ~/dotfiles/research/stocks/*/IONQ/*.md

# List all portfolio summaries
ls ~/dotfiles/research/stocks/*/quantum-computing/daily-summary_*.md

# Archive old research (>3 months)
mv ~/dotfiles/research/stocks/2025-07/ ~/dotfiles/research/stocks/archive/

# Review watch lists from past week
ls -lt ~/dotfiles/research/stocks/watch-lists/ | head -8
```

---

## Integration with Commands

### `/discover-stocks` - Find Hidden Gem Stocks
**NEW**: Uses agentic research loop (Comet/Perplexity MCP) to discover under-the-radar stocks.

**Usage:**
```bash
/discover-stocks --sector=quantum-computing  # Find quantum hidden gems
/discover-stocks --sector=AI-chips --market-cap-max=10B  # Higher cap limit
/discover-stocks --sector=neuromorphic --min-stocks=8  # At least 8 stocks
```

**What it does:**
1. Multi-round Perplexity research to discover 15-20 candidates
2. Financial screening (revenue growth, margins, debt, liquidity)
3. Catalyst analysis (recent news, insider activity, momentum)
4. Risk assessment (regulatory, competitive, execution risks)
5. Generates comprehensive discovery report with 5-7 top picks
6. Runs deep research on top 3-5 candidates automatically
7. Creates portfolio CSV for immediate tracking

**Output:**
- `discoveries/{sector}-hidden-gems_YYYY-MM-DD.md` - Discovery report
- `{TICKER}/comprehensive-research_YYYY-MM-DD.md` - Full analysis (top picks)
- `portfolios/{sector}-hidden-gems.csv` - Portfolio config for tracking

**Next Steps After Discovery:**
```bash
# Track discovered stocks daily
/deep-stock-research --portfolio=quantum-computing-hidden-gems --type=daily-update

# Generate morning watch list
/morning-watch-list --portfolio=quantum-computing-hidden-gems
```

### `/morning-watch-list` - Daily Pre-Market Watch List
Pure Claude command that analyzes portfolios and generates actionable watch list.

**Usage:**
```bash
/morning-watch-list --portfolio=quantum-computing  # Specific portfolio
/morning-watch-list --all                          # All portfolios (default)
/morning-watch-list                                # Same as --all
```

**What it does:**
1. Reads portfolio CSV files for entry zones and risk levels
2. Extracts latest prices from daily update files
3. Calculates distance from entry zones
4. Ranks stocks into 3 tiers
5. Generates specific intraday strategies for actionable stocks
6. **Automatically saves to:** `watch-lists/YYYY-MM-DD_morning.md`

**Output Tiers:**
- **Tier 1**: Stocks within 5% of entry zones → **TRADE TODAY**
- **Tier 2**: Stocks 5-10% from entry → **SET ALERTS**
- **Tier 3**: Stocks >10% away → **DO NOT TRADE**

**For each Tier 1 stock:**
- Exact entry triggers (price + volume)
- Intraday timing (9:30-9:45 AM optimal)
- Stop loss levels (-7% auto-calculated)
- Profit targets (+15% target 1)
- Position sizing (based on CSV risk level)
- Recent news/catalysts from daily updates

### `/deep-stock-research` - Daily Updates & Research
**Automatically:**
1. Reads portfolio CSV for ticker/entry zone data
2. Creates month/stock directory structure
3. Saves reports with correct naming convention
4. Generates audit trail (query, response, metadata)
5. Creates portfolio summary for multi-stock portfolios

---

## Best Practices

### DO ✅
- Create new dated files (preserve history)
- Use portfolio CSVs for configuration
- Cross-reference previous research
- Include audit trails (raw data)
- Archive research >3 months

### DON'T ❌
- Overwrite existing reports (data loss)
- Mix naming conventions
- Skip cross-references
- Delete old research (archive instead)

---

## Maintenance

**Monthly (first week):**
1. Check previous month completeness: `ls ~/dotfiles/research/stocks/YYYY-MM/`
2. Archive research >3 months: `mv 2025-07/ archive/`
3. Create new month folder: `mkdir -p ~/dotfiles/research/stocks/$(date +%Y-%m)`

**Quarterly (Jan/Apr/Jul/Oct):**
1. Review active folders
2. Validate naming consistency
3. Update portfolio CSVs with new entry zones

---

## Related Documentation

- **Daily workflow guide:** [DAILY-WORKFLOW.md](./DAILY-WORKFLOW.md) - Complete checklist for daily runs
- **AI workflow instructions:** [CLAUDE.md](./CLAUDE.md)
- **Command implementation:** `~/.claude/commands/deep-stock-research.md`
- **Morning watch list command:** `~/.claude/commands/morning-watch-list.md`
- **Browser automation:** `~/dotfiles/docs/COMET_BROWSER_AUTOMATION.md`
- **Portfolio CSV format:** [portfolios/README.md](./portfolios/README.md)

---

**Last Updated:** October 6, 2025
