"""
Flow Alert Notification System

Sends desktop notifications, audio alerts, and logs for critical flow events
"""

import subprocess
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


class AlertNotifier:
    """
    Multi-channel alert notification system

    Channels:
    - Desktop notifications (macOS/Linux)
    - Audio alerts
    - Log file
    - Console output
    """

    def __init__(self, enable_sound: bool = True, enable_desktop: bool = True):
        """
        Initialize alert notifier

        Args:
            enable_sound: Play audio on critical alerts
            enable_desktop: Show desktop notifications
        """
        self.enable_sound = enable_sound
        self.enable_desktop = enable_desktop

        # Create alerts log directory
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"flow_alerts_{datetime.now().strftime('%Y%m%d')}.log"

    def send_alert(self, ticker: str, alert: Dict):
        """
        Send alert through all enabled channels

        Args:
            ticker: Stock ticker
            alert: Alert dictionary from flow scanner
        """
        # Log to file
        self._log_alert(ticker, alert)

        # Console output
        self._print_alert(ticker, alert)

        # Desktop notification (CRITICAL and HIGH only)
        if self.enable_desktop and alert['severity'] in ['CRITICAL', 'HIGH']:
            self._send_desktop_notification(ticker, alert)

        # Audio alert (CRITICAL only)
        if self.enable_sound and alert['severity'] == 'CRITICAL':
            self._play_alert_sound()

    def _log_alert(self, ticker: str, alert: Dict):
        """Write alert to log file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(self.log_file, 'a') as f:
            f.write(f"\n{timestamp} | {ticker} | {alert['severity']} | {alert['title']}\n")
            f.write(f"  Message: {alert['message']}\n")
            f.write(f"  Recommendation: {alert['recommendation']}\n")
            f.write("-" * 80 + "\n")

    def _print_alert(self, ticker: str, alert: Dict):
        """Print formatted alert to console"""
        severity_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(alert['severity'], '⚪')

        print(f"\n{'='*60}")
        print(f"{severity_emoji} FLOW ALERT: {ticker} - {alert['severity']}")
        print(f"{'='*60}")
        print(f"  {alert['title']}")
        print(f"  {alert['message']}")
        print(f"  → {alert['recommendation']}")
        print(f"{'='*60}\n")

    def _send_desktop_notification(self, ticker: str, alert: Dict):
        """Send macOS desktop notification"""
        try:
            # macOS notification using osascript
            title = f"Flow Alert: {ticker}"
            message = f"{alert['title']}\n{alert['message']}"

            # Use osascript to trigger notification
            script = f'''
            display notification "{message}" with title "{title}" sound name "Glass"
            '''

            subprocess.run(
                ['osascript', '-e', script],
                check=True,
                capture_output=True
            )

        except subprocess.CalledProcessError:
            # Fallback: try terminal-notifier if installed
            try:
                subprocess.run([
                    'terminal-notifier',
                    '-title', f'Flow Alert: {ticker}',
                    '-message', alert['message'],
                    '-sound', 'Glass'
                ], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Silent fail - desktop notifications are optional
                pass

    def _play_alert_sound(self):
        """Play alert sound (macOS system sound)"""
        try:
            # Play system alert sound
            subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Silent fail - sound is optional
            pass

    def send_summary_notification(self, stats: Dict):
        """
        Send daily/hourly summary notification

        Args:
            stats: Flow statistics summary
        """
        message = f"""
Flow Summary:
  Total Alerts: {stats.get('total_alerts', 0)}
  Critical: {stats.get('critical_alerts', 0)}
  High: {stats.get('high_alerts', 0)}
  Most Active: {stats.get('most_active_ticker', 'N/A')}
        """

        print(f"\n📊 {message}")

        # Log summary
        with open(self.log_file, 'a') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(message)
            f.write(f"{'='*80}\n\n")


class AlertFilter:
    """
    Smart alert filtering to reduce noise

    Features:
    - Deduplication (don't alert on same ticker/event repeatedly)
    - Severity thresholds
    - Time-based rate limiting
    """

    def __init__(self, cooldown_minutes: int = 60, min_severity: str = 'MEDIUM'):
        """
        Initialize alert filter

        Args:
            cooldown_minutes: Minimum time between alerts for same ticker
            min_severity: Minimum severity to pass through
        """
        self.cooldown_minutes = cooldown_minutes
        self.min_severity = min_severity

        self.severity_levels = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }

        self.recent_alerts = {}  # ticker -> {last_time, last_type}

    def should_alert(self, ticker: str, alert: Dict) -> bool:
        """
        Determine if alert should be sent

        Args:
            ticker: Stock ticker
            alert: Alert dictionary

        Returns:
            True if alert should be sent
        """
        # Check severity threshold
        if self.severity_levels.get(alert['severity'], 0) < self.severity_levels.get(self.min_severity, 2):
            return False

        # Check for duplicates
        if ticker in self.recent_alerts:
            last_alert = self.recent_alerts[ticker]
            minutes_since = (datetime.now() - last_alert['time']).total_seconds() / 60

            # Same type of alert within cooldown period
            if last_alert['type'] == alert['type'] and minutes_since < self.cooldown_minutes:
                return False

        # Update recent alerts
        self.recent_alerts[ticker] = {
            'time': datetime.now(),
            'type': alert['type']
        }

        return True

    def reset(self):
        """Clear alert history"""
        self.recent_alerts = {}


# Example usage
def create_alert_callback(enable_sound: bool = True):
    """
    Create alert callback for background scanner

    Args:
        enable_sound: Enable audio alerts

    Returns:
        Callback function
    """
    notifier = AlertNotifier(enable_sound=enable_sound)
    filter_system = AlertFilter(cooldown_minutes=60, min_severity='MEDIUM')

    def callback(ticker: str, alert: Dict):
        """Alert callback"""
        if filter_system.should_alert(ticker, alert):
            notifier.send_alert(ticker, alert)

    return callback
