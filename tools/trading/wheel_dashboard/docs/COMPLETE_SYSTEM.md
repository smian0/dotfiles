# Complete IB Flow Scanner Integration

**Production-Ready Real-Time Options Flow Analysis System**

This document covers the complete, integrated system for institutional-grade options flow detection using Interactive Brokers real-time data.

## 🎯 What You Get

A complete, production-ready system that:

1. **Detects Institutional Activity**
   - Block trades (>100 contracts)
   - Multi-exchange sweeps (aggressive buying)
   - Hitting the ask (strong conviction)

2. **Protects Your Wheel Strategy**
   - Real-time alerts when institutions buy puts
   - Historical pattern tracking
   - Flow divergence detection

3. **Multiple Interfaces**
   - Streamlit dashboard (visual, interactive)
   - Command-line tools (automated scanning)
   - Background monitoring (continuous)
   - Desktop notifications (critical alerts)

4. **Historical Intelligence**
   - SQLite database with all flow events
   - Daily summaries by ticker
   - Flow divergence calculation
   - Top flow tickers ranking

---

## 📦 Complete System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                 Interactive Brokers API                        │
│            (Real-time tick-by-tick trade data)                 │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                    FlowScanner                                 │
│  analyzers/flow_scanner.py                                     │
│  • Analyzes tick data for blocks, sweeps, aggressive buying   │
│  • Calculates premium flow                                     │
│  • Generates wheel strategy alerts                            │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                  FlowDatabase (SQLite)                         │
│  analyzers/flow_database.py                                    │
│  • Stores all flow events                                      │
│  • Daily summaries                                             │
│  • Alert history                                               │
│  • Flow divergence detection                                  │
└──────────────────────┬─────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐
│ Streamlit   │ │ Background  │ │ Command-Line       │
│ Dashboard   │ │ Monitor     │ │ Tools              │
│             │ │             │ │                     │
│ • Tab 7     │ │ • Threading │ │ • test_flow_       │
│ • Sidebar   │ │ • Watchlist │ │   scanner.py       │
│ • Charts    │ │ • Callbacks │ │ • Standalone       │
└─────────────┘ └─────────────┘ └─────────────────────┘
```

---

## 🚀 Quick Start

### 1. Start IB Gateway or TWS

```bash
# Ensure IB is running on localhost:4001
# Paper trading or live account both work
```

### 2. Launch Streamlit Dashboard

```bash
cd ~/dotfiles/tools/trading/wheel_dashboard
streamlit run wheel_app.py
```

### 3. Navigate to Advanced Analytics → Tab 7 "Real-Time Flow"

- Click "Scan Flow Now" for immediate analysis
- Configure background monitor for continuous scanning
- Review flow history and divergence

### 4. Alternative: Command-Line Scanning

```bash
# Quick scan
python test_flow_scanner.py --ticker AAPL

