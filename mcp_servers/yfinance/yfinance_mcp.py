#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "fastmcp>=2.13.0",
#   "yfinance>=0.2.55,<0.3.0",
#   "pandas>=2.1.0",
#   "pydantic>=2.0.0",
#   "tabulate>=0.9.0",
#   "lxml>=4.9.0",
# ]
# requires-python = ">=3.12"
# ///

"""
MCP Server for Yahoo Finance (yfinance) API.

Provides tools to fetch stock data, company information, financial statements,
and historical price data using the yfinance library.
"""

from typing import Annotated, Literal
from enum import Enum
import json
import asyncio
from datetime import datetime
import yfinance as yf
from pydantic import Field
from fastmcp import FastMCP, Context

# Initialize the MCP server
mcp = FastMCP("yfinance_mcp")

# Constants
CHARACTER_LIMIT = 25000
DEFAULT_PERIOD = "1mo"
DEFAULT_INTERVAL = "1d"


class Period(str, Enum):
    """Valid period values for historical data."""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YTD = "ytd"
    MAX = "max"


class Interval(str, Enum):
    """Valid interval values for historical data."""
    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


# Utility Functions

def truncate_text(text: str, max_chars: int = CHARACTER_LIMIT) -> str:
    """Truncate text to maximum character limit."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 50] + f"\n\n... [truncated, {len(text) - max_chars} chars omitted]"


def format_dataframe_as_markdown(df, max_rows: int = 100) -> str:
    """Convert DataFrame to markdown table format."""
    if df.empty:
        return "No data available."

    # Limit rows
    if len(df) > max_rows:
        df_display = df.head(max_rows)
        truncated_msg = f"\n\n*Showing first {max_rows} of {len(df)} rows*"
    else:
        df_display = df
        truncated_msg = ""

    # Convert to markdown
    markdown = df_display.to_markdown()
    return truncate_text(markdown + truncated_msg)


def handle_yfinance_error(ticker: str, operation: str) -> dict:
    """Generate error response for yfinance operations."""
    return {
        "error": True,
        "message": f"Failed to {operation} for ticker '{ticker}'. Verify ticker symbol is correct.",
        "ticker": ticker
    }


async def handle_rate_limit(ctx: Context, retry_count: int = 0, max_retries: int = 3):
    """
    Handle rate limiting with exponential backoff.

    Raises YfRateLimitError if max retries exceeded.
    """
    if retry_count >= max_retries:
        error_msg = "Rate limit exceeded: Max retries reached. Yahoo Finance may be blocking requests."
        if ctx:
            await ctx.error(error_msg)
        raise Exception(error_msg)

    wait_time = 2 ** retry_count  # Exponential backoff: 1s, 2s, 4s
    if ctx:
        await ctx.warning(f"Rate limit detected, waiting {wait_time}s before retry...")

    await asyncio.sleep(wait_time)


# MCP Tools

@mcp.tool
async def get_ticker_info(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT, TSLA)")],
    ctx: Context
) -> str:
    """
    Get comprehensive company information and current market data for a stock ticker.

    Returns company profile, market cap, sector, industry, and key statistics.
    """
    await ctx.info(f"Fetching information for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or len(info) <= 1:
            return json.dumps(handle_yfinance_error(ticker, "retrieve information"))

        # Extract key information
        result = {
            "ticker": ticker.upper(),
            "company_name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "currency": info.get("currency", "N/A"),
            "exchange": info.get("exchange", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "avg_volume": info.get("averageVolume", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "beta": info.get("beta", "N/A"),
            "website": info.get("website", "N/A"),
            "description": info.get("longBusinessSummary", "N/A")
        }

        output = json.dumps(result, indent=2)
        return truncate_text(output)

    except Exception as e:
        await ctx.error(f"Error fetching ticker info: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve information"))


@mcp.tool
async def get_historical_data(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    period: Annotated[str, Field(description="Time period (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")] = DEFAULT_PERIOD,
    interval: Annotated[str, Field(description="Data interval (e.g., 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")] = DEFAULT_INTERVAL,
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get historical price data (OHLCV) for a stock ticker.

    Returns Open, High, Low, Close, Volume data for the specified period and interval.
    Note: Intraday data (1m, 2m, 5m, etc.) is limited to last 60 days.
    """
    if ctx:
        await ctx.info(f"Fetching {period} of {interval} data for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            return json.dumps(handle_yfinance_error(ticker, "retrieve historical data"))

        # Reset index to include date as column
        df = df.reset_index()

        if format == "json":
            # Convert to JSON
            result = {
                "ticker": ticker.upper(),
                "period": period,
                "interval": interval,
                "data_points": len(df),
                "data": df.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            # Markdown format
            markdown = f"# Historical Data for {ticker.upper()}\n\n"
            markdown += f"**Period:** {period} | **Interval:** {interval} | **Data Points:** {len(df)}\n\n"
            markdown += format_dataframe_as_markdown(df)
            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching historical data: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve historical data"))


@mcp.tool
async def get_dividends(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get dividend payment history for a stock ticker.

    Returns all historical dividend payments with dates and amounts.
    """
    if ctx:
        await ctx.info(f"Fetching dividend history for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        dividends = stock.dividends

        if dividends.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No dividend history available (may not pay dividends or data unavailable)"
            })

        # Convert to DataFrame
        df = dividends.reset_index()
        df.columns = ["Date", "Dividend"]

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "total_payments": len(df),
                "dividends": df.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Dividend History for {ticker.upper()}\n\n"
            markdown += f"**Total Payments:** {len(df)}\n\n"
            markdown += format_dataframe_as_markdown(df)
            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching dividends: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve dividend history"))


@mcp.tool
async def get_financials(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    statement: Annotated[Literal["income", "balance", "cashflow"], Field(description="Financial statement type")] = "income",
    period: Annotated[Literal["annual", "quarterly"], Field(description="Reporting period")] = "annual",
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get financial statements for a stock ticker.

    Available statements:
    - income: Income statement (revenue, expenses, net income)
    - balance: Balance sheet (assets, liabilities, equity)
    - cashflow: Cash flow statement (operating, investing, financing)
    """
    if ctx:
        await ctx.info(f"Fetching {period} {statement} statement for {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        # Get appropriate statement
        if statement == "income":
            df = stock.income_stmt if period == "annual" else stock.quarterly_income_stmt
            title = "Income Statement"
        elif statement == "balance":
            df = stock.balance_sheet if period == "annual" else stock.quarterly_balance_sheet
            title = "Balance Sheet"
        else:  # cashflow
            df = stock.cashflow if period == "annual" else stock.quarterly_cashflow
            title = "Cash Flow Statement"

        if df.empty:
            return json.dumps(handle_yfinance_error(ticker, f"retrieve {statement} statement"))

        # Transpose for better readability (periods as rows)
        df = df.T
        df = df.reset_index()
        df.columns = ["Period"] + list(df.columns[1:])

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "statement": statement,
                "period": period,
                "data": df.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# {title} for {ticker.upper()}\n\n"
            markdown += f"**Period:** {period.capitalize()}\n\n"
            markdown += format_dataframe_as_markdown(df, max_rows=50)
            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching financials: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, f"retrieve {statement} statement"))


@mcp.tool
async def download_multiple_tickers(
    tickers: Annotated[str, Field(description="Space-separated ticker symbols (e.g., 'AAPL MSFT GOOGL')")],
    period: Annotated[str, Field(description="Time period (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")] = DEFAULT_PERIOD,
    interval: Annotated[str, Field(description="Data interval (e.g., 1d, 1wk, 1mo)")] = DEFAULT_INTERVAL,
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Download historical data for multiple tickers in parallel.

    Efficient bulk data retrieval using yfinance's threading capabilities.
    Returns combined data for all tickers.
    """
    ticker_list = tickers.upper().split()

    if ctx:
        await ctx.info(f"Downloading {period} data for {len(ticker_list)} tickers...")

    try:
        # Download data for all tickers (uses threading internally)
        data = yf.download(
            ticker_list,
            period=period,
            interval=interval,
            group_by='ticker',
            threads=True,
            progress=False
        )

        if data.empty:
            return json.dumps({
                "error": True,
                "message": f"No data retrieved for tickers: {tickers}",
                "tickers": ticker_list
            })

        # Reset index to include date
        data = data.reset_index()

        if format == "json":
            result = {
                "tickers": ticker_list,
                "period": period,
                "interval": interval,
                "data_points": len(data),
                "data": data.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Multi-Ticker Data\n\n"
            markdown += f"**Tickers:** {', '.join(ticker_list)}\n\n"
            markdown += f"**Period:** {period} | **Interval:** {interval} | **Data Points:** {len(data)}\n\n"
            markdown += format_dataframe_as_markdown(data, max_rows=100)
            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error downloading multiple tickers: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"Failed to download data for tickers: {str(e)}",
            "tickers": ticker_list
        })


# Options Trading Tools

@mcp.tool
async def get_options_dates(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, SPY)")],
    ctx: Context = None
) -> str:
    """
    Get available expiration dates for options on a stock ticker.

    Returns list of expiration dates grouped by timeframe:
    - Near-term: 0-60 days
    - Mid-term: 60-180 days
    - Long-term: 180+ days
    """
    if ctx:
        await ctx.info(f"Fetching options expiration dates for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        dates = stock.options

        if not dates or len(dates) == 0:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No options available for this ticker (may not have listed options)"
            })

        # Group by timeframe
        today = datetime.now().date()
        near_term = []
        mid_term = []
        long_term = []

        for date_str in dates:
            exp_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            days_until = (exp_date - today).days

            if days_until <= 60:
                near_term.append(date_str)
            elif days_until <= 180:
                mid_term.append(date_str)
            else:
                long_term.append(date_str)

        result = {
            "ticker": ticker.upper(),
            "total_expirations": len(dates),
            "near_term_0_60d": near_term,
            "mid_term_60_180d": mid_term,
            "long_term_180d_plus": long_term,
            "all_dates": list(dates)
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching options dates: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve options dates"))


@mcp.tool
async def get_options_chain(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, SPY)")],
    expiration_date: Annotated[str, Field(description="Expiration date in YYYY-MM-DD format")],
    option_type: Annotated[Literal["calls", "puts", "both"], Field(description="Type of options to retrieve")] = "both",
    detail_level: Annotated[Literal["summary", "full"], Field(description="Data granularity: summary (ATM ±5 strikes) or full (all strikes)")] = "summary",
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get options chain for a specific expiration date.

    Summary mode: Returns ATM strike and nearest 5 strikes above/below
    Full mode: Returns all available strikes with prices, volume, Greeks

    Includes: last price, bid, ask, volume, open interest, implied volatility,
    Greeks (delta, gamma, theta, vega, rho), in-the-money status
    """
    if ctx:
        await ctx.info(f"Fetching {detail_level} {option_type} chain for {ticker} expiring {expiration_date}...")

    try:
        stock = yf.Ticker(ticker)

        # Validate expiration date
        available_dates = stock.options
        if expiration_date not in available_dates:
            return json.dumps({
                "error": True,
                "message": f"Invalid expiration date. Available dates: {', '.join(list(available_dates)[:10])}...",
                "ticker": ticker.upper(),
                "requested_date": expiration_date
            })

        # Get options chain
        chain = stock.option_chain(expiration_date)

        # Select calls, puts, or both
        if option_type == "calls":
            dfs = {"calls": chain.calls}
        elif option_type == "puts":
            dfs = {"puts": chain.puts}
        else:  # both
            dfs = {"calls": chain.calls, "puts": chain.puts}

        # Get current stock price for ATM calculation
        current_price = stock.info.get("currentPrice", stock.info.get("regularMarketPrice", 0))

        result_data = {}

        for opt_type, df in dfs.items():
            if df.empty:
                result_data[opt_type] = []
                continue

            # Filter based on detail level
            if detail_level == "summary" and current_price > 0:
                # Find ATM strike (closest to current price)
                df['distance'] = abs(df['strike'] - current_price)
                atm_idx = df['distance'].idxmin()

                # Get ATM ± 5 strikes
                start_idx = max(0, atm_idx - 5)
                end_idx = min(len(df), atm_idx + 6)
                df = df.iloc[start_idx:end_idx]

            # Convert to records
            records = df.to_dict(orient="records")
            result_data[opt_type] = records

        # Build response
        if format == "json":
            output = {
                "ticker": ticker.upper(),
                "expiration": expiration_date,
                "current_price": current_price,
                "option_type": option_type,
                "detail_level": detail_level,
                "data": result_data
            }
            return truncate_text(json.dumps(output, indent=2, default=str))
        else:
            # Markdown format
            markdown = f"# Options Chain for {ticker.upper()}\n\n"
            markdown += f"**Expiration:** {expiration_date} | **Current Price:** ${current_price:.2f} | **Detail:** {detail_level}\n\n"

            for opt_type, records in result_data.items():
                if not records:
                    continue

                markdown += f"## {opt_type.capitalize()}\n\n"
                markdown += f"**Contracts:** {len(records)}\n\n"

                # Create DataFrame for markdown table
                import pandas as pd
                df_display = pd.DataFrame(records)

                # Select key columns for display
                display_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest',
                               'impliedVolatility', 'inTheMoney']
                # Only include columns that exist
                display_cols = [col for col in display_cols if col in df_display.columns]
                df_display = df_display[display_cols]

                markdown += format_dataframe_as_markdown(df_display, max_rows=100)
                markdown += "\n\n"

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching options chain: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"Failed to retrieve options chain: {str(e)}",
            "ticker": ticker.upper(),
            "expiration": expiration_date
        })


