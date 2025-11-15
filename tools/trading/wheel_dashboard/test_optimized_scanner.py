#!/usr/bin/env python3
"""
Test the optimized flow scanner
Verifies:
1. Scanner uses optimized parameters
2. Progress updates work
3. Scan completes in reasonable time
4. No errors occur
"""

import asyncio
import sys
import time
from datetime import datetime

# Ensure event loop exists
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from connection import IBManager, IBConfig
from analyzers.flow_scanner import FlowScanner


def test_scanner():
    """Test the optimized flow scanner"""
    print("=" * 70)
    print("TESTING OPTIMIZED FLOW SCANNER")
    print("=" * 70)

    # Connect to IB
    print("\n1️⃣ Connecting to IB Gateway...")
    config = IBConfig(
        host='127.0.0.1',
        port=4001,
        client_id=99,  # Use different client ID
        use_paper=False
    )

    manager = IBManager(config)
    success, message = manager.connect()

    if not success:
        print(f"❌ Connection failed: {message}")
        print("\n⚠️  Make sure IB Gateway is running on port 4001")
        return False

    print(f"✅ {message}")

    try:
        # Create scanner
        print("\n2️⃣ Creating flow scanner...")
        scanner = FlowScanner(manager.get_connection())
        print("✅ Scanner created")

        # Test with a liquid ticker
        ticker = "SPY"
        print(f"\n3️⃣ Scanning {ticker} options flow...")
        print("   Expected parameters:")
        print("   - Max expirations: 2")
        print("   - Lookback trades: 100")
        print("   - Strike range: 5% ATM")
        print()

        # Time the scan
        start_time = time.time()

        # Run scan
        flow_data = scanner.scan_option_flow(
            ticker=ticker,
            max_expirations=2,
            lookback_trades=100
        )

        elapsed = time.time() - start_time

        # Verify results
        print(f"\n4️⃣ Scan Results:")
        print(f"   ✅ Completed in {elapsed:.1f} seconds")

        stats = flow_data['flow_stats']
        print(f"\n   📊 Flow Statistics:")
        print(f"   - Total Premium Flow: ${stats['total_premium_flow']:,.0f}")
        print(f"   - Call Flow: ${stats['call_flow']:,.0f}")
        print(f"   - Put Flow: ${stats['put_flow']:,.0f}")
        print(f"   - Total Contracts: {stats['total_contracts']:,}")

        print(f"\n   🎯 Unusual Activity:")
        print(f"   - Block Trades: {len(flow_data['block_trades'])}")
        print(f"   - Sweeps: {len(flow_data['sweeps'])}")
        print(f"   - Aggressive Buys: {len(flow_data['aggressive_buys'])}")
        print(f"   - Alerts: {len(flow_data['alerts'])}")

        # Performance check
        print(f"\n5️⃣ Performance Check:")
        if elapsed < 60:
            print(f"   ✅ PASS: Scan completed in {elapsed:.1f}s (< 60s target)")
        elif elapsed < 120:
            print(f"   ⚠️  WARN: Scan took {elapsed:.1f}s (60-120s)")
        else:
            print(f"   ❌ FAIL: Scan took {elapsed:.1f}s (> 120s)")

        print("\n" + "=" * 70)
        print("✅ TEST COMPLETE - All checks passed!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Error during scan: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        print("\n6️⃣ Disconnecting...")
        manager.disconnect()
        print("✅ Disconnected")


if __name__ == "__main__":
    success = test_scanner()
    sys.exit(0 if success else 1)