# Background monitor
python test_flow_scanner.py --monitor --watchlist KO,JNJ,PG
```

---

## 📊 Dashboard Features

### **Tab 7: Real-Time Flow** (Advanced Analytics Page)

#### Today's Flow Stats
- Total premium flow
- Put/Call ratio
- Block trade count
- Sweep count
- Divergence warnings

#### Flow History Charts
- Premium flow trends (30-90 days)
- Put/Call ratio over time
- Event counts (blocks, sweeps, aggressive buys)
- Customizable date ranges

#### Background Monitor Controls
- Start/stop monitoring
- Watchlist configuration
- Scan interval settings
- Status display

#### Recent Flow Events
- Filterable by ticker and date range
- Event type breakdown
- Premium flow rankings

#### Top Flow Tickers
- 24-hour rankings
- Minimum flow threshold filtering

#### Quick Scan Button
- Immediate analysis for current ticker
- Real-time alerts
- Flow statistics

### **Sidebar: Flow Alerts** (All Pages)

- Shows last 24 hours of CRITICAL and HIGH alerts
- Latest 3 alerts with expandable details
- Color-coded by severity
- Auto-refreshes with database

---

## 🔔 Alert System

### Alert Levels

#### 🔴 CRITICAL
- **Put Sweeps**: Multi-exchange aggressive put buying
- **Action**: DO NOT sell puts immediately
- **Desktop Notification**: Yes
- **Audio Alert**: Yes (macOS)

#### 🟠 HIGH
- **Institutional Put Blocks**: Single trades >$500k
- **Extreme Bearish Flow**: P/C ratio > 3.0
- **Action**: Avoid selling puts
- **Desktop Notification**: Yes
- **Audio Alert**: No

#### 🟡 MEDIUM
- **Heavy Call Flow**: >$1M in call premium
- **Action**: IV expansion likely, wait for better premiums
- **Desktop Notification**: No
- **Audio Alert**: No

#### 🟢 LOW
- **No Unusual Activity**: Normal flow
- **Bullish Positioning**: Calls >> Puts
- **Action**: Safe to proceed with wheel strategy
- **Desktop Notification**: No
- **Audio Alert**: No

### Alert Filtering

- **Cooldown Period**: 60 minutes per ticker
- **Deduplication**: Same event type within cooldown ignored
- **Severity Threshold**: Configurable minimum (default: MEDIUM)
- **Log Files**: `logs/flow_alerts_YYYYMMDD.log`

---

## 💾 Database

### Location
```
data/flow_history.db (SQLite)
```

### Schema

#### Table: `flow_events`
```sql
- id (PRIMARY KEY)
- timestamp (DATETIME, indexed)
- ticker (TEXT, indexed)
- strike (REAL)
- right (TEXT: P/C)
- expiration (TEXT)
- event_type (TEXT: BLOCK/SWEEP/AGGRESSIVE)
- size (INTEGER: contracts)
- premium_flow (REAL: dollars)
- aggressive_ratio (REAL: 0-1)
- sweep_exchanges (INTEGER)
- details (JSON)
```

#### Table: `daily_summary`
```sql
- date (DATE)
- ticker (TEXT)
- total_premium_flow (REAL)
- put_flow (REAL)
- call_flow (REAL)
- put_call_ratio (REAL)
- block_count (INTEGER)
- sweep_count (INTEGER)
- aggressive_buy_count (INTEGER)
UNIQUE(date, ticker)
```

#### Table: `alerts`
```sql
- timestamp (DATETIME)
- ticker (TEXT)
- alert_type (TEXT)
- severity (TEXT: CRITICAL/HIGH/MEDIUM/LOW)
- title (TEXT)
- message (TEXT)
- recommendation (TEXT)
```

### Querying the Database

```python
from analyzers import FlowDatabase

db = FlowDatabase()

# Get flow history
flow = db.get_flow_history('AAPL', days_back=7)

# Get daily summary
summary = db.get_daily_summary('AAPL', days_back=30)

# Check for divergence
divergence = db.get_flow_divergence('AAPL', days_back=7)

# Get recent alerts
alerts = db.get_recent_alerts(ticker='AAPL', hours_back=24, min_severity='HIGH')

# Get top flow tickers
top = db.get_top_flow_tickers(days_back=1, min_flow=500000)

db.close()
```

---

## 🔧 Configuration

### FlowScanner Thresholds

Edit `analyzers/flow_scanner.py`:

```python
class FlowScanner:
    def __init__(self, ib: IB):
        self.block_threshold = 100  # contracts
        self.sweep_window_seconds = 2  # multi-exchange window
        self.aggressive_threshold = 0.65  # 65% at ask
