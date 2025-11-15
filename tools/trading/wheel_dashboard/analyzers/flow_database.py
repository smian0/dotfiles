"""
Historical Options Flow Database

Stores and tracks unusual options activity over time for:
- Pattern recognition (what preceded big moves)
- Smart money tracking
- Flow divergence detection
- Historical backtesting
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path


class FlowDatabase:
    """
    SQLite database for tracking options flow history

    Tables:
    - flow_events: Individual unusual flow events
    - daily_summary: Daily flow aggregates by ticker
    - alerts: Historical alert log
    """

    def __init__(self, db_path: str = "data/flow_history.db"):
        """
        Initialize flow database

        Args:
            db_path: Path to SQLite database file
        """
        # Create data directory if needed
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Table 1: Individual flow events
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS flow_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            ticker TEXT NOT NULL,
            strike REAL NOT NULL,
            right TEXT NOT NULL,
            expiration TEXT NOT NULL,
            event_type TEXT NOT NULL,
            size INTEGER NOT NULL,
            premium_flow REAL NOT NULL,
            aggressive_ratio REAL,
            sweep_exchanges INTEGER,
            details TEXT
        )
        """)

        # Create indexes for flow_events
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ticker_time
        ON flow_events (ticker, timestamp)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_event_type
        ON flow_events (event_type)
        """)

        # Table 2: Daily summary
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            ticker TEXT NOT NULL,
            total_premium_flow REAL NOT NULL,
            put_flow REAL NOT NULL,
            call_flow REAL NOT NULL,
            put_call_ratio REAL NOT NULL,
            block_count INTEGER NOT NULL,
            sweep_count INTEGER NOT NULL,
            aggressive_buy_count INTEGER NOT NULL,
            UNIQUE(date, ticker)
        )
        """)

        # Table 3: Alert history
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            ticker TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            recommendation TEXT NOT NULL
        )
        """)

        # Create index for alerts
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_alert_ticker_time
        ON alerts (ticker, timestamp)
        """)

        self.conn.commit()

    def save_flow_event(self, event: Dict):
        """
        Save individual flow event

        Args:
            event: Flow event dictionary from FlowScanner
        """
        cursor = self.conn.cursor()

        # Determine event type
        event_type = []
        if event.get('block_trade'):
            event_type.append('BLOCK')
        if event.get('is_sweep'):
            event_type.append('SWEEP')
        if event.get('aggressive_buy'):
            event_type.append('AGGRESSIVE')

        event_type_str = ','.join(event_type) if event_type else 'NORMAL'

        cursor.execute("""
        INSERT INTO flow_events (
            timestamp, ticker, strike, right, expiration,
            event_type, size, premium_flow, aggressive_ratio,
            sweep_exchanges, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(),
            event['ticker'],
            event['strike'],
            event['right'],
            event['expiration'],
            event_type_str,
            event['total_volume'],
            event['premium_flow'],
            event.get('aggressive_ratio', 0),
            event.get('sweep_exchanges', 0),
            f"Avg trade: {event.get('avg_trade_size', 0):.0f} contracts"
        ))

        self.conn.commit()

    def save_daily_summary(self, ticker: str, flow_stats: Dict):
        """
        Save or update daily flow summary

        Args:
            ticker: Stock ticker
            flow_stats: Flow statistics from scan
        """
        cursor = self.conn.cursor()
        today = datetime.now().date()

        put_flow = flow_stats.get('put_flow', 0)
        call_flow = flow_stats.get('call_flow', 0)
        put_call_ratio = put_flow / call_flow if call_flow > 0 else 0

        cursor.execute("""
        INSERT OR REPLACE INTO daily_summary (
            date, ticker, total_premium_flow, put_flow, call_flow,
            put_call_ratio, block_count, sweep_count, aggressive_buy_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today,
            ticker,
            flow_stats.get('total_premium_flow', 0),
            put_flow,
            call_flow,
            put_call_ratio,
            flow_stats.get('block_count', 0),
            flow_stats.get('sweep_count', 0),
            flow_stats.get('aggressive_count', 0)
        ))

        self.conn.commit()

    def save_alert(self, ticker: str, alert: Dict):
        """
        Save flow alert to history

        Args:
            ticker: Stock ticker
            alert: Alert dictionary
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO alerts (
            timestamp, ticker, alert_type, severity,
            title, message, recommendation
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.get('timestamp', datetime.now()),
            ticker,
            alert['type'],
            alert['severity'],
            alert['title'],
            alert['message'],
            alert['recommendation']
        ))

        self.conn.commit()

    def get_flow_history(
        self,
        ticker: str,
        days_back: int = 30,
        event_types: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get historical flow events for a ticker

        Args:
            ticker: Stock ticker
            days_back: Number of days to look back
            event_types: Filter by event types (BLOCK, SWEEP, AGGRESSIVE)

        Returns:
            DataFrame of flow events
        """
        query = """
        SELECT * FROM flow_events
        WHERE ticker = ?
        AND timestamp >= datetime('now', ?)
        """

        params = [ticker, f'-{days_back} days']

        if event_types:
            placeholders = ','.join(['?' for _ in event_types])
            query += f" AND event_type IN ({placeholders})"
            params.extend(event_types)

        query += " ORDER BY timestamp DESC"

        df = pd.read_sql_query(query, self.conn, params=params)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        return df

    def get_daily_summary(self, ticker: str, days_back: int = 90) -> pd.DataFrame:
        """
        Get daily flow summary for charting

        Args:
            ticker: Stock ticker
            days_back: Number of days to look back

        Returns:
            DataFrame of daily summaries
        """
        query = """
        SELECT * FROM daily_summary
        WHERE ticker = ?
        AND date >= date('now', ?)
        ORDER BY date DESC
        """

        df = pd.read_sql_query(
            query,
            self.conn,
            params=[ticker, f'-{days_back} days']
        )
        df['date'] = pd.to_datetime(df['date'])

        return df

    def get_recent_alerts(
        self,
        ticker: Optional[str] = None,
        hours_back: int = 24,
        min_severity: str = 'MEDIUM'
    ) -> pd.DataFrame:
        """
        Get recent flow alerts

        Args:
            ticker: Filter by ticker (None = all tickers)
            hours_back: Number of hours to look back
            min_severity: Minimum severity (LOW, MEDIUM, HIGH, CRITICAL)

        Returns:
            DataFrame of alerts
        """
        severity_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        min_level = severity_levels.get(min_severity, 2)

        query = """
        SELECT * FROM alerts
        WHERE timestamp >= datetime('now', ?)
        """

        params = [f'-{hours_back} hours']

        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)

        query += " ORDER BY timestamp DESC"

        df = pd.read_sql_query(query, self.conn, params=params)

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Filter by severity level
            df['severity_level'] = df['severity'].map(severity_levels)
            df = df[df['severity_level'] >= min_level]
            df = df.drop('severity_level', axis=1)

        return df

    def get_flow_divergence(self, ticker: str, days_back: int = 7) -> Dict:
        """
        Detect flow divergence (unusual patterns vs historical)

        Args:
            ticker: Stock ticker
            days_back: Number of days for baseline

        Returns:
            Dictionary with divergence metrics
        """
        df = self.get_daily_summary(ticker, days_back)

        if df.empty or len(df) < 3:
            return {'has_divergence': False}

        # Calculate averages
        avg_put_flow = df['put_flow'].mean()
        avg_call_flow = df['call_flow'].mean()
        avg_pcr = df['put_call_ratio'].mean()

        # Get today's data
        today = df.iloc[0]

        # Detect divergence (today > 2x average)
        put_divergence = today['put_flow'] > (avg_put_flow * 2)
        call_divergence = today['call_flow'] > (avg_call_flow * 2)
        pcr_divergence = abs(today['put_call_ratio'] - avg_pcr) > 1.0

        return {
            'has_divergence': put_divergence or call_divergence or pcr_divergence,
            'put_divergence': put_divergence,
            'call_divergence': call_divergence,
            'pcr_divergence': pcr_divergence,
            'today_put_flow': today['put_flow'],
            'avg_put_flow': avg_put_flow,
            'today_call_flow': today['call_flow'],
            'avg_call_flow': avg_call_flow,
            'today_pcr': today['put_call_ratio'],
            'avg_pcr': avg_pcr
        }

    def get_top_flow_tickers(self, days_back: int = 1, min_flow: float = 1000000) -> pd.DataFrame:
        """
        Get tickers with highest unusual flow

        Args:
            days_back: Number of days to aggregate
            min_flow: Minimum total flow to include

        Returns:
            DataFrame of top flow tickers
        """
        query = """
        SELECT
            ticker,
            SUM(total_premium_flow) as total_flow,
            SUM(put_flow) as total_put_flow,
            SUM(call_flow) as total_call_flow,
            AVG(put_call_ratio) as avg_pcr,
            SUM(block_count) as total_blocks,
            SUM(sweep_count) as total_sweeps
        FROM daily_summary
        WHERE date >= date('now', ?)
        GROUP BY ticker
        HAVING total_flow >= ?
        ORDER BY total_flow DESC
        LIMIT 20
        """

        df = pd.read_sql_query(
            query,
            self.conn,
            params=[f'-{days_back} days', min_flow]
        )

        return df

    def cleanup_old_data(self, days_to_keep: int = 90):
        """
        Remove old flow data to keep database size manageable

        Args:
            days_to_keep: Number of days of history to retain
        """
        cursor = self.conn.cursor()

        # Delete old flow events
        cursor.execute("""
        DELETE FROM flow_events
        WHERE timestamp < datetime('now', ?)
        """, (f'-{days_to_keep} days',))

        # Delete old daily summaries
        cursor.execute("""
        DELETE FROM daily_summary
        WHERE date < date('now', ?)
        """, (f'-{days_to_keep} days',))

        # Delete old alerts
        cursor.execute("""
        DELETE FROM alerts
        WHERE timestamp < datetime('now', ?)
        """, (f'-{days_to_keep} days',))

        self.conn.commit()

        print(f"✅ Cleaned up data older than {days_to_keep} days")

    def close(self):
        """Close database connection"""
        self.conn.close()
