#!/usr/bin/env python3
"""
Wheel Strategy Dashboard - Workflow Home
Guides users through: DISCOVER → ANALYZE → EXECUTE → MONITOR
"""

import streamlit as st
from datetime import datetime, time
import pytz
from components.workflow_progress import (
    render_workflow_progress,
    render_workflow_stats,
    get_session_summary
)
from components.disclaimers import render_compact_disclaimer

# Page configuration
st.set_page_config(
    page_title="Wheel Strategy Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and introduction
st.title("🎯 Wheel Strategy Dashboard")
st.markdown("### Institutional-grade options signal generator")

# Market status widget
NYSE_TZ = pytz.timezone('America/New_York')
now_et = datetime.now(NYSE_TZ)
current_time = now_et.time()
is_market_hours = time(9, 30) <= current_time <= time(16, 0)
is_weekday = now_et.weekday() < 5

market_open = is_market_hours and is_weekday

col1, col2, col3 = st.columns(3)

with col1:
    if market_open:
        st.success("🟢 **Market OPEN**")
    else:
        st.info("🔴 **Market CLOSED**")

with col2:
    st.metric("Current Time (ET)", now_et.strftime("%I:%M %p"))

with col3:
    if not market_open:
        if current_time < time(9, 30):
            next_open = now_et.replace(hour=9, minute=30, second=0)
            time_until = next_open - now_et
            hours, remainder = divmod(time_until.seconds, 3600)
            minutes = remainder // 60
            st.metric("Opens In", f"{hours}h {minutes}m")
        elif current_time > time(16, 0):
            st.metric("Next Open", "Tomorrow 9:30 AM")
    else:
        market_close = now_et.replace(hour=16, minute=0, second=0)
        time_remaining = market_close - now_et
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes = remainder // 60
        st.metric("Closes In", f"{hours}h {minutes}m")

st.markdown("---")

# Disclaimers (compact, collapsible)
render_compact_disclaimer()

st.markdown("---")

# Workflow overview section
st.markdown("## 🚀 Wheel Strategy Workflow")

st.markdown("""
This dashboard guides you through a systematic 4-phase process for finding and executing
high-probability wheel strategy opportunities:

**📍 Phase 1: DISCOVER** - Scan the market for unusual activity and hidden gems
**📍 Phase 2: ANALYZE** - Deep dive into fundamentals, technicals, and insider sentiment
**📍 Phase 3: EXECUTE** - Configure optimal strikes and position sizing
**📍 Phase 4: MONITOR** - Track positions and manage roll decisions
""")

# Workflow stats
st.markdown("### 📊 Current Session Status")
render_workflow_stats()

st.markdown("---")

# Quick start guide
st.markdown("## 🎯 Getting Started")

tab1, tab2, tab3 = st.tabs(["New to Wheel Strategy", "Start Workflow", "Advanced"])

with tab1:
    st.markdown("""
    ### What is the Wheel Strategy?

    The wheel is a mechanical options income strategy with three steps:

    1. **Sell Cash-Secured Puts** - Get paid to wait for stocks you want to own
    2. **Get Assigned (if exercised)** - Buy the stock at a discount
    3. **Sell Covered Calls** - Generate income while holding the stock

    ### Why This Dashboard?

    Finding the right wheel candidates requires screening for:
    - ✅ High IV/HV ratios (elevated premium opportunities)
    - ✅ Strong fundamentals (quality companies you want to own)
    - ✅ Insider conviction (insiders buying, not selling)
    - ✅ News catalysts (recent events driving volatility)
    - ✅ Sufficient liquidity (tight bid/ask spreads)

    This dashboard automates the entire discovery → analysis → execution pipeline.

    ### Typical Returns
    - **Target:** 1-3% monthly premium (12-36% annualized)
    - **Risk:** Stock ownership at predetermined price
    - **Time Commitment:** 30 minutes weekly for scanning + monitoring
    """)

with tab2:
    st.markdown("""
    ### 🚀 Launch Workflow

    Follow these steps to find your first wheel opportunity:
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        #### Phase 1: Discover Opportunities

        Start by scanning the market for high-probability candidates:

        1. Navigate to **🔍 Discover** page (sidebar)
        2. Select scan universe (S&P 500, Russell 2000, or Custom)
        3. Adjust filters (min discovery score, quality threshold)
        4. Run scan and review top 10 gems
        5. Add 3-5 candidates to your shortlist

        **Time:** 10-15 minutes
        **Output:** Shortlist of 3-5 tickers to analyze
        """)

    with col2:
        if st.button("🔍 Start Discovery →", use_container_width=True, type="primary"):
            st.switch_page("pages/01_🔍_Discover.py")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        #### Phase 2: Analyze Candidates

        Deep dive into your shortlisted stocks:

        1. Review fundamental quality (ROE, margins, debt)
        2. Check insider trading sentiment (buying vs selling)
        3. Validate technical setup (support levels, volatility)
        4. Assess risk metrics (beta, correlation)
        5. Assign conviction scores (High/Medium/Low)

        **Time:** 15-20 minutes
        **Output:** 2-3 high-conviction candidates
        """)

    with col2:
        summary = get_session_summary()
        enabled = summary['shortlist_count'] > 0

        if enabled:
            if st.button(
                f"📊 Analyze ({summary['shortlist_count']}) →",
                use_container_width=True,
                type="primary"
            ):
                st.switch_page("pages/02_📊_Analyze.py")
        else:
            st.button(
                "📊 Analyze →",
                use_container_width=True,
                disabled=True,
                help="Complete Discovery first"
            )

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        #### Phase 3: Execute Trades

        Configure and place your wheel positions:

        1. Select optimal strike (2-5% OTM)
        2. Calculate position size based on risk tolerance
        3. Verify liquidity (bid/ask spread < 5%)
        4. Review execution checklist
        5. Place orders via your broker

        **Time:** 10 minutes
        **Output:** Active wheel positions
        """)

    with col2:
        enabled = summary['analyzed_count'] > 0

        if enabled:
            if st.button(
                f"🎯 Execute ({summary['analyzed_count']}) →",
                use_container_width=True,
                type="primary"
            ):
                st.switch_page("pages/03_🎯_Execute.py")
        else:
            st.button(
                "🎯 Execute →",
                use_container_width=True,
                disabled=True,
                help="Complete Analysis first"
            )

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        #### Phase 4: Monitor Positions

        Track and manage your active wheel positions:

        1. Daily P&L and Greeks monitoring
        2. Assignment risk assessment
        3. Roll vs close decisions
        4. Performance attribution
        5. Repeat workflow for new opportunities

        **Time:** 5 minutes daily
        **Output:** Optimized portfolio returns
        """)

    with col2:
        enabled = summary['active_positions'] > 0

        if enabled:
            if st.button(
                f"📈 Monitor ({summary['active_positions']}) →",
                use_container_width=True,
                type="primary"
            ):
                st.switch_page("pages/04_📈_Monitor.py")
        else:
            st.button(
                "📈 Monitor →",
                use_container_width=True,
                disabled=True,
                help="Execute trades first"
            )

with tab3:
    st.markdown("""
    ### 🛠️ Advanced Features

    #### Custom Universes
    Upload your own watchlist of tickers to scan instead of using predefined universes.

    #### Risk Parameters
    Configure position sizing rules:
    - Max allocation per position (default: 5%)
    - Max total wheel exposure (default: 25%)
    - Max beta-weighted delta (default: 0.3)

    #### Alert Configuration
    Set up notifications for:
    - Discovery score thresholds
    - Insider buying activity
    - IV rank spikes
    - Assignment risk alerts

    #### Interactive Brokers Integration
    Connect your IB account for:
    - Real-time positions sync
    - One-click order execution
    - Live P&L tracking
    - Greeks monitoring

    #### Export & Reporting
    - Export scan results to CSV
    - Generate weekly performance reports
    - Track historical trades
    - Tax loss harvesting opportunities
    """)

st.markdown("---")

# Footer with key metrics and last update
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p><strong>Wheel Strategy Dashboard v1.1</strong></p>
    <p>Last Updated: 2025-10-26 | Data Source: yfinance | Update Frequency: 5-minute cache</p>
    <p>⚠️ For educational purposes only. Not financial advice. Options involve risk.</p>
</div>
""", unsafe_allow_html=True)