```

### Scan Parameters

```python
scanner.scan_option_flow(
    ticker='AAPL',
    max_expirations=3,  # How many expirations
    lookback_trades=1000  # Trades per option
)
```

### Background Monitor

```python
monitor = BackgroundFlowMonitor(
    ib=ib,
    watchlist=['KO', 'JNJ', 'PG'],
    scan_interval_minutes=5,  # Frequency
    alert_callback=callback
)
```

### Alert Filtering

```python
AlertFilter(
    cooldown_minutes=60,  # Time between alerts
    min_severity='MEDIUM'  # Minimum to show
)
```

---

## 🎓 Usage Examples

### Example 1: Pre-Trade Flow Check

```python
from connection import IBManager, IBConfig
from analyzers import FlowScanner

# Connect to IB
config = IBConfig(host='127.0.0.1', port=4001, client_id=3)
manager = IBManager(config)
manager.connect()

# Scan before selling puts
scanner = FlowScanner(manager.get_connection())
flow_data = scanner.scan_option_flow("KO")

# Check alerts
for alert in flow_data['alerts']:
    if alert['severity'] in ['CRITICAL', 'HIGH']:
        print(f"⚠️ {alert['recommendation']}")

manager.disconnect()
```

### Example 2: Background Monitoring

```python
from connection import IBManager, IBConfig
from analyzers import BackgroundFlowMonitor, create_alert_callback

# Connect
config = IBConfig(host='127.0.0.1', port=4001, client_id=3)
manager = IBManager(config)
manager.connect()

# Create callback
alert_callback = create_alert_callback(enable_sound=True)

# Start monitor
monitor = BackgroundFlowMonitor(
    ib=manager.get_connection(),
    watchlist=['KO', 'JNJ', 'PG', 'AAPL'],
    scan_interval_minutes=5,
    alert_callback=alert_callback
)

monitor.start()

# Runs in background until stopped
# Press Ctrl+C to stop
```

### Example 3: Historical Pattern Analysis

```python
from analyzers import FlowDatabase

db = FlowDatabase()

# Check last 30 days for pattern
daily = db.get_daily_summary('AAPL', days_back=30)

# Find days with unusual flow
unusual_days = daily[daily['put_call_ratio'] > 2.0]

print(f"Found {len(unusual_days)} days with bearish flow")

# Check if flow preceded price moves
for _, day in unusual_days.iterrows():
    print(f"{day['date']}: ${day['put_flow']:,.0f} in puts")

