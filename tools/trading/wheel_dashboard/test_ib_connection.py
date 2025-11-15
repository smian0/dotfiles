#!/usr/bin/env python3
"""
IB Connection Test Script - Read-Only Mode
Safe for real accounts - No order execution
"""

import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, '.')

from connection import IBManager, IBConfig

def test_connection():
    """Test 1: Basic connection"""
    print("\n" + "="*60)
    print("TEST 1: IB Connection")
    print("="*60)

    # Use environment config or defaults
    config = IBConfig(
        host='127.0.0.1',
        port=4001,  # IB Gateway Live (detected from port scan)
        client_id=1,
        use_paper=False  # Real account
    )

    print(f"Connecting to: {config.get_connection_string()}")

    manager = IBManager(config)
    success, message = manager.connect()

    if success:
        print(f"✅ {message}")
        print(f"Connected: {manager.is_connected()}")
        return manager
    else:
        print(f"❌ {message}")
        print("\nTroubleshooting:")
        print("1. Is TWS/IB Gateway running?")
        print("2. Is API enabled in TWS settings?")
        print("3. Is port 7496 correct for your setup?")
        print("4. Is 127.0.0.1 trusted in API settings?")
        return None


def test_stock_data(manager):
    """Test 2: Get stock information"""
    print("\n" + "="*60)
    print("TEST 2: Stock Data Retrieval (Read-Only)")
    print("="*60)

    try:
        from ib_insync import Stock

        ib = manager.get_connection()

        # Test with KO (Coca-Cola)
        ticker = "KO"
        print(f"\nFetching data for {ticker}...")

        stock = Stock(ticker, 'SMART', 'USD')
        ib.qualifyContracts(stock)

        print(f"✅ Contract qualified: {stock.symbol}")
        print(f"   Exchange: {stock.exchange}")
        print(f"   Currency: {stock.currency}")
        print(f"   ConId: {stock.conId}")

        # Get market data
        ticker_obj = ib.reqMktData(stock, '', False, False)
        ib.sleep(2)  # Wait for data

        print(f"\n📊 Market Data:")
        print(f"   Last Price: ${ticker_obj.last:.2f}" if ticker_obj.last else "   Last Price: N/A")
        print(f"   Bid: ${ticker_obj.bid:.2f}" if ticker_obj.bid else "   Bid: N/A")
        print(f"   Ask: ${ticker_obj.ask:.2f}" if ticker_obj.ask else "   Ask: N/A")
        print(f"   Volume: {ticker_obj.volume:,}" if ticker_obj.volume else "   Volume: N/A")

        # Cancel market data subscription
        ib.cancelMktData(stock)

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_options_expirations(manager):
    """Test 3: Get options expirations"""
    print("\n" + "="*60)
    print("TEST 3: Options Expirations (Read-Only)")
    print("="*60)

    try:
        from ib_insync import Stock

        ib = manager.get_connection()
        ticker = "KO"

        print(f"\nFetching options expirations for {ticker}...")

        stock = Stock(ticker, 'SMART', 'USD')
        ib.qualifyContracts(stock)

        # Get option parameters
        chains = ib.reqSecDefOptParams(
            stock.symbol, '', stock.secType, stock.conId
        )

        if not chains:
            print("❌ No options data available")
            return False

        # Use SMART exchange
        chain = next((c for c in chains if c.exchange == 'SMART'), chains[0])

        print(f"✅ Found {len(chain.expirations)} expirations")
        print(f"   Exchange: {chain.exchange}")
        print(f"   Strikes available: {len(chain.strikes)}")

        # Show first 5 expirations
        print(f"\n📅 Next 5 Expirations:")
        today = datetime.now().date()

        for i, exp_str in enumerate(sorted(chain.expirations)[:5]):
            exp_date = datetime.strptime(exp_str, '%Y%m%d').date()
            dte = (exp_date - today).days
            print(f"   {i+1}. {exp_date} ({dte} DTE)")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_options_chain(manager):
    """Test 4: Get options chain for specific expiration"""
    print("\n" + "="*60)
    print("TEST 4: Options Chain (Read-Only)")
    print("="*60)

    try:
        from ib_insync import Stock, Option

        ib = manager.get_connection()
        ticker = "KO"

        print(f"\nFetching options chain for {ticker}...")

        # Get stock
        stock = Stock(ticker, 'SMART', 'USD')
        ib.qualifyContracts(stock)

        # Get expirations
        chains = ib.reqSecDefOptParams(
            stock.symbol, '', stock.secType, stock.conId
        )
        chain = next((c for c in chains if c.exchange == 'SMART'), chains[0])

        # Use first expiration
        exp_str = sorted(chain.expirations)[0]
        exp_date = datetime.strptime(exp_str, '%Y%m%d').date()

        print(f"   Expiration: {exp_date}")

        # Get a few put strikes
        strikes = sorted(chain.strikes)
        mid_idx = len(strikes) // 2
        sample_strikes = strikes[mid_idx-2:mid_idx+1]  # 3 strikes around mid

        print(f"\n📋 Sample Put Options:")

        for strike in sample_strikes:
            # Create put option contract
            put = Option(ticker, exp_str, strike, 'P', 'SMART')
            ib.qualifyContracts(put)

            # Request market data
            ticker_obj = ib.reqMktData(put, '', False, False)
            ib.sleep(1)

            bid = ticker_obj.bid if ticker_obj.bid and ticker_obj.bid > 0 else 0
            ask = ticker_obj.ask if ticker_obj.ask and ticker_obj.ask > 0 else 0
            mid = (bid + ask) / 2 if bid and ask else 0

            print(f"   ${strike:.0f} Put: Bid ${bid:.2f} / Ask ${ask:.2f} (Mid ${mid:.2f})")

            # Cancel subscription
            ib.cancelMktData(put)

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("IB CONNECTION TEST - READ-ONLY MODE")
    print("Safe for Real Accounts - No Order Execution")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test 1: Connection
    manager = test_connection()
    if not manager:
        print("\n❌ Connection failed - stopping tests")
        return

    try:
        # Test 2: Stock data
        if test_stock_data(manager):
            print("✅ Stock data test passed")

        # Test 3: Options expirations
        if test_options_expirations(manager):
            print("✅ Options expirations test passed")

        # Test 4: Options chain
        if test_options_chain(manager):
            print("✅ Options chain test passed")

        print("\n" + "="*60)
        print("ALL TESTS COMPLETE")
        print("="*60)
        print("✅ IB connection is working properly!")
        print("✅ Read-only access confirmed (no orders)")
        print("✅ Ready to implement Phase 1 analyzers")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Always disconnect
        print("\nDisconnecting...")
        manager.disconnect()
        print("✅ Disconnected safely")


if __name__ == "__main__":
    main()
