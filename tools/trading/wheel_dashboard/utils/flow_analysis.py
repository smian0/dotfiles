"""
Options Flow Analysis Utilities

Detect unusual options activity, institutional flow, and generate
trading signals for wheel strategy.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def calculate_vol_to_oi(options_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Volume/OI ratio for each option

    Args:
        options_df: DataFrame with 'volume' and 'openInterest' columns

    Returns:
        DataFrame with added 'vol_to_oi' column
    """
    df = options_df.copy()

    df['vol_to_oi'] = np.where(
        df['openInterest'] > 0,
        df['volume'] / df['openInterest'],
        np.nan
    )

    return df


def calculate_premium_flow(options_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate premium flow (dollar volume) for each option

    Args:
        options_df: DataFrame with 'volume' and 'lastPrice' columns

    Returns:
        DataFrame with added 'premium_flow' column
    """
    df = options_df.copy()

    # Premium flow = volume * price * 100 (contract multiplier)
    df['premium_flow'] = df['volume'] * df['lastPrice'] * 100

    return df


def calculate_pcr_by_expiration(puts_df: pd.DataFrame, calls_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Put/Call Ratio (PCR) by expiration based on Open Interest

    Args:
        puts_df: DataFrame of put options with 'expiration' and 'openInterest'
        calls_df: DataFrame of call options with 'expiration' and 'openInterest'

    Returns:
        DataFrame with PCR_OI by expiration
    """
    # Aggregate OI by expiration
    put_oi = puts_df.groupby('expiration')['openInterest'].sum()
    call_oi = calls_df.groupby('expiration')['openInterest'].sum()

    # Combine into single DataFrame
    pcr_df = pd.DataFrame({
        'put_oi': put_oi,
        'call_oi': call_oi
    })

    # Calculate PCR
    pcr_df['PCR_OI'] = pcr_df['put_oi'] / pcr_df['call_oi']

    return pcr_df


def detect_unusual_activity(
    puts_df: pd.DataFrame,
    calls_df: pd.DataFrame,
    vol_oi_threshold: float = 2.0,
    premium_threshold: float = 500000
) -> Dict:
    """
    Detect unusual options activity across all strikes and expirations

    Args:
        puts_df: Put options DataFrame
        calls_df: Call options DataFrame
        vol_oi_threshold: Minimum Volume/OI ratio to flag (default: 2.0)
        premium_threshold: Minimum premium flow to flag (default: $500k)

    Returns:
        Dictionary with unusual activity data and signals
    """
    # Calculate metrics for puts
    puts = calculate_vol_to_oi(puts_df)
    puts = calculate_premium_flow(puts)
    puts['side'] = 'put'

    # Calculate metrics for calls
    calls = calculate_vol_to_oi(calls_df)
    calls = calculate_premium_flow(calls)
    calls['side'] = 'call'

    # Find unusual options
    unusual_puts = puts[
        (puts['vol_to_oi'] > vol_oi_threshold) |
        (puts['premium_flow'] > premium_threshold)
    ].copy()

    unusual_calls = calls[
        (calls['vol_to_oi'] > vol_oi_threshold) |
        (calls['premium_flow'] > premium_threshold)
    ].copy()

    # Calculate PCR by expiration
    pcr_df = calculate_pcr_by_expiration(puts, calls)

    # Aggregate flow statistics
    total_put_flow = unusual_puts['premium_flow'].sum()
    total_call_flow = unusual_calls['premium_flow'].sum()
    total_put_volume = unusual_puts['volume'].sum()
    total_call_volume = unusual_calls['volume'].sum()

    return {
        'unusual_puts': unusual_puts,
        'unusual_calls': unusual_calls,
        'pcr_by_expiration': pcr_df,
        'stats': {
            'total_put_flow': total_put_flow,
            'total_call_flow': total_call_flow,
            'total_put_volume': total_put_volume,
            'total_call_volume': total_call_volume,
            'put_call_flow_ratio': total_put_flow / total_call_flow if total_call_flow > 0 else 0
        }
    }


def generate_wheel_signals(activity_data: Dict, ticker: str) -> List[Dict]:
    """
    Generate actionable trading signals for wheel strategy based on flow

    Args:
        activity_data: Output from detect_unusual_activity()
        ticker: Stock ticker

    Returns:
        List of signal dictionaries with type, severity, message, and recommendation
    """
    signals = []
    stats = activity_data['stats']
    pcr_df = activity_data['pcr_by_expiration']

    # Signal 1: Heavy put buying (bearish - avoid selling puts)
    if stats['total_put_flow'] > 1_000_000:
        signals.append({
            'type': 'WARNING',
            'severity': 'HIGH',
            'title': '🚨 Heavy Institutional Put Buying',
            'message': f"${stats['total_put_flow']:,.0f} in unusual put premium flow",
            'recommendation': f"AVOID selling puts on {ticker}. Institutions are betting on downside.",
            'details': f"{stats['total_put_volume']:,.0f} contracts traded"
        })

    # Signal 2: Heavy call buying (potential IV expansion)
    if stats['total_call_flow'] > 1_000_000:
        signals.append({
            'type': 'INFO',
            'severity': 'MEDIUM',
            'title': '💡 Heavy Call Buying Detected',
            'message': f"${stats['total_call_flow']:,.0f} in unusual call premium flow",
            'recommendation': f"Potential IV expansion on {ticker}. Better covered call premiums likely soon.",
            'details': f"{stats['total_call_volume']:,.0f} contracts traded"
        })

    # Signal 3: Extreme put/call flow imbalance
    if stats['put_call_flow_ratio'] > 3.0:
        signals.append({
            'type': 'WARNING',
            'severity': 'HIGH',
            'title': '⚠️ Extreme Bearish Flow',
            'message': f"Put flow is {stats['put_call_flow_ratio']:.1f}x call flow",
            'recommendation': f"Strong bearish positioning on {ticker}. Reduce put-selling exposure.",
            'details': "Market expects significant downside"
        })
    elif stats['put_call_flow_ratio'] > 0 and stats['put_call_flow_ratio'] < 0.33:
        signals.append({
            'type': 'SUCCESS',
            'severity': 'LOW',
            'title': '✅ Bullish Flow Detected',
            'message': f"Call flow is {1/stats['put_call_flow_ratio']:.1f}x put flow",
            'recommendation': f"Bullish sentiment on {ticker}. Good environment for selling puts.",
            'details': "Market expects upside or stability"
        })
    elif stats['put_call_flow_ratio'] == 0 and stats['total_call_flow'] > 0:
        # Only call flow, no put flow
        signals.append({
            'type': 'SUCCESS',
            'severity': 'LOW',
            'title': '✅ Pure Bullish Flow',
            'message': f"Only call flow detected (${stats['total_call_flow']:,.0f}), no unusual put activity",
            'recommendation': f"Very bullish sentiment on {ticker}. Excellent environment for selling puts.",
            'details': "Zero put flow = extremely bullish positioning"
        })

    # Signal 4: Extreme PCR on near-term expirations
    if not pcr_df.empty:
        # Check first 2 expirations (most relevant for wheel)
        near_term_pcr = pcr_df.head(2)
        max_pcr = near_term_pcr['PCR_OI'].max()

        if max_pcr > 2.0:
            signals.append({
                'type': 'WARNING',
                'severity': 'MEDIUM',
                'title': '⚠️ Extreme Bearish Positioning',
                'message': f"PCR of {max_pcr:.2f} on near-term expirations",
                'recommendation': "Wait for sentiment to normalize before selling puts.",
                'details': "More than 2x puts vs calls outstanding"
            })
        elif max_pcr < 0.5:
            signals.append({
                'type': 'INFO',
                'severity': 'LOW',
                'title': '📊 Bullish Positioning',
                'message': f"PCR of {max_pcr:.2f} on near-term expirations",
                'recommendation': "Favorable environment for wheel strategy.",
                'details': "Calls significantly outnumber puts"
            })

    # Signal 5: No unusual activity (all clear)
    if not signals:
        signals.append({
            'type': 'SUCCESS',
            'severity': 'LOW',
            'title': '✅ No Unusual Activity',
            'message': 'Normal options flow detected',
            'recommendation': f"No red flags for wheel strategy on {ticker}.",
            'details': 'Proceed with standard analysis'
        })

    return signals


def get_top_unusual_strikes(activity_data: Dict, top_n: int = 10) -> Dict:
    """
    Get top N most unusual strikes by premium flow

    Args:
        activity_data: Output from detect_unusual_activity()
        top_n: Number of top strikes to return

    Returns:
        Dictionary with top puts and calls
    """
    puts = activity_data['unusual_puts']
    calls = activity_data['unusual_calls']

    if len(puts) > 0:
        top_puts = puts.nlargest(top_n, 'premium_flow')[
            ['strike', 'expiration', 'lastPrice', 'volume', 'openInterest',
             'vol_to_oi', 'premium_flow', 'impliedVolatility']
        ]
    else:
        top_puts = pd.DataFrame()

    if len(calls) > 0:
        top_calls = calls.nlargest(top_n, 'premium_flow')[
            ['strike', 'expiration', 'lastPrice', 'volume', 'openInterest',
             'vol_to_oi', 'premium_flow', 'impliedVolatility']
        ]
    else:
        top_calls = pd.DataFrame()

    return {
        'top_puts': top_puts,
        'top_calls': top_calls
    }