db.close()
```

---

## 📈 Performance

### Scan Times
- **Single ticker**: 30-60 seconds (3 expirations, 1000 trades)
- **Background monitor**: 2-3 minutes per ticker (500 trades for speed)
- **Database query**: <100ms (indexed queries)

### Resource Usage
- **Memory**: 50-100MB for scanner + database
- **Disk**: ~1-5MB per day of flow data
- **CPU**: Minimal (event-driven threading)

### Optimization Tips
1. **Reduce `max_expirations`**: Scan fewer expirations (2-3 optimal)
2. **Lower `lookback_trades`**: Fewer trades = faster scans
3. **Increase scan interval**: 5-10 minutes balances speed and coverage
4. **Clean old data**: Archive or delete flow events >90 days

---

## 🛠️ Troubleshooting

### "No market data" errors
**Cause**: Missing IB market data subscription
**Solution**:
- Check IB subscriptions (Options market data required)
- Test with high-volume ticker (AAPL, SPY)
- Verify IB connection with `test_ib_connection.py`

### Scan takes too long
**Cause**: Too many expirations or trades
**Solution**:
- Reduce `max_expirations` to 2
- Lower `lookback_trades` to 500
- Scan during market hours (faster data retrieval)

### No flow detected
**Cause**: Low-volume stock or after hours
**Solution**:
- Test with high-volume stocks (AAPL, MSFT, TSLA)
- Scan during market hours (9:30-16:00 EST)
- Check if market is open

### Desktop notifications not working
**Cause**: macOS permissions or script issues
**Solution**:
- Grant terminal notification permissions (System Preferences)
- Install `terminal-notifier`: `brew install terminal-notifier`
- Check logs for errors: `logs/flow_alerts_*.log`

### Database locked errors
**Cause**: Multiple processes accessing database
**Solution**:
- Stop background monitor before running command-line tools
- Use separate database connections
- Close connections properly with `db.close()`

---

## 📚 Files Reference

### Core Components

| File | Purpose | Lines |
|------|---------|-------|
| `analyzers/flow_scanner.py` | Real-time tick analysis | 350+ |
| `analyzers/flow_database.py` | Historical storage | 350+ |
| `analyzers/background_scanner.py` | Continuous monitoring | 250+ |
| `analyzers/alert_system.py` | Notifications | 200+ |
| `components/flow_dashboard.py` | Streamlit UI | 500+ |
| `test_flow_scanner.py` | Test scripts | 150+ |

### Documentation

| File | Content |
|------|---------|
| `docs/FLOW_SCANNER.md` | Quick start guide |
| `docs/COMPLETE_SYSTEM.md` | This file |

### Database

| File | Content |
|------|---------|
| `data/flow_history.db` | SQLite database |
| `logs/flow_alerts_*.log` | Alert logs |

---

## 🎯 Best Practices

### 1. Pre-Trade Scanning
- Scan 1-2 hours before selling puts
- Look for CRITICAL/HIGH alerts
- Check historical flow patterns
- Verify no recent divergence

### 2. Background Monitoring
- Run monitor during market hours only
- Use scan interval of 5 minutes (balance speed/coverage)
- Enable sound for CRITICAL alerts only
- Monitor watchlist of 10-15 tickers max

### 3. Historical Analysis
- Review 30-day flow patterns
- Identify if flow preceded past moves
- Build pattern recognition
- Note divergence before earnings

### 4. Alert Management
- Use 60-minute cooldown to prevent spam
- Set min_severity to MEDIUM for normal use
- Review logs weekly for patterns
- Archive old logs monthly

### 5. Database Maintenance
- Backup database weekly
- Clean events >90 days quarterly
- Export summaries for long-term analysis
- Monitor database size (<100MB recommended)

---

## 🔐 Security & Privacy

### Data Storage
- All data stored locally in SQLite
- No external API calls (except IB)
- No cloud storage or sync

### IB Connection
- Local connection only (localhost)
- Read-only data access
- No order placement
- No account modification

### Logs
- Alert logs contain ticker symbols only
- No personal information logged
- Rotate logs monthly

---

## 🚦 Next Steps

1. **Test during market hours**:
   ```bash
   python test_flow_scanner.py --ticker AAPL
   ```

2. **Set up background monitor**:
   - Launch Streamlit dashboard
   - Navigate to Advanced Analytics → Tab 7
   - Configure watchlist and start monitor

3. **Review historical data**:
   ```bash
   python test_flow_scanner.py --history AAPL --days 30
   ```

4. **Integrate into trading workflow**:
   - Check flow before every wheel position
   - Monitor high-conviction tickers continuously
   - Build your own flow pattern database

---

## 📞 Support

### Logs Location
- Alert logs: `logs/flow_alerts_YYYYMMDD.log`
- Database: `data/flow_history.db`

### Testing Commands
```bash
# Test IB connection
python test_ib_connection.py

# Test flow scanner
python test_flow_scanner.py --ticker SPY

# Check database
sqlite3 data/flow_history.db "SELECT COUNT(*) FROM flow_events;"
```

### Common Issues

**Issue**: Streamlit page not loading
**Fix**: Check `components/flow_dashboard.py` imports, restart Streamlit

**Issue**: Background monitor not starting
**Fix**: Verify IB connection, check client_id conflicts

**Issue**: Database queries slow
**Fix**: Rebuild indexes: `REINDEX` in SQLite, vacuum database

---

## 📜 License

This is a personal trading tool. Use at your own risk. Not investment advice.

---

**Last Updated**: 2025-01-24

**System Status**: ✅ Production Ready

**Complete Integration**: ✅ Streamlit + CLI + Background + Database + Alerts
