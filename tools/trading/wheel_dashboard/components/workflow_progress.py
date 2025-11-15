"""
Workflow Progress Tracker Component
Shows user where they are in the wheel strategy pipeline
"""

import streamlit as st
from typing import Literal

WorkflowPhase = Literal['discover', 'analyze', 'execute', 'monitor']

def render_workflow_progress(current_phase: WorkflowPhase):
    """
    Renders a visual progress tracker showing workflow phases

    Args:
        current_phase: Which phase the user is currently on
    """

    # Define workflow phases
    phases = {
        'discover': {'emoji': '🔍', 'label': 'Discover', 'description': 'Find opportunities'},
        'analyze': {'emoji': '📊', 'label': 'Analyze', 'description': 'Deep dive research'},
        'execute': {'emoji': '🎯', 'label': 'Execute', 'description': 'Configure trades'},
        'monitor': {'emoji': '📈', 'label': 'Monitor', 'description': 'Track positions'}
    }

    phase_order = ['discover', 'analyze', 'execute', 'monitor']
    current_idx = phase_order.index(current_phase)

    # Create progress bar HTML
    progress_html = '<div style="display: flex; justify-content: space-between; align-items: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">'

    for idx, phase_key in enumerate(phase_order):
        phase = phases[phase_key]

        # Determine state
        if idx < current_idx:
            state = 'completed'
            icon = '✅'
            opacity = '0.7'
        elif idx == current_idx:
            state = 'current'
            icon = phase['emoji']
            opacity = '1.0'
        else:
            state = 'pending'
            icon = '⚪'
            opacity = '0.5'

        # Build phase box
        progress_html += f'''
        <div style="flex: 1; text-align: center; opacity: {opacity};">
            <div style="font-size: 32px; margin-bottom: 5px;">{icon}</div>
            <div style="font-weight: bold; color: white; font-size: 16px;">{phase['label'].upper()}</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 12px;">{phase['description']}</div>
        </div>
        '''

        # Add arrow between phases (except after last one)
        if idx < len(phase_order) - 1:
            arrow_opacity = '1.0' if idx < current_idx else '0.3'
            progress_html += f'<div style="font-size: 24px; color: white; opacity: {arrow_opacity}; margin: 0 10px;">→</div>'

    progress_html += '</div>'

    st.markdown(progress_html, unsafe_allow_html=True)

    # Show contextual guidance
    guidance = _get_phase_guidance(current_phase)
    if guidance:
        st.info(guidance)


def _get_phase_guidance(phase: WorkflowPhase) -> str:
    """Returns contextual guidance for current phase"""

    guidance_map = {
        'discover': (
            "💡 **Step 1: Discover Opportunities**\n\n"
            "Scan the market for high-probability wheel candidates. Look for:\n"
            "- High IV/HV ratios (elevated premium)\n"
            "- Strong fundamentals (quality score > 60)\n"
            "- Positive insider sentiment\n"
            "- Recent news catalysts\n\n"
            "**Action:** Run scan → Select 3-5 candidates → Click 'Add to Shortlist'"
        ),
        'analyze': (
            "🔬 **Step 2: Analyze Candidates**\n\n"
            "Deep dive into your shortlist. Validate:\n"
            "- Financial health (ROE, debt, cash flow)\n"
            "- Technical setup (support levels, volatility)\n"
            "- Risk metrics (beta, correlation)\n"
            "- Insider confidence\n\n"
            "**Action:** Review each ticker → Assign conviction level → Move top 2-3 to Execute"
        ),
        'execute': (
            "⚡ **Step 3: Execute Trades**\n\n"
            "Configure your wheel positions:\n"
            "- Select optimal strike (2-5% OTM)\n"
            "- Calculate position size (risk per trade)\n"
            "- Verify liquidity (bid/ask spread < 5%)\n"
            "- Set premium targets (annualized yield > 12%)\n\n"
            "**Action:** Configure parameters → Review checklist → Execute via broker"
        ),
        'monitor': (
            "👀 **Step 4: Monitor Positions**\n\n"
            "Track and manage active wheel positions:\n"
            "- Check assignment risk\n"
            "- Evaluate roll opportunities\n"
            "- Monitor P&L and Greeks\n"
            "- Manage winners/losers\n\n"
            "**Action:** Daily review → Roll/close when appropriate → Return to Discover for new setups"
        )
    }

    return guidance_map.get(phase, '')


def render_next_step_button(
    current_phase: WorkflowPhase,
    enabled: bool = True,
    count: int = 0
):
    """
    Renders a 'Next Step' button to advance workflow

    Args:
        current_phase: Current phase
        enabled: Whether button should be clickable
        count: Number of items ready for next phase (e.g., shortlisted tickers)
    """

    next_phase_map = {
        'discover': ('Analyze Candidates', '02_📊_Analyze'),
        'analyze': ('Execute Trades', '03_🎯_Execute'),
        'execute': ('Monitor Positions', '04_📈_Monitor'),
        'monitor': ('Discover New Opportunities', '01_🔍_Discover')
    }

    if current_phase not in next_phase_map:
        return

    button_text, next_page = next_phase_map[current_phase]

    if count > 0:
        button_text += f" ({count})"

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if enabled:
            if st.button(
                f"✅ Next: {button_text} →",
                use_container_width=True,
                type="primary"
            ):
                st.switch_page(f"pages/{next_page}.py")
        else:
            st.button(
                f"⚠️ Complete this step first",
                use_container_width=True,
                disabled=True
            )
            st.caption("Add items to proceed to next phase")


def get_session_summary() -> dict:
    """Returns summary of workflow state from session"""

    return {
        'shortlist_count': len(st.session_state.get('shortlist', [])),
        'analyzed_count': len(st.session_state.get('analyzed_tickers', [])),
        'pending_trades': len(st.session_state.get('pending_trades', [])),
        'active_positions': len(st.session_state.get('active_positions', []))
    }


def render_workflow_stats():
    """Renders quick stats about workflow progress"""

    stats = get_session_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Shortlisted",
            stats['shortlist_count'],
            help="Tickers from discovery scan"
        )

    with col2:
        st.metric(
            "Analyzed",
            stats['analyzed_count'],
            help="Tickers with conviction scores"
        )

    with col3:
        st.metric(
            "Pending",
            stats['pending_trades'],
            help="Configured trades ready to execute"
        )

    with col4:
        st.metric(
            "Active",
            stats['active_positions'],
            help="Open wheel positions"
        )
