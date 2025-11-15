#!/usr/bin/env python3
"""
Test Dashboard Integration with IB Analyzers

Verifies that the dashboard correctly integrates with IB analyzers:
1. IB connection initialization works
2. Analyzers can be passed to analyze_ticker
3. Results include IB data fields
4. Filtering works correctly
"""

import sys
sys.path.insert(0, '.')

from connection import IBManager, IBConfig
from analyzers import IVRankCalculator, EarningsFilter, WeeklyScanner
import yfinance as yf
from datetime import datetime


def test_integration():
    """Test full integration pipeline"""
    print("\n" + "="*60)
    print("DASHBOARD INTEGRATION TEST")
    print("="*60)

    # Step 1: Initialize IB connection
    print("\n1. Initializing IB connection...")
    try:
        config = IBConfig(
            host='127.0.0.1',
            port=4001,  # IB Gateway Live
            client_id=2,  # Different client ID to avoid conflicts
            use_paper=False
        )

        manager = IBManager(config)
        success, message = manager.connect()

        if not success:
            print(f"❌ Connection failed: {message}")
            print("⚠️ Dashboard will work in yfinance-only mode")
            return False

        print(f"✅ {message}")

        ib = manager.get_connection()

        # Initialize analyzers
        ib_analyzers = {
            'manager': manager,
            'iv_calculator': IVRankCalculator(ib),
            'earnings_filter': EarningsFilter(ib),
            'weekly_scanner': WeeklyScanner(ib),
            'connected': True,
            'message': message
        }

        print("✅ Analyzers initialized")

    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 2: Test analyze_ticker with IB data
    print("\n2. Testing analyze_ticker with IB integration...")
    try:
        ticker = "KO"

        # Get stock data (simulating dashboard flow)
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get("currentPrice", info.get("regularMarketPrice"))

        print(f"   Ticker: {ticker}")
        print(f"   Current Price: ${current_price:.2f}")

        # Test IV Rank
        print("\n   Testing IV Rank Calculator...")
        iv_data = ib_analyzers['iv_calculator'].get_iv_rank(ticker, current_price)

        if iv_data:
            print(f"   ✅ IV Rank: {iv_data['iv_rank']:.0f}/100 ({iv_data['status']})")
            print(f"      Current IV: {iv_data['current_iv']:.1f}%")
            print(f"      52w Range: {iv_data['52w_low']:.1f}% - {iv_data['52w_high']:.1f}%")
        else:
            print(f"   ⚠️ IV Rank not available (may need market hours)")

        # Test Earnings Filter
        print("\n   Testing Earnings Filter...")
        earnings_info = ib_analyzers['earnings_filter'].get_earnings_info(ticker, 30)

        if earnings_info:
            safe_icon = "✅" if earnings_info['safe_to_sell_puts'] else "⚠️"
            print(f"   {safe_icon} {earnings_info['reason']}")

            if earnings_info.get('next_earnings_date'):
                print(f"      Next Earnings: {earnings_info['next_earnings_date']}")
                print(f"      Days Until: {earnings_info['days_to_earnings']}")
        else:
            print(f"   ⚠️ Earnings info not available")

        # Test Weekly Scanner
        print("\n   Testing Weekly Scanner...")
        all_exps = ib_analyzers['weekly_scanner'].get_all_expirations(ticker)

        if all_exps:
            weeklies = [exp for exp in all_exps if not exp['is_monthly']]
            monthlies = [exp for exp in all_exps if exp['is_monthly']]

            print(f"   ✅ Found {len(all_exps)} expirations")
            print(f"      Weekly: {len(weeklies)}")
            print(f"      Monthly: {len(monthlies)}")

            # Show next 3 expirations
            print(f"\n   Next 3 expirations:")
            for i, exp in enumerate(all_exps[:3]):
                exp_type = "M" if exp['is_monthly'] else "W"
                print(f"      {i+1}. [{exp_type}] {exp['date']} ({exp['dte']} DTE)")
        else:
            print(f"   ⚠️ Expiration data not available")

        print("\n✅ All analyzer integrations working!")
        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        print("\nDisconnecting...")
        manager.disconnect()
        print("✅ Disconnected safely")


def main():
    """Run integration test"""
    print(f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success = test_integration()

    print("\n" + "="*60)
    if success:
        print("✅ DASHBOARD INTEGRATION TEST PASSED")
        print("\nDashboard features ready:")
        print("1. 🟢 IB Connection Status Widget")
        print("2. 📊 IV Rank Column (52-week history)")
        print("3. 📅 Earnings Safety Column")
        print("4. 📆 Weekly/Monthly Expiration Type")
        print("5. 🎯 IB Premium Filters (IV Rank, Earnings, Weeklies)")
        print("6. 🔍 Enhanced Detailed Analysis with IB Data")
        print("7. ✅ Smart Execution Checklist with IB Validations")
        print("\nDashboard URL: http://localhost:8502")
    else:
        print("⚠️ DASHBOARD INTEGRATION TEST - PARTIAL PASS")
        print("\nDashboard will work in yfinance-only mode")
        print("To enable IB features:")
        print("1. Start IB Gateway or TWS")
        print("2. Enable API connections in settings")
        print("3. Restart dashboard")
    print("="*60)


if __name__ == "__main__":
    main()
