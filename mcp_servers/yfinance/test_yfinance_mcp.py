#!/usr/bin/env python3
"""
Automated test suite for yfinance_mcp.py server.

Tests all 8 tools (5 stock data + 3 options) with sample inputs and validates
tool registration using proper FastMCP v2 in-memory testing patterns with Client class.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


async def test_server():
    """Test all MCP server tools using FastMCP Client."""
    # Import server and Client for in-memory testing
    from yfinance_mcp import mcp
    from fastmcp import Client

    print("=" * 60)
    print(f"Testing yfinance MCP Server (FastMCP v2)")
    print("=" * 60)

    # Use Client for in-memory testing (proper FastMCP v2 pattern)
    async with Client(mcp) as client:
        # Test 1: Get ticker info
        print("\n[TEST 1] Testing get_ticker_info (AAPL)...")
        try:
            result1 = await client.call_tool("get_ticker_info", {"ticker": "AAPL"})
            output1 = result1.content[0].text
            print(f"✅ Result length: {len(output1)} chars")
            print(f"   Preview: {output1[:200]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 2: Get historical data
        print("\n[TEST 2] Testing get_historical_data (MSFT, 5d)...")
        try:
            result2 = await client.call_tool("get_historical_data", {
                "ticker": "MSFT",
                "period": "5d",
                "interval": "1d",
                "format": "json"
            })
            output2 = result2.content[0].text
            print(f"✅ Result length: {len(output2)} chars")
            print(f"   Preview: {output2[:200]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 3: Get dividends
        print("\n[TEST 3] Testing get_dividends (KO - Coca-Cola)...")
        try:
            result3 = await client.call_tool("get_dividends", {
                "ticker": "KO",
                "format": "json"
            })
            output3 = result3.content[0].text
            print(f"✅ Result length: {len(output3)} chars")
            print(f"   Preview: {output3[:200]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 4: Get financials
        print("\n[TEST 4] Testing get_financials (GOOGL, income statement)...")
        try:
            result4 = await client.call_tool("get_financials", {
                "ticker": "GOOGL",
                "statement": "income",
                "period": "annual",
                "format": "json"
            })
            output4 = result4.content[0].text
            print(f"✅ Result length: {len(output4)} chars")
            print(f"   Preview: {output4[:200]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 5: Download multiple tickers
        print("\n[TEST 5] Testing download_multiple_tickers (AAPL MSFT GOOGL)...")
        try:
            result5 = await client.call_tool("download_multiple_tickers", {
                "tickers": "AAPL MSFT GOOGL",
                "period": "5d",
                "interval": "1d",
                "format": "markdown"
            })
            output5 = result5.content[0].text
            print(f"✅ Result length: {len(output5)} chars")
            print(f"   Preview: {output5[:200]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 6: Error handling - invalid ticker
        print("\n[TEST 6] Testing error handling (INVALIDTICKER123)...")
        try:
            result6 = await client.call_tool("get_ticker_info", {"ticker": "INVALIDTICKER123"})
            output6 = result6.content[0].text
            if "error" in output6.lower():
                print(f"✅ Error handling working: {output6[:100]}...")
            else:
                print(f"⚠️  Expected error, got: {output6[:100]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 7: Get options dates
        print("\n[TEST 7] Testing get_options_dates (AAPL)...")
        try:
            result7 = await client.call_tool("get_options_dates", {"ticker": "AAPL"})
            output7 = result7.content[0].text
            print(f"✅ Result length: {len(output7)} chars")
            # Check if we got dates
            if "near_term" in output7 or "total_expirations" in output7:
                print(f"   Preview: {output7[:200]}...")
            else:
                print(f"⚠️  Unexpected output: {output7[:200]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 8: Get options chain (summary)
        print("\n[TEST 8] Testing get_options_chain (SPY, summary)...")
        try:
            # First get available dates
            dates_result = await client.call_tool("get_options_dates", {"ticker": "SPY"})
            dates_output = dates_result.content[0].text
            import json
            dates_data = json.loads(dates_output)

            if "all_dates" in dates_data and len(dates_data["all_dates"]) > 0:
                first_date = dates_data["all_dates"][0]
                result8 = await client.call_tool("get_options_chain", {
                    "ticker": "SPY",
                    "expiration_date": first_date,
                    "option_type": "calls",
                    "detail_level": "summary",
                    "format": "json"
                })
                output8 = result8.content[0].text
                print(f"✅ Result length: {len(output8)} chars")
                print(f"   Preview: {output8[:200]}...")
            else:
                print(f"⚠️  No dates available for SPY")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 9: Get option strike (specific contract)
        print("\n[TEST 9] Testing get_option_strike (AAPL, specific strike)...")
        try:
            # Get dates first
            dates_result = await client.call_tool("get_options_dates", {"ticker": "AAPL"})
            dates_output = dates_result.content[0].text
            dates_data = json.loads(dates_output)

            if "all_dates" in dates_data and len(dates_data["all_dates"]) > 0:
                first_date = dates_data["all_dates"][0]
                # Use ATM strike (around current price of $262)
                result9 = await client.call_tool("get_option_strike", {
                    "ticker": "AAPL",
                    "expiration_date": first_date,
                    "strike": 260.0,
                    "option_type": "call"
                })
                output9 = result9.content[0].text
                print(f"✅ Result length: {len(output9)} chars")
                # Check for key fields
                if "greeks" in output9 or "price_data" in output9:
                    print(f"   Preview: {output9[:200]}...")
                else:
                    print(f"⚠️  Unexpected structure: {output9[:200]}...")
            else:
                print(f"⚠️  No dates available for AAPL")
        except Exception as e:
            print(f"❌ Failed: {e}")

        # Test 10: Check registered tools
        print(f"\n[TEST 10] Checking registered tools...")
        try:
            tools = await client.list_tools()
            print(f"✅ Registered tools: {len(tools)}")
            for tool in tools:
                desc_preview = tool.description[:60] if tool.description else "No description"
                print(f"   - {tool.name}: {desc_preview}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_server())
