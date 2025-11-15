# Real-Time Options Flow Scanner

Institutional-grade options flow detection using Interactive Brokers real-time data.

## What It Detects

### 1. **Block Trades** (Institutional Positioning)
- Single trades >100 contracts
- Indicates institutional money entering positions
- **Signal**: Large players making bets

### 2. **Sweeps** (Aggressive Buying)
- Multiple exchanges hit simultaneously (< 2 seconds)
- Traders willing to pay up across all venues
- **Signal**: Urgent positioning, strong conviction

### 3. **Aggressive Buyers** (Hitting the Ask)
- >65% of volume traded at ask price
- Indicates buyers paying premium to get in
- **Signal**: Strong directional bias

## Quick Start

### Option 1: Single Ticker Scan

```bash
python test_flow_scanner.py --ticker AAPL
```

**What this does:**
- Scans AAPL options (3 expirations)
- Analyzes last 1000 trades per option
- Detects blocks, sweeps, aggressive buying
- Generates wheel strategy alerts
- Takes ~30-60 seconds

**Example Output:**
```
🔍 Scanning Options Flow for AAPL
📊 Found 15 expirations on SMART
📅 Scanning expiration 1/3: 2024-01-19
   Analyzing 45 strikes near ATM
   🎯 BLOCK: P 175 - 250 contracts
   💥 SWEEP: P 170 - 3 exchanges

📊 FLOW ANALYSIS SUMMARY: AAPL
💰 Premium Flow:
   Total: $2,450,000
   Puts:  $1,800,000
   Calls: $650,000

🚨 ALERTS (1):
🟠 🚨 INSTITUTIONAL PUT BLOCKS
   4 large put blocks totaling 850 contracts
   → 🛑 AVOID selling puts on AAPL - Institutions hedging/betting on downside
```

### Option 2: View Historical Flow

```bash
python test_flow_scanner.py --history AAPL --days 7
```

**What this does:**
- Retrieves 7 days of stored flow data
- Shows event counts (blocks, sweeps, etc.)
- Daily flow summaries
- Recent alerts
- Flow divergence detection

**Use Case**: Check if unusual flow preceded a big move

### Option 3: Background Monitoring

```bash
python test_flow_scanner.py --monitor --watchlist KO,JNJ,PG --duration 10
```

**What this does:**
- Monitors watchlist continuously
- Scans every 5 minutes during market hours
- Sends desktop notifications for critical alerts
- Saves all flow to database
- Runs for 10 minutes (for testing)

**Production Use**: Remove `--duration` to run indefinitely

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IB Real-Time Data                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   FlowScanner                               │
│  • Analyzes tick-by-tick trades                            │
│  • Detects blocks, sweeps, aggressive buyers               │
│  • Calculates premium flow                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FlowDatabase (SQLite)                      │
│  • Stores all flow events                                  │
│  • Daily summaries                                         │
│  • Alert history                                           │
│  • Flow divergence detection                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              BackgroundFlowMonitor                          │
│  • Continuous scanning during market hours                 │
│  • Alert callbacks                                         │
│  • Watchlist management                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  AlertSystem                                │
│  • Desktop notifications (macOS)                           │
│  • Audio alerts (critical only)                           │
│  • Log files                                               │
│  • Smart filtering (deduplication)                        │
└─────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Scan Before Selling Puts

```python
from connection import IBManager, IBConfig
from analyzers import FlowScanner

# Connect to IB
config = IBConfig(host='127.0.0.1', port=4001, client_id=3, use_paper=False)
manager = IBManager(config)
manager.connect()

# Scan flow
scanner = FlowScanner(manager.get_connection())
flow_data = scanner.scan_option_flow("AAPL")

# Check for warnings
for alert in flow_data['alerts']:
    if alert['severity'] in ['CRITICAL', 'HIGH']:
        print(f"⚠️ {alert['recommendation']}")

manager.disconnect()
```

### Background Monitor with Alerts

```python
from connection import IBManager, IBConfig
from analyzers import BackgroundFlowMonitor, create_alert_callback

# Connect to IB
config = IBConfig(host='127.0.0.1', port=4001, client_id=3, use_paper=False)
manager = IBManager(config)
manager.connect()

# Create alert callback (with desktop notifications)
alert_callback = create_alert_callback(enable_sound=True)

# Start background monitor
monitor = BackgroundFlowMonitor(
    ib=manager.get_connection(),
    watchlist=['KO', 'JNJ', 'PG', 'AAPL'],
    scan_interval_minutes=5,
    alert_callback=alert_callback
)

monitor.start()

# Monitor runs in background
# Press Ctrl+C to stop
```

### Query Historical Flow

