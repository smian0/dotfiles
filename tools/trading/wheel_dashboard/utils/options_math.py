"""
Options Mathematics Utilities

Probability calculations, expected moves, and other statistical tools
for options analysis.
"""

import numpy as np
from scipy.stats import norm
from typing import Optional
import math


def calculate_probability_of_profit(
    stock_price: float,
    strike_price: float,
    dte: int,
    implied_volatility: float,
    option_type: str = 'put',
    risk_free_rate: float = 0.05
) -> Optional[float]:
    """
    Calculate probability that option expires worthless (seller's PoP)

    For puts: Probability stock stays above strike
    For calls: Probability stock stays below strike

    Args:
        stock_price: Current stock price
        strike_price: Option strike price
        dte: Days to expiration
        implied_volatility: IV as decimal (e.g., 0.25 for 25%)
        option_type: 'put' or 'call'
        risk_free_rate: Risk-free rate as decimal (default: 0.05 = 5%)

    Returns:
        Probability as percentage (0-100) or None if invalid inputs
    """
    try:
        if dte <= 0 or implied_volatility <= 0 or stock_price <= 0 or strike_price <= 0:
            return None

        # Convert to years
        T = dte / 365.0

        # Calculate d2 from Black-Scholes
        d2 = (math.log(stock_price / strike_price) +
              (risk_free_rate - 0.5 * implied_volatility**2) * T) / \
             (implied_volatility * math.sqrt(T))

        if option_type.lower() == 'put':
            # PoP for put seller = probability stock > strike at expiration
            pop = norm.cdf(d2) * 100
        else:  # call
            # PoP for call seller = probability stock < strike at expiration
            pop = norm.cdf(-d2) * 100

        return pop

    except Exception as e:
        return None


def calculate_expected_move(
    stock_price: float,
    atm_iv: float,
    dte: int,
    std_deviations: float = 1.0
) -> dict:
    """
    Calculate expected stock move based on ATM implied volatility

    Expected Move = Stock Price * IV * sqrt(DTE/365) * std_deviations

    Args:
        stock_price: Current stock price
        atm_iv: ATM implied volatility as decimal (e.g., 0.25 for 25%)
        dte: Days to expiration
        std_deviations: Number of standard deviations (1.0 = 68% probability)

    Returns:
        Dictionary with expected move data:
        {
            'move_dollars': Expected move in dollars,
            'move_percent': Expected move as percentage,
            'upper_bound': Stock price + move,
            'lower_bound': Stock price - move,
            'probability': Probability of staying within range
        }
    """
    try:
        if dte <= 0 or atm_iv <= 0 or stock_price <= 0:
            return None

        # Expected move formula
        T = dte / 365.0
        move_dollars = stock_price * atm_iv * math.sqrt(T) * std_deviations
        move_percent = (move_dollars / stock_price) * 100

        # Probability mapping (approximate)
        prob_map = {
            1.0: 68.27,  # 1 SD
            1.5: 86.64,  # 1.5 SD
            2.0: 95.45,  # 2 SD
            2.5: 98.76,  # 2.5 SD
            3.0: 99.73   # 3 SD
        }

        probability = prob_map.get(std_deviations,
                                   norm.cdf(std_deviations) - norm.cdf(-std_deviations)) * 100

        return {
            'move_dollars': move_dollars,
            'move_percent': move_percent,
            'upper_bound': stock_price + move_dollars,
            'lower_bound': stock_price - move_dollars,
            'probability': probability,
            'std_deviations': std_deviations
        }

    except Exception as e:
        return None


def get_atm_iv(options_chain, stock_price: float) -> Optional[float]:
    """
    Get ATM (at-the-money) implied volatility from options chain

    Args:
        options_chain: DataFrame with strike and impliedVolatility columns
        stock_price: Current stock price

    Returns:
        ATM IV as decimal or None
    """
    try:
        if options_chain.empty:
            return None

        # Find ATM strike (closest to current price)
        options_chain = options_chain.copy()
        options_chain['distance'] = abs(options_chain['strike'] - stock_price)
        atm_option = options_chain.nsmallest(1, 'distance').iloc[0]

        iv = atm_option.get('impliedVolatility')

        # Return as decimal (yfinance returns decimal, not percentage)
        if iv and iv > 0:
            return iv
        else:
            return None

    except Exception as e:
        return None


def calculate_break_even(
    strike_price: float,
    premium: float,
    option_type: str = 'put'
) -> float:
    """
    Calculate break-even price for option seller

    Args:
        strike_price: Option strike
        premium: Premium received
        option_type: 'put' or 'call'

    Returns:
        Break-even price
    """
    if option_type.lower() == 'put':
        # Put seller break-even = strike - premium
        return strike_price - premium
    else:
        # Call seller break-even = strike + premium
        return strike_price + premium


def calculate_delta_from_pop(pop: float, option_type: str = 'put') -> float:
    """
    Approximate delta from probability of profit

    For puts: Delta ≈ -(100 - PoP)
    For calls: Delta ≈ PoP

    Args:
        pop: Probability of profit (0-100)
        option_type: 'put' or 'call'

    Returns:
        Approximate delta
    """
    if option_type.lower() == 'put':
        return -(100 - pop) / 100
    else:
        return pop / 100


def iv_percentile(current_iv: float, iv_history: list) -> float:
    """
    Calculate IV percentile (what % of days had lower IV)

    Args:
        current_iv: Current IV
        iv_history: List of historical IV values

    Returns:
        Percentile (0-100)
    """
    if not iv_history or current_iv is None:
        return None

    lower_count = sum(1 for iv in iv_history if iv < current_iv)
    return (lower_count / len(iv_history)) * 100


def iv_rank(current_iv: float, min_iv: float, max_iv: float) -> float:
    """
    Calculate IV Rank: (Current - Min) / (Max - Min) * 100

    Args:
        current_iv: Current IV
        min_iv: 52-week low IV
        max_iv: 52-week high IV

    Returns:
        IV Rank (0-100)
    """
    if max_iv == min_iv:
        return 50.0  # Neutral if no range

    return ((current_iv - min_iv) / (max_iv - min_iv)) * 100


def annualized_return(
    premium: float,
    strike: float,
    dte: int,
    include_assignment: bool = False,
    stock_price: float = None
) -> float:
    """
    Calculate annualized return for wheel strategy

    Args:
        premium: Premium received
        strike: Strike price (capital at risk)
        dte: Days to expiration
        include_assignment: If True, calculate return if assigned
        stock_price: Current stock price (required if include_assignment)

    Returns:
        Annualized return as percentage
    """
    if dte <= 0:
        return 0.0

    # Basic annualized premium yield
    basic_return = (premium / strike) * (365 / dte) * 100

    if include_assignment and stock_price:
        # If assigned, potential upside from selling calls
        # (Simplified - assumes selling ATM call at similar premium)
        # This is very approximate
        assignment_boost = (premium / strike) * 100  # One more premium cycle
        return basic_return + assignment_boost

    return basic_return