@mcp.tool
async def get_option_strike(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, SPY)")],
    expiration_date: Annotated[str, Field(description="Expiration date in YYYY-MM-DD format")],
    strike: Annotated[float, Field(description="Strike price (e.g., 260.0)")],
    option_type: Annotated[Literal["call", "put"], Field(description="Option type")],
    ctx: Context = None
) -> str:
    """
    Get detailed information for a specific option contract.

    Returns complete contract details including:
    - Price data: last, bid, ask, spread percentage
    - Volume, open interest, last trade time
    - Greeks: delta, gamma, theta, vega, rho (if available)
    - Intrinsic/extrinsic value
    - In-the-money status
    - Contract symbol
    """
    if ctx:
        await ctx.info(f"Fetching {option_type} option details for {ticker} ${strike} expiring {expiration_date}...")

    try:
        stock = yf.Ticker(ticker)

        # Validate expiration date
        available_dates = stock.options
        if expiration_date not in available_dates:
            return json.dumps({
                "error": True,
                "message": f"Invalid expiration date. Use get_options_dates to see available dates.",
                "ticker": ticker.upper()
            })

        # Get options chain
        chain = stock.option_chain(expiration_date)
        df = chain.calls if option_type == "call" else chain.puts

        # Find the strike
        strike_data = df[df['strike'] == strike]

        if strike_data.empty:
            # Try to find closest strike
            df['distance'] = abs(df['strike'] - strike)
            closest_idx = df['distance'].idxmin()
            closest_strike = df.loc[closest_idx, 'strike']

            return json.dumps({
                "error": True,
                "message": f"Strike ${strike} not found. Closest available strike: ${closest_strike}",
                "ticker": ticker.upper(),
                "expiration": expiration_date,
                "requested_strike": strike,
                "closest_strike": float(closest_strike)
            })

        # Get the contract data
        contract = strike_data.iloc[0].to_dict()

        # Calculate spread percentage
        bid = contract.get('bid', 0)
        ask = contract.get('ask', 0)
        spread_pct = ((ask - bid) / ask * 100) if ask > 0 else 0

        # Get current stock price for intrinsic value calculation
        current_price = stock.info.get("currentPrice", stock.info.get("regularMarketPrice", 0))

        # Calculate intrinsic and extrinsic value
        if option_type == "call":
            intrinsic = max(0, current_price - strike)
        else:  # put
            intrinsic = max(0, strike - current_price)

        last_price = contract.get('lastPrice', 0)
        extrinsic = last_price - intrinsic if last_price > 0 else 0

        # Build detailed response
        result = {
            "ticker": ticker.upper(),
            "expiration": expiration_date,
            "strike": strike,
            "option_type": option_type,
            "contract_symbol": contract.get('contractSymbol', 'N/A'),
            "price_data": {
                "last": contract.get('lastPrice'),
                "bid": bid,
                "ask": ask,
                "spread_pct": round(spread_pct, 2),
                "change": contract.get('change'),
                "percent_change": contract.get('percentChange')
            },
            "volume_data": {
                "volume": contract.get('volume'),
                "open_interest": contract.get('openInterest'),
                "last_trade_date": str(contract.get('lastTradeDate', 'N/A'))
            },
            "greeks": {
                "delta": contract.get('delta'),
                "gamma": contract.get('gamma'),
                "theta": contract.get('theta'),
                "vega": contract.get('vega'),
                "rho": contract.get('rho')
            },
            "value_breakdown": {
                "intrinsic_value": round(intrinsic, 2),
                "extrinsic_value": round(extrinsic, 2),
                "implied_volatility": contract.get('impliedVolatility')
            },
            "status": {
                "in_the_money": bool(contract.get('inTheMoney', False)),
                "current_stock_price": current_price
            }
        }

        return json.dumps(result, indent=2, default=str)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching option strike: {str(e)}")
        return json.dumps({
            "error": True,
            "message": f"Failed to retrieve option details: {str(e)}",
            "ticker": ticker.upper(),
            "expiration": expiration_date,
            "strike": strike
        })


