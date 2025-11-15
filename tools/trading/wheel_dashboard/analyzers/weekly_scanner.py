"""
Weekly Expiration Scanner - Opportunity Multiplier

Detects weekly options expirations for high-frequency wheel strategy.
Unlocks 52 opportunities/year vs 12 with monthly-only.
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
import logging

try:
    from ib_insync import IB, Stock
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False

logger = logging.getLogger(__name__)


class WeeklyScanner:
    """
    Scan for weekly options expirations

    Weekly expirations enable high-frequency wheel strategy:
    - Sell 7-14 DTE puts instead of 30-45 DTE
    - Higher theta decay (time value erosion)
    - More frequent premium collection
    - Better assignment control
    """

    def __init__(self, ib_connection: Optional['IB'] = None):
        """
        Initialize Weekly Scanner

        Args:
            ib_connection: Active IB connection (from IBManager)
        """
        if not IB_AVAILABLE:
            raise ImportError("ib_insync not installed")

        self.ib = ib_connection
        self.cache = {}  # Cache expiration data
        self.cache_duration = timedelta(hours=12)  # Cache for 12 hours

    def get_all_expirations(self, ticker: str) -> List[Dict]:
        """
        Get all available expirations (weekly + monthly)

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of expiration dictionaries:
            [
                {
                    "date": "2025-10-31",
                    "dte": 7,
                    "type": "weekly" | "monthly",
                    "is_monthly": False,
                    "day_of_week": "Friday"
                },
                ...
            ]
        """
        if not self.ib:
            logger.error("No IB connection available")
            return []

        try:
            # Check cache first
            cache_key = ticker
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_duration:
                    logger.info(f"Using cached expiration data for {ticker}")
                    return cached_data

            # Get expirations from IB
            stock = Stock(ticker, 'SMART', 'USD')
            self.ib.qualifyContracts(stock)

            # Get option parameters
            chains = self.ib.reqSecDefOptParams(
                stock.symbol, '', stock.secType, stock.conId
            )

            if not chains:
                logger.warning(f"No options data for {ticker}")
                return []

            # Use SMART exchange
            chain = next((c for c in chains if c.exchange == 'SMART'), chains[0])

            # Process expirations
            expirations = []
            today = date.today()

            for exp_str in sorted(chain.expirations):
                exp_date = datetime.strptime(exp_str, '%Y%m%d').date()
                dte = (exp_date - today).days

                # Only include future expirations
                if dte < 0:
                    continue

                # Determine if monthly (3rd Friday)
                is_monthly = self._is_monthly_expiration(exp_date)

                expirations.append({
                    "date": exp_date.isoformat(),
                    "dte": dte,
                    "type": "monthly" if is_monthly else "weekly",
                    "is_monthly": is_monthly,
                    "day_of_week": exp_date.strftime('%A')
                })

            # Cache result
            self.cache[cache_key] = (expirations, datetime.now())

            return expirations

        except Exception as e:
            logger.error(f"Error getting expirations for {ticker}: {e}")
            return []

    def scan_weekly_opportunities(
        self,
        ticker: str,
        min_dte: int = 7,
        max_dte: int = 21
    ) -> List[Dict]:
        """
        Scan weekly expirations for wheel opportunities

        Args:
            ticker: Stock ticker symbol
            min_dte: Minimum days to expiration (default: 7 = 1 week)
            max_dte: Maximum days to expiration (default: 21 = 3 weeks)

        Returns:
            List of weekly expiration opportunities:
            [
                {
                    "date": "2025-11-07",
                    "dte": 14,
                    "type": "weekly",
                    "is_monthly": False,
                    "day_of_week": "Friday"
                },
                ...
            ]
        """
        all_expirations = self.get_all_expirations(ticker)

        # Filter weekly expirations in DTE range
        weekly_opportunities = [
            exp for exp in all_expirations
            if not exp['is_monthly'] and min_dte <= exp['dte'] <= max_dte
        ]

        return weekly_opportunities

    def get_next_weekly(self, ticker: str) -> Optional[Dict]:
        """
        Get next weekly expiration (excluding monthlies)

        Args:
            ticker: Stock ticker symbol

        Returns:
            Next weekly expiration or None
        """
        weeklies = self.scan_weekly_opportunities(ticker, min_dte=1, max_dte=90)

        if not weeklies:
            return None

        # Return earliest weekly
        return min(weeklies, key=lambda x: x['dte'])

    def get_expiration_calendar(self, ticker: str, days_ahead: int = 60) -> Dict:
        """
        Get expiration calendar for next N days

        Args:
            ticker: Stock ticker symbol
            days_ahead: Number of days to include (default: 60)

        Returns:
            Dictionary with expiration summary:
            {
                "ticker": "KO",
                "total_expirations": 8,
                "weekly_count": 6,
                "monthly_count": 2,
                "next_weekly": {...},
                "next_monthly": {...},
                "all_expirations": [...]
            }
        """
        all_exps = self.get_all_expirations(ticker)

        # Filter to days_ahead
        filtered_exps = [exp for exp in all_exps if exp['dte'] <= days_ahead]

        weeklies = [exp for exp in filtered_exps if not exp['is_monthly']]
        monthlies = [exp for exp in filtered_exps if exp['is_monthly']]

        return {
            "ticker": ticker,
            "total_expirations": len(filtered_exps),
            "weekly_count": len(weeklies),
            "monthly_count": len(monthlies),
            "next_weekly": weeklies[0] if weeklies else None,
            "next_monthly": monthlies[0] if monthlies else None,
            "all_expirations": filtered_exps
        }

    @staticmethod
    def _is_monthly_expiration(exp_date: date) -> bool:
        """
        Check if expiration is monthly (3rd Friday of month)

        Monthly options expire on the 3rd Friday of the month.
        All other Friday expirations are weekly.

        Args:
            exp_date: Expiration date

        Returns:
            True if monthly expiration, False if weekly
        """
        # Monthly options expire on 3rd Friday
        first_day = exp_date.replace(day=1)

        # Find first Friday of month
        days_to_friday = (4 - first_day.weekday()) % 7  # Friday = 4
        first_friday = first_day + timedelta(days=days_to_friday)

        # Third Friday is 14 days after first Friday
        third_friday = first_friday + timedelta(days=14)

        return exp_date == third_friday

    def compare_weekly_vs_monthly(
        self,
        ticker: str,
        weekly_dte: int = 14,
        monthly_dte: int = 35
    ) -> Dict:
        """
        Compare weekly vs monthly wheel strategy opportunities

        Args:
            ticker: Stock ticker symbol
            weekly_dte: Target DTE for weekly (default: 14)
            monthly_dte: Target DTE for monthly (default: 35)

        Returns:
            Comparison dictionary:
            {
                "weekly": {...},
                "monthly": {...},
                "weekly_advantages": [...],
                "monthly_advantages": [...]
            }
        """
        all_exps = self.get_all_expirations(ticker)

        # Find nearest weekly to target DTE
        weeklies = [exp for exp in all_exps if not exp['is_monthly']]
        weekly = min(weeklies, key=lambda x: abs(x['dte'] - weekly_dte)) if weeklies else None

        # Find nearest monthly to target DTE
        monthlies = [exp for exp in all_exps if exp['is_monthly']]
        monthly = min(monthlies, key=lambda x: abs(x['dte'] - monthly_dte)) if monthlies else None

        weekly_advantages = [
            "Higher theta decay (faster time value erosion)",
            "More frequent premium collection (4x per month vs 1x)",
            "Better assignment control (shorter duration)",
            "Can adjust strikes more frequently"
        ]

        monthly_advantages = [
            "Lower trading costs (fewer transactions)",
            "Less time intensive (fewer decisions)",
            "Higher absolute premium per trade",
            "More time for stock to recover if assigned"
        ]

        return {
            "weekly": weekly,
            "monthly": monthly,
            "weekly_advantages": weekly_advantages,
            "monthly_advantages": monthly_advantages,
            "annual_opportunities": {
                "weekly": 52,  # Every Friday
                "monthly": 12  # 12 months
            }
        }

    def clear_cache(self):
        """Clear expiration calendar cache"""
        self.cache.clear()
        logger.info("Weekly scanner cache cleared")
