# Interactive Brokers Integration Design - Wheel Strategy Dashboard

**Date:** 2025-10-24
**Status:** Approved
**Purpose:** Strategic options screening data enhancement

## Overview

Enhance the Wheel Strategy Dashboard with Interactive Brokers data for superior options screening capabilities. Focus on strategic data points that yfinance cannot provide, particularly IV Rank, earnings calendar, and weekly expirations.

## Design Principles

1. **Screening-First, Execution-Optional** - Prioritize data quality over trade automation
2. **Hybrid Architecture** - Combine yfinance (free, broad) + IB (precise, deep)
3. **Paper Trading Default** - Start with paper account, live trading optional
4. **Graceful Degradation** - Dashboard works if IB disconnected (falls back to yfinance)
5. **Zero Breaking Changes** - Existing yfinance workflow remains functional

## Architecture

### Three-Layer Data Stack

```
┌──────────────────────────────────────────────────────────┐
│              Wheel Strategy Dashboard v2.0               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Layer 1: Universe Screening (yfinance - Free)          │
│  ├─ Fundamental filtering (100+ stocks)                 │
│  ├─ Dividend yield, market cap, beta                    │
│  ├─ Basic options chain (monthly expirations)           │
│  └─ Cost: $0/month                                      │
│       ↓ Output: ~30 qualified candidates                │
│                                                          │
│  Layer 2: Strategic Filtering (IB - Precision)          │
│  ├─ IV Rank calculation (52-week history)               │
│  ├─ Earnings calendar validation                        │
│  ├─ Weekly expiration scanning                          │
│  ├─ Real-time Greeks (delta, theta, gamma)              │
│  ├─ OI change detection                                 │
│  └─ Cost: $10-15/month (market data)                    │
│       ↓ Output: ~10 best opportunities                  │
│                                                          │
│  Layer 3: Execution (IB - Optional)                     │
│  └─ Order placement (future enhancement)                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Component Architecture

```
wheel_app.py (Main Dashboard)
    │
    ├─── data/
    │    ├─── yfinance_provider.py (Existing - Basic data)
    │    └─── ib_provider.py (NEW - Strategic data)
    │
    ├─── analyzers/
    │    ├─── iv_rank_calculator.py (NEW - Critical)
    │    ├─── earnings_filter.py (NEW - Critical)
    │    ├─── weekly_scanner.py (NEW - Critical)
    │    ├─── greeks_analyzer.py (NEW - Phase 2)
    │    └─── oi_tracker.py (NEW - Phase 2)
    │
    ├─── connection/
    │    ├─── ib_manager.py (NEW - Connection handling)
    │    └─── ib_config.py (NEW - Settings)
    │
    └─── ui/
         └─── ib_indicators.py (NEW - Status widgets)
```

## Implementation Plan

### Phase 1: Critical Screening Data (Week 1)

**Priority: MUST HAVE**

#### 1.1 IV Rank Calculator

**Data Required:**
- 52-week historical IV for each option expiration
- Current IV for comparison
- Min/Max IV in range

**Implementation:**
```python
# analyzers/iv_rank_calculator.py

class IVRankCalculator:
    def __init__(self, ib_connection):
        self.ib = ib_connection
        self.cache = {}  # Cache IV history

    def get_iv_rank(self, ticker: str, expiration: str) -> Dict:
        """
        Calculate IV Rank and Percentile

        Returns:
        {
            "current_iv": 25.5,
            "iv_rank": 85.2,  # 0-100 scale
            "iv_percentile": 87.3,  # % of days with lower IV
            "52w_high": 45.2,
            "52w_low": 12.8,
            "status": "HIGH" | "NORMAL" | "LOW"
        }
        """
        # Get historical IV (252 trading days)
        iv_history = self._fetch_iv_history(ticker, expiration, days=252)
        current_iv = iv_history[-1]

        # Calculate rank
        min_iv = min(iv_history)
        max_iv = max(iv_history)
        iv_rank = (current_iv - min_iv) / (max_iv - min_iv) * 100

        # Calculate percentile
        iv_percentile = (sum(1 for iv in iv_history if iv < current_iv) /
                         len(iv_history) * 100)

        # Determine status
        if iv_rank >= 80:
            status = "HIGH"  # Excellent for selling premium
        elif iv_rank >= 50:
            status = "NORMAL"  # Conditional
        else:
            status = "LOW"  # Skip

        return {
            "current_iv": current_iv,
            "iv_rank": iv_rank,
            "iv_percentile": iv_percentile,
            "52w_high": max_iv,
            "52w_low": min_iv,
            "status": status
        }

    def _fetch_iv_history(self, ticker: str, expiration: str, days: int) -> List[float]:
        """Fetch historical IV from IB"""
        # Check cache first
        cache_key = f"{ticker}_{expiration}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Request historical data from IB
        contract = self._create_option_contract(ticker, expiration)
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=f'{days} D',
            barSizeSetting='1 day',
            whatToShow='OPTION_IMPLIED_VOLATILITY',
            useRTH=True
        )

        iv_history = [bar.close for bar in bars]
        self.cache[cache_key] = iv_history

        return iv_history