# Analyst & Insider Data Tools (Phase 2)

@mcp.tool
async def get_analyst_recommendations(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get analyst recommendations summary and recent upgrades/downgrades.

    Returns:
    - Recommendations summary: buy/hold/sell counts over time
    - Recent upgrades/downgrades: firm, action, rating change, date
    - Price targets: current consensus, high, low, mean
    """
    if ctx:
        await ctx.info(f"Fetching analyst recommendations for {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        # Get recommendations data
        recommendations = stock.recommendations
        upgrades_downgrades = stock.upgrades_downgrades

        if recommendations is None or recommendations.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No analyst recommendations available"
            })

        # Get recommendations summary (recent period grouping)
        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "recommendations": recommendations.to_dict(orient="records") if not recommendations.empty else [],
                "upgrades_downgrades": upgrades_downgrades.to_dict(orient="records") if upgrades_downgrades is not None and not upgrades_downgrades.empty else []
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Analyst Recommendations for {ticker.upper()}\n\n"

            # Recommendations history
            if not recommendations.empty:
                markdown += "## Recommendations History\n\n"
                df_rec = recommendations.reset_index().tail(20)  # Last 20
                markdown += format_dataframe_as_markdown(df_rec, max_rows=20)
                markdown += "\n\n"

            # Upgrades/Downgrades
            if upgrades_downgrades is not None and not upgrades_downgrades.empty:
                markdown += "## Recent Upgrades & Downgrades\n\n"
                df_updown = upgrades_downgrades.reset_index().tail(20)  # Last 20
                markdown += format_dataframe_as_markdown(df_updown, max_rows=20)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching analyst recommendations: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve analyst recommendations"))


@mcp.tool
async def get_analyst_estimates(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get analyst estimates and trends for earnings and revenue.

    Returns:
    - Earnings estimates (current quarter, next quarter, current year, next year)
    - Revenue estimates
    - EPS trends and revisions
    - Growth estimates
    """
    if ctx:
        await ctx.info(f"Fetching analyst estimates for {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        # Get estimate data
        earnings_estimate = stock.earnings_estimate
        revenue_estimate = stock.revenue_estimate
        eps_trend = stock.eps_trend
        eps_revisions = stock.eps_revisions
        growth_estimates = stock.growth_estimates

        # Check if any data available
        has_data = any([
            earnings_estimate is not None and not earnings_estimate.empty,
            revenue_estimate is not None and not revenue_estimate.empty,
            eps_trend is not None and not eps_trend.empty
        ])

        if not has_data:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No analyst estimates available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "earnings_estimate": earnings_estimate.to_dict() if earnings_estimate is not None and not earnings_estimate.empty else {},
                "revenue_estimate": revenue_estimate.to_dict() if revenue_estimate is not None and not revenue_estimate.empty else {},
                "eps_trend": eps_trend.to_dict() if eps_trend is not None and not eps_trend.empty else {},
                "eps_revisions": eps_revisions.to_dict() if eps_revisions is not None and not eps_revisions.empty else {},
                "growth_estimates": growth_estimates.to_dict() if growth_estimates is not None and not growth_estimates.empty else {}
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Analyst Estimates for {ticker.upper()}\n\n"

            if earnings_estimate is not None and not earnings_estimate.empty:
                markdown += "## Earnings Estimates\n\n"
                markdown += format_dataframe_as_markdown(earnings_estimate.reset_index())
                markdown += "\n\n"

            if revenue_estimate is not None and not revenue_estimate.empty:
                markdown += "## Revenue Estimates\n\n"
                markdown += format_dataframe_as_markdown(revenue_estimate.reset_index())
                markdown += "\n\n"

            if eps_trend is not None and not eps_trend.empty:
                markdown += "## EPS Trends\n\n"
                markdown += format_dataframe_as_markdown(eps_trend.reset_index())
                markdown += "\n\n"

            if eps_revisions is not None and not eps_revisions.empty:
                markdown += "## EPS Revisions\n\n"
                markdown += format_dataframe_as_markdown(eps_revisions.reset_index())
                markdown += "\n\n"

            if growth_estimates is not None and not growth_estimates.empty:
                markdown += "## Growth Estimates\n\n"
                markdown += format_dataframe_as_markdown(growth_estimates.reset_index())

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching analyst estimates: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve analyst estimates"))


@mcp.tool
async def get_insider_activity(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    transaction_type: Annotated[Literal["all", "purchases", "sales"], Field(description="Filter by transaction type")] = "all",
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get insider trading activity and roster.

    Returns:
    - Insider roster: Current insiders and their positions
    - Insider transactions: Recent trading activity
    - Insider purchases: Filter for buy activity only
    """
    if ctx:
        await ctx.info(f"Fetching insider activity for {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        # Get insider data
        insider_roster = stock.insider_roster_holders
        insider_transactions = stock.insider_transactions
        insider_purchases = stock.insider_purchases

        # Check if any data available
        has_data = any([
            insider_roster is not None and not insider_roster.empty,
            insider_transactions is not None and not insider_transactions.empty,
            insider_purchases is not None and not insider_purchases.empty
        ])

        if not has_data:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No insider activity data available"
            })

        # Filter transactions based on type
        if transaction_type == "purchases":
            transactions = insider_purchases if insider_purchases is not None else None
        elif transaction_type == "sales":
            # Filter for sales (if available in transactions)
            if insider_transactions is not None and not insider_transactions.empty:
                # Assuming sales have negative shares or specific transaction code
                transactions = insider_transactions
            else:
                transactions = None
        else:  # all
            transactions = insider_transactions

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "transaction_type": transaction_type,
                "insider_roster": insider_roster.to_dict(orient="records") if insider_roster is not None and not insider_roster.empty else [],
                "insider_transactions": transactions.to_dict(orient="records") if transactions is not None and not transactions.empty else []
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Insider Activity for {ticker.upper()}\n\n"

            if insider_roster is not None and not insider_roster.empty:
                markdown += "## Insider Roster\n\n"
                markdown += format_dataframe_as_markdown(insider_roster.reset_index(), max_rows=50)
                markdown += "\n\n"

            if transactions is not None and not transactions.empty:
                markdown += f"## {'Insider Purchases' if transaction_type == 'purchases' else 'Insider Transactions'}\n\n"
                df_trans = transactions.reset_index()
                markdown += format_dataframe_as_markdown(df_trans, max_rows=50)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching insider activity: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve insider activity"))


@mcp.tool
async def get_institutional_holders(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get institutional and major holders information.

    Returns:
    - Major holders: Top shareholder percentages
    - Institutional holders: Top institutions with share counts
    - Mutual fund holders: Top mutual funds holding the stock
    """
    if ctx:
        await ctx.info(f"Fetching institutional holders for {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        # Get holder data
        major_holders = stock.major_holders
        institutional_holders = stock.institutional_holders
        mutualfund_holders = stock.mutualfund_holders

        # Check if any data available
        has_data = any([
            major_holders is not None and not major_holders.empty,
            institutional_holders is not None and not institutional_holders.empty,
            mutualfund_holders is not None and not mutualfund_holders.empty
        ])

        if not has_data:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No institutional holder data available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "major_holders": major_holders.to_dict(orient="records") if major_holders is not None and not major_holders.empty else [],
                "institutional_holders": institutional_holders.to_dict(orient="records") if institutional_holders is not None and not institutional_holders.empty else [],
                "mutualfund_holders": mutualfund_holders.to_dict(orient="records") if mutualfund_holders is not None and not mutualfund_holders.empty else []
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Institutional Holders for {ticker.upper()}\n\n"

            if major_holders is not None and not major_holders.empty:
                markdown += "## Major Holders Summary\n\n"
                markdown += format_dataframe_as_markdown(major_holders)
                markdown += "\n\n"

            if institutional_holders is not None and not institutional_holders.empty:
                markdown += "## Top Institutional Holders\n\n"
                markdown += format_dataframe_as_markdown(institutional_holders, max_rows=20)
                markdown += "\n\n"

            if mutualfund_holders is not None and not mutualfund_holders.empty:
                markdown += "## Top Mutual Fund Holders\n\n"
                markdown += format_dataframe_as_markdown(mutualfund_holders, max_rows=20)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching institutional holders: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve institutional holders"))


# Enhanced Financials & Calendar Tools (Phase 3)

@mcp.tool
async def get_ttm_financials(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    statement: Annotated[Literal["income", "cashflow", "all"], Field(description="Financial statement type or all")] = "all",
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get Trailing Twelve Months (TTM) financial statements.

    TTM financials provide more accurate metrics than quarterly annualization.
    Available statements:
    - income: TTM income statement (revenue, expenses, net income)
    - cashflow: TTM cash flow statement (operating, investing, financing)
    - all: Both income and cashflow TTM statements

    Note: Balance sheet does not support TTM (uses most recent quarterly data).
    """
    if ctx:
        await ctx.info(f"Fetching TTM {statement} financials for {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        # Get TTM statements (only income and cashflow support TTM)
        statements = {}
        if statement in ["income", "all"]:
            statements["income"] = stock.get_income_stmt(freq="trailing")
        if statement in ["cashflow", "all"]:
            statements["cashflow"] = stock.get_cash_flow(freq="trailing")

        # Check if any data available
        has_data = any(df is not None and not df.empty for df in statements.values())

        if not has_data:
            return json.dumps(handle_yfinance_error(ticker, f"retrieve TTM {statement} financials"))

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "period": "TTM (Trailing Twelve Months)",
                "statements": {}
            }
            for stmt_type, df in statements.items():
                if df is not None and not df.empty:
                    result["statements"][stmt_type] = df.to_dict()
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# TTM Financials for {ticker.upper()}\n\n"
            markdown += "**Period:** Trailing Twelve Months (TTM)\n\n"

            for stmt_type, df in statements.items():
                if df is not None and not df.empty:
                    title_map = {
                        "income": "Income Statement (TTM)",
                        "cashflow": "Cash Flow Statement (TTM)"
                    }
                    markdown += f"## {title_map[stmt_type]}\n\n"

                    # Transpose for better readability
                    df_display = df.T.reset_index()
                    df_display.columns = ["Metric"] + list(df_display.columns[1:])
                    markdown += format_dataframe_as_markdown(df_display, max_rows=100)
                    markdown += "\n\n"

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching TTM financials: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, f"retrieve TTM {statement} financials"))


@mcp.tool
async def get_earnings_calendar(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    limit: Annotated[int, Field(description="Maximum number of earnings dates to return")] = 12,
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get earnings calendar with historical and upcoming earnings dates.

    Returns earnings dates, EPS estimates, actual EPS, and surprises.
    Useful for tracking earnings performance over time.
    """
    if ctx:
        await ctx.info(f"Fetching earnings calendar for {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        # Get earnings dates and apply limit
        earnings_dates = stock.get_earnings_dates()

        if earnings_dates is None or earnings_dates.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No earnings calendar data available"
            })

        # Apply limit by taking most recent entries
        earnings_dates = earnings_dates.head(limit)

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "earnings_count": len(earnings_dates),
                "earnings_dates": earnings_dates.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Earnings Calendar for {ticker.upper()}\n\n"
            markdown += f"**Total Entries:** {len(earnings_dates)}\n\n"

            df_display = earnings_dates.reset_index()
            markdown += format_dataframe_as_markdown(df_display, max_rows=limit)

            return truncate_text(markdown)

    except Exception as e:
        error_msg = f"Error fetching earnings calendar: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        # Return detailed error for debugging
        return json.dumps({
            "error": True,
            "message": error_msg,
            "exception_type": type(e).__name__,
            "ticker": ticker
        })


@mcp.tool
async def get_capital_gains(
    ticker: Annotated[str, Field(description="Stock/fund ticker symbol (e.g., VFIAX, SPY)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get capital gains distributions history.

    Primarily used for mutual funds and ETFs. Returns historical capital gains
    distributions which are important for tax planning.
    """
    if ctx:
        await ctx.info(f"Fetching capital gains for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        capital_gains = stock.capital_gains

        if capital_gains is None or capital_gains.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No capital gains distributions available (may not be a fund or no distributions made)"
            })

        # Convert to DataFrame
        df = capital_gains.reset_index()
        df.columns = ["Date", "Capital Gains"]

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "total_distributions": len(df),
                "capital_gains": df.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Capital Gains Distributions for {ticker.upper()}\n\n"
            markdown += f"**Total Distributions:** {len(df)}\n\n"
            markdown += format_dataframe_as_markdown(df)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching capital gains: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve capital gains"))


# News & Extended Data Tools (Phase 4)

@mcp.tool
async def get_news(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    count: Annotated[int, Field(description="Number of news articles to return")] = 10,
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get recent news articles and press releases for a stock.

    Returns news with titles, publishers, links, and publication dates.
    Useful for sentiment analysis and event detection.
    """
    if ctx:
        await ctx.info(f"Fetching news for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        news = stock.get_news()

        if not news or len(news) == 0:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No news articles available"
            })

        # Limit to requested count
        news = news[:count]

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "count": len(news),
                "news": news
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# News for {ticker.upper()}\n\n"
            markdown += f"**Articles Found:** {len(news)}\n\n"

            for i, article in enumerate(news, 1):
                # Extract from nested 'content' structure
                content = article.get('content', {})
                title = content.get('title', 'No title')
                publisher = content.get('provider', {}).get('displayName', 'Unknown')
                link = content.get('clickThroughUrl', {}).get('url', '#')
                pub_date = content.get('pubDate', 'Unknown')

                markdown += f"### {i}. {title}\n\n"
                markdown += f"**Publisher:** {publisher}  \n"
                markdown += f"**Published:** {pub_date}  \n"
                markdown += f"**Link:** [{link}]({link})\n\n"

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching news: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve news"))


@mcp.tool
async def get_sustainability(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get ESG (Environmental, Social, Governance) sustainability scores and metrics.

    Returns ESG ratings, controversies, and performance metrics.
    Useful for ESG-focused investing and sustainability analysis.
    """
    if ctx:
        await ctx.info(f"Fetching sustainability data for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        sustainability = stock.sustainability

        if sustainability is None or sustainability.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No sustainability data available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "sustainability": sustainability.to_dict()
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# ESG Sustainability Data for {ticker.upper()}\n\n"

            df_display = sustainability.reset_index()
            df_display.columns = ["Metric", "Value"]
            markdown += format_dataframe_as_markdown(df_display)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching sustainability data: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve sustainability data"))


@mcp.tool
async def get_sec_filings(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get SEC filing references and links.

    Returns recent SEC filings (10-K, 10-Q, 8-K, etc.) with links to documents.
    Useful for regulatory research and due diligence.
    """
    if ctx:
        await ctx.info(f"Fetching SEC filings for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        sec_filings = stock.sec_filings

        if sec_filings is None or len(sec_filings) == 0:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No SEC filings data available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "filings_count": len(sec_filings),
                "sec_filings": sec_filings
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# SEC Filings for {ticker.upper()}\n\n"
            markdown += f"**Total Filings:** {len(sec_filings)}\n\n"

            # Convert list of dicts to markdown table
            import pandas as pd
            df = pd.DataFrame(sec_filings)

            # Select and format key columns
            if 'date' in df.columns:
                df_display = df[['date', 'type', 'title', 'edgarUrl']].copy()
                df_display.columns = ['Date', 'Type', 'Title', 'URL']
            else:
                df_display = df

            markdown += format_dataframe_as_markdown(df_display, max_rows=50)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching SEC filings: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve SEC filings"))


@mcp.tool
async def get_calendar(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get upcoming earnings and dividend calendar dates with estimates.

    Returns:
    - Next earnings date with estimate range
    - Dividend dates (ex-dividend, payment)
    - Revenue estimates (high, low, average)
    - Earnings estimates (high, low, average)

    Useful for planning trades around corporate events.
    """
    if ctx:
        await ctx.info(f"Fetching calendar for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar

        if calendar is None or (isinstance(calendar, dict) and len(calendar) == 0):
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No calendar data available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "calendar": calendar
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Calendar for {ticker.upper()}\n\n"

            if isinstance(calendar, dict):
                # Format as key-value pairs
                markdown += "## Upcoming Events\n\n"
                for key, value in calendar.items():
                    markdown += f"**{key}:** {value}\n\n"
            else:
                # If it's a DataFrame
                import pandas as pd
                df = pd.DataFrame([calendar]) if not isinstance(calendar, pd.DataFrame) else calendar
                markdown += format_dataframe_as_markdown(df)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching calendar: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve calendar"))


@mcp.tool
async def get_splits(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get historical stock split data.

    Returns dates and split ratios for all historical stock splits.
    Useful for adjusting historical price analysis.
    """
    if ctx:
        await ctx.info(f"Fetching stock splits for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        splits = stock.splits

        if splits is None or splits.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No stock split data available"
            })

        # Convert Series to DataFrame
        df = splits.reset_index()
        df.columns = ["Date", "Split Ratio"]

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "splits_count": len(df),
                "splits": df.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Stock Splits for {ticker.upper()}\n\n"
            markdown += f"**Total Splits:** {len(df)}\n\n"
            markdown += format_dataframe_as_markdown(df)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching splits: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve stock splits"))


@mcp.tool
async def get_actions(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get all corporate actions (dividends + stock splits) history.

    Returns comprehensive corporate actions including:
    - Dividend payments with amounts
    - Stock splits with ratios

    Useful for complete historical corporate action analysis.
    """
    if ctx:
        await ctx.info(f"Fetching corporate actions for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        actions = stock.actions

        if actions is None or actions.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No corporate actions data available"
            })

        # Reset index to get dates as column
        df = actions.reset_index()

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "actions_count": len(df),
                "actions": df.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Corporate Actions for {ticker.upper()}\n\n"
            markdown += f"**Total Actions:** {len(df)}\n\n"
            markdown += format_dataframe_as_markdown(df, max_rows=100)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching corporate actions: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve corporate actions"))


@mcp.tool
async def get_fast_info(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get quick access to key stock statistics (faster than full info).

    Returns essential data:
    - Current price
    - Market cap
    - 52-week high/low
    - Volume
    - Shares outstanding
    - Currency and exchange

    Much faster than get_ticker_info for quick lookups.
    """
    if ctx:
        await ctx.info(f"Fetching fast info for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        fast_info = stock.fast_info

        # Convert FastInfo object to dict
        info_dict = {}
        for attr in dir(fast_info):
            if not attr.startswith('_'):
                try:
                    value = getattr(fast_info, attr)
                    if not callable(value):
                        info_dict[attr] = value
                except:
                    pass

        if len(info_dict) == 0:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No fast info data available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "fast_info": info_dict
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Quick Stats for {ticker.upper()}\n\n"

            # Group by category
            price_fields = ['last_price', 'open', 'previous_close', 'day_high', 'day_low']
            market_fields = ['market_cap', 'shares', 'currency', 'exchange', 'quote_type']
            range_fields = ['fifty_two_week_high', 'fifty_two_week_low', 'year_high', 'year_low']
            volume_fields = ['last_volume', 'ten_day_average_volume', 'three_month_average_volume']

            if any(k in info_dict for k in price_fields):
                markdown += "## Price Information\n\n"
                for key in price_fields:
                    if key in info_dict:
                        label = key.replace('_', ' ').title()
                        markdown += f"**{label}:** {info_dict[key]}\n\n"

            if any(k in info_dict for k in market_fields):
                markdown += "## Market Information\n\n"
                for key in market_fields:
                    if key in info_dict:
                        label = key.replace('_', ' ').title()
                        markdown += f"**{label}:** {info_dict[key]}\n\n"

            if any(k in info_dict for k in range_fields):
                markdown += "## 52-Week Range\n\n"
                for key in range_fields:
                    if key in info_dict:
                        label = key.replace('_', ' ').title()
                        markdown += f"**{label}:** {info_dict[key]}\n\n"

            if any(k in info_dict for k in volume_fields):
                markdown += "## Volume Statistics\n\n"
                for key in volume_fields:
                    if key in info_dict:
                        label = key.replace('_', ' ').title()
                        markdown += f"**{label}:** {info_dict[key]}\n\n"

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching fast info: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve fast info"))


@mcp.tool
async def get_earnings_history(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get recent quarterly earnings performance (last 4 quarters).

    Returns for each quarter:
    - EPS Actual (reported earnings per share)
    - EPS Estimate (analyst estimates)
    - EPS Difference (actual - estimate)
    - Surprise % (beat/miss percentage)

    Useful for tracking earnings momentum and analyst accuracy.
    """
    if ctx:
        await ctx.info(f"Fetching earnings history for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        earnings_history = stock.earnings_history

        if earnings_history is None or earnings_history.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No earnings history data available"
            })

        # Reset index to get dates as column
        df = earnings_history.reset_index()

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "quarters": len(df),
                "earnings_history": df.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Earnings History for {ticker.upper()}\n\n"
            markdown += f"**Quarters Reported:** {len(df)}\n\n"
            markdown += format_dataframe_as_markdown(df)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching earnings history: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve earnings history"))


@mcp.tool
async def get_analyst_price_targets(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get analyst price target consensus.

    Returns:
    - Current consensus target
    - High target
    - Low target
    - Mean target
    - Median target

    Useful for understanding analyst valuation expectations.
    """
    if ctx:
        await ctx.info(f"Fetching analyst price targets for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        price_targets = stock.analyst_price_targets

        if price_targets is None or (isinstance(price_targets, dict) and len(price_targets) == 0):
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No analyst price targets available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "price_targets": price_targets
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Analyst Price Targets for {ticker.upper()}\n\n"

            if isinstance(price_targets, dict):
                for key, value in price_targets.items():
                    label = key.replace('_', ' ').title()
                    markdown += f"**{label}:** {value}\n\n"
            else:
                markdown += str(price_targets)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching price targets: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve analyst price targets"))


@mcp.tool
async def get_recommendations_summary(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get analyst recommendations summary by period.

    Returns recommendations counts over multiple periods:
    - Strong Buy
    - Buy
    - Hold
    - Sell
    - Strong Sell

    Shows trends in analyst sentiment over time.
    """
    if ctx:
        await ctx.info(f"Fetching recommendations summary for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        rec_summary = stock.recommendations_summary

        if rec_summary is None or rec_summary.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No recommendations summary available"
            })

        # Reset index to get period as column
        df = rec_summary.reset_index(drop=True)

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "periods": len(df),
                "recommendations_summary": df.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Recommendations Summary for {ticker.upper()}\n\n"
            markdown += f"**Periods Tracked:** {len(df)}\n\n"
            markdown += format_dataframe_as_markdown(df)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching recommendations summary: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve recommendations summary"))


@mcp.tool
async def get_history_metadata(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get historical trading metadata.

    Returns rich metadata including:
    - Currency and exchange information
    - Timezone and trading hours
    - Instrument type
    - First trade date
    - 52-week high/low
    - Current trading period info
    - Price hint and scale

    Useful for understanding market context and trading parameters.
    """
    if ctx:
        await ctx.info(f"Fetching history metadata for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        metadata = stock.history_metadata

        if metadata is None or (isinstance(metadata, dict) and len(metadata) == 0):
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No history metadata available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "metadata": metadata
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# History Metadata for {ticker.upper()}\n\n"

            if isinstance(metadata, dict):
                # Group related fields
                basic_info = ['symbol', 'currency', 'exchangeName', 'fullExchangeName',
                             'instrumentType', 'timezone', 'exchangeTimezoneName']
                trading_info = ['regularMarketPrice', 'previousClose', 'regularMarketVolume',
                               'regularMarketTime', 'regularMarketDayHigh', 'regularMarketDayLow']
                range_info = ['fiftyTwoWeekHigh', 'fiftyTwoWeekLow', 'chartPreviousClose']
                other_info = ['firstTradeDate', 'gmtoffset', 'priceHint', 'scale',
                             'longName', 'shortName']

                if any(k in metadata for k in basic_info):
                    markdown += "## Basic Information\n\n"
                    for key in basic_info:
                        if key in metadata:
                            label = key.replace('_', ' ').title()
                            markdown += f"**{label}:** {metadata[key]}\n\n"

                if any(k in metadata for k in trading_info):
                    markdown += "## Trading Information\n\n"
                    for key in trading_info:
                        if key in metadata:
                            label = key.replace('_', ' ').title()
                            markdown += f"**{label}:** {metadata[key]}\n\n"

                if any(k in metadata for k in range_info):
                    markdown += "## Price Range\n\n"
                    for key in range_info:
                        if key in metadata:
                            label = key.replace('_', ' ').title()
                            markdown += f"**{label}:** {metadata[key]}\n\n"

                if any(k in metadata for k in other_info):
                    markdown += "## Other Metadata\n\n"
                    for key in other_info:
                        if key in metadata:
                            label = key.replace('_', ' ').title()
                            markdown += f"**{label}:** {metadata[key]}\n\n"

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching history metadata: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve history metadata"))


@mcp.tool
async def get_major_holders(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get major holders breakdown.

    Returns ownership structure:
    - Insider ownership percentage
    - Institutional ownership percentage
    - Float percentage
    - Shares outstanding

    Quick overview of stock ownership concentration.
    """
    if ctx:
        await ctx.info(f"Fetching major holders for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        major_holders = stock.major_holders

        if major_holders is None or major_holders.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No major holders data available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "major_holders": major_holders.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Major Holders for {ticker.upper()}\n\n"
            markdown += format_dataframe_as_markdown(major_holders)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching major holders: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve major holders"))


@mcp.tool
async def get_mutualfund_holders(
    ticker: Annotated[str, Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")],
    format: Annotated[Literal["json", "markdown"], Field(description="Output format")] = "markdown",
    ctx: Context = None
) -> str:
    """
    Get top mutual fund holders.

    Returns top 10 mutual funds holding the stock:
    - Date reported
    - Fund name
    - Percentage held
    - Number of shares
    - Total value
    - Percentage change in position

    Different from institutional holders - shows specific mutual funds
    (e.g., Vanguard 500 Index Fund) rather than institutions (e.g., Vanguard Group).
    Useful for understanding retail fund exposure.
    """
    if ctx:
        await ctx.info(f"Fetching mutual fund holders for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        mf_holders = stock.mutualfund_holders

        if mf_holders is None or mf_holders.empty:
            return json.dumps({
                "ticker": ticker.upper(),
                "message": "No mutual fund holders data available"
            })

        if format == "json":
            result = {
                "ticker": ticker.upper(),
                "funds_count": len(mf_holders),
                "mutualfund_holders": mf_holders.to_dict(orient="records")
            }
            output = json.dumps(result, indent=2, default=str)
            return truncate_text(output)
        else:
            markdown = f"# Mutual Fund Holders for {ticker.upper()}\n\n"
            markdown += f"**Top Funds:** {len(mf_holders)}\n\n"
            markdown += format_dataframe_as_markdown(mf_holders, max_rows=50)

            return truncate_text(markdown)

    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching mutual fund holders: {str(e)}")
        return json.dumps(handle_yfinance_error(ticker, "retrieve mutual fund holders"))


if __name__ == "__main__":
    mcp.run()