```python
from analyzers import FlowDatabase

db = FlowDatabase()

# Get last 7 days of flow for AAPL
flow_history = db.get_flow_history('AAPL', days_back=7)

# Get daily summary (for charting)
daily_summary = db.get_daily_summary('AAPL', days_back=30)

# Check for flow divergence
divergence = db.get_flow_divergence('AAPL', days_back=7)

if divergence['has_divergence']:
    print(f"⚠️ Unusual flow detected!")
    print(f"   Today: ${divergence['today_put_flow']:,.0f}")
    print(f"   Average: ${divergence['avg_put_flow']:,.0f}")

db.close()
```

## Alert Types

### 🔴 CRITICAL - Immediate Action Required
- **Put Sweeps**: Multi-exchange aggressive put buying
- **Recommendation**: DO NOT sell puts, urgent

### 🟠 HIGH - Strong Warning
- **Institutional Put Blocks**: Large put trades (>$500k)
- **Extreme Bearish Flow**: Put/Call ratio > 3.0
- **Recommendation**: Avoid selling puts

### 🟡 MEDIUM - Monitor Closely
- **Heavy Call Flow**: >$1M in call premium
- **Recommendation**: IV expansion likely, wait for better premiums

### 🟢 LOW - Informational
- **No Unusual Activity**: Normal flow
- **Bullish Positioning**: Calls >> Puts
- **Recommendation**: Safe to proceed with wheel strategy

## Database Schema

### flow_events
```sql
id, timestamp, ticker, strike, right, expiration,
event_type, size, premium_flow, aggressive_ratio,
sweep_exchanges, details
```

### daily_summary
```sql
id, date, ticker, total_premium_flow, put_flow, call_flow,
put_call_ratio, block_count, sweep_count, aggressive_buy_count
```

### alerts
```sql
id, timestamp, ticker, alert_type, severity,
title, message, recommendation
```

## Requirements

- **IB Account**: Active Interactive Brokers account
- **Market Data**: Options market data subscription
  - Usually included with IB Pro ($10/month)
  - Or free with active trading
- **Connection**: TWS or IB Gateway running locally
- **Python**: 3.8+
- **Dependencies**: ib_insync, pandas, sqlite3 (built-in)

## Performance

- **Single ticker scan**: ~30-60 seconds (3 expirations, 1000 trades)
- **Background monitoring**: ~2-3 minutes per ticker (fewer trades for speed)
- **Database**: Efficient SQLite with indexes
- **Memory**: ~50-100MB for scanner + database

## Configuration

### Thresholds (in FlowScanner)
```python
self.block_threshold = 100  # contracts
self.sweep_window_seconds = 2  # multi-exchange window
self.aggressive_threshold = 0.65  # 65% at ask
```

### Scan Parameters
```python
scanner.scan_option_flow(
    ticker='AAPL',
    max_expirations=3,  # How many expirations to scan
    lookback_trades=1000  # Trades per option
)
```

### Alert Filtering
```python
AlertFilter(
    cooldown_minutes=60,  # Min time between alerts
    min_severity='MEDIUM'  # Minimum to pass through
)
```

## Troubleshooting

### "No market data" errors
- **Solution**: Check IB market data subscriptions
- **Test**: Try a popular ticker (AAPL, SPY) first

### Scan takes too long
- **Solution**: Reduce `max_expirations` or `lookback_trades`
- **Optimal**: 2-3 expirations, 500 trades

### No flow detected
- **Normal**: Low-volume stocks may have no unusual activity
- **Try**: High-volume stocks (AAPL, MSFT, TSLA)

### Desktop notifications not working
- **macOS**: Should work out of box (osascript)
- **Optional**: Install `terminal-notifier` for better notifications

## Best Practices

1. **Scan before opening positions**
   - Check flow 1-2 hours before selling puts
   - Look for CRITICAL/HIGH alerts

2. **Monitor during market hours**
   - Run background monitor on watchlist
   - Set `scan_interval_minutes=5` (balance speed vs detail)

3. **Review historical patterns**
   - Check if flow preceded past moves
   - Build pattern recognition

4. **Combine with other signals**
   - Flow + IV Rank + Earnings = complete picture
   - Don't rely solely on flow

5. **Alert fatigue prevention**
   - Use AlertFilter with 60-minute cooldown
   - Only enable sound for CRITICAL

## Next Steps

1. **Test with live data** (during market hours):
   ```bash
   python test_flow_scanner.py --ticker AAPL
   ```

2. **Set up background monitor**:
   ```bash
   python test_flow_scanner.py --monitor --watchlist KO,JNJ,PG,AAPL
   ```

3. **Review flow history**:
   ```bash
   python test_flow_scanner.py --history AAPL --days 30
   ```

4. **Integrate with dashboard** (future feature):
   - Real-time flow alerts in Streamlit sidebar
   - Flow history charts
   - Divergence warnings

## Support

For issues or questions:
1. Check IB connection: `python test_ib_connection.py`
2. Verify market data: Try AAPL or SPY first
3. Review logs: `logs/flow_alerts_YYYYMMDD.log`
4. Database location: `data/flow_history.db`
