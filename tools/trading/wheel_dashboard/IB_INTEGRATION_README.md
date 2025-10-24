# Interactive Brokers Integration - Implementation Guide

**Status:** Phase 1 Foundation Complete (Core modules ready)
**Next Steps:** Install ib_insync → Connect to IB → Implement analyzers

## What's Been Built

### 📁 File Structure Created

```
wheel_dashboard/
├─ connection/          # IB Connection Management
│  ├─ __init__.py      ✅ Module exports
│  ├─ ib_config.py     ✅ Configuration (env vars, ports, thresholds)
│  └─ ib_manager.py    ✅ Connection handling with graceful fallback
│
├─ analyzers/           # Strategic Data Analyzers (Ready to implement)
│  ├─ iv_rank_calculator.py    ⏳ Next: IV Rank from 52-week history
│  ├─ earnings_filter.py       ⏳ Next: Earnings calendar integration
│  └─ weekly_scanner.py        ⏳ Next: Weekly expiration detection
│
├─ ui/                  # UI Components (Ready to implement)
│  └─ ib_indicators.py  ⏳ Next: IB status widgets & enhanced tables
│
└─ data/                # Data Providers
   └─ ib_provider.py    ⏳ Next: Unified IB data interface
```

### ✅ Core Modules Implemented

**1. IB Configuration (`connection/ib_config.py`)**
- Environment variable support
- Paper/Live trading toggle
- Configurable thresholds (IV Rank, earnings safety)
- Port reference guide (TWS vs Gateway, Paper vs Live)

**2. IB Manager (`connection/ib_manager.py`)**
- Auto-connection with retry
- Graceful degradation (works without ib_insync installed)
- Read-only mode (safe for screening)
- Context manager support
- Connection health monitoring

## Installation & Setup

### Step 1: Install ib_insync

```bash
cd ~/dotfiles/tools/trading/wheel_dashboard

# Add to requirements.txt
echo "ib_insync>=0.9.86" >> requirements.txt

# Install
pip install ib_insync
```

### Step 2: Setup IB Gateway (Paper Trading)

**Download:**
https://www.interactivebrokers.com/en/trading/ibgateway-stable.php

**Configure API Settings:**
1. Launch IB Gateway
2. Login with paper trading credentials
3. Go to API Settings:
   - ✅ Enable ActiveX and Socket Clients
   - Socket port: `4002` (paper) or `7497` (TWS paper)
   - Trusted IP: `127.0.0.1`
   - ✅ Read-Only API (for screening only)

**Ports Reference:**
- TWS Paper Trading: `7497`
- TWS Live Trading: `7496`
- IB Gateway Paper: `4002`
- IB Gateway Live: `4001`

### Step 3: Configure Environment

Create `.env` file:
```bash
# IB Connection
IB_HOST=127.0.0.1
IB_PORT=4002              # IB Gateway Paper
IB_CLIENT_ID=1
IB_ACCOUNT=DU1234567      # Your paper account
IB_USE_PAPER=true

# Screening Thresholds
MIN_IV_RANK=50.0
EARNINGS_SAFETY_DAYS=10
```

### Step 4: Test Connection

```python
# Test script
from connection import IBManager, IBConfig

# Load config
config = IBConfig.from_env()
print(f"Connecting to: {config.get_connection_string()}")

# Test connection
manager = IBManager(config)
success, message = manager.connect()

if success:
    print(f"✅ {message}")
    print(f"Connected: {manager.is_connected()}")
    manager.disconnect()
else:
    print(f"❌ {message}")
```

## Phase 1: Critical Features Implementation

### Priority 1: IV Rank Calculator ⭐⭐⭐⭐⭐

**File:** `analyzers/iv_rank_calculator.py`

**Purpose:** Calculate IV Rank from 52-week historical IV

**Key Methods:**
```python
class IVRankCalculator:
    def get_iv_rank(ticker, expiration) -> Dict:
        """
        Returns:
        {
            "current_iv": 25.5,
            "iv_rank": 85.2,  # 0-100 scale
            "iv_percentile": 87.3,
            "52w_high": 45.2,
            "52w_low": 12.8,
            "status": "HIGH" | "NORMAL" | "LOW"
        }
        """

    def _fetch_iv_history(ticker, expiration, days=252) -> List[float]:
        """Fetch 52-week IV history from IB"""
```

**Status Interpretation:**
- `HIGH` (80-100): Excellent for selling premium
- `NORMAL` (50-79): Conditional
- `LOW` (0-49): Skip

**Dashboard Integration:**
- Add "IV Rank" column to summary table
- Color-code: Green (80-100), Yellow (50-79), Red (0-49)
- Filter slider: "Min IV Rank"
- Detail view: 52-week IV chart

### Priority 2: Earnings Calendar ⭐⭐⭐⭐⭐

**File:** `analyzers/earnings_filter.py`

**Purpose:** Filter opportunities based on earnings dates

**Key Methods:**
```python
class EarningsFilter:
    def get_earnings_info(ticker) -> Dict:
        """
        Returns:
        {
            "next_earnings_date": "2025-11-01",
            "days_to_earnings": 8,
            "safe_to_sell_puts": False,
            "reason": "Earnings in 8 days"
        }
        """

    def filter_watchlist(tickers, dte) -> List[Dict]:
        """Filter entire watchlist for earnings safety"""
```

**Safety Rules:**
- Don't sell puts < 10 days before earnings
- Don't sell puts with expiration after earnings
- Flag earnings week opportunities with warning

