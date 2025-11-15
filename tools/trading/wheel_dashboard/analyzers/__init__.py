"""Strategic Options Analyzers

NOTE: IB-dependent modules (IVRankCalculator, WeeklyScanner, FlowScanner,
BackgroundFlowMonitor, EarningsFilter) are imported lazily to avoid event loop
issues with Streamlit.

Use direct imports when needed:
    from analyzers.flow_scanner import FlowScanner
    from analyzers.earnings_filter import EarningsFilter
"""

# Non-IB modules - safe to import (no IB dependencies)
from .flow_database import FlowDatabase
from .alert_system import AlertNotifier, AlertFilter, create_alert_callback

# IB-dependent modules - lazy import only (use direct import when needed)
# These modules import ib_insync which requires an event loop
def _lazy_import_ib_modules():
    """
    Lazy import IB-dependent modules to avoid event loop issues
    Only import when actually using IB functionality
    """
    global IVRankCalculator, WeeklyScanner, FlowScanner, BackgroundFlowMonitor, EarningsFilter

    from .iv_rank_calculator import IVRankCalculator
    from .weekly_scanner import WeeklyScanner
    from .flow_scanner import FlowScanner
    from .background_scanner import BackgroundFlowMonitor
    from .earnings_filter import EarningsFilter

    return IVRankCalculator, WeeklyScanner, FlowScanner, BackgroundFlowMonitor, EarningsFilter

__all__ = [
    # Safe imports (no IB dependency)
    'FlowDatabase',
    'AlertNotifier',
    'AlertFilter',
    'create_alert_callback',
    # IB-dependent (use direct import when needed)
    # 'IVRankCalculator',
    # 'WeeklyScanner',
    # 'FlowScanner',
    # 'BackgroundFlowMonitor',
    # 'EarningsFilter',
]
