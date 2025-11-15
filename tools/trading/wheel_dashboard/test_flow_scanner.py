#!/usr/bin/env python3
"""
Test Script for Real-Time Options Flow Scanner

Tests all flow detection components:
1. FlowScanner - Real-time flow analysis
2. FlowDatabase - Historical tracking
3. BackgroundMonitor - Continuous monitoring
4. AlertSystem - Notifications

Usage:
    python test_flow_scanner.py --ticker AAPL
    python test_flow_scanner.py --monitor --watchlist KO,JNJ,PG
    python test_flow_scanner.py --history AAPL --days 7
"""

import argparse
from connection import IBManager, IBConfig
from analyzers.flow_scanner import FlowScanner
from analyzers.flow_database import FlowDatabase
from analyzers.background_scanner import BackgroundFlowMonitor
from analyzers.alert_system import create_alert_callback
import time


def test_flow_scan(ticker: str):
    """
    Test basic flow scanning on a single ticker

    Args:
        ticker: Stock ticker to scan
    """
    print(f"\n{'='*60}")
    print(f"TEST 1: Basic Flow Scan")
    print(f"{'='*60}\n")

    # Connect to IB
    config = IBConfig(host='127.0.0.1', port=4001, client_id=3, use_paper=False)
    manager = IBManager(config)

    success, message = manager.connect()
    if not success:
        print(f"❌ Failed to connect to IB: {message}")
        return

    print(f"✅ Connected to IB ({message})\n")

    # Initialize scanner
    ib = manager.get_connection()
    scanner = FlowScanner(ib)

    # Scan ticker
    print(f"🔍 Scanning {ticker} for unusual flow...\n")

    flow_data = scanner.scan_option_flow(
        ticker=ticker,
        max_expirations=3,
        lookback_trades=1000
    )

    # Results are printed by scanner
    print(f"\n✅ Scan complete!\n")

    # Disconnect
    manager.disconnect()


def test_flow_database(ticker: str, days: int = 7):
    """
    Test flow database and historical tracking

    Args:
        ticker: Stock ticker
        days: Days of history to retrieve
    """
    print(f"\n{'='*60}")
    print(f"TEST 2: Flow Database & History")
    print(f"{'='*60}\n")

    # Initialize database
    db = FlowDatabase()

    # Get flow history
    print(f"📚 Retrieving {days} days of flow history for {ticker}...\n")

    flow_history = db.get_flow_history(ticker, days_back=days)

    if flow_history.empty:
        print(f"ℹ️ No historical flow data found for {ticker}")
        print(f"   Run a scan first to populate database\n")
    else:
        print(f"📊 Found {len(flow_history)} flow events:\n")

        # Show summary by event type
        event_counts = flow_history['event_type'].value_counts()
        for event_type, count in event_counts.items():
            print(f"   {event_type}: {count}")

        print(f"\n📈 Daily Summary:")
        daily = db.get_daily_summary(ticker, days_back=days)

        if not daily.empty:
            for _, row in daily.head(5).iterrows():
                print(f"\n   Date: {row['date']}")
                print(f"   Total Flow: ${row['total_premium_flow']:,.0f}")
                print(f"   Put/Call Ratio: {row['put_call_ratio']:.2f}")
                print(f"   Blocks: {row['block_count']}, Sweeps: {row['sweep_count']}")

    # Get recent alerts
    print(f"\n🚨 Recent Alerts (last 24 hours):")
    alerts = db.get_recent_alerts(ticker=ticker, hours_back=24, min_severity='MEDIUM')

    if alerts.empty:
        print(f"   No recent alerts for {ticker}\n")
    else:
        for _, alert in alerts.iterrows():
            print(f"\n   [{alert['timestamp']}] {alert['severity']}")
            print(f"   {alert['title']}")
            print(f"   → {alert['recommendation']}")

    # Flow divergence check
    print(f"\n🔍 Checking for flow divergence...")
    divergence = db.get_flow_divergence(ticker, days_back=7)

    if divergence['has_divergence']:
        print(f"   ⚠️ DIVERGENCE DETECTED!")

        if divergence.get('put_divergence'):
            print(f"   📉 Put flow: ${divergence['today_put_flow']:,.0f} (avg: ${divergence['avg_put_flow']:,.0f})")

        if divergence.get('call_divergence'):
            print(f"   📈 Call flow: ${divergence['today_call_flow']:,.0f} (avg: ${divergence['avg_call_flow']:,.0f})")
    else:
        print(f"   ✅ No unusual divergence detected\n")

    db.close()


def test_background_monitor(watchlist: list, duration_minutes: int = 5):
    """
    Test background monitoring

    Args:
        watchlist: List of tickers to monitor
        duration_minutes: How long to run monitor (for testing)
    """
    print(f"\n{'='*60}")
    print(f"TEST 3: Background Monitor")
    print(f"{'='*60}\n")

    # Connect to IB
    config = IBConfig(host='127.0.0.1', port=4001, client_id=3, use_paper=False)
    manager = IBManager(config)

    success, message = manager.connect()
    if not success:
        print(f"❌ Failed to connect to IB: {message}")
        return

    print(f"✅ Connected to IB ({message})\n")

    # Create alert callback
    alert_callback = create_alert_callback(enable_sound=True)

    # Initialize background monitor
    ib = manager.get_connection()
    monitor = BackgroundFlowMonitor(
        ib=ib,
        watchlist=watchlist,
        scan_interval_minutes=1,  # Fast scanning for testing
        alert_callback=alert_callback
    )

    # Start monitoring
    monitor.start()

    print(f"\n⏱️ Running monitor for {duration_minutes} minutes (Ctrl+C to stop)...")
    print(f"   Watchlist: {', '.join(watchlist)}\n")

    try:
        # Run for specified duration
        time.sleep(duration_minutes * 60)

    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopping monitor...")

    finally:
        monitor.stop()
        manager.disconnect()

    print(f"\n✅ Background monitor test complete\n")


def main():
    parser = argparse.ArgumentParser(description='Test IB Flow Scanner')

    parser.add_argument('--ticker', type=str, help='Single ticker to scan')
    parser.add_argument('--monitor', action='store_true', help='Run background monitor')
    parser.add_argument('--watchlist', type=str, help='Comma-separated watchlist for monitor')
    parser.add_argument('--history', type=str, help='Show flow history for ticker')
    parser.add_argument('--days', type=int, default=7, help='Days of history to retrieve')
    parser.add_argument('--duration', type=int, default=5, help='Minutes to run monitor (for testing)')

    args = parser.parse_args()

    # Test 1: Basic flow scan
    if args.ticker:
        test_flow_scan(args.ticker)

    # Test 2: Flow history
    if args.history:
        test_flow_database(args.history, args.days)

    # Test 3: Background monitor
    if args.monitor:
        if not args.watchlist:
            print("❌ --watchlist required for background monitor")
            return

        watchlist = [t.strip().upper() for t in args.watchlist.split(',')]
        test_background_monitor(watchlist, args.duration)

    # If no args, show help
    if not any([args.ticker, args.monitor, args.history]):
        parser.print_help()
        print(f"\n💡 Examples:")
        print(f"   python test_flow_scanner.py --ticker AAPL")
        print(f"   python test_flow_scanner.py --history AAPL --days 7")
        print(f"   python test_flow_scanner.py --monitor --watchlist KO,JNJ,PG --duration 10")


if __name__ == "__main__":
    main()