```

**UI Integration:**
- Add "IV Rank" column to summary table
- Color-code: Green (80-100), Yellow (50-79), Red (0-49)
- Filter slider: "Min IV Rank" (default: 50)
- Detail view: Show 52-week IV chart

#### 1.2 Earnings Calendar Integration

**Data Required:**
- Next earnings date
- Days until earnings
- Earnings time (BMO/AMC/Unknown)

**Implementation:**
```python
# analyzers/earnings_filter.py

class EarningsFilter:
    def __init__(self, ib_connection):
        self.ib = ib_connection

    def get_earnings_info(self, ticker: str) -> Dict:
        """
        Get earnings information from IB

        Returns:
        {
            "next_earnings_date": "2025-11-01",
            "days_to_earnings": 8,
            "earnings_time": "AMC" | "BMO" | "Unknown",
            "safe_to_sell_puts": False,
            "reason": "Earnings in 8 days (< 10 day threshold)"
        }
        """
        contract = Stock(ticker, 'SMART', 'USD')
        self.ib.qualifyContracts(contract)

        # Request fundamental data
        fundamentals = self.ib.reqFundamentalData(
            contract,
            'ReportSnapshot'
        )

        # Parse earnings date
        earnings_date = self._parse_earnings_date(fundamentals)

        if not earnings_date:
            return {"safe_to_sell_puts": True, "reason": "No earnings scheduled"}

        # Calculate days to earnings
        days_to_earnings = (earnings_date - datetime.now().date()).days

        # Safety check
        safe = days_to_earnings > 10  # Conservative threshold
        reason = (f"Earnings in {days_to_earnings} days" if not safe
                  else "Safe window (>10 days to earnings)")

        return {
            "next_earnings_date": earnings_date.isoformat(),
            "days_to_earnings": days_to_earnings,
            "safe_to_sell_puts": safe,
            "reason": reason
        }

    def filter_watchlist(self, tickers: List[str], dte: int) -> List[Dict]:
        """
        Filter watchlist for earnings safety

        Returns list of tickers with earnings info and safety status
        """
        results = []
        for ticker in tickers:
            earnings_info = self.get_earnings_info(ticker)

            # Additional check: expiration after earnings
            if earnings_info.get("days_to_earnings"):
                if dte > earnings_info["days_to_earnings"]:
                    earnings_info["safe_to_sell_puts"] = False
                    earnings_info["reason"] = "Expiration after earnings"

            results.append({
                "ticker": ticker,
                **earnings_info
            })

        return results
```

**UI Integration:**
- Add "Earnings" column with date and days countdown
- Filter checkbox: "Exclude earnings in next 10 days" (default: enabled)
- Alert icon ⚠️ for unsafe windows
- Detail view: Show earnings calendar for next 4 quarters

#### 1.3 Weekly Expiration Scanner

**Data Required:**
- All available expirations (including weeklies)
- For each expiration: DTE, type (weekly/monthly)
- Options chain for weekly expirations

**Implementation:**
```python
# analyzers/weekly_scanner.py

