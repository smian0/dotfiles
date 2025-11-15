"""
Flow Dashboard Component

Real-time options flow analysis with:
- Live flow alerts
- Historical flow charts
- Background monitor controls
- Flow statistics
"""

import asyncio
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only FlowDatabase (no IB dependencies)
from analyzers.flow_database import FlowDatabase

# Lazy imports for IB-dependent modules (imported only when needed)
def _ensure_event_loop():
    """Ensure event loop exists for ib_insync"""
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

def _get_background_monitor():
    _ensure_event_loop()
    from analyzers.background_scanner import BackgroundFlowMonitor
    return BackgroundFlowMonitor

def _get_flow_scanner():
    _ensure_event_loop()
    from analyzers.flow_scanner import FlowScanner
    return FlowScanner

def _get_alert_callback():
    _ensure_event_loop()
    from analyzers.alert_system import create_alert_callback
    return create_alert_callback


def render_flow_alerts_sidebar():
    """
    Render flow alerts in sidebar

    Shows critical/high alerts from last 24 hours
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Flow Alerts")

    db = FlowDatabase()

    # Get recent critical/high alerts
    alerts = db.get_recent_alerts(hours_back=24, min_severity='HIGH')

    if alerts.empty:
        st.sidebar.success("✅ No critical alerts")
    else:
        # Show count
        critical_count = len(alerts[alerts['severity'] == 'CRITICAL'])
        high_count = len(alerts[alerts['severity'] == 'HIGH'])

        if critical_count > 0:
            st.sidebar.error(f"🔴 {critical_count} CRITICAL alerts")
        if high_count > 0:
            st.sidebar.warning(f"🟠 {high_count} HIGH alerts")

        # Show latest 3 alerts
        for _, alert in alerts.head(3).iterrows():
            severity_emoji = {
                'CRITICAL': '🔴',
                'HIGH': '🟠'
            }.get(alert['severity'], '⚪')

            with st.sidebar.expander(f"{severity_emoji} {alert['ticker']} - {alert['timestamp'].strftime('%H:%M')}"):
                st.markdown(f"**{alert['title']}**")
                st.markdown(alert['message'])
                st.info(alert['recommendation'])

    db.close()


def render_flow_stats_widget(ticker: str):
    """
    Render flow statistics widget for a ticker

    Args:
        ticker: Stock ticker symbol
    """
    db = FlowDatabase()

    # Get today's summary
    today = datetime.now().date()
    summary = db.get_daily_summary(ticker, days_back=1)

    if summary.empty:
        st.info(f"No flow data available for {ticker} today")
        db.close()
        return

    latest = summary.iloc[0]

    # Display stats in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Premium Flow",
            f"${latest['total_premium_flow']:,.0f}",
            help="Total options premium traded today"
        )

    with col2:
        st.metric(
            "Put/Call Ratio",
            f"{latest['put_call_ratio']:.2f}",
            help="Put premium flow / Call premium flow"
        )

    with col3:
        st.metric(
            "Block Trades",
            int(latest['block_count']),
            help="Trades >100 contracts (institutional size)"
        )

    with col4:
        st.metric(
            "Sweeps",
            int(latest['sweep_count']),
            help="Multi-exchange aggressive buying"
        )

    # Check for divergence
    divergence = db.get_flow_divergence(ticker, days_back=7)

    if divergence['has_divergence']:
        st.warning("⚠️ **Unusual Flow Detected**")

        if divergence.get('put_divergence'):
            st.markdown(f"📉 Put flow: **${divergence['today_put_flow']:,.0f}** (avg: ${divergence['avg_put_flow']:,.0f})")

        if divergence.get('call_divergence'):
            st.markdown(f"📈 Call flow: **${divergence['today_call_flow']:,.0f}** (avg: ${divergence['avg_call_flow']:,.0f})")

    db.close()


def render_flow_history_charts(ticker: str, days_back: int = 30):
    """
    Render flow history charts

    Args:
        ticker: Stock ticker symbol
        days_back: Number of days to show
    """
    db = FlowDatabase()

    # Get daily summary
    summary = db.get_daily_summary(ticker, days_back=days_back)

    if summary.empty:
        st.info(f"No historical flow data for {ticker}")
        db.close()
        return

    # Chart 1: Premium Flow (Stacked Bar)
    fig_flow = go.Figure()

    fig_flow.add_trace(go.Bar(
        x=summary['date'],
        y=summary['put_flow'],
        name='Put Flow',
        marker_color='indianred'
    ))

    fig_flow.add_trace(go.Bar(
        x=summary['date'],
        y=summary['call_flow'],
        name='Call Flow',
        marker_color='lightseagreen'
    ))

    fig_flow.update_layout(
        title=f'{ticker} Premium Flow History',
        xaxis_title='Date',
        yaxis_title='Premium Flow ($)',
        barmode='stack',
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig_flow, use_container_width=True)

    # Chart 2: Put/Call Ratio
    fig_pcr = go.Figure()

    fig_pcr.add_trace(go.Scatter(
        x=summary['date'],
        y=summary['put_call_ratio'],
        mode='lines+markers',
        name='P/C Ratio',
        line=dict(color='steelblue', width=2),
        marker=dict(size=6)
    ))

    # Add reference lines
    fig_pcr.add_hline(y=1.0, line_dash="dash", line_color="gray",
                      annotation_text="Neutral (1.0)")
    fig_pcr.add_hline(y=3.0, line_dash="dash", line_color="red",
                      annotation_text="Extreme Bearish (3.0)")

    fig_pcr.update_layout(
        title=f'{ticker} Put/Call Ratio Trend',
        xaxis_title='Date',
        yaxis_title='Put/Call Ratio',
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig_pcr, use_container_width=True)

    # Chart 3: Event Counts
    fig_events = go.Figure()

    fig_events.add_trace(go.Scatter(
        x=summary['date'],
        y=summary['block_count'],
        mode='lines+markers',
        name='Blocks',
        line=dict(color='orange', width=2)
    ))

    fig_events.add_trace(go.Scatter(
        x=summary['date'],
        y=summary['sweep_count'],
        mode='lines+markers',
        name='Sweeps',
        line=dict(color='red', width=2)
    ))

    fig_events.add_trace(go.Scatter(
        x=summary['date'],
        y=summary['aggressive_buy_count'],
        mode='lines+markers',
        name='Aggressive Buys',
        line=dict(color='purple', width=2)
    ))

    fig_events.update_layout(
        title=f'{ticker} Unusual Activity Events',
        xaxis_title='Date',
        yaxis_title='Event Count',
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig_events, use_container_width=True)

    db.close()


def render_recent_flow_events(ticker: Optional[str] = None, days_back: int = 7):
    """
    Render table of recent flow events

    Args:
        ticker: Optional ticker filter (None = all tickers)
        days_back: Number of days to show
    """
    db = FlowDatabase()

    # Get flow history
    flow = db.get_flow_history(ticker, days_back=days_back) if ticker else db.get_top_flow_tickers(days_back=days_back)

    if flow.empty:
        st.info("No recent flow events")
        db.close()
        return

    # Format for display
    display_df = flow.copy()

    if 'timestamp' in display_df.columns:
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')

    if 'premium_flow' in display_df.columns:
        display_df['premium_flow'] = display_df['premium_flow'].apply(lambda x: f"${x:,.0f}")

    if 'aggressive_ratio' in display_df.columns:
        display_df['aggressive_ratio'] = display_df['aggressive_ratio'].apply(
            lambda x: f"{x:.1%}" if pd.notna(x) else "N/A"
        )

    # Show table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    db.close()


def render_monitor_control_panel():
    """
    Render background monitor control panel

    Allows user to start/stop monitoring and configure watchlist
    """
    st.subheader("🔄 Background Monitor")

    # Check if monitor is running (via session state)
    if 'flow_monitor' not in st.session_state:
        st.session_state.flow_monitor = None

    monitor_running = st.session_state.flow_monitor is not None

    # Status display
    if monitor_running:
        status = st.session_state.flow_monitor.get_status()
        st.success(f"✅ Monitor Running - Watchlist: {', '.join(status['watchlist'])}")
        st.info(f"Scan Interval: {status['scan_interval_minutes']} minutes")

        if st.button("🛑 Stop Monitor"):
            st.session_state.flow_monitor.stop()
            st.session_state.flow_monitor = None
            st.rerun()
    else:
        st.warning("⏸️ Monitor Not Running")

        # Configuration
        col1, col2 = st.columns(2)

        with col1:
            watchlist_input = st.text_input(
                "Watchlist (comma-separated)",
                value="AAPL,MSFT,GOOGL,AMZN",
                help="Enter tickers separated by commas"
            )

        with col2:
            scan_interval = st.number_input(
                "Scan Interval (minutes)",
                min_value=1,
                max_value=60,
                value=5,
                help="How often to scan for flow"
            )

        if st.button("▶️ Start Monitor"):
            # Parse watchlist
            watchlist = [t.strip().upper() for t in watchlist_input.split(',')]

            if not watchlist:
                st.error("Please enter at least one ticker")
            else:
                # Check for IB connection
                if 'ib_manager' not in st.session_state or not st.session_state.ib_manager:
                    st.error("⚠️ IB connection required. Please connect in Settings.")
                else:
                    try:
                        # Lazy import IB-dependent modules
                        create_alert_callback = _get_alert_callback()
                        BackgroundFlowMonitor = _get_background_monitor()

                        # Create alert callback
                        alert_callback = create_alert_callback(enable_sound=False)

                        # Start background monitor
                        monitor = BackgroundFlowMonitor(
                            ib=st.session_state.ib_manager.get_connection(),
                            watchlist=watchlist,
                            scan_interval_minutes=scan_interval,
                            alert_callback=alert_callback
                        )

                        monitor.start()
                        st.session_state.flow_monitor = monitor

                        st.success(f"✅ Monitor started for {', '.join(watchlist)}")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Failed to start monitor: {e}")


def render_flow_analysis_tab(ticker: str):
    """
    Complete Flow Analysis tab for Advanced Analytics

    Args:
        ticker: Stock ticker to analyze
    """
    st.header(f"🔍 Options Flow Analysis - {ticker}")

    # Quick stats at top
    st.subheader("Today's Flow")
    render_flow_stats_widget(ticker)

    st.markdown("---")

    # Control panel
    with st.expander("⚙️ Background Monitor Controls", expanded=False):
        render_monitor_control_panel()

    st.markdown("---")

    # Historical charts
    st.subheader("📊 Flow History")

    days_back = st.slider("Days to Display", min_value=7, max_value=90, value=30)
    render_flow_history_charts(ticker, days_back=days_back)

    st.markdown("---")

    # Recent events table
    st.subheader("📋 Recent Flow Events")

    event_days = st.slider("Event History (days)", min_value=1, max_value=30, value=7)
    render_recent_flow_events(ticker, days_back=event_days)

    st.markdown("---")

    # Top flow tickers
    st.subheader("🔥 Top Flow Tickers (Last 24 Hours)")

    db = FlowDatabase()
    top_tickers = db.get_top_flow_tickers(days_back=1, min_flow=100000)

    if not top_tickers.empty:
        # Format display
        display = top_tickers.copy()
        display['total_premium_flow'] = display['total_premium_flow'].apply(lambda x: f"${x:,.0f}")
        display['put_call_ratio'] = display['put_call_ratio'].apply(lambda x: f"{x:.2f}")

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ticker": "Ticker",
                "total_premium_flow": "Total Flow",
                "put_call_ratio": "P/C Ratio",
                "block_count": "Blocks",
                "sweep_count": "Sweeps"
            }
        )
    else:
        st.info("No significant flow detected in last 24 hours")

    db.close()


def render_live_scan_button(ticker: str):
    """
    Render "Scan Now" button for manual flow scanning

    Args:
        ticker: Stock ticker to scan
    """
    if st.button(f"🔍 Scan {ticker} Flow Now"):
        if 'ib_manager' not in st.session_state or not st.session_state.ib_manager:
            st.error("⚠️ IB connection required. Please connect in Settings.")
            return

        with st.spinner(f"Scanning {ticker} options flow..."):
            try:
                # Lazy import FlowScanner
                FlowScanner = _get_flow_scanner()

                scanner = FlowScanner(st.session_state.ib_manager.get_connection())

                # Scan flow (optimized for speed)
                flow_data = scanner.scan_option_flow(
                    ticker=ticker,
                    max_expirations=2,      # Reduced from 3
                    lookback_trades=100     # Reduced from 1000 - recent trades matter most
                )

                # Display results
                st.success("✅ Scan complete!")

                # Show alerts
                if flow_data['alerts']:
                    for alert in flow_data['alerts']:
                        severity_color = {
                            'CRITICAL': 'error',
                            'HIGH': 'warning',
                            'MEDIUM': 'info',
                            'LOW': 'success'
                        }.get(alert['severity'], 'info')

                        getattr(st, severity_color)(
                            f"**{alert['title']}**\n\n{alert['message']}\n\n→ {alert['recommendation']}"
                        )
                else:
                    st.success("✅ No unusual activity detected")

                # Show stats
                stats = flow_data['flow_stats']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Flow", f"${stats['total_premium_flow']:,.0f}")
                with col2:
                    st.metric("Put Flow", f"${stats['total_put_flow']:,.0f}")
                with col3:
                    st.metric("Call Flow", f"${stats['total_call_flow']:,.0f}")

            except Exception as e:
                st.error(f"Scan failed: {e}")
