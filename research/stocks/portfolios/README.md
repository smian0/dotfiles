# Stock Portfolio Configuration Files

This directory contains CSV configuration files for stock portfolios tracked with the `/deep-stock-research` command.

## File Format

Each portfolio is a CSV file with the following columns:

```csv
ticker,entry_zone_low,entry_zone_high,next_earnings,risk_level,notes
```

### Column Definitions

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **ticker** | string | Stock ticker symbol | `LSCC` |
| **entry_zone_low** | number | Conservative entry zone low price | `66` |
| **entry_zone_high** | number | Conservative entry zone high price | `68` |
| **next_earnings** | date | Next earnings report date (YYYY-MM-DD) | `2025-11-03` |
| **risk_level** | enum | Risk assessment: `low`, `medium`, `high`, `extreme` | `medium` |
| **notes** | string | Important context, warnings, or highlights | `A+ leadership` |

### Risk Levels

- **low**: Established company, high liquidity, stable technicals
- **medium**: Normal swing trading risk, good liquidity
- **high**: Elevated volatility, momentum-driven, or near-term catalysts
- **extreme**: Microcap, illiquid, or critical warnings - reduce position size or avoid

## Usage

### Create New Portfolio

1. Create CSV file: `{portfolio-name}.csv`
2. Add stocks with their parameters
3. Use in command:
   ```bash
   /deep-stock-research --portfolio={portfolio-name} --type=daily-update
   ```

### Update Existing Portfolio

1. Edit the CSV file to update entry zones, earnings dates, or risk levels
2. Changes take effect immediately on next command run
3. Commit changes to git for tracking

### Command Examples

```bash
# Daily update for entire portfolio (reads CSV)
/deep-stock-research --portfolio=AI-chips-hidden-gems --type=daily-update

# Override with specific tickers (still creates consolidated summary)
/deep-stock-research LSCC,AMBA --type=daily-update --portfolio=AI-chips-hidden-gems

# Single stock from portfolio (no consolidated summary)
/deep-stock-research LSCC --type=daily-update
```

## Example Portfolio File

```csv
ticker,entry_zone_low,entry_zone_high,next_earnings,risk_level,notes
LSCC,66,68,2025-11-03,medium,A+ leadership - Dr. Ford Tamer
AMBA,80,82,2025-11-25,medium,Automotive ADAS design wins
BRCHF,0.155,0.155,2026-03-03,extreme,EXTREME liquidity warning - DO NOT TRADE
GSIT,4.10,4.60,2025-10-23,high,Overbought RSI - reduce position size
```

## Available Portfolios

- **AI-chips-hidden-gems.csv**: Semiconductor/AI chip stocks (LSCC, AMBA, BRCHF, GSIT)

## Benefits

✅ **Centralized Configuration**: All stock parameters in one place
✅ **Version Control**: Track entry zone changes over time in git
✅ **Risk Management**: Explicit risk levels guide position sizing
✅ **Documentation**: CSV serves as portfolio reference
✅ **Flexibility**: Override with command-line tickers when needed

## File Location

```
~/dotfiles/research/stocks/portfolios/
├── README.md (this file)
├── AI-chips-hidden-gems.csv
└── {your-portfolio-name}.csv
```

---

**Last Updated:** October 6, 2025
