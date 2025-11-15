"""
Disclaimer components for institutional-grade transparency

Addresses Priority 1 from institutional audit:
- Data lag warnings (yfinance 15-60 min delay)
- Insider data lag (2-4 business days)
- No guarantee of accuracy
- Not financial advice
"""

import streamlit as st
from typing import Literal


def render_data_source_disclaimer(
    disclaimer_type: Literal['full', 'data_only', 'insider_only'] = 'full'
):
    """
    Render transparent data source disclaimer

    Args:
        disclaimer_type: Type of disclaimer to show
            - 'full': Complete disclaimer with all limitations
            - 'data_only': Only market data lag warnings
            - 'insider_only': Only insider trading data lag
    """

    if disclaimer_type in ['full', 'data_only']:
        st.warning(
            "⚠️ **Market Data Limitations**\n\n"
            "This dashboard uses **yfinance** (unofficial Yahoo Finance API) which has:\n"
            "- **15-60 minute data lag** (not real-time)\n"
            "- **No service level agreement** (data may be incomplete or unavailable)\n"
            "- **No guaranteed accuracy** (scrapes public Yahoo Finance data)\n\n"
            "**For institutional/professional use**, consider:\n"
            "- Bloomberg Terminal (real-time, SLA, $24K/year)\n"
            "- Refinitiv Eikon (real-time, compliance-ready)\n"
            "- Interactive Brokers API (real-time for clients)\n\n"
            "**Current data is suitable for**: Retail traders, swing trading, end-of-day analysis"
        )

    if disclaimer_type in ['full', 'insider_only']:
        st.info(
            "📅 **Insider Trading Data Lag**\n\n"
            "SEC Form 4 filings have a **2-4 business day reporting lag**:\n"
            "- Insiders must file within 2 business days of transaction\n"
            "- Data appears in this dashboard after SEC processing\n"
            "- Sentiment reflects activity from 2-6 days ago\n\n"
            "**Implication**: Insider signals are confirmation indicators, not predictive."
        )


def render_legal_disclaimer():
    """Render standard not-financial-advice disclaimer"""
    st.error(
        "⚖️ **Legal Disclaimer**\n\n"
        "This tool is for **educational and informational purposes only**.\n\n"
        "**NOT FINANCIAL ADVICE**: The information provided does not constitute "
        "investment advice, financial advice, trading advice, or any other sort of advice. "
        "You should not treat any of the dashboard's content as such.\n\n"
        "**DO YOUR OWN RESEARCH**: Always conduct your own research and consult "
        "a licensed financial advisor before making investment decisions.\n\n"
        "**NO LIABILITY**: The creators assume no liability for trading losses "
        "resulting from the use of this tool."
    )


def render_options_risk_disclaimer():
    """Render options-specific risk disclaimer"""
    st.warning(
        "⚠️ **Options Trading Risks**\n\n"
        "Options involve substantial risk and are not suitable for all investors:\n"
        "- **Cash-secured puts**: Risk of assignment and holding underlying stock\n"
        "- **Covered calls**: Caps upside potential, downside risk remains\n"
        "- **Wheel strategy**: Requires significant capital and discipline\n\n"
        "**Risk of total loss**: Options can expire worthless. Only trade with capital "
        "you can afford to lose.\n\n"
        "**Understand the Greeks**: Delta, gamma, theta, vega affect option prices. "
        "Educate yourself before trading."
    )


def render_compact_disclaimer():
    """
    Render minimal disclaimer for pages where full disclaimers would be intrusive

    Use this at the top of data-heavy pages (tables, charts) where full warnings
    would push content below the fold.
    """
    with st.expander("⚠️ Important Disclaimers - Click to Read", expanded=False):
        render_data_source_disclaimer('full')
        st.markdown("---")
        render_legal_disclaimer()
        st.markdown("---")
        render_options_risk_disclaimer()


def render_full_disclaimer_page():
    """
    Render complete disclaimer page (for settings/about page)

    Shows all disclaimers in full detail with no collapsing.
    """
    st.title("⚖️ Disclaimers & Limitations")

    st.markdown("---")
    render_data_source_disclaimer('full')

    st.markdown("---")
    render_legal_disclaimer()

    st.markdown("---")
    render_options_risk_disclaimer()

    st.markdown("---")
    st.markdown("### 🔒 Privacy & Data Usage")
    st.info(
        "This dashboard runs **locally on your machine**:\n"
        "- No data is sent to external servers (except yfinance API calls)\n"
        "- No user tracking or analytics\n"
        "- All analysis happens client-side\n\n"
        "**Your tickers, watchlists, and positions remain private.**"
    )

    st.markdown("---")
    st.markdown("### 📊 Data Source Transparency")
    st.markdown("""
    **Market Data**: yfinance (Yahoo Finance unofficial API)
    - Price data: 15-60 min delay
    - Options data: 15-60 min delay
    - News: Real-time RSS feeds
    - Fundamentals: Quarterly/annual SEC filings

    **Insider Data**: SEC EDGAR via yfinance
    - Form 4 filings: 2-4 business day lag
    - Coverage: All public companies

    **Quality Metrics**: Calculated in-app
    - IV Percentile: Rolling 252-day window
    - P/C Ratios: Aggregated across 6 expirations
    - Confidence Scores: 6-factor proprietary model
    """)

    st.markdown("---")
    st.markdown(f"**Version**: 2.0 (Institutional Improvements)")
    st.markdown(f"**Last Updated**: 2025-10-26")
