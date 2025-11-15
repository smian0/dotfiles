"""
Market Discovery Dashboard Component

Interactive Streamlit dashboard for the market-wide discovery scanner.
Displays hidden gems found by unusual activity detection.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import asyncio
from typing import List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.scan_presets import ScanPresets

# Lazy imports for IB (avoid event loop issues)
def _ensure_event_loop():
    """Ensure event loop exists for ib_insync"""
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def render_discovery_dashboard():
    """Main discovery dashboard render function"""

    st.markdown("### 💎 Market-Wide Discovery Scanner")
    st.markdown("""
    Automatically scans **thousands of stocks** to find hidden gems based on unusual activity.

    **What it finds:**
    - 📈 Unusual options volume (today vs historical average)
    - ⚡ IV rank surges (volatility explosions)
    - 🏢 Large open interest changes (institutional positioning)
    - 🎯 Extreme put/call ratios (sentiment extremes)
    - 💎 Under-followed small/mid caps (less analyst coverage)
    """)

    # Configuration section
    st.markdown("---")

    # Get all available presets
    presets_list = ScanPresets.list_presets()

    # Add traditional universes to the list
    preset_options = {
        'sp500': '📊 S&P 500 (All Sectors)',
        'nasdaq100': '💻 NASDAQ 100 (Tech Heavy)',
        'custom': '✏️ Custom Ticker List'
    }

    # Add sector-specific presets
    for preset in presets_list:
        preset_options[preset['key']] = f"{preset['name']} ({preset['risk_profile']})"

    col1, col2, col3 = st.columns(3)

    with col1:
        universe_display = st.selectbox(
            "Scan Strategy",
            list(preset_options.values()),
            help="Choose your scan strategy based on risk tolerance and goals"
        )

        # Reverse lookup to get the key
        universe = [k for k, v in preset_options.items() if v == universe_display][0]

        # Show preset info if it's a sector-specific preset
        if universe not in ['sp500', 'nasdaq100', 'custom']:
            preset_info = ScanPresets.get_preset(universe)
            if preset_info:
                st.info(f"""
                **{preset_info['description']}**

                📊 Expected Premium: {preset_info['expected_premium']}
                📈 Risk Level: {preset_info['risk_profile']}
                🎯 {len(preset_info['tickers'])} stocks in this universe
                """)


    with col2:
        min_score = st.slider(
            "Min Discovery Score",
            0, 100, 60,
            help="Minimum composite score to qualify as a hidden gem"
        )

    with col3:
        max_results = st.slider(
            "Max Results",
            5, 50, 20,
            help="Maximum number of gems to display"
        )

    col4, col5 = st.columns(2)

    with col4:
        prefer_small_caps = st.checkbox(
            "Prefer Small/Mid Caps",
            value=True,
            help="Boost scores for companies under $10B market cap"
        )

    with col5:
        prefer_low_coverage = st.checkbox(
            "Prefer Low Analyst Coverage",
            value=True,
            help="Boost scores for stocks with <10 analysts (more hidden)"
        )

    # Scan button
    st.markdown("---")
    col_scan1, col_scan2, col_scan3 = st.columns([2, 1, 2])

    with col_scan2:
        if st.button("🔍 Scan Market Now", type="primary", use_container_width=True):
            with st.spinner(f"Scanning {universe.upper()} for hidden gems..."):
                try:
                    # Run the scanner
                    _ensure_event_loop()
                    from analyzers.market_discovery import MarketDiscoveryScanner

                    # Check for IB connection
                    ib_manager = st.session_state.get('ib_manager')
                    ib = ib_manager.ib if ib_manager and ib_manager.is_connected() else None

                    scanner = MarketDiscoveryScanner(ib=ib)

                    # Run discovery
                    loop = asyncio.get_event_loop()
                    gems = loop.run_until_complete(
                        scanner.discover_gems(
                            universe=universe,
                            min_discovery_score=min_score,
                            max_results=max_results,
                            signals_required=2,
                            prefer_small_caps=prefer_small_caps,
                            prefer_low_analyst_coverage=prefer_low_coverage
                        )
                    )

                    # Store in session state
                    st.session_state.discovered_gems = gems
                    st.session_state.discovery_timestamp = datetime.now()

                    st.success(f"✅ Found {len(gems)} hidden gems!")

                except Exception as e:
                    st.error(f"❌ Scan failed: {e}")
                    st.exception(e)

    # Display results
    if 'discovered_gems' in st.session_state and st.session_state.discovered_gems:
        st.markdown("---")
        _display_discovery_results(st.session_state.discovered_gems)
    else:
        st.info("👆 Click 'Scan Market Now' to discover hidden gems")


def _display_discovery_results(gems: List):
    """Display the discovered hidden gems"""

    # Summary metrics
    st.markdown("### 📊 Discovery Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Hidden Gems Found", len(gems))

    with col2:
        avg_score = sum(g.discovery_score for g in gems) / len(gems)
        st.metric("Avg Discovery Score", f"{avg_score:.1f}")

    with col3:
        total_signals = sum(len(g.signals) for g in gems)
        st.metric("Total Signals", total_signals)

    with col4:
        small_caps = sum(1 for g in gems if g.market_cap < 10e9)
        st.metric("Small/Mid Caps", small_caps)

    # Top gems table
    st.markdown("### 💎 Top Hidden Gems")

    # Convert to DataFrame for display
    gems_data = []
    sentiment_emoji_map = {'positive': '🟢', 'negative': '🔴', 'neutral': '⚪', 'mixed': '🟡'}

    for gem in gems:
        news_indicator = sentiment_emoji_map.get(gem.news_sentiment, '⚪') if gem.recent_news else '-'

        # Calculate days since most recent news
        latest_news_date = ''
        if gem.recent_news and len(gem.recent_news) > 0:
            most_recent = gem.recent_news[0]['timestamp']
            days_ago = (datetime.now() - most_recent).days
            if days_ago == 0:
                latest_news_date = 'Today'
            elif days_ago == 1:
                latest_news_date = 'Yesterday'
            else:
                latest_news_date = f'{days_ago}d ago'

        # NEW: IV/HV ratio and quality score
        iv_hv_display = f"{gem.iv_hv_ratio:.2f}x" if gem.iv_hv_ratio > 0 else "N/A"
        quality_display = f"{gem.quality_score:.0f}/100" if gem.quality_score > 0 else "N/A"

        gems_data.append({
            'Ticker': gem.ticker,
            'Company': gem.company_name[:30] + '...' if len(gem.company_name) > 30 else gem.company_name,
            'Score': gem.discovery_score,
            'IV/HV': iv_hv_display,  # NEW: Premium opportunity indicator
            'Quality': quality_display,  # NEW: Fundamental quality
            'News': news_indicator,
            'Last News': latest_news_date if latest_news_date else '-',
            'Price': f"${gem.price:.2f}",
            'Market Cap': _format_market_cap(gem.market_cap),
            'Signals': len(gem.signals),
            'IV%': f"{gem.iv_percentile:.0f}" if gem.iv_percentile > 0 else "N/A",
            'P/C Ratio': f"{gem.put_call_ratio:.2f}" if gem.put_call_ratio > 0 else "N/A",
            'Sector': gem.sector,
        })

    df = pd.DataFrame(gems_data)

    # Display table with color coding
    st.dataframe(
        df.style.background_gradient(subset=['Score'], cmap='RdYlGn', vmin=50, vmax=100),
        use_container_width=True,
        height=400
    )

    # Detailed view
    st.markdown("### 🔍 Detailed Analysis")

    selected_ticker = st.selectbox(
        "Select ticker for detailed view",
        [g.ticker for g in gems],
        format_func=lambda t: f"{t} - {next(g.company_name for g in gems if g.ticker == t)}"
    )

    selected_gem = next((g for g in gems if g.ticker == selected_ticker), None)

    if selected_gem:
        # Quick analyze button at the top
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(f"📊 Analyze {selected_gem.ticker} →", type="primary", use_container_width=True):
                # Save selected ticker to session state for Analyze page
                st.session_state.selected_ticker = selected_gem.ticker
                st.session_state.from_discovery = {
                    'ticker': selected_gem.ticker,
                    'company_name': selected_gem.company_name,
                    'discovery_score': selected_gem.discovery_score,
                    'price': selected_gem.price,
                    'sector': selected_gem.sector
                }
                st.switch_page("pages/02_📊_Analyze.py")

        st.markdown("---")
        _display_gem_details(selected_gem)

    # Charts
    st.markdown("---")
    st.markdown("### 📈 Discovery Analytics")

    tab1, tab2, tab3 = st.tabs(["Sector Distribution", "Signal Types", "Score vs Market Cap"])

    with tab1:
        _plot_sector_distribution(gems)

    with tab2:
        _plot_signal_types(gems)

    with tab3:
        _plot_score_vs_market_cap(gems)


def _display_gem_details(gem):
    """Display detailed information about a specific gem"""

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {gem.company_name} ({gem.ticker})")
        st.markdown(f"**Sector:** {gem.sector}")
        st.markdown(f"**Price:** ${gem.price:.2f}")
        st.markdown(f"**Market Cap:** {_format_market_cap(gem.market_cap)}")

        if gem.pe_ratio:
            st.markdown(f"**P/E Ratio:** {gem.pe_ratio:.2f}")

        if gem.dividend_yield:
            st.markdown(f"**Dividend Yield:** {gem.dividend_yield*100:.2f}%")

        st.markdown(f"**Analyst Coverage:** {gem.analyst_coverage} analysts")

        # NEW: IV/HV ratio and interpretation
        st.markdown("---")
        st.markdown("##### 💰 Options Premium Opportunity")
        if gem.iv_hv_ratio > 0:
            st.markdown(f"**IV/HV Ratio:** {gem.iv_hv_ratio:.2f}x")
            st.markdown(f"**Interpretation:** {gem.iv_hv_interpretation}")
            st.markdown(f"**HV (30d):** {gem.hv_30d:.1f}%")
        else:
            st.markdown("_No IV/HV data available_")

        # NEW: Insider trading sentiment
        st.markdown("---")
        st.markdown("##### 👔 Insider Trading Sentiment")

        # Determine sentiment color and emoji
        sentiment_styles = {
            'BULLISH': ('🟢', 'green', 'Insiders are buying'),
            'BEARISH': ('🔴', 'red', 'Insiders are selling'),
            'NEUTRAL': ('⚪', 'gray', 'No significant insider activity')
        }

        emoji, color, interpretation = sentiment_styles.get(gem.insider_sentiment, ('⚪', 'gray', 'Unknown'))

        st.markdown(f"{emoji} **{gem.insider_sentiment}** - {interpretation}")
        st.markdown(f"**Buys (90d):** {gem.insider_buys_90d}")
        st.markdown(f"**Sells (90d):** {gem.insider_sells_90d}")

        if gem.insider_confidence_boost != 0:
            boost_icon = "📈" if gem.insider_confidence_boost > 0 else "📉"
            st.markdown(f"{boost_icon} **Score Impact:** {gem.insider_confidence_boost:+.1f} points")

    with col2:
        # Discovery score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gem.discovery_score,
            title={'text': "Discovery Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 70], 'color': "lightyellow"},
                    {'range': [70, 85], 'color': "lightgreen"},
                    {'range': [85, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)

        # NEW: Quality score gauge
        if gem.quality_score > 0:
            quality_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=gem.quality_score,
                title={'text': "Quality Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "purple"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightcoral"},
                        {'range': [30, 50], 'color': "lightyellow"},
                        {'range': [50, 70], 'color': "lightgreen"},
                        {'range': [70, 100], 'color': "darkgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "blue", 'width': 4},
                        'thickness': 0.75,
                        'value': 60
                    }
                }
            ))
            quality_fig.update_layout(height=250)
            st.plotly_chart(quality_fig, use_container_width=True)

    # Fundamental quality breakdown (NEW)
    if gem.quality_score > 0:
        st.markdown("#### ⭐ Fundamental Quality Analysis")

        qual_col1, qual_col2, qual_col3 = st.columns(3)

        with qual_col1:
            st.metric("ROE", f"{gem.roe:.1f}%", help="Return on Equity - profitability vs equity")
            st.metric("Free Cash Flow", f"${gem.free_cash_flow:.2f}B",
                     delta="Positive ✅" if gem.free_cash_flow > 0 else "Negative ❌")

        with qual_col2:
            st.metric("Profit Margin", f"{gem.profit_margin:.1f}%")
            st.metric("Debt/Equity", f"{gem.debt_to_equity:.0f}",
                     delta="Conservative" if gem.debt_to_equity < 100 else "Leveraged")

        with qual_col3:
            st.metric("Short Interest", f"{gem.short_interest_pct:.2f}%")
            st.metric("Insider Own.", f"{gem.insider_ownership_pct:.1f}%")

    # Discovery reasons
    st.markdown("#### 🎯 Why This is a Hidden Gem")
    for reason in gem.discovery_reasons:
        st.markdown(f"- {reason}")

    # News catalyst section
    if gem.recent_news and len(gem.recent_news) > 0:
        st.markdown("#### 📰 Recent Catalyst News")

        # Sentiment badge
        sentiment_colors = {
            'positive': '🟢',
            'negative': '🔴',
            'neutral': '⚪',
            'mixed': '🟡'
        }
        sentiment_emoji = sentiment_colors.get(gem.news_sentiment, '⚪')

        col_sentiment1, col_sentiment2 = st.columns(2)
        with col_sentiment1:
            st.metric("News Sentiment", f"{sentiment_emoji} {gem.news_sentiment.title()}")
        with col_sentiment2:
            if gem.catalyst_score != 0:
                st.metric("Catalyst Impact", f"{gem.catalyst_score:+.0f} points")

        # Display news items with full grounding
        st.markdown("##### 📑 Source Citations")
        st.caption("All news items verified from yfinance API with publication dates and source links")

        for i, news_item in enumerate(gem.recent_news[:5], 1):  # Show top 5 news items
            # Full timestamp with timezone-aware formatting
            timestamp_str = news_item['timestamp'].strftime('%B %d, %Y at %I:%M %p')
            days_ago = (datetime.now() - news_item['timestamp']).days
            recency = f"({days_ago} days ago)" if days_ago > 0 else "(Today)"

            # Create citation box
            with st.container():
                st.markdown(f"**[{i}]** {news_item['title']}")
                st.caption(f"📅 Published: {timestamp_str} {recency}")
                st.caption(f"📰 Source: {news_item['publisher']}")
                st.caption(f"🔗 [Verify Article]({news_item['link']})")
                st.markdown("---")

    # Signals breakdown
    st.markdown("#### 📡 Detection Signals")

    for signal in gem.signals:
        severity_emoji = {
            'low': '🟡',
            'medium': '🟠',
            'high': '🔴',
            'extreme': '🔥'
        }.get(signal.severity, '⚪')

        signal_name = signal.signal_type.replace('_', ' ').title()

        with st.expander(f"{severity_emoji} {signal_name} (Score: {signal.score:.1f})"):
            st.json(signal.details)

    # Options metrics
    st.markdown("#### 📊 Options Metrics")

    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

    with metrics_col1:
        if gem.iv_percentile > 0:
            st.metric("IV Percentile", f"{gem.iv_percentile:.0f}%")
        if gem.unusual_volume_ratio > 1:
            st.metric("Volume Ratio", f"{gem.unusual_volume_ratio:.1f}x")

    with metrics_col2:
        if gem.put_call_ratio > 0:
            st.metric("Put/Call Ratio", f"{gem.put_call_ratio:.2f}")
        if gem.oi_change_pct != 0:
            st.metric("OI Change", f"{gem.oi_change_pct:+.1f}%")

    with metrics_col3:
        if gem.block_trades_count > 0:
            st.metric("Block Trades", gem.block_trades_count)
        if gem.sweep_count > 0:
            st.metric("Sweeps", gem.sweep_count)


def _plot_sector_distribution(gems):
    """Plot sector distribution of discovered gems"""
    sector_counts = {}
    for gem in gems:
        sector = gem.sector if gem.sector != 'Unknown' else 'Other'
        sector_counts[sector] = sector_counts.get(sector, 0) + 1

    fig = px.pie(
        values=list(sector_counts.values()),
        names=list(sector_counts.keys()),
        title="Hidden Gems by Sector"
    )
    st.plotly_chart(fig, use_container_width=True)


def _plot_signal_types(gems):
    """Plot distribution of signal types"""
    signal_counts = {}
    for gem in gems:
        for signal in gem.signals:
            signal_type = signal.signal_type.replace('_', ' ').title()
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1

    fig = px.bar(
        x=list(signal_counts.keys()),
        y=list(signal_counts.values()),
        labels={'x': 'Signal Type', 'y': 'Count'},
        title="Detection Signals Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)


def _plot_score_vs_market_cap(gems):
    """Plot discovery score vs market cap"""
    data = {
        'Ticker': [g.ticker for g in gems],
        'Score': [g.discovery_score for g in gems],
        'Market Cap': [g.market_cap / 1e9 for g in gems],  # Convert to billions
        'Sector': [g.sector for g in gems]
    }

    df = pd.DataFrame(data)

    fig = px.scatter(
        df,
        x='Market Cap',
        y='Score',
        color='Sector',
        size=[10] * len(gems),
        hover_data=['Ticker'],
        labels={'Market Cap': 'Market Cap ($B)', 'Score': 'Discovery Score'},
        title="Discovery Score vs Market Cap"
    )

    fig.update_layout(xaxis_type="log")
    st.plotly_chart(fig, use_container_width=True)


def _format_market_cap(market_cap: float) -> str:
    """Format market cap for display"""
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"
