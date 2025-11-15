#!/usr/bin/env python3
"""
Advanced Analytics Page - OI Heatmaps & Strike Analysis

Deep dive analytics for options traders:
- Open Interest heatmaps
- Volume vs OI comparison
- Max Pain calculator
- Strike distribution analysis
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.flow_analysis import (
    detect_unusual_activity,
    generate_wheel_signals,
    get_top_unusual_strikes
)

# Import flow dashboard components
from components.flow_dashboard import (
    render_flow_analysis_tab,
    render_flow_stats_widget,
    render_flow_alerts_sidebar,
    render_live_scan_button
)
from components.ib_connection import render_ib_connection_sidebar

# Page configuration
st.set_page_config(
    page_title="Advanced Analytics",
    page_icon="📊",
    layout="wide"
)


def init_ib_connection():
    """
    Initialize IB connection (optional for advanced analytics)

    Note: Advanced analytics works fine with yfinance data alone.
    IB connection disabled for this page to avoid threading issues.
    """
    # IB connection disabled for advanced analytics page
    # yfinance provides all needed data (OI, volume, strikes)
    return {
        'manager': None,
        'scanner': None,
        'connected': False,
        'message': 'IB not required for Advanced Analytics (using yfinance)'
    }


@st.cache_data(ttl=300)
def get_full_options_chain(ticker: str, max_expirations: int = 6) -> Optional[Dict]:
    """Get complete options chain for all expirations"""
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options[:max_expirations]  # Limit to avoid slowdown

        all_puts = []
        all_calls = []

        for exp in expirations:
            chain = stock.option_chain(exp)

            # Add expiration column
            chain.puts['expiration'] = exp
            chain.calls['expiration'] = exp

            all_puts.append(chain.puts)
            all_calls.append(chain.calls)

        puts_df = pd.concat(all_puts, ignore_index=True)
        calls_df = pd.concat(all_calls, ignore_index=True)

        return {
            'puts': puts_df,
            'calls': calls_df,
            'expirations': expirations
        }

    except Exception as e:
        st.error(f"Error fetching options chain: {e}")
        return None


def create_oi_heatmap(options_df: pd.DataFrame, option_type: str, ticker: str, current_price: float) -> go.Figure:
    """Create Open Interest heatmap"""

    # Pivot data for heatmap
    pivot_data = options_df.pivot_table(
        values='openInterest',
        index='expiration',
        columns='strike',
        aggfunc='sum',
        fill_value=0
    )

    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Viridis',
        colorbar=dict(title="Open Interest"),
        hovertemplate='Strike: $%{x}<br>Expiration: %{y}<br>OI: %{z:,.0f}<extra></extra>'
    ))

    # Add current price line
    fig.add_vline(
        x=current_price,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Current: ${current_price:.2f}",
        annotation_position="top"
    )

    fig.update_layout(
        title=f"{ticker} {option_type.upper()} Open Interest Heatmap",
        xaxis_title="Strike Price",
        yaxis_title="Expiration Date",
        height=500
    )

    return fig


def create_oi_volume_comparison(options_df: pd.DataFrame, expiration: str, option_type: str) -> go.Figure:
    """Compare Volume vs Open Interest for single expiration"""

    exp_data = options_df[options_df['expiration'] == expiration].copy()
    exp_data = exp_data.sort_values('strike')

    fig = go.Figure()

    # Volume bars
    fig.add_trace(go.Bar(
        x=exp_data['strike'],
        y=exp_data['volume'],
        name='Volume',
        marker_color='lightblue',
        yaxis='y'
    ))

    # OI line
    fig.add_trace(go.Scatter(
        x=exp_data['strike'],
        y=exp_data['openInterest'],
        name='Open Interest',
        line=dict(color='orange', width=3),
        yaxis='y2'
    ))

    fig.update_layout(
        title=f"{option_type.upper()} Volume vs Open Interest - {expiration}",
        xaxis_title="Strike Price",
        yaxis=dict(title="Volume", side='left'),
        yaxis2=dict(title="Open Interest", overlaying='y', side='right'),
        hovermode='x unified',
        height=400
    )

    return fig


def create_strike_distribution(options_df: pd.DataFrame, expiration: str, current_price: float) -> go.Figure:
    """Visualize OI distribution across strikes"""

    exp_data = options_df[options_df['expiration'] == expiration].copy()
    exp_data = exp_data.sort_values('strike')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=exp_data['strike'],
        y=exp_data['openInterest'],
        name='Open Interest',
        marker_color='steelblue',
        hovertemplate='Strike: $%{x}<br>OI: %{y:,.0f}<extra></extra>'
    ))

    # Add current price line
    fig.add_vline(
        x=current_price,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Current: ${current_price:.2f}",
        annotation_position="top"
    )

    fig.update_layout(
        title=f"Strike Distribution - {expiration}",
        xaxis_title="Strike Price",
        yaxis_title="Open Interest",
        height=400
    )

    return fig


def calculate_max_pain(puts_df: pd.DataFrame, calls_df: pd.DataFrame, expiration: str, current_price: float) -> Dict:
    """
    Calculate Max Pain - strike where most options expire worthless

    Max Pain theory: Market makers have incentive to push price toward strike
    where they pay out the least money to option holders.
    """

    puts = puts_df[puts_df['expiration'] == expiration].copy()
    calls = calls_df[calls_df['expiration'] == expiration].copy()

    if puts.empty or calls.empty:
        return None

    # Get unique strikes
    strikes = sorted(set(puts['strike'].unique()) | set(calls['strike'].unique()))

    max_pain_data = []

    for strike in strikes:
        # Calculate pain (value option holders would receive)

        # ITM puts (strike > current_price at expiration)
        itm_puts = puts[puts['strike'] > strike]
        put_pain = ((itm_puts['strike'] - strike) * itm_puts['openInterest']).sum()

        # ITM calls (strike < current_price at expiration)
        itm_calls = calls[calls['strike'] < strike]
        call_pain = ((strike - itm_calls['strike']) * itm_calls['openInterest']).sum()

        total_pain = put_pain + call_pain

        max_pain_data.append({
            'strike': strike,
            'total_pain': total_pain,
            'put_pain': put_pain,
            'call_pain': call_pain
        })

    max_pain_df = pd.DataFrame(max_pain_data)

    # Max pain is strike with MINIMUM total pain
    max_pain_strike = max_pain_df.loc[max_pain_df['total_pain'].idxmin()]

    return {
        'strike': max_pain_strike['strike'],
        'total_pain': max_pain_strike['total_pain'],
        'put_pain': max_pain_strike['put_pain'],
        'call_pain': max_pain_strike['call_pain'],
        'distance_from_current': ((max_pain_strike['strike'] - current_price) / current_price * 100),
        'data': max_pain_df
    }


def create_max_pain_chart(max_pain_result: Dict, current_price: float) -> go.Figure:
    """Visualize max pain across strikes"""

    df = max_pain_result['data']
    max_pain_strike = max_pain_result['strike']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['strike'],
        y=df['total_pain'],
        mode='lines',
        name='Total Pain',
        line=dict(color='purple', width=3),
        fill='tozeroy',
        fillcolor='rgba(128, 0, 128, 0.1)'
    ))

    # Mark max pain point
    fig.add_vline(
        x=max_pain_strike,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Max Pain: ${max_pain_strike:.2f}",
        annotation_position="top"
    )

    # Current price
    fig.add_vline(
        x=current_price,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Current: ${current_price:.2f}",
        annotation_position="bottom"
    )

    fig.update_layout(
        title="Max Pain Analysis",
        xaxis_title="Strike Price",
        yaxis_title="Total Pain (Lower = Max Pain)",
        hovermode='x unified',
        height=400
    )

    return fig


def create_put_call_ratio_chart(puts_df: pd.DataFrame, calls_df: pd.DataFrame, expiration: str) -> go.Figure:
    """Put/Call OI ratio at each strike"""

    puts = puts_df[puts_df['expiration'] == expiration][['strike', 'openInterest']].rename(columns={'openInterest': 'put_oi'})
    calls = calls_df[calls_df['expiration'] == expiration][['strike', 'openInterest']].rename(columns={'openInterest': 'call_oi'})

    merged = pd.merge(puts, calls, on='strike', how='outer').fillna(0)
    merged['pc_ratio'] = merged['put_oi'] / (merged['call_oi'] + 1)  # Avoid div by zero
    merged = merged.sort_values('strike')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=merged['strike'],
        y=merged['pc_ratio'],
        name='Put/Call Ratio',
        marker_color=['red' if r > 1 else 'green' for r in merged['pc_ratio']],
        hovertemplate='Strike: $%{x}<br>P/C Ratio: %{y:.2f}<extra></extra>'
    ))

    # Add reference line at 1.0
    fig.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="gray",
        annotation_text="Neutral (1.0)"
    )

    fig.update_layout(
        title=f"Put/Call Ratio by Strike - {expiration}",
        xaxis_title="Strike Price",
        yaxis_title="Put/Call Ratio (OI)",
        height=400
    )

    return fig


def create_iv_skew_chart(options_df: pd.DataFrame, expiration: str, option_type: str, current_price: float) -> go.Figure:
    """Visualize IV skew (volatility smile) across strikes"""

    exp_data = options_df[options_df['expiration'] == expiration].copy()
    exp_data = exp_data[exp_data['impliedVolatility'] > 0]  # Filter out zero IV
    exp_data = exp_data.sort_values('strike')

    if exp_data.empty:
        return None

    # Convert IV to percentage
    exp_data['iv_pct'] = exp_data['impliedVolatility'] * 100

    # Calculate moneyness (strike / spot)
    exp_data['moneyness'] = (exp_data['strike'] / current_price - 1) * 100

    fig = go.Figure()

    # IV Skew line
    fig.add_trace(go.Scatter(
        x=exp_data['strike'],
        y=exp_data['iv_pct'],
        mode='lines+markers',
        name='Implied Volatility',
        line=dict(color='blue', width=3),
        marker=dict(size=8),
        hovertemplate='Strike: $%{x}<br>IV: %{y:.1f}%<extra></extra>'
    ))

    # Mark ATM strike
    atm_strike = exp_data.iloc[(exp_data['strike'] - current_price).abs().argsort()[0]]

    fig.add_vline(
        x=current_price,
        line_dash="dash",
        line_color="red",
        annotation_text=f"ATM: ${current_price:.2f}",
        annotation_position="top"
    )

    # Highlight expensive strikes (high IV)
    if len(exp_data) > 3:
        top_iv_percentile = exp_data['iv_pct'].quantile(0.75)
        expensive_strikes = exp_data[exp_data['iv_pct'] >= top_iv_percentile]

        fig.add_trace(go.Scatter(
            x=expensive_strikes['strike'],
            y=expensive_strikes['iv_pct'],
            mode='markers',
            name='High IV Strikes',
            marker=dict(size=12, color='orange', symbol='star'),
            hovertemplate='Strike: $%{x}<br>IV: %{y:.1f}% (Expensive!)<extra></extra>'
        ))

    fig.update_layout(
        title=f"{option_type.upper()} IV Skew - {expiration}",
        xaxis_title="Strike Price",
        yaxis_title="Implied Volatility (%)",
        hovermode='x unified',
        height=450
    )

    return fig


def analyze_iv_skew(options_df: pd.DataFrame, expiration: str, current_price: float) -> Dict:
    """Analyze IV skew pattern and identify opportunities"""

    exp_data = options_df[options_df['expiration'] == expiration].copy()
    exp_data = exp_data[exp_data['impliedVolatility'] > 0]

    if exp_data.empty:
        return None

    exp_data['iv_pct'] = exp_data['impliedVolatility'] * 100
    exp_data = exp_data.sort_values('strike')

    # Find ATM strike
    atm_idx = (exp_data['strike'] - current_price).abs().argsort()[0]
    atm_strike = exp_data.iloc[atm_idx]

    # Analyze OTM put skew (strikes below ATM)
    otm_puts = exp_data[exp_data['strike'] < current_price].copy()

    if not otm_puts.empty:
        # Compare 5% OTM to ATM
        target_strike = current_price * 0.95
        otm_5pct = otm_puts.iloc[(otm_puts['strike'] - target_strike).abs().argsort()[0]]

        skew_premium = otm_5pct['iv_pct'] - atm_strike['iv_pct']

        return {
            'atm_strike': atm_strike['strike'],
            'atm_iv': atm_strike['iv_pct'],
            'otm_5pct_strike': otm_5pct['strike'],
            'otm_5pct_iv': otm_5pct['iv_pct'],
            'skew_premium': skew_premium,
            'interpretation': (
                "Steep skew - OTM puts expensive (good for selling)"
                if skew_premium > 2 else
                "Flat skew - normal pricing" if abs(skew_premium) <= 2 else
                "Reverse skew - OTM puts cheap (avoid selling)"
            )
        }

    return None


def main():
    st.title("📊 Advanced Options Analytics")
    st.markdown("*Deep dive into Open Interest, Volume, and Market Structure*")

    # Show discovery context if coming from Discovery page
    if 'from_discovery' in st.session_state:
        discovery_info = st.session_state.from_discovery
        st.info(f"📊 Analyzing **{discovery_info['ticker']}** from Discovery: {discovery_info['company_name']} (Score: {discovery_info['discovery_score']:.0f})")
        st.markdown("---")

    # Initialize IB
    ib_connection = init_ib_connection()

    # Sidebar
    st.sidebar.header("⚙️ Configuration")

    # IB status
    if ib_connection['connected']:
        st.sidebar.success("🟢 IB Connected")
    else:
        st.sidebar.warning("🟡 Using yfinance only")

    # IB connection controls (for flow scanner)
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

    # Ticker input - pre-populate from Discovery if available
    default_ticker = st.session_state.get('selected_ticker', 'KO')

    ticker = st.sidebar.text_input("Ticker Symbol", default_ticker).upper()

    if ticker != default_ticker:
        # User changed ticker manually, clear discovery context
        if 'from_discovery' in st.session_state:
            del st.session_state.from_discovery
        if 'selected_ticker' in st.session_state:
            del st.session_state.selected_ticker

    max_expirations = st.sidebar.slider("Max Expirations to Load", 3, 12, 6)

    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    # Main content
    st.header(f"Analyzing: {ticker}")

    # Get stock price
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get("currentPrice", info.get("regularMarketPrice"))
        st.metric("Current Price", f"${current_price:.2f}")
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return

    # Load options chain
    with st.spinner("Loading options chain..."):
        chain_data = get_full_options_chain(ticker, max_expirations)

    if not chain_data:
        st.error("Could not load options chain")
        return

    puts_df = chain_data['puts']
    calls_df = chain_data['calls']
    expirations = chain_data['expirations']

    st.success(f"Loaded {len(expirations)} expirations with {len(puts_df)} puts and {len(calls_df)} calls")

    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 OI Heatmaps",
        "📊 Volume vs OI",
        "🎯 Max Pain",
        "⚖️ Put/Call Ratios",
        "📉 IV Skew",
        "🔥 Unusual Activity",
        "⚡ Real-Time Flow"
    ])

    # Tab 1: OI Heatmaps
    with tab1:
        st.subheader("Open Interest Heatmaps")
        st.markdown("""
        **How to use**:
        - Brighter colors = higher open interest (more liquidity)
        - For wheel strategy: Target bright zones 2-5% below current price
        - Red line = current stock price
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Puts (Wheel Strategy Focus)")
            fig_puts = create_oi_heatmap(puts_df, 'puts', ticker, current_price)
            st.plotly_chart(fig_puts, use_container_width=True)

        with col2:
            st.markdown("### Calls")
            fig_calls = create_oi_heatmap(calls_df, 'calls', ticker, current_price)
            st.plotly_chart(fig_calls, use_container_width=True)

    # Tab 2: Volume vs OI
    with tab2:
        st.subheader("Volume vs Open Interest Comparison")
        st.markdown("""
        **Interpretation**:
        - High OI + Low Volume = Existing positions (stable)
        - High Volume + Low OI = New activity (opportunity or risk)
        - High both = Very active strike (excellent liquidity)
        """)

        selected_exp = st.selectbox("Select Expiration", expirations, key='vol_oi_exp')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Puts")
            fig_put_vol_oi = create_oi_volume_comparison(puts_df, selected_exp, 'puts')
            st.plotly_chart(fig_put_vol_oi, use_container_width=True)

            # Strike distribution
            fig_put_dist = create_strike_distribution(puts_df, selected_exp, current_price)
            st.plotly_chart(fig_put_dist, use_container_width=True)

        with col2:
            st.markdown("### Calls")
            fig_call_vol_oi = create_oi_volume_comparison(calls_df, selected_exp, 'calls')
            st.plotly_chart(fig_call_vol_oi, use_container_width=True)

            # Strike distribution
            fig_call_dist = create_strike_distribution(calls_df, selected_exp, current_price)
            st.plotly_chart(fig_call_dist, use_container_width=True)

    # Tab 3: Max Pain
    with tab3:
        st.subheader("🎯 Max Pain Analysis")
        st.markdown("""
        **Theory**: Market makers have incentive to push stock price toward "max pain" strike
        where most options expire worthless (minimizes their payout).

        **For Wheel Strategy**:
        - If selling puts BELOW max pain → safer (less likely to be assigned)
        - If selling puts ABOVE max pain → riskier (price may be pulled down)
        - Max pain acts as a "price magnet" into expiration
        """)

        selected_exp_mp = st.selectbox("Select Expiration", expirations, key='max_pain_exp')

        max_pain_result = calculate_max_pain(puts_df, calls_df, selected_exp_mp, current_price)

        if max_pain_result:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Max Pain Strike", f"${max_pain_result['strike']:.2f}")

            with col2:
                distance = max_pain_result['distance_from_current']
                st.metric("Distance from Current", f"{distance:+.1f}%")

            with col3:
                st.metric("Total Pain", f"${max_pain_result['total_pain']:,.0f}")

            with col4:
                direction = "⬇️ Bearish" if distance < 0 else "⬆️ Bullish" if distance > 0 else "➡️ Neutral"
                st.metric("Bias", direction)

            # Max pain chart
            fig_max_pain = create_max_pain_chart(max_pain_result, current_price)
            st.plotly_chart(fig_max_pain, use_container_width=True)

            # Interpretation
            if abs(distance) < 2:
                st.success(f"✅ Stock near max pain - price may stay range-bound around ${max_pain_result['strike']:.2f}")
            elif distance < -5:
                st.warning(f"⚠️ Max pain significantly below current price - possible downward pressure")
            elif distance > 5:
                st.info(f"📈 Max pain significantly above current price - possible upward pull")

        else:
            st.warning("Could not calculate max pain for this expiration")

    # Tab 4: Put/Call Ratios
    with tab4:
        st.subheader("⚖️ Put/Call Ratio by Strike")
        st.markdown("""
        **Interpretation**:
        - Ratio > 1.0 (Red): More puts than calls (bearish/hedging)
        - Ratio < 1.0 (Green): More calls than puts (bullish)
        - Very high ratio at strike: Potential support level (institutions protecting)

        **For Wheel**: Look for strikes with high put OI ratio as potential support zones
        """)

        selected_exp_pc = st.selectbox("Select Expiration", expirations, key='pc_ratio_exp')

        fig_pc_ratio = create_put_call_ratio_chart(puts_df, calls_df, selected_exp_pc)
        st.plotly_chart(fig_pc_ratio, use_container_width=True)

        # Show strikes with highest put concentration
        puts_exp = puts_df[puts_df['expiration'] == selected_exp_pc].copy()
        puts_exp = puts_exp.nlargest(10, 'openInterest')[['strike', 'openInterest', 'volume']]
        puts_exp.columns = ['Strike', 'Open Interest', 'Volume']

        st.markdown("### Top 10 Strikes by Put OI")
        st.markdown("*These strikes may act as support levels (institutional hedging)*")
        st.dataframe(puts_exp, use_container_width=True)

    # Tab 5: IV Skew
    with tab5:
        st.subheader("📉 IV Skew Analysis")
        st.markdown("""
        **What is IV Skew?**
        - Variation in implied volatility across different strike prices
        - Shows which strikes have expensive or cheap options
        - Useful for finding best premium opportunities

        **For Wheel Strategy**:
        - **Steep skew** (OTM puts more expensive than ATM): Excellent for selling puts
        - **Flat skew**: Normal market, standard pricing
        - **Reverse skew** (OTM puts cheaper): Avoid - low premium
        """)

        selected_exp_skew = st.selectbox("Select Expiration", expirations, key='skew_exp')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Put IV Skew")
            fig_put_skew = create_iv_skew_chart(puts_df, selected_exp_skew, 'puts', current_price)

            if fig_put_skew:
                st.plotly_chart(fig_put_skew, use_container_width=True)

                # Analyze skew
                skew_analysis = analyze_iv_skew(puts_df, selected_exp_skew, current_price)

                if skew_analysis:
                    st.markdown("#### Skew Analysis")

                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.metric("ATM Strike", f"${skew_analysis['atm_strike']:.2f}")
                        st.metric("ATM IV", f"{skew_analysis['atm_iv']:.1f}%")

                    with col_b:
                        st.metric("5% OTM Strike", f"${skew_analysis['otm_5pct_strike']:.2f}")
                        st.metric("5% OTM IV", f"{skew_analysis['otm_5pct_iv']:.1f}%")

                    skew_premium = skew_analysis['skew_premium']

                    if skew_premium > 2:
                        st.success(f"✅ {skew_analysis['interpretation']} (Skew: +{skew_premium:.1f}%)")
                    elif abs(skew_premium) <= 2:
                        st.info(f"➡️ {skew_analysis['interpretation']} (Skew: {skew_premium:+.1f}%)")
                    else:
                        st.warning(f"⚠️ {skew_analysis['interpretation']} (Skew: {skew_premium:+.1f}%)")

            else:
                st.warning("No IV data available for this expiration")

        with col2:
            st.markdown("### Call IV Skew")
            fig_call_skew = create_iv_skew_chart(calls_df, selected_exp_skew, 'calls', current_price)

            if fig_call_skew:
                st.plotly_chart(fig_call_skew, use_container_width=True)
            else:
                st.warning("No IV data available for this expiration")

        # Show strikes ranked by IV (find most expensive puts)
        st.markdown("### Strikes Ranked by IV (Most Expensive Puts)")
        st.markdown("*Target these strikes for best premium when selling puts*")

        puts_skew_ranked = puts_df[puts_df['expiration'] == selected_exp_skew].copy()
        puts_skew_ranked = puts_skew_ranked[puts_skew_ranked['impliedVolatility'] > 0]

        if not puts_skew_ranked.empty:
            puts_skew_ranked['iv_pct'] = puts_skew_ranked['impliedVolatility'] * 100
            puts_skew_ranked['moneyness'] = ((puts_skew_ranked['strike'] / current_price - 1) * 100)

            puts_skew_ranked = puts_skew_ranked.nlargest(10, 'iv_pct')[
                ['strike', 'iv_pct', 'moneyness', 'openInterest', 'volume']
            ]

            puts_skew_ranked.columns = ['Strike', 'IV %', 'Moneyness %', 'OI', 'Volume']

            st.dataframe(
                puts_skew_ranked.style.format({
                    'Strike': '${:.2f}',
                    'IV %': '{:.1f}%',
                    'Moneyness %': '{:+.1f}%',
                    'OI': '{:,.0f}',
                    'Volume': '{:,.0f}'
                }),
                use_container_width=True
            )

            # Trading insight
            top_strike = puts_skew_ranked.iloc[0]
            if top_strike['Moneyness %'] >= -10 and top_strike['Moneyness %'] <= 0:
                st.info(f"""
                💡 **Trading Insight**: Strike ${top_strike['Strike']:.2f} has highest IV ({top_strike['IV %']:.1f}%)
                and is {abs(top_strike['Moneyness %']):.1f}% OTM - potentially excellent for wheel strategy
                """)
        else:
            st.warning("No IV data available for ranking")

    # Tab 6: Unusual Activity
    with tab6:
        st.subheader("🔥 Unusual Options Activity Detector")

        st.info("""
        **What to look for:**
        - **Volume/OI > 2.0**: Fresh positioning (not existing contracts trading hands)
        - **Large Premium Flow**: Institutional-size bets (> $500k)
        - **Heavy Put Buying**: 🚨 RED FLAG for selling puts
        - **Heavy Call Buying**: Potential IV expansion → better covered call premiums later

        **How this helps your wheel strategy:**
        - Avoid selling puts when institutions are aggressively buying puts
        - Identify stocks where IV is about to expand
        - Detect hidden catalysts before they become public
        """)

        # Configuration
        col1, col2 = st.columns(2)

        with col1:
            vol_oi_threshold = st.slider(
                "Volume/OI Threshold",
                min_value=1.0,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="Higher = stricter (only very unusual activity)"
            )

        with col2:
            premium_threshold = st.slider(
                "Premium Flow Threshold ($)",
                min_value=100000,
                max_value=2000000,
                value=500000,
                step=100000,
                help="Minimum dollar volume to flag"
            )

        if st.button("🔍 Scan for Unusual Activity", type="primary"):
            with st.spinner("Analyzing options flow..."):
                # Detect unusual activity
                activity_data = detect_unusual_activity(
                    puts_df,
                    calls_df,
                    vol_oi_threshold=vol_oi_threshold,
                    premium_threshold=premium_threshold
                )

                # Generate wheel strategy signals
                signals = generate_wheel_signals(activity_data, ticker)

                # Display signals
                st.markdown("---")
                st.subheader("📊 Trading Signals")

                for signal in signals:
                    if signal['type'] == 'WARNING':
                        st.error(f"""
                        **{signal['title']}**

                        {signal['message']}

                        **Recommendation**: {signal['recommendation']}

                        *{signal['details']}*
                        """)
                    elif signal['type'] == 'SUCCESS':
                        st.success(f"""
                        **{signal['title']}**

                        {signal['message']}

                        **Recommendation**: {signal['recommendation']}

                        *{signal['details']}*
                        """)
                    else:  # INFO
                        st.info(f"""
                        **{signal['title']}**

                        {signal['message']}

                        **Recommendation**: {signal['recommendation']}

                        *{signal['details']}*
                        """)

                # Display stats
                st.markdown("---")
                st.subheader("📈 Flow Statistics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Total Put Flow",
                        f"${activity_data['stats']['total_put_flow']:,.0f}",
                        delta=f"{activity_data['stats']['total_put_volume']:,.0f} contracts"
                    )

                with col2:
                    st.metric(
                        "Total Call Flow",
                        f"${activity_data['stats']['total_call_flow']:,.0f}",
                        delta=f"{activity_data['stats']['total_call_volume']:,.0f} contracts"
                    )

                with col3:
                    ratio = activity_data['stats']['put_call_flow_ratio']
                    st.metric(
                        "Put/Call Flow Ratio",
                        f"{ratio:.2f}",
                        delta="Bearish" if ratio > 1.5 else "Bullish" if ratio < 0.67 else "Neutral"
                    )

                with col4:
                    total_unusual = len(activity_data['unusual_puts']) + len(activity_data['unusual_calls'])
                    st.metric(
                        "Unusual Strikes",
                        f"{total_unusual}",
                        delta=f"{len(activity_data['unusual_puts'])} puts, {len(activity_data['unusual_calls'])} calls"
                    )

                # Display top unusual strikes
                st.markdown("---")
                st.subheader("🎯 Top Unusual Strikes by Premium Flow")

                top_strikes = get_top_unusual_strikes(activity_data, top_n=10)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 🔻 Top Unusual Puts")
                    if len(top_strikes['top_puts']) > 0:
                        display_df = top_strikes['top_puts'].copy()
                        display_df['premium_flow'] = display_df['premium_flow'].apply(lambda x: f"${x:,.0f}")
                        display_df['vol_to_oi'] = display_df['vol_to_oi'].apply(lambda x: f"{x:.1f}x")
                        display_df['impliedVolatility'] = display_df['impliedVolatility'].apply(lambda x: f"{x*100:.1f}%")

                        st.dataframe(
                            display_df.rename(columns={
                                'strike': 'Strike',
                                'expiration': 'Exp',
                                'lastPrice': 'Price',
                                'volume': 'Vol',
                                'openInterest': 'OI',
                                'vol_to_oi': 'Vol/OI',
                                'premium_flow': 'Flow',
                                'impliedVolatility': 'IV'
                            }),
                            use_container_width=True
                        )
                    else:
                        st.success("✅ No unusual put activity detected")

                with col2:
                    st.markdown("### 🔺 Top Unusual Calls")
                    if len(top_strikes['top_calls']) > 0:
                        display_df = top_strikes['top_calls'].copy()
                        display_df['premium_flow'] = display_df['premium_flow'].apply(lambda x: f"${x:,.0f}")
                        display_df['vol_to_oi'] = display_df['vol_to_oi'].apply(lambda x: f"{x:.1f}x")
                        display_df['impliedVolatility'] = display_df['impliedVolatility'].apply(lambda x: f"{x*100:.1f}%")

                        st.dataframe(
                            display_df.rename(columns={
                                'strike': 'Strike',
                                'expiration': 'Exp',
                                'lastPrice': 'Price',
                                'volume': 'Vol',
                                'openInterest': 'OI',
                                'vol_to_oi': 'Vol/OI',
                                'premium_flow': 'Flow',
                                'impliedVolatility': 'IV'
                            }),
                            use_container_width=True
                        )
                    else:
                        st.info("📊 No unusual call activity detected")

                # Display PCR by expiration
                st.markdown("---")
                st.subheader("📊 Put/Call Ratio by Expiration")

                pcr_display = activity_data['pcr_by_expiration'].copy()
                pcr_display = pcr_display.reset_index()

                st.dataframe(
                    pcr_display.style.format({
                        'put_oi': '{:,.0f}',
                        'call_oi': '{:,.0f}',
                        'PCR_OI': '{:.2f}'
                    }).background_gradient(subset=['PCR_OI'], cmap='RdYlGn_r'),
                    use_container_width=True
                )

                st.caption("""
                **PCR Interpretation:**
                - PCR > 1.5 = Bearish (more puts than calls)
                - PCR 0.7-1.5 = Neutral
                - PCR < 0.7 = Bullish (more calls than puts)
                """)

    # Tab 7: Real-Time Flow (IB Integration)
    with tab7:
        st.subheader("⚡ Real-Time Options Flow Scanner")
        st.markdown("""
        **Institutional-Grade Flow Detection using Interactive Brokers**

        This tab provides real-time analysis of options flow using IB tick-by-tick data:
        - **Block Trades**: Single trades >100 contracts (institutional positioning)
        - **Sweeps**: Multi-exchange aggressive buying (urgent conviction)
        - **Aggressive Buyers**: >65% volume at ask (strong directional bias)
        - **Historical Tracking**: Database of flow patterns and divergence
        - **Background Monitoring**: Continuous scanning during market hours

        **🔴 CRITICAL ALERTS**: Protect your wheel strategy from institutional put buying
        """)

        # Render the complete flow analysis tab
        render_flow_analysis_tab(ticker)

        st.markdown("---")

        # Quick scan button
        st.subheader("🚀 Quick Scan")
        st.markdown("Scan this ticker for unusual flow right now (requires IB connection)")
        render_live_scan_button(ticker)

        st.markdown("---")

        # Documentation
        with st.expander("📖 How to Use Real-Time Flow Scanner"):
            st.markdown("""
            ### Getting Started

            1. **Connect to Interactive Brokers**
               - Ensure IB Gateway or TWS is running
               - Configure connection in Settings (default: localhost:4001)
               - Verify market data subscription is active

            2. **Quick Scan**
               - Click "Scan Flow Now" for immediate analysis
               - Results show blocks, sweeps, and aggressive buying
               - Alerts indicate safety for wheel strategy

            3. **Background Monitor**
               - Configure watchlist (comma-separated tickers)
               - Set scan interval (5 minutes recommended)
               - Click "Start Monitor" to enable continuous scanning
               - Desktop notifications for critical alerts

            4. **Historical Analysis**
               - View flow history charts (premium flow, P/C ratio)
               - Detect divergence (today vs 7-day average)
               - Review recent events and top flow tickers

            ### Alert Levels

            - **🔴 CRITICAL**: DO NOT sell puts immediately
              - Put sweeps across exchanges
              - Institutions aggressively hedging downside

            - **🟠 HIGH**: Avoid selling puts
              - Institutional put blocks >$500k
              - Extreme bearish flow (P/C ratio > 3.0)

            - **🟡 MEDIUM**: Monitor closely
              - Heavy call flow (>$1M)
              - Potential IV expansion

            - **🟢 LOW**: Safe to proceed
              - No unusual activity
              - Normal flow patterns

            ### Best Practices

            1. **Scan before opening positions** (1-2 hours before market close)
            2. **Run background monitor during market hours** (9:30-16:00 EST)
            3. **Review historical patterns** to build pattern recognition
            4. **Combine with other signals** (IV Rank, Earnings, Max Pain)

            ### Database

            All flow data is automatically saved to `data/flow_history.db`:
            - Individual flow events (blocks, sweeps, aggressive buys)
            - Daily summaries by ticker
            - Alert history
            - Flow divergence calculations

            ### Command-Line Tools

            Advanced users can use standalone scripts:

            ```bash
            # Scan single ticker
            python test_flow_scanner.py --ticker AAPL

            # View historical flow
            python test_flow_scanner.py --history AAPL --days 30

            # Background monitor (CLI)
            python test_flow_scanner.py --monitor --watchlist KO,JNJ,PG
            ```

            See `docs/FLOW_SCANNER.md` for complete documentation.
            """)


if __name__ == "__main__":
    main()