class WeeklyScanner:
    def __init__(self, ib_connection):
        self.ib = ib_connection

    def get_all_expirations(self, ticker: str) -> List[Dict]:
        """
        Get all available expirations including weeklies

        Returns:
        [
            {
                "date": "2025-10-31",
                "dte": 7,
                "type": "weekly",
                "is_monthly": False
            },
            {
                "date": "2025-11-07",
                "dte": 14,
                "type": "weekly",
                "is_monthly": False
            },
            {
                "date": "2025-11-21",
                "dte": 28,
                "type": "monthly",
                "is_monthly": True
            }
        ]
        """
        contract = Stock(ticker, 'SMART', 'USD')
        self.ib.qualifyContracts(contract)

        # Get all option parameters
        chains = self.ib.reqSecDefOptParams(
            contract.symbol, '', contract.secType, contract.conId
        )

        if not chains:
            return []

        # Use SMART exchange chain
        chain = next(c for c in chains if c.exchange == 'SMART')

        # Process expirations
        expirations = []
        today = datetime.now().date()

        for exp_str in sorted(chain.expirations):
            exp_date = datetime.strptime(exp_str, '%Y%m%d').date()
            dte = (exp_date - today).days

            # Determine if monthly (3rd Friday)
            is_monthly = self._is_monthly_expiration(exp_date)

            expirations.append({
                "date": exp_date.isoformat(),
                "dte": dte,
                "type": "monthly" if is_monthly else "weekly",
                "is_monthly": is_monthly
            })

        return expirations

    def scan_weekly_opportunities(
        self,
        ticker: str,
        min_dte: int = 7,
        max_dte: int = 21
    ) -> List[Dict]:
        """
        Scan weekly expirations for wheel opportunities

        Focus on 1-3 week weeklies for high-frequency wheel
        """
        expirations = self.get_all_expirations(ticker)

        # Filter weekly expirations in DTE range
        weekly_exps = [
            exp for exp in expirations
            if not exp['is_monthly'] and min_dte <= exp['dte'] <= max_dte
        ]

        # Analyze each weekly
        opportunities = []
        for exp in weekly_exps:
            # Get options chain for this expiration
            puts = self._get_puts_for_expiration(ticker, exp['date'])

            # Find optimal put
            optimal = self._find_optimal_put(puts, exp['dte'])

            if optimal:
                opportunities.append({
                    **exp,
                    "optimal_put": optimal
                })

        return opportunities

    @staticmethod
    def _is_monthly_expiration(exp_date: date) -> bool:
        """Check if expiration is monthly (3rd Friday)"""
        # Monthly options expire on 3rd Friday of month
        first_day = exp_date.replace(day=1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
        third_friday = first_friday + timedelta(days=14)

        return exp_date == third_friday
```

**UI Integration:**
- Toggle: "Include Weekly Expirations" (default: enabled with IB)
- Expiration selector: Show all weeklies + monthlies
- Calendar view: Visual expiration timeline
- Summary: "X weekly opportunities" badge

### Phase 2: Enhanced Analytics (Week 2)

**Priority: SHOULD HAVE**

#### 2.1 Real-Time Greeks Streaming

```python
# analyzers/greeks_analyzer.py

class GreeksAnalyzer:
    def __init__(self, ib_connection):
        self.ib = ib_connection
        self.subscriptions = {}

    def stream_greeks(self, ticker: str, strike: float, expiration: str) -> Dict:
        """
        Stream real-time Greeks for specific option

        Returns:
        {
            "delta": 0.22,
            "gamma": 0.05,
            "theta": -0.08,
            "vega": 0.12,
            "implied_vol": 25.5,
            "timestamp": "2025-10-24T14:30:00"
        }
        """
        contract = Option(ticker, expiration, strike, 'P', 'SMART')
        self.ib.qualifyContracts(contract)

        # Request market data with Greeks
        ticker_obj = self.ib.reqMktData(
            contract,
            genericTickList='106',  # Option Greeks
            snapshot=False
        )

        # Store subscription
        self.subscriptions[f"{ticker}_{strike}_{expiration}"] = ticker_obj

        # Wait for data
        self.ib.sleep(1)

        greeks = ticker_obj.modelGreeks

        return {
            "delta": greeks.delta,
            "gamma": greeks.gamma,
            "theta": greeks.theta,
            "vega": greeks.vega,
            "implied_vol": greeks.impliedVol,
            "timestamp": datetime.now().isoformat()
        }
```

#### 2.2 OI Change Tracker

```python
# analyzers/oi_tracker.py

class OITracker:
    def __init__(self, ib_connection):
        self.ib = ib_connection
        self.history = {}  # Store daily OI snapshots

    def track_oi_changes(self, ticker: str, strike: float, expiration: str) -> Dict:
        """
        Track open interest changes

        Returns:
        {
            "oi_current": 500,
            "oi_yesterday": 350,
            "oi_change": 150,
            "oi_change_pct": 42.9,
            "signal": "BULLISH" | "NEUTRAL" | "BEARISH"
        }
        """
        # Get current OI
        contract = Option(ticker, expiration, strike, 'P', 'SMART')
        self.ib.qualifyContracts(contract)

        details = self.ib.reqContractDetails(contract)[0]
        oi_current = details.summary.openInterest

        # Get historical OI
        key = f"{ticker}_{strike}_{expiration}"
        oi_yesterday = self.history.get(key, {}).get('oi', 0)

        # Calculate change
        if oi_yesterday > 0:
            oi_change = oi_current - oi_yesterday
            oi_change_pct = (oi_change / oi_yesterday * 100)

            # Signal interpretation
            if oi_change_pct > 20:
                signal = "BULLISH"  # Growing interest
            elif oi_change_pct < -20:
                signal = "BEARISH"  # Declining interest
            else:
                signal = "NEUTRAL"
        else:
            oi_change = 0
            oi_change_pct = 0
            signal = "NEUTRAL"

        # Update history
        self.history[key] = {
            'oi': oi_current,
            'date': datetime.now().date()
        }

        return {
            "oi_current": oi_current,
            "oi_yesterday": oi_yesterday,
            "oi_change": oi_change,
            "oi_change_pct": oi_change_pct,
            "signal": signal
        }
```

### Phase 3: Advanced Features (Week 3+)

**Priority: NICE TO HAVE**

- IV skew analysis
- Put/call ratio
- Max pain calculation
- Implied move
- Order execution UI

## Connection Management

### IB Connection Module

```python
# connection/ib_manager.py

from ib_insync import IB, util
import streamlit as st

class IBManager:
    def __init__(self, config):
        self.config = config
        self.ib = IB()
        self.connected = False

    def connect(self):
        """Connect to IB Gateway or TWS"""
        try:
            self.ib.connect(
                host=self.config.host,
                port=self.config.port,
                clientId=self.config.client_id,
                readonly=True,  # Read-only for screening
                account=self.config.account  # Paper or live
            )
            self.connected = True
            return True, "Connected to IB"

        except Exception as e:
            self.connected = False
            return False, f"Connection failed: {str(e)}"

    def disconnect(self):
        """Disconnect from IB"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False

    def is_connected(self) -> bool:
        """Check connection status"""
        return self.connected and self.ib.isConnected()

    def get_connection(self):
        """Get IB connection object"""
        if not self.is_connected():
            self.connect()
        return self.ib
```

### Configuration

```python
# connection/ib_config.py

from dataclasses import dataclass
import os

@dataclass
class IBConfig:
    # Connection settings
    host: str = '127.0.0.1'
    port: int = 7497  # TWS paper trading port
    client_id: int = 1

    # Account settings
    account: str = ''  # Paper trading account
    use_paper: bool = True

    # Data settings
    iv_history_days: int = 252  # 1 year
    cache_ttl: int = 300  # 5 minutes

    # Thresholds
    min_iv_rank: float = 50.0
    earnings_safety_days: int = 10

    @classmethod
    def from_env(cls):
        """Load config from environment variables"""
        return cls(
            host=os.getenv('IB_HOST', '127.0.0.1'),
            port=int(os.getenv('IB_PORT', 7497)),
            client_id=int(os.getenv('IB_CLIENT_ID', 1)),
            account=os.getenv('IB_ACCOUNT', ''),
            use_paper=os.getenv('IB_USE_PAPER', 'true').lower() == 'true'
        )

# Port reference:
# TWS Paper Trading: 7497
# TWS Live Trading: 7496
# IB Gateway Paper: 4002
# IB Gateway Live: 4001
```

## Dashboard UI Integration

### Status Indicators

```python
# ui/ib_indicators.py

def render_ib_status(ib_manager):
    """Render IB connection status widget"""
    col1, col2, col3 = st.columns(3)

    with col1:
        if ib_manager.is_connected():
            st.success("🟢 IB Connected")
        else:
            st.error("🔴 IB Disconnected")
            if st.button("Connect"):
                success, msg = ib_manager.connect()
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

    with col2:
        account_type = "📄 Paper" if ib_manager.config.use_paper else "💰 Live"
        st.info(account_type)

    with col3:
        if ib_manager.is_connected():
            st.metric("Data Source", "IB + yfinance")
        else:
            st.warning("Data Source", "yfinance only")

def render_iv_rank_badge(iv_rank: float):
    """Render IV Rank badge with color coding"""
    if iv_rank >= 80:
        st.success(f"IV Rank: {iv_rank:.0f}% (HIGH)")
    elif iv_rank >= 50:
        st.info(f"IV Rank: {iv_rank:.0f}% (NORMAL)")
    else:
        st.warning(f"IV Rank: {iv_rank:.0f}% (LOW)")

def render_earnings_warning(earnings_info: Dict):
    """Render earnings warning if applicable"""
    if not earnings_info.get('safe_to_sell_puts'):
        st.error(f"⚠️ {earnings_info['reason']}")
    else:
        st.success(f"✅ {earnings_info['reason']}")
```

### Enhanced Summary Table

```python
def create_enhanced_summary_table(results: List[Dict]) -> pd.DataFrame:
    """
    Create summary DataFrame with IB data

    New columns:
    - IV Rank
    - Earnings Date
    - Days to Earnings
    - Weekly/Monthly indicator
    """
    rows = []
    for r in results:
        # Base columns (existing)
        base = {
            "Ticker": r['ticker'],
            "Score": f"{r['score']:.1f}",
            # ... existing columns
        }

        # IB-enhanced columns (if available)
        if 'iv_rank' in r:
            base["IV Rank"] = f"{r['iv_rank']:.0f}%"
            base["IV Status"] = r['iv_status']

        if 'earnings_info' in r:
            base["Earnings"] = r['earnings_info']['next_earnings_date']
            base["Days to Earn"] = r['earnings_info']['days_to_earnings']

        if 'expiration_type' in r:
            base["Exp Type"] = r['expiration_type']  # W or M

        rows.append(base)

    return pd.DataFrame(rows)
```

## Deployment

### Installation

```bash
# Add to requirements.txt
ib_insync>=0.9.86

# Install
pip install -r requirements.txt
```

### IB Gateway Setup

**For Paper Trading (Recommended):**

1. Download IB Gateway: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
2. Install and launch IB Gateway
3. Login with paper trading credentials
4. Configure API settings:
   - Enable ActiveX and Socket Clients: ✓
   - Socket port: 4002 (paper)
   - Trusted IP: 127.0.0.1
   - Read-Only API: ✓ (for screening only)

**Environment Variables:**

```bash
# .env file
IB_HOST=127.0.0.1
IB_PORT=4002
IB_CLIENT_ID=1
IB_ACCOUNT=DU1234567  # Your paper account
IB_USE_PAPER=true
```

### Testing

```bash
# Test IB connection
python -c "from ib_insync import IB; ib = IB(); ib.connect('127.0.0.1', 4002, clientId=1); print('Connected:', ib.isConnected())"

# Test IV Rank calculator
cd tools/trading/wheel_dashboard
python -c "
from analyzers.iv_rank_calculator import IVRankCalculator
from connection.ib_manager import IBManager, IBConfig

config = IBConfig.from_env()
manager = IBManager(config)
manager.connect()

calculator = IVRankCalculator(manager.get_connection())
iv_rank = calculator.get_iv_rank('KO', '20251128')
print(iv_rank)
"
```

## Success Criteria

### Phase 1 Complete When:
✅ IV Rank calculated for all opportunities
✅ Earnings calendar filters unsafe windows
✅ Weekly expirations displayed alongside monthlies
✅ Dashboard works with IB disconnected (graceful fallback)
✅ UI clearly indicates IB vs yfinance data source

### Phase 2 Complete When:
✅ Real-time Greeks stream for selected ticker
✅ OI changes tracked and displayed
✅ Liquidity quality score enhanced with IB data

### Quality Metrics:
- IV Rank accuracy: ±1% vs manual calculation
- Earnings dates: 100% accurate (vs yfinance 60-70%)
- Weekly expirations: 4x more opportunities
- Connection uptime: >95% during market hours

## Risk Management

### Fallback Strategy
```python
# If IB disconnected, fall back to yfinance
if not ib_manager.is_connected():
    st.warning("IB disconnected - using yfinance data (limited features)")
    use_yfinance_fallback = True
```

### Rate Limiting
```python
# IB API limits
MAX_CONCURRENT_REQUESTS = 50
REQUESTS_PER_SECOND = 5

# Throttle requests
from time import sleep
sleep(1 / REQUESTS_PER_SECOND)
```

### Error Handling
```python
# Graceful degradation
try:
    iv_rank = calculator.get_iv_rank(ticker, expiration)
except IBConnectionError:
    iv_rank = None  # Show N/A in UI
    st.warning(f"IV Rank unavailable for {ticker}")
```

## Timeline

**Week 1:** Phase 1 (Critical features)
- Days 1-2: IB connection module + config
- Days 3-4: IV Rank calculator
- Day 5: Earnings calendar integration
- Days 6-7: Weekly scanner + UI integration

**Week 2:** Phase 2 (Enhanced analytics)
- Days 1-3: Real-time Greeks streaming
- Days 4-5: OI change tracker
- Days 6-7: Testing + refinement

**Week 3+:** Phase 3 (Advanced features)
- IV skew, P/C ratio, execution UI

---

**References:**
- ib_insync docs: https://ib-insync.readthedocs.io/
- IB API guide: https://interactivebrokers.github.io/tws-api/
- Original dashboard: `tools/trading/wheel_dashboard/wheel_app.py`
- Data comparison: `docs/analysis/ib-vs-yfinance-options-data.md`
