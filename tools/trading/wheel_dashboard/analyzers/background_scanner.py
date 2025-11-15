"""
Background Options Flow Monitor

Runs continuously during market hours to:
- Monitor watchlist for unusual flow
- Send real-time alerts
- Update flow database
- Track flow patterns
"""

import time
import threading
from datetime import datetime, time as dt_time
from typing import List, Dict, Callable, Optional
import pytz
from ib_insync import IB

from .flow_scanner import FlowScanner
from .flow_database import FlowDatabase


class BackgroundFlowMonitor:
    """
    Continuous background scanner for options flow

    Features:
    - Scans watchlist every N minutes
    - Only runs during market hours
    - Saves flow to database
    - Triggers callbacks for alerts
    """

    def __init__(
        self,
        ib: IB,
        watchlist: List[str],
        scan_interval_minutes: int = 5,
        alert_callback: Optional[Callable] = None
    ):
        """
        Initialize background monitor

        Args:
            ib: Active IB connection
            watchlist: List of tickers to monitor
            scan_interval_minutes: How often to scan (default: 5 min)
            alert_callback: Function to call when alert is triggered
        """
        self.ib = ib
        self.watchlist = watchlist
        self.scan_interval = scan_interval_minutes * 60  # Convert to seconds
        self.alert_callback = alert_callback

        self.scanner = FlowScanner(ib)
        self.database = FlowDatabase()

        self.is_running = False
        self.thread = None

        # Market hours (NYSE)
        self.market_tz = pytz.timezone('America/New_York')
        self.market_open = dt_time(9, 30)
        self.market_close = dt_time(16, 0)

        # Alert tracking (avoid duplicate alerts)
        self.recent_alerts = {}  # ticker -> last_alert_time

    def start(self):
        """Start background monitoring"""
        if self.is_running:
            print("⚠️ Monitor already running")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        print(f"✅ Background flow monitor started")
        print(f"   Watchlist: {', '.join(self.watchlist)}")
        print(f"   Scan interval: {self.scan_interval // 60} minutes")

    def stop(self):
        """Stop background monitoring"""
        self.is_running = False

        if self.thread:
            self.thread.join(timeout=5)

        print("🛑 Background flow monitor stopped")

    def _is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now(self.market_tz)
        current_time = now.time()
        current_weekday = now.weekday()

        # Monday = 0, Friday = 4
        is_weekday = 0 <= current_weekday <= 4

        # Check time
        is_market_hours = self.market_open <= current_time <= self.market_close

        return is_weekday and is_market_hours

    def _monitor_loop(self):
        """Main monitoring loop"""
        print(f"\n🔄 Starting monitoring loop...")

        while self.is_running:
            try:
                # Check if market is open
                if not self._is_market_open():
                    # Market closed - wait and check again
                    next_open = self._get_next_market_open()
                    print(f"\n💤 Market closed. Next scan at market open: {next_open.strftime('%Y-%m-%d %H:%M %Z')}")
                    time.sleep(60)  # Check every minute
                    continue

                # Market is open - scan watchlist
                print(f"\n{'='*60}")
                print(f"🔍 Flow Scan - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}\n")

                for ticker in self.watchlist:
                    try:
                        self._scan_ticker(ticker)
                    except Exception as e:
                        print(f"❌ Error scanning {ticker}: {e}")
                        continue

                # Wait for next scan
                print(f"\n⏳ Next scan in {self.scan_interval // 60} minutes...")
                time.sleep(self.scan_interval)

            except Exception as e:
                print(f"❌ Monitor loop error: {e}")
                time.sleep(60)  # Wait a minute before retrying

    def _scan_ticker(self, ticker: str):
        """
        Scan single ticker and process results

        Args:
            ticker: Stock ticker to scan
        """
        print(f"\n📊 Scanning {ticker}...")

        # Scan flow
        flow_data = self.scanner.scan_option_flow(
            ticker,
            max_expirations=2,  # Scan fewer expirations for speed
            lookback_trades=500  # Fewer trades for faster scans
        )

        # Save to database
        self._save_flow_data(ticker, flow_data)

        # Process alerts
        self._process_alerts(ticker, flow_data['alerts'])

    def _save_flow_data(self, ticker: str, flow_data: Dict):
        """
        Save flow data to database

        Args:
            ticker: Stock ticker
            flow_data: Flow scan results
        """
        # Save daily summary
        stats = flow_data['flow_stats'].copy()
        stats['block_count'] = len(flow_data['block_trades'])
        stats['sweep_count'] = len(flow_data['sweeps'])
        stats['aggressive_count'] = len(flow_data['aggressive_buys'])

        self.database.save_daily_summary(ticker, stats)

        # Save individual events
        for event in flow_data['block_trades'] + flow_data['sweeps'] + flow_data['aggressive_buys']:
            self.database.save_flow_event(event)

    def _process_alerts(self, ticker: str, alerts: List[Dict]):
        """
        Process flow alerts

        Args:
            ticker: Stock ticker
            alerts: List of alert dictionaries
        """
        now = datetime.now()

        for alert in alerts:
            # Skip low severity if configured
            if alert['severity'] in ['LOW']:
                continue

            # Check for duplicate alerts (avoid spam)
            if ticker in self.recent_alerts:
                last_alert_time = self.recent_alerts[ticker]
                minutes_since = (now - last_alert_time).total_seconds() / 60

                # Only alert once per hour per ticker
                if minutes_since < 60:
                    continue

            # Save alert to database
            self.database.save_alert(ticker, alert)

            # Update recent alerts
            self.recent_alerts[ticker] = now

            # Trigger callback if provided
            if self.alert_callback:
                try:
                    self.alert_callback(ticker, alert)
                except Exception as e:
                    print(f"❌ Alert callback error: {e}")

            # Print alert
            self._print_alert(ticker, alert)

    def _print_alert(self, ticker: str, alert: Dict):
        """Print formatted alert"""
        severity_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(alert['severity'], '⚪')

        print(f"\n{severity_emoji} ALERT: {ticker}")
        print(f"  {alert['title']}")
        print(f"  {alert['message']}")
        print(f"  → {alert['recommendation']}")
        print(f"  Time: {alert['timestamp'].strftime('%H:%M:%S')}\n")

    def _get_next_market_open(self) -> datetime:
        """Calculate next market open time"""
        now = datetime.now(self.market_tz)

        # If before market open today, return today's open
        if now.time() < self.market_open:
            return now.replace(
                hour=self.market_open.hour,
                minute=self.market_open.minute,
                second=0,
                microsecond=0
            )

        # Otherwise, find next weekday
        days_ahead = 1
        if now.weekday() == 4:  # Friday
            days_ahead = 3  # Skip to Monday
        elif now.weekday() == 5:  # Saturday
            days_ahead = 2

        next_open = now + pytz.timezone('America/New_York').localize(
            datetime.timedelta(days=days_ahead)
        )

        return next_open.replace(
            hour=self.market_open.hour,
            minute=self.market_open.minute,
            second=0,
            microsecond=0
        )

    def get_status(self) -> Dict:
        """Get current monitor status"""
        return {
            'running': self.is_running,
            'watchlist': self.watchlist,
            'scan_interval_minutes': self.scan_interval // 60,
            'market_open': self._is_market_open(),
            'recent_alerts_count': len(self.recent_alerts)
        }

    def add_ticker(self, ticker: str):
        """Add ticker to watchlist"""
        if ticker not in self.watchlist:
            self.watchlist.append(ticker)
            print(f"✅ Added {ticker} to watchlist")

    def remove_ticker(self, ticker: str):
        """Remove ticker from watchlist"""
        if ticker in self.watchlist:
            self.watchlist.remove(ticker)
            print(f"🗑️ Removed {ticker} from watchlist")

    def set_scan_interval(self, minutes: int):
        """Change scan interval"""
        self.scan_interval = minutes * 60
        print(f"⏱️ Scan interval updated to {minutes} minutes")