**Dashboard Integration:**
- Add "Earnings" column with date
- Alert icon ⚠️ for unsafe windows
- Filter checkbox: "Exclude earnings in next 10 days"

### Priority 3: Weekly Scanner ⭐⭐⭐⭐⭐

**File:** `analyzers/weekly_scanner.py`

**Purpose:** Detect and analyze weekly expirations

**Key Methods:**
```python
class WeeklyScanner:
    def get_all_expirations(ticker) -> List[Dict]:
        """
        Returns all expirations (weekly + monthly)
        """

    def scan_weekly_opportunities(ticker, min_dte=7, max_dte=21) -> List[Dict]:
        """
        Scan 1-3 week weekly expirations for high-frequency wheel
        """

    def _is_monthly_expiration(date) -> bool:
        """Check if expiration is monthly (3rd Friday)"""
```

**Dashboard Integration:**
- Toggle: "Include Weekly Expirations"
- Expiration selector: Show all weeklies + monthlies
- Badge: "X weekly opportunities"

## Usage Example

### With IB Connected

```python
from connection import IBManager, IBConfig
from analyzers import IVRankCalculator, EarningsFilter, WeeklyScanner

# Setup
config = IBConfig.from_env()
manager = IBManager(config)
manager.connect()

ib = manager.get_connection()

# Calculate IV Rank
iv_calc = IVRankCalculator(ib)
ko_iv = iv_calc.get_iv_rank("KO", "20251128")
print(f"KO IV Rank: {ko_iv['iv_rank']:.1f}% ({ko_iv['status']})")

# Check earnings
earnings_filter = EarningsFilter(ib)
ko_earnings = earnings_filter.get_earnings_info("KO")
print(f"KO Earnings: {ko_earnings['next_earnings_date']}")
print(f"Safe to trade: {ko_earnings['safe_to_sell_puts']}")

# Scan weeklies
weekly_scanner = WeeklyScanner(ib)
ko_weeklies = weekly_scanner.scan_weekly_opportunities("KO")
print(f"KO has {len(ko_weeklies)} weekly opportunities")

manager.disconnect()
```

### With Graceful Fallback (IB Disconnected)

```python
manager = IBManager(config)

if not manager.is_connected():
    print("⚠️ IB unavailable - using yfinance fallback")
    # Dashboard continues with limited features
    use_yfinance_only = True
else:
    print("✅ IB connected - full features available")
    use_enhanced_screening = True
```

## Dashboard Enhancement Plan

### Current Dashboard (yfinance only)
```
Screening Capabilities:
✅ Basic options chain
✅ Estimated Greeks
✅ Monthly expirations (partial)
❌ IV Rank (cannot calculate)
❌ Accurate earnings dates
❌ Weekly expirations (often missing)
```

### Enhanced Dashboard (IB + yfinance)
```
Screening Capabilities:
✅ Complete options chain
✅ Real Greeks (exchange-calculated)
✅ All expirations (weekly + monthly)
✅ IV Rank (52-week history)
✅ Accurate earnings calendar
✅ OI change detection
```

### UI Changes

**Header:**
```
🎯 Wheel Strategy Dashboard v2.0
Status: 🟢 IB Connected (Paper) | 📊 IB + yfinance
```

**Summary Table (New Columns):**
| Ticker | Score | IV Rank | Earnings | Exp Type | ... |
|--------|-------|---------|----------|----------|-----|
| KO     | 92    | 85% (HIGH) | 11/15 (22d) | W | ... |
| JNJ    | 89    | 72% (NORMAL) | 11/01 (8d) ⚠️ | M | ... |

**Filters (New):**
- Min IV Rank: [ 50 ] (0-100)
- ☑ Exclude earnings < 10 days
- ☑ Include weekly expirations

## Testing Checklist

### Pre-Flight Checks
- [ ] IB Gateway running
- [ ] Paper trading account credentials
- [ ] `ib_insync` package installed
- [ ] Environment variables configured

### Connection Tests
- [ ] Connect to IB Gateway
- [ ] Verify read-only mode
- [ ] Test reconnection
- [ ] Test graceful fallback (disconnect IB)

### Analyzer Tests
- [ ] IV Rank for known ticker (KO)
- [ ] Earnings date accuracy
- [ ] Weekly expiration detection
- [ ] Compare IB vs yfinance data

### Dashboard Tests
- [ ] UI renders with IB connected
- [ ] UI renders with IB disconnected
- [ ] IV Rank column displays
- [ ] Earnings warnings appear
- [ ] Weekly expirations selectable

## Troubleshooting

### "ib_insync not found"
```bash
pip install ib_insync
```

### "Connection refused"
- Check IB Gateway is running
- Verify port (4002 for Gateway Paper)
- Check API settings enabled

### "Authentication failed"
- Verify paper trading credentials
- Check IB_ACCOUNT in .env

### "Historical data unavailable"
- Market data subscription required
- Check IB account permissions

## Next Steps

1. **Install ib_insync** → `pip install ib_insync`
2. **Setup IB Gateway** → Download and configure
3. **Test connection** → Run test script
4. **Implement analyzers** → IV Rank, Earnings, Weekly
5. **Enhance dashboard** → Add IB data columns
6. **Test end-to-end** → Full workflow validation

## References

- Design Doc: `docs/plans/2025-10-24-ib-integration-design.md`
- Data Comparison: `docs/analysis/ib-vs-yfinance-options-data.md`
- ib_insync Docs: https://ib-insync.readthedocs.io/
- IB API Guide: https://interactivebrokers.github.io/tws-api/

---

**Ready to implement Phase 1 analyzers!** 🚀
