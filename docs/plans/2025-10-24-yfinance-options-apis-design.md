# yfinance Options APIs Design

**Date:** 2025-10-24
**Status:** Approved
**Target:** yfinance MCP Server Enhancement

## Overview

Extend the existing yfinance MCP server with three options trading tools using a tiered progressive-disclosure architecture. Data-only approach keeps server focused on retrieval; strategy analysis will be handled by future workflow.

## Use Cases

- Comprehensive options analysis across multiple expirations
- Compare strikes for specific expiration dates
- Deep dive into individual option contracts
- **Future:** Foundation for multi-leg options strategy workflows

## Design Decisions

### Architecture: Tiered (3 Tools)

**Rationale:** Balance between simplicity and flexibility. Progressive disclosure pattern matches natural exploration workflow.

**Rejected Alternatives:**
- **Minimal (2 tools):** Single tool with too many parameters, harder to use
- **Granular (4 tools):** Too much redundancy, tool proliferation

### Data Handling: Summary + Details

**Rationale:** Default to summary view to avoid token limits, allow drilling into specific data on demand.

**Strategy:**
- Summary mode: ATM + nearest 5 strikes above/below
- Full mode: All strikes with smart truncation at 25K chars
- Detail tool: Complete data for single strike

### Data Structure: Flexible Filtering

**Rationale:** Single tool with option_type parameter ('calls', 'puts', 'both') provides maximum flexibility without tool duplication.

### Scope: Data-Only MCP

**Rationale:** Keep yfinance MCP as pure data retrieval. Strategy calculations belong in separate skill/workflow for better separation of concerns.

**Future Work:** Strategy analysis workflow using workflow-orchestrator pattern (research → fetch data → calculate → visualize).

## Tool Specifications

### Tool 1: `get_options_dates`

**Purpose:** Discover available expiration dates for a ticker

**Parameters:**
- `ticker: str` - Stock ticker symbol

**Returns:**
- List of expiration dates in ISO format (YYYY-MM-DD)
- Grouped by timeframe: Near-term (0-60d), Mid-term (60-180d), Long-term (180d+)

**Example:**
```python
get_options_dates("AAPL")
# Returns: ["2025-10-31", "2025-11-15", "2025-12-20", "2026-01-17", ...]
```

