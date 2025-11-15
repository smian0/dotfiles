"""
Market Discovery Page - Find Hidden Gems Automatically

Scans the entire market for unusual options activity and under-the-radar opportunities.
"""

import streamlit as st
from components.discovery_dashboard import render_discovery_dashboard
from components.ib_connection import render_ib_connection_sidebar
from components.flow_dashboard import render_flow_alerts_sidebar
from components.workflow_progress import (
    render_workflow_progress,
    render_next_step_button
)
from components.disclaimers import render_data_source_disclaimer

# Page config
st.set_page_config(
    page_title="Market Discovery - Wheel Dashboard",
    page_icon="💎",
    layout="wide"
)

# Workflow progress tracker
render_workflow_progress(current_phase='discover')

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    st.markdown("🟡 Using yfinance only")

    # IB Connection (optional - enhances discovery with real-time data)
    render_ib_connection_sidebar()

    # Flow alerts
    render_flow_alerts_sidebar()

# Main content
st.title("💎 Market-Wide Discovery Scanner")
st.markdown("**Find hidden gem opportunities automatically**")

# Data source disclaimer
render_data_source_disclaimer('data_only')

st.markdown("---")

# Info banner
st.info("""
**🎯 What This Scanner Does:**

Unlike traditional screeners that require you to know what to look for, this scanner **automatically discovers**
unusual activity across the entire market that you might have missed.

**Key Features:**
- 📈 Scans S&P 500, NASDAQ 100, or custom universes (500-2000 stocks)
- ⚡ Detects unusual options volume, IV surges, and institutional flow
- 💎 Surfaces under-the-radar opportunities (small caps, low analyst coverage)
- 🎯 Ranks by composite "discovery score" (0-100)
- 🔍 Detailed analysis of why each stock is a "hidden gem"

**Perfect for:**
- Finding new wheel strategy candidates
- Discovering stocks before they trend
- Identifying institutional positioning early
- Spotting sector rotation opportunities
""")

# Render the discovery dashboard
render_discovery_dashboard()

# Usage tips
with st.expander("💡 How to Use This Scanner"):
    st.markdown("""
    ### Getting Started

    1. **Choose Universe**: Start with S&P 500 for liquid, well-known stocks, or NASDAQ 100 for tech-focused opportunities
    2. **Set Discovery Score**: Higher scores (70+) = stronger signals. Lower scores (50-60) = more results but weaker signals
    3. **Click "Scan Market Now"**: The scanner will analyze hundreds of stocks in parallel
    4. **Review Results**: Examine the "Discovery Reasons" to understand why each stock was flagged
    5. **Deep Dive**: Select a ticker for detailed analysis of all signals and metrics

    ### Understanding Discovery Signals

    - **Unusual Volume**: Options volume significantly higher than normal (>2x average = strong signal)
    - **IV Surge**: Implied volatility percentile >70% (market expecting large move)
    - **OI Surge**: Large open interest indicates institutional positioning
    - **P/C Ratio Extreme**: Extremely bullish (<0.3) or bearish (>3.0) sentiment

    ### Best Practices

    - **Run daily scans**: Market conditions change - new opportunities emerge daily
    - **Cross-reference**: Use MarketChameleon or other tools to validate signals
    - **Focus on multiple signals**: Stocks with 3+ signals are higher conviction
    - **Small caps**: Enable "Prefer Small/Mid Caps" for true hidden gems
    - **Analyst coverage**: Enable "Prefer Low Coverage" for under-the-radar stocks

    ### Integration with Wheel Strategy

    1. Run discovery scanner to find new candidates
    2. Add promising tickers to your watchlist
    3. Navigate to main Wheel Dashboard for detailed wheel opportunity analysis
    4. Use Advanced Analytics → Real-Time Flow to monitor institutional activity

    ### Performance Notes

    - **Scan time**: Approximately 1-3 minutes for S&P 500 (500 stocks)
    - **IB Connection**: Optional but recommended for real-time tick data (block trades, sweeps)
    - **Market hours**: Scanner works 24/7, but best results during market hours
    - **Caching**: Results are cached for 15 minutes to avoid redundant API calls
    """)

# Technical notes
with st.expander("🔧 Technical Details"):
    st.markdown("""
    ### Data Sources

    - **yfinance**: Stock fundamentals, options chains, volume data
    - **Interactive Brokers** (optional): Real-time tick data for block trades and sweeps

    ### Scoring Algorithm

    The composite discovery score (0-100) is calculated from:

    1. **Signal Scores** (70% weight)
       - Each signal contributes 0-100 points based on severity
       - Average of all signals forms base score

    2. **Market Cap Bonus** (15% weight)
       - Small cap (<$2B): +15 points
       - Mid cap ($2B-$10B): +10 points
       - Large cap ($10B-$50B): +5 points
       - Mega cap (>$50B): +0 points

    3. **Analyst Coverage Bonus** (15% weight)
       - <5 analysts: +15 points (very hidden)
       - 5-10 analysts: +10 points (somewhat hidden)
       - 10-20 analysts: +5 points (moderately followed)
       - >20 analysts: +0 points (well covered)

    ### Detection Thresholds

    - **Unusual Volume**: Vol/OI ratio > 0.5
    - **IV Surge**: IV > 50%
    - **OI Surge**: Total OI > 10,000 contracts
    - **P/C Extreme**: Ratio < 0.3 or > 3.0

    ### Scan Optimization

    - Parallel processing with ThreadPoolExecutor (10 workers)
    - Two-phase filtering: Quick filter → Deep scan
    - Caching with 15-minute TTL
    - Fail-fast on broken data
    """)
