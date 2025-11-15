"""
IV Rank Calculator - Critical for Premium Timing

Calculates IV Rank and Percentile from 52-week historical IV data.
This is the GAME CHANGER - enables selling premium only when IV is elevated.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

try:
    from ib_insync import IB, Stock, Option
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False

logger = logging.getLogger(__name__)


class IVRankCalculator:
    """
    Calculate IV Rank from historical implied volatility data

    IV Rank = (Current IV - Min IV) / (Max IV - Min IV) * 100

    Interpretation:
    - 80-100: HIGH - Excellent for selling premium (wheel strategy)
    - 50-79: NORMAL - Conditional
    - 0-49: LOW - Skip selling premium, wait for IV expansion
    """

    def __init__(self, ib_connection: Optional['IB'] = None):
        """
        Initialize IV Rank Calculator

        Args:
            ib_connection: Active IB connection (from IBManager)
        """
        if not IB_AVAILABLE:
            raise ImportError("ib_insync not installed")

        self.ib = ib_connection
        self.cache = {}  # Cache IV history to reduce API calls
        self.cache_duration = timedelta(hours=4)  # Cache for 4 hours

    def get_iv_rank(self, ticker: str, current_price: float,
                    days: int = 252) -> Optional[Dict]:
        """
        Calculate IV Rank and Percentile for a stock

        Args:
            ticker: Stock ticker symbol
            current_price: Current stock price (for ATM option selection)
            days: Number of trading days for history (default: 252 = 1 year)

        Returns:
            Dictionary with IV rank data or None if unavailable:
            {
                "current_iv": 25.5,
                "iv_rank": 85.2,  # 0-100 scale
                "iv_percentile": 87.3,  # % of days with lower IV
                "52w_high": 45.2,
                "52w_low": 12.8,
                "status": "HIGH" | "NORMAL" | "LOW",
                "last_updated": "2025-10-24T18:00:00"
            }
        """
        if not self.ib:
            logger.error("No IB connection available")
            return None

        try:
            # Check cache first
            cache_key = f"{ticker}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_duration:
                    logger.info(f"Using cached IV data for {ticker}")
                    return cached_data

            # Get current IV from ATM option
            current_iv = self._get_current_atm_iv(ticker, current_price)

            if current_iv is None or current_iv <= 0:
                logger.warning(f"Could not get current IV for {ticker}")
                return None

            # Get historical IV (30-day moving average of ATM IV)
            iv_history = self._fetch_iv_history(ticker, current_price, days)

            if not iv_history or len(iv_history) < 30:
                logger.warning(f"Insufficient IV history for {ticker}: {len(iv_history) if iv_history else 0} days")
                return None

            # Calculate IV Rank
            min_iv = min(iv_history)
            max_iv = max(iv_history)

            if max_iv == min_iv:
                iv_rank = 50.0  # Neutral if no range
            else:
                iv_rank = (current_iv - min_iv) / (max_iv - min_iv) * 100

            # Calculate IV Percentile (% of days with lower IV)
            iv_percentile = (sum(1 for iv in iv_history if iv < current_iv) /
                           len(iv_history) * 100)

            # Determine status
            if iv_rank >= 80:
                status = "HIGH"  # Excellent for selling premium
            elif iv_rank >= 50:
                status = "NORMAL"  # Conditional
            else:
                status = "LOW"  # Skip - wait for IV expansion

            result = {
                "current_iv": round(current_iv, 2),
                "iv_rank": round(iv_rank, 1),
                "iv_percentile": round(iv_percentile, 1),
                "52w_high": round(max_iv, 2),
                "52w_low": round(min_iv, 2),
                "status": status,
                "last_updated": datetime.now().isoformat()
            }

            # Cache result
            self.cache[cache_key] = (result, datetime.now())

            return result

        except Exception as e:
            logger.error(f"Error calculating IV rank for {ticker}: {e}")
            return None

    def _get_current_atm_iv(self, ticker: str, current_price: float) -> Optional[float]:
        """
        Get current ATM (at-the-money) implied volatility

        Uses nearest ATM option ~30-45 DTE for consistency
        """
        try:
            stock = Stock(ticker, 'SMART', 'USD')
            self.ib.qualifyContracts(stock)

            # Get option parameters
            chains = self.ib.reqSecDefOptParams(
                stock.symbol, '', stock.secType, stock.conId
            )

            if not chains:
                return None

            chain = next((c for c in chains if c.exchange == 'SMART'), chains[0])

            # Find expiration 30-45 DTE
            target_exp = self._find_target_expiration(chain.expirations, 30, 45)

            if not target_exp:
                return None

            # Find ATM strike
            atm_strike = min(chain.strikes, key=lambda x: abs(x - current_price))

            # Get ATM call IV (calls typically more liquid)
            call = Option(ticker, target_exp, atm_strike, 'C', 'SMART')
            self.ib.qualifyContracts(call)

            # Request market data
            ticker_obj = self.ib.reqMktData(call, '', False, False)
            self.ib.sleep(2)  # Wait for data

            iv = None
            if hasattr(ticker_obj, 'impliedVolatility') and ticker_obj.impliedVolatility:
                iv = ticker_obj.impliedVolatility * 100  # Convert to percentage

            # Cancel subscription
            self.ib.cancelMktData(call)

            return iv

        except Exception as e:
            logger.error(f"Error getting current IV for {ticker}: {e}")
            return None

    def _fetch_iv_history(self, ticker: str, current_price: float,
                         days: int) -> Optional[List[float]]:
        """
        Fetch historical IV data using historical option prices

        Note: This is a simplified approach using 30-day ATM straddle IV
        More sophisticated approach would track multiple strikes
        """
        try:
            # For now, use VIX-style approximation from historical prices
            # In production, you'd want to store daily IV snapshots

            # Get ATM straddle historical data
            stock = Stock(ticker, 'SMART', 'USD')
            self.ib.qualifyContracts(stock)

            # Request historical volatility (30-day)
            bars = self.ib.reqHistoricalData(
                stock,
                endDateTime='',
                durationStr=f'{days} D',
                barSizeSetting='1 day',
                whatToShow='HISTORICAL_VOLATILITY',  # HV as proxy for IV
                useRTH=True,
                formatDate=1
            )

            if not bars:
                logger.warning(f"No historical volatility data for {ticker}")
                return None

            # Extract volatility values
            iv_history = [bar.close for bar in bars if bar.close > 0]

            return iv_history

        except Exception as e:
            logger.error(f"Error fetching IV history for {ticker}: {e}")
            return None

    @staticmethod
    def _find_target_expiration(expirations: List[str],
                               min_dte: int, max_dte: int) -> Optional[str]:
        """Find expiration in target DTE range"""
        today = datetime.now().date()
        best_exp = None
        best_diff = float('inf')

        for exp_str in expirations:
            exp_date = datetime.strptime(exp_str, '%Y%m%d').date()
            dte = (exp_date - today).days

            if min_dte <= dte <= max_dte:
                # Prefer closer to 37 DTE (midpoint)
                diff = abs(dte - 37)
                if diff < best_diff:
                    best_exp = exp_str
                    best_diff = diff

        return best_exp

    def clear_cache(self):
        """Clear IV history cache"""
        self.cache.clear()
        logger.info("IV rank cache cleared")