**Error Handling:**
- Invalid ticker: Clear message suggesting verification
- No options available: Explain why (e.g., security doesn't have options)

---

### Tool 2: `get_options_chain`

**Purpose:** Analyze options chain for specific expiration

**Parameters:**
- `ticker: str` - Stock ticker symbol
- `expiration_date: str` - Expiration date (ISO format)
- `option_type: Literal["calls", "puts", "both"]` - Contract type (default: "both")
- `detail_level: Literal["summary", "full"]` - Data granularity (default: "summary")
- `format: Literal["json", "markdown"]` - Output format (default: "markdown")

**Summary Mode Returns:**
- ATM strike identification
- Nearest 5 strikes above/below ATM
- Total volume and open interest
- Implied volatility summary (if available)

**Full Mode Returns:**
- All available strikes with:
  - Price data: last, bid, ask
  - Volume and open interest
  - Implied volatility
  - Greeks: delta, gamma, theta, vega, rho (if available)
  - In-the-money boolean
- Smart truncation at 25K characters (most liquid strikes first)

**Example:**
```python
get_options_chain("AAPL", "2025-11-15", "calls", "summary")
# Returns focused summary of call options

get_options_chain("SPY", "2025-12-20", "both", "full", "json")
# Returns complete chain in JSON format
```

**Error Handling:**
- Invalid expiration: Show available dates
- No data for date: Explain why
- Missing Greeks: Indicate when unavailable vs data issue

---

### Tool 3: `get_option_strike`

**Purpose:** Deep dive into single option contract

**Parameters:**
- `ticker: str` - Stock ticker symbol
- `expiration_date: str` - Expiration date (ISO format)
- `strike: float` - Strike price
- `option_type: Literal["call", "put"]` - Contract type

**Returns:**
- Complete contract details:
  - Price data: last, bid, ask, spread percentage
  - Volume, open interest, last trade timestamp
  - All Greeks: delta, gamma, theta, vega, rho
  - Intrinsic value, extrinsic value
  - Contract symbol (OCC format)
  - In-the-money boolean

**Example:**
```python
get_option_strike("AAPL", "2025-11-15", 260.0, "call")
# Returns all available data for AAPL Nov 15 260 Call
```

**Error Handling:**
- Invalid strike: Show available strikes near requested price
- No data: Explain if contract doesn't exist or data unavailable

## Data Format

### Consistent Structure

All tools follow the existing yfinance MCP pattern:

**JSON Format:**
```json
{
  "ticker": "AAPL",
  "expiration": "2025-11-15",
  "option_type": "calls",
  "data": [...],
  "metadata": {
    "data_points": 50,
    "timestamp": "2025-10-24T16:40:00Z"
  }
}
```

**Markdown Format:**
```markdown
# Options Chain for AAPL

**Expiration:** 2025-11-15 | **Type:** Calls | **Strikes:** 50

[Formatted table]
```

### Strategy-Friendly Fields

Chain data includes fields for future strategy calculations:
- `strike`: Float (precise comparisons)
- `lastPrice`, `bid`, `ask`: Decimals (P&L calculations)
- `delta`, `gamma`, `theta`, `vega`: Greeks (risk analysis)
- `openInterest`, `volume`: Liquidity metrics
- `impliedVolatility`: IV for spread analysis
- `inTheMoney`: Boolean (quick filtering)

This structure enables future strategy workflow to:
1. Fetch multiple chains/strikes efficiently
2. Parse and combine multi-leg strategies
3. Calculate net Greeks and P&L curves
4. Analyze risk/reward profiles

## Implementation Plan

### File Structure
```
mcp_servers/yfinance/
├── yfinance_mcp.py          # Add 3 new @mcp.tool functions
├── test_yfinance_mcp.py     # Add 3 new test cases
└── .mcp.json                # Already configured (no changes)
```

### Implementation Strategy

1. **Add Tools to Existing Server**
   - Add 3 new `@mcp.tool` decorated functions
   - Reuse existing utilities: `truncate_text`, `format_dataframe_as_markdown`, `handle_yfinance_error`
   - Follow FastMCP v2 Annotated pattern (no Pydantic models as single params)
   - Include `Context` parameter for progress logging

2. **Use yfinance Native Methods**
   - `stock.options` → List of expiration dates
   - `stock.option_chain(date)` → Returns calls/puts DataFrames
   - Parse DataFrame columns: strike, lastPrice, bid, ask, volume, openInterest, impliedVolatility, inTheMoney
   - Greeks may not always be available (handle gracefully)

3. **Testing**
   - Add test cases to existing test_yfinance_mcp.py
   - Test with liquid tickers: AAPL, SPY (guaranteed to have options)
   - Validate error handling: invalid ticker, invalid date, missing data
   - Verify truncation: test with ticker having 100+ strikes

4. **Hot-Reload Enabled**
   - No .mcp.json changes needed (auto-restart already configured)
   - Changes to yfinance_mcp.py will hot-reload automatically

### Testing Checklist

```
Options Tools Testing:
- [ ] get_options_dates returns valid ISO dates
- [ ] get_options_dates handles invalid ticker gracefully
- [ ] get_options_chain summary mode returns ~10-15 strikes
- [ ] get_options_chain full mode returns all strikes (truncated if needed)
- [ ] get_options_chain handles "calls", "puts", "both" correctly
- [ ] get_options_chain markdown format is readable
- [ ] get_option_strike returns complete contract details
- [ ] get_option_strike handles invalid strike gracefully
- [ ] All tools log progress via Context
- [ ] Error messages are clear and actionable
```

## Future: Strategy Analysis Workflow

After implementation, use **workflow-orchestrator** to create strategy analysis workflow:

```
Strategy Analysis Workflow (3 phases):
├─ Phase 1: Fetch Options Data
│   └─ Skill: yfinance MCP (get chains, strikes)
├─ Phase 2: Calculate Strategy Metrics
│   └─ Skill: TBD (P&L curves, Greeks, breakeven, max risk/reward)
└─ Phase 3: Visualize & Validate
    ├─ Skill: vtree (strategy structure)
    └─ Skill: research (market conditions)
```

**Strategy Types to Support:**
- Spreads (bull/bear call/put, calendar, diagonal)
- Straddles/Strangles (volatility plays)
- Iron Condors/Butterflies (range-bound)
- Custom multi-leg (4+ legs)

## Success Criteria

- ✅ 3 new tools implemented following existing patterns
- ✅ All tests passing (10/10 total: 7 existing + 3 new)
- ✅ Data structure supports future strategy calculations
- ✅ Clear error messages for all failure cases
- ✅ Hot-reload works without .mcp.json changes
- ✅ Documentation complete (this design doc + inline docstrings)

## References

- Existing yfinance MCP implementation: `mcp_servers/yfinance/yfinance_mcp.py`
- FastMCP v2 patterns: Context7 MCP (/jlowin/fastmcp)
- yfinance options API: https://github.com/ranaroussi/yfinance
