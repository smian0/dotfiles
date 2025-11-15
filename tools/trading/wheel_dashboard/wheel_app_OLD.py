#!/usr/bin/env python3
"""
Wheel Strategy Dashboard - Real-time Options Screening
Institutional-grade signal generator with actionable alerts
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px

# Options math utilities
from utils.options_math import (
    calculate_probability_of_profit,
    calculate_expected_move,
    get_atm_iv
)

# Flow dashboard components
from components.flow_dashboard import render_flow_alerts_sidebar
from components.ib_connection import render_ib_connection_sidebar

# Page configuration
st.set_page_config(
    page_title="Wheel Strategy Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Market hours configuration
NYSE_TZ = pytz.timezone('America/New_York')
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)

# Pre-configured watchlists
WATCHLISTS = {
    "S&P 100 Dividend Aristocrats": [
        "KO", "JNJ", "PG", "WMT", "T", "PEP", "CL", "MMM", "CAT", "XOM",
        "CVX", "ABT", "MDT", "TMO", "LLY", "UNH", "WBA", "HD", "LOW", "TGT"
    ],
    "Dividend Kings": ["KO", "JNJ", "PG", "CL", "EMR", "GPC", "HRL", "SJW"],
    "Low Beta Blue Chips": ["KO", "JNJ", "PG", "WMT", "PEP", "MCD", "NEE", "DUK"],
    "Test Portfolio": ["KO", "JNJ", "PG"]
}

# Alert thresholds
ALERT_THRESHOLDS = {
    "min_score": 35.0,
    "min_premium_yield": 8.0,
    "max_spread_pct": 30.0,
    "min_open_interest": 50
}


def is_market_open() -> bool:
    """Check if market is currently open"""
    now = datetime.now(NYSE_TZ)

    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Check if market hours
    current_time = now.time()
    return MARKET_OPEN <= current_time <= MARKET_CLOSE


def get_next_market_open() -> datetime:
    """Get next market open time"""
    now = datetime.now(NYSE_TZ)

    # If it's before market open today, return today's open
    if now.time() < MARKET_OPEN and now.weekday() < 5:
        return now.replace(hour=9, minute=30, second=0, microsecond=0)

    # Otherwise, find next trading day
    days_ahead = 1
    if now.weekday() == 4:  # Friday
        days_ahead = 3
    elif now.weekday() == 5:  # Saturday
        days_ahead = 2

    next_open = now + timedelta(days=days_ahead)
    return next_open.replace(hour=9, minute=30, second=0, microsecond=0)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(ticker: str) -> Optional[Dict]:
    """Fetch stock fundamentals"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker,
            "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
            "dividend_yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0,
            "beta": info.get("beta", 1.0),
            "market_cap": info.get("marketCap", 0),
            "company_name": info.get("longName", ticker)
        }
    except Exception as e:
        st.error(f"Error fetching {ticker}: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_options_data(ticker: str, target_dte_min: int = 30, target_dte_max: int = 45) -> Optional[Dict]:
    """Fetch options chain data for target DTE range"""
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options

        if not expirations:
            return None

        # Find expiration in target DTE range
        today = datetime.now().date()
        best_expiration = None
        best_dte_diff = float('inf')

        for exp_str in expirations:
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
            dte = (exp_date - today).days

            if target_dte_min <= dte <= target_dte_max:
                dte_diff = abs(dte - 37)  # Prefer 37 DTE (midpoint)
                if dte_diff < best_dte_diff:
                    best_expiration = exp_str
                    best_dte_diff = dte_diff

        if not best_expiration:
            # Fallback to nearest expiration
            best_expiration = min(expirations,
                                key=lambda x: abs((datetime.strptime(x, "%Y-%m-%d").date() - today).days - 37))

        # Get options chain
        opt_chain = stock.option_chain(best_expiration)
        puts = opt_chain.puts

        exp_date = datetime.strptime(best_expiration, "%Y-%m-%d").date()
        dte = (exp_date - today).days

        return {
            "expiration": best_expiration,
            "dte": dte,
            "puts": puts
        }

    except Exception as e:
        st.error(f"Error fetching options for {ticker}: {str(e)}")
        return None


def find_optimal_put(current_price: float, puts_df: pd.DataFrame, dte: int) -> Optional[Dict]:
    """Find optimal put strike (2-5% OTM)"""
    if puts_df.empty:
        return None

    # Target range: 2-5% below current price
    target_low = current_price * 0.95
    target_high = current_price * 0.98

    # Filter puts in range
    candidates = puts_df[
        (puts_df['strike'] >= target_low) &
        (puts_df['strike'] <= target_high)
    ].copy()

    if candidates.empty:
        # Fallback: closest to 5% OTM
        candidates = puts_df.copy()

    # Calculate metrics for each candidate
    candidates['mid_price'] = (candidates['bid'] + candidates['ask']) / 2
    candidates['spread_pct'] = ((candidates['ask'] - candidates['bid']) / candidates['mid_price'] * 100)
    candidates['annualized_yield'] = (candidates['mid_price'] / candidates['strike']) * (365 / dte) * 100
    candidates['distance_pct'] = ((current_price - candidates['strike']) / current_price * 100)

    # Score candidates (prefer higher premium, tighter spread, decent OI)
    candidates['score'] = (
        candidates['annualized_yield'] * 0.5 +
        (100 - candidates['spread_pct']) * 0.3 +
        np.log1p(candidates['openInterest']) * 0.2
    )

    # Select best candidate
    best = candidates.nlargest(1, 'score').iloc[0]

    # Calculate Probability of Profit
    iv_decimal = best['impliedVolatility'] if pd.notna(best['impliedVolatility']) else None
    pop = None

    if iv_decimal and iv_decimal > 0:
        pop = calculate_probability_of_profit(
            stock_price=current_price,
            strike_price=best['strike'],
            dte=dte,
            implied_volatility=iv_decimal,
            option_type='put'
        )

    return {
        "strike": best['strike'],
        "premium": best['mid_price'],
        "bid": best['bid'],
        "ask": best['ask'],
        "annualized_yield": best['annualized_yield'],
        "spread_pct": best['spread_pct'],
        "open_interest": int(best['openInterest']),
        "volume": int(best['volume']) if pd.notna(best['volume']) else 0,
        "implied_volatility": best['impliedVolatility'] * 100 if pd.notna(best['impliedVolatility']) else 0,
        "distance_pct": best['distance_pct'],
        "probability_of_profit": pop,
        # Greeks (from yfinance, may be None)
        "delta": best.get('delta') if pd.notna(best.get('delta')) else None,
        "gamma": best.get('gamma') if pd.notna(best.get('gamma')) else None,
        "theta": best.get('theta') if pd.notna(best.get('theta')) else None,
        "vega": best.get('vega') if pd.notna(best.get('vega')) else None
    }


def calculate_wheel_score(ticker_data: Dict) -> float:
    """Calculate institutional wheel strategy score (0-100)"""
    premium_yield = ticker_data['recommended_put']['annualized_yield']
    dividend_yield = ticker_data['dividend_yield']
    iv = ticker_data['recommended_put']['implied_volatility']
    open_interest = ticker_data['recommended_put']['open_interest']
    spread_pct = ticker_data['recommended_put']['spread_pct']
    beta = ticker_data['beta']

    # Normalize components (0-1 scale)
    premium_score = min(premium_yield / 30, 1.0)  # 30% = perfect
    dividend_score = min(dividend_yield / 8, 1.0)  # 8% div = perfect
    iv_score = min(iv / 50, 1.0)  # 50% IV = perfect
    liquidity_score = min(open_interest / 10000, 1.0) * (1 - min(spread_pct / 50, 1.0))
    quality_score = 1.0 if beta < 1.2 else 0.5

    # Weighted sum
    total_score = (
        0.40 * premium_score +
        0.20 * dividend_score +
        0.20 * iv_score +
        0.10 * liquidity_score +
        0.10 * quality_score
    )

    return total_score * 100


def analyze_ticker(ticker: str, target_dte_min: int = 30, target_dte_max: int = 45) -> Optional[Dict]:
    """Complete wheel strategy analysis for a ticker"""

    # Get stock data
    stock_data = fetch_stock_data(ticker)
    if not stock_data or not stock_data['current_price']:
        return None

    # Get options data
    options_data = get_options_data(ticker, target_dte_min, target_dte_max)
    if not options_data:
        return None

    # Find optimal put
    optimal_put = find_optimal_put(
        stock_data['current_price'],
        options_data['puts'],
        options_data['dte']
    )

    if not optimal_put:
        return None

    # Calculate metrics
    breakeven = optimal_put['strike'] - optimal_put['premium']
    downside_protection = ((stock_data['current_price'] - breakeven) / stock_data['current_price'] * 100)

    # Combine data
    result = {
        **stock_data,
        "recommended_put": optimal_put,
        "expiration": options_data['expiration'],
        "dte": options_data['dte'],
        "metrics": {
            "breakeven": breakeven,
            "downside_protection_pct": downside_protection
        }
    }

    # IB features not available in web dashboard (use standalone scripts)
    result['iv_rank'] = None
    result['earnings'] = None
    result['exp_type'] = 'unknown'
    result['is_weekly'] = False

    # Calculate score
    result['score'] = calculate_wheel_score(result)

    return result


def create_gauge_chart(score: float, title: str = "Wheel Strategy Score") -> go.Figure:
    """Create gauge chart for score visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgray"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': ALERT_THRESHOLDS['min_score']
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def create_summary_table(results: List[Dict]) -> pd.DataFrame:
    """Create summary DataFrame for display"""
    rows = []
    for r in results:
        # IV Rank
        if r.get('iv_rank'):
            iv_rank_str = f"{r['iv_rank']['iv_rank']:.0f}"
            iv_status = r['iv_rank']['status']
        else:
            iv_rank_str = "N/A"
            iv_status = "UNKNOWN"

        # Earnings
        if r.get('earnings'):
            if r['earnings'].get('next_earnings_date'):
                earnings_str = f"{r['earnings']['days_to_earnings']}d"
                earnings_safe = "✅" if r['earnings']['safe_to_sell_puts'] else "⚠️"
            else:
                earnings_str = "None"
                earnings_safe = "✅"
        else:
            earnings_str = "N/A"
            earnings_safe = ""

        # Expiration type
        exp_type = r.get('exp_type', 'unknown')
        exp_type_display = "W" if exp_type == 'weekly' else "M" if exp_type == 'monthly' else "?"

        # Probability of Profit
        pop = r['recommended_put'].get('probability_of_profit')
        if pop:
            pop_str = f"{pop:.0f}%"
        else:
            pop_str = "N/A"

        # Greeks
        delta = r['recommended_put'].get('delta')
        delta_str = f"{delta:.3f}" if delta else "N/A"

        theta = r['recommended_put'].get('theta')
        # Theta is daily premium decay (negative for option sellers = positive for us)
        if theta:
            theta_str = f"${abs(theta):.2f}/day"
        else:
            theta_str = "N/A"

        rows.append({
            "Ticker": r['ticker'],
            "Score": f"{r['score']:.1f}",
            "PoP": pop_str,
            "Delta": delta_str,
            "Theta": theta_str,
            "IV Rank": iv_rank_str,
            "IV Status": iv_status,
            "Earnings": earnings_str,
            "Safe": earnings_safe,
            "Type": exp_type_display,
            "Company": r['company_name'][:30],
            "Price": f"${r['current_price']:.2f}",
            "Trade": f"Sell ${r['recommended_put']['strike']:.0f} Put",
            "Premium": f"${r['recommended_put']['premium']:.2f}",
            "Annual Yield": f"{r['recommended_put']['annualized_yield']:.1f}%",
            "Div Yield": f"{r['dividend_yield']:.2f}%",
            "Total Return": f"{r['recommended_put']['annualized_yield'] + r['dividend_yield']:.1f}%",
            "OI": r['recommended_put']['open_interest'],
            "Spread": f"{r['recommended_put']['spread_pct']:.1f}%",
            "DTE": r['dte'],
            "Exp": r['expiration']
        })

    return pd.DataFrame(rows)


def check_alerts(results: List[Dict]) -> List[Dict]:
    """Check which opportunities meet alert criteria"""
    alerts = []

    for r in results:
        alert_reasons = []

        if r['score'] >= ALERT_THRESHOLDS['min_score']:
            alert_reasons.append(f"High Score ({r['score']:.1f})")

        if r['recommended_put']['annualized_yield'] >= ALERT_THRESHOLDS['min_premium_yield']:
            alert_reasons.append(f"High Premium ({r['recommended_put']['annualized_yield']:.1f}%)")

        if (r['recommended_put']['spread_pct'] <= ALERT_THRESHOLDS['max_spread_pct'] and
            r['recommended_put']['open_interest'] >= ALERT_THRESHOLDS['min_open_interest']):
            alert_reasons.append("Excellent Liquidity")

        if alert_reasons:
            alerts.append({
                "ticker": r['ticker'],
                "score": r['score'],
                "reasons": alert_reasons,
                "data": r
            })

    return alerts


# Main Streamlit App
def main():
    # Header
    st.title("🎯 Wheel Strategy Dashboard")
    st.markdown("*Institutional-grade options screening with real-time alerts*")

    # Market status
    market_open = is_market_open()
    next_open = get_next_market_open()

    col1, col2, col3 = st.columns(3)

    with col1:
        if market_open:
            st.success("🟢 **Market OPEN**")
        else:
            st.error("🔴 **Market CLOSED**")
            st.info(f"Next open: {next_open.strftime('%Y-%m-%d %H:%M %Z')}")

    with col2:
        st.metric("Current Time (EST)", datetime.now(NYSE_TZ).strftime("%H:%M:%S"))

    with col3:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")

    # Watchlist selection
    watchlist_name = st.sidebar.selectbox(
        "Select Watchlist",
        list(WATCHLISTS.keys())
    )

    tickers = WATCHLISTS[watchlist_name]
    st.sidebar.info(f"**{len(tickers)} tickers** in watchlist")

    # DTE range
    st.sidebar.subheader("Options Filters")
    dte_min = st.sidebar.slider("Min DTE", 7, 60, 30)
    dte_max = st.sidebar.slider("Max DTE", 7, 90, 45)

    # Alert thresholds
    st.sidebar.subheader("Alert Thresholds")
    ALERT_THRESHOLDS['min_score'] = st.sidebar.slider("Min Score", 0.0, 100.0, 35.0)
    ALERT_THRESHOLDS['min_premium_yield'] = st.sidebar.slider("Min Premium Yield %", 0.0, 30.0, 8.0)

    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("Auto-refresh (market hours)", value=False)
    if auto_refresh and market_open:
        refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 30, 300, 60)
        st.sidebar.info(f"Refreshing every {refresh_interval}s")

    # IB connection controls
    try:
        render_ib_connection_sidebar()
    except Exception:
        # Silently fail if IB not available
        pass

    # Flow alerts sidebar
    try:
        render_flow_alerts_sidebar()
    except Exception:
        # Silently fail if flow database not available
        pass

    # Main content
    st.header(f"📊 Analyzing: {watchlist_name}")

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Analyze tickers
    results = []
    for i, ticker in enumerate(tickers):
        status_text.text(f"Analyzing {ticker}... ({i+1}/{len(tickers)})")
        progress_bar.progress((i + 1) / len(tickers))

        result = analyze_ticker(ticker, dte_min, dte_max)
        if result:
            results.append(result)

    status_text.empty()
    progress_bar.empty()

    if not results:
        st.warning("No valid opportunities found. Try adjusting filters.")
        return

    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)

    # Calculate Expected Move for top opportunity
    if results:
        top_result = results[0]
        iv_decimal = top_result['recommended_put'].get('implied_volatility', 0) / 100.0

        if iv_decimal > 0:
            expected_move = calculate_expected_move(
                stock_price=top_result['current_price'],
                atm_iv=iv_decimal,
                dte=top_result['dte']
            )

            if expected_move:
                st.info(f"""
                **Expected Move for {top_result['ticker']}**:
                ±${expected_move['move_dollars']:.2f} (±{expected_move['move_percent']:.1f}%)
                with {expected_move['probability']:.0f}% probability

                **Range**: ${expected_move['lower_bound']:.2f} - ${expected_move['upper_bound']:.2f}
                (Based on {top_result['dte']} DTE, {iv_decimal*100:.1f}% IV)
                """)

    # Check alerts
    alerts = check_alerts(results)

    # Display alerts
    if alerts:
        st.header("🚨 Active Alerts")

        for alert in alerts:
            with st.expander(f"⚠️ {alert['ticker']} - Score: {alert['score']:.1f} - {', '.join(alert['reasons'])}", expanded=True):
                data = alert['data']

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Current Price", f"${data['current_price']:.2f}")
                    st.metric("Recommended Strike", f"${data['recommended_put']['strike']:.0f}")
                    st.metric("Premium", f"${data['recommended_put']['premium']:.2f}")

                with col2:
                    st.metric("Annual Yield", f"{data['recommended_put']['annualized_yield']:.1f}%")
                    st.metric("Dividend Yield", f"{data['dividend_yield']:.2f}%")
                    st.metric("Total Return", f"{data['recommended_put']['annualized_yield'] + data['dividend_yield']:.1f}%")

                with col3:
                    st.metric("Open Interest", data['recommended_put']['open_interest'])
                    st.metric("Bid/Ask Spread", f"{data['recommended_put']['spread_pct']:.1f}%")
                    st.metric("Breakeven", f"${data['metrics']['breakeven']:.2f}")

                # Action button
                st.info(f"**Trade:** Sell {data['ticker']} {data['expiration']} ${data['recommended_put']['strike']:.0f} Put @ ${data['recommended_put']['premium']:.2f}")

    # Summary table
    st.header("📈 Top Opportunities")

    summary_df = create_summary_table(results[:10])

    # Style the dataframe
    def highlight_score(row):
        score = float(row['Score'])
        if score >= 60:
            return ['background-color: lightgreen'] * len(row)
        elif score >= 35:
            return ['background-color: lightyellow'] * len(row)
        return [''] * len(row)

    st.dataframe(
        summary_df.style.apply(highlight_score, axis=1),
        use_container_width=True,
        height=400
    )

    # Detailed analysis
    st.header("🔍 Detailed Analysis")

    selected_ticker = st.selectbox(
        "Select ticker for detailed view",
        [r['ticker'] for r in results]
    )

    selected_data = next(r for r in results if r['ticker'] == selected_ticker)

    # Display detailed metrics
    col1, col2 = st.columns([1, 2])

    with col1:
        fig = create_gauge_chart(selected_data['score'], f"{selected_ticker} Score")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader(f"{selected_data['company_name']}")

        # Build markdown sections
        markdown_parts = [f"""
        **Current Price:** ${selected_data['current_price']:.2f}
        **Market Cap:** ${selected_data['market_cap']/1e9:.1f}B
        **Beta:** {selected_data['beta']:.2f}
        **Dividend Yield:** {selected_data['dividend_yield']:.2f}%
        """]

        # Add IB data if available
        if selected_data.get('iv_rank'):
            iv = selected_data['iv_rank']
            status_emoji = "🟢" if iv['status'] == 'HIGH' else "🟡" if iv['status'] == 'NORMAL' else "🔴"
            markdown_parts.append(f"""
        **IV Rank:** {iv['iv_rank']:.0f}/100 {status_emoji} {iv['status']}
        **Current IV:** {iv['current_iv']:.1f}% (52w: {iv['52w_low']:.1f}% - {iv['52w_high']:.1f}%)
        **IV Percentile:** {iv['iv_percentile']:.0f}%
            """)

        if selected_data.get('earnings'):
            earnings = selected_data['earnings']
            if earnings.get('next_earnings_date'):
                safe_emoji = "✅" if earnings['safe_to_sell_puts'] else "⚠️"
                markdown_parts.append(f"""
        **Next Earnings:** {earnings['next_earnings_date']} ({earnings['days_to_earnings']} days)
        **Earnings Safety:** {safe_emoji} {earnings['reason']}
                """)
            else:
                markdown_parts.append(f"""
        **Next Earnings:** No scheduled earnings ✅
                """)

        if selected_data.get('exp_type') != 'unknown':
            exp_type_str = "Weekly" if selected_data['exp_type'] == 'weekly' else "Monthly"
            markdown_parts.append(f"""
        **Expiration Type:** {exp_type_str} ({selected_data['dte']} DTE)
            """)

        markdown_parts.append(f"""
        ---

        **Recommended Trade:**
        Sell {selected_ticker} {selected_data['expiration']} ${selected_data['recommended_put']['strike']:.0f} Put

        **Premium:** ${selected_data['recommended_put']['premium']:.2f} (${selected_data['recommended_put']['premium'] * 100:.0f} per contract)
        **Annualized Yield:** {selected_data['recommended_put']['annualized_yield']:.1f}%
        **Total Return:** {selected_data['recommended_put']['annualized_yield'] + selected_data['dividend_yield']:.1f}% (with dividends)

        **Breakeven:** ${selected_data['metrics']['breakeven']:.2f} ({selected_data['metrics']['downside_protection_pct']:.1f}% protection)

        **Liquidity:**
        Open Interest: {selected_data['recommended_put']['open_interest']:,}
        Bid/Ask: ${selected_data['recommended_put']['bid']:.2f} / ${selected_data['recommended_put']['ask']:.2f} ({selected_data['recommended_put']['spread_pct']:.1f}% spread)
        """)

        # Add Greeks section if available
        greeks_data = selected_data['recommended_put']
        if any([greeks_data.get('delta'), greeks_data.get('theta'), greeks_data.get('gamma'), greeks_data.get('vega')]):
            greeks_section = "\n---\n\n**📊 Greeks (Risk Metrics):**\n"

            if greeks_data.get('delta'):
                delta = greeks_data['delta']
                greeks_section += f"\n**Delta:** {delta:.3f} → If stock moves $1, put value changes by ${abs(delta):.2f}"

            if greeks_data.get('theta'):
                theta = greeks_data['theta']
                daily_income = abs(theta) * 100  # Per contract
                greeks_section += f"\n**Theta:** {theta:.3f} → Earn ${daily_income:.2f}/day per contract from time decay 🎯"

            if greeks_data.get('gamma'):
                gamma = greeks_data['gamma']
                gamma_risk = "LOW" if abs(gamma) < 0.05 else "MEDIUM" if abs(gamma) < 0.10 else "HIGH"
                greeks_section += f"\n**Gamma:** {gamma:.3f} → Delta stability: {gamma_risk}"

            if greeks_data.get('vega'):
                vega = greeks_data['vega']
                iv_risk = "LOW" if abs(vega) < 0.15 else "MEDIUM" if abs(vega) < 0.25 else "HIGH"
                greeks_section += f"\n**Vega:** {vega:.3f} → IV sensitivity: {iv_risk}"

            markdown_parts.append(greeks_section)

        st.markdown("\n".join(markdown_parts))

    # Execution checklist
    st.header("✅ Execution Checklist")

    # Build checklist
    checklist = [
        f"Account has ${selected_data['recommended_put']['strike'] * 100:.0f} in cash to secure put"
    ]

    # Add earnings check based on IB data
    if selected_data.get('earnings'):
        earnings = selected_data['earnings']
        if earnings.get('safe_to_sell_puts'):
            checklist.append(f"✅ Earnings check passed: {earnings['reason']}")
        else:
            checklist.append(f"⚠️ EARNINGS RISK: {earnings['reason']}")
    else:
        checklist.append("Checked earnings date (avoid selling puts before earnings)")

    # Add IV Rank check if available
    if selected_data.get('iv_rank'):
        iv = selected_data['iv_rank']
        if iv['status'] == 'HIGH':
            checklist.append(f"✅ IV Rank {iv['iv_rank']:.0f}/100 - EXCELLENT for selling premium")
        elif iv['status'] == 'NORMAL':
            checklist.append(f"🟡 IV Rank {iv['iv_rank']:.0f}/100 - Normal (consider other factors)")
        else:
            checklist.append(f"⚠️ IV Rank {iv['iv_rank']:.0f}/100 - LOW (wait for IV expansion)")

    checklist.extend([
        f"Bid/ask spread is acceptable ({selected_data['recommended_put']['spread_pct']:.1f}%)",
        f"Ready to use limit order at mid-price (${selected_data['recommended_put']['premium']:.2f})",
        "Position sizing appropriate (< 10% of portfolio)",
        f"Happy to own {selected_ticker} at ${selected_data['recommended_put']['strike']:.0f}?"
    ])

    checklist_md = "\n".join([f"- [ ] {item}" for item in checklist])

    st.markdown(f"""
    Before placing trade for **{selected_ticker}**:

    {checklist_md}

    **Risk Warning:** Maximum loss = Breakeven price (${selected_data['metrics']['breakeven']:.2f} per share)
    """)

    # Auto-refresh logic
    if auto_refresh and market_open:
        import time
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
