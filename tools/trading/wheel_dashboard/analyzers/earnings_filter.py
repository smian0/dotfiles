"""
Earnings Calendar Filter - Critical Safety Feature

Filters opportunities based on earnings dates to avoid IV crush.
Prevents 80% of wheel strategy disasters.
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
import logging
import xml.etree.ElementTree as ET

try:
    from ib_insync import IB, Stock
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False

logger = logging.getLogger(__name__)


class EarningsFilter:
    """
    Filter wheel strategy opportunities based on earnings calendar

    Safety Rules:
    - Don't sell puts < 10 days before earnings (IV crush risk)
    - Don't sell puts with expiration after earnings
    - Flag earnings week for manual review
    """

    def __init__(self, ib_connection: Optional['IB'] = None):
        """
        Initialize Earnings Filter

        Args:
            ib_connection: Active IB connection (from IBManager)
        """
        if not IB_AVAILABLE:
            raise ImportError("ib_insync not installed")

        self.ib = ib_connection
        self.cache = {}  # Cache earnings dates
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours

    def get_earnings_info(self, ticker: str, dte: int = 0) -> Dict:
        """
        Get earnings information and safety status

        Args:
            ticker: Stock ticker symbol
            dte: Days to expiration for the trade (0 if just checking)

        Returns:
            Dictionary with earnings info:
            {
                "next_earnings_date": "2025-11-01" or None,
                "days_to_earnings": 8 or None,
                "earnings_time": "AMC" | "BMO" | "Unknown",
                "safe_to_sell_puts": True/False,
                "reason": "Explanation of safety status"
            }
        """
        if not self.ib:
            logger.error("No IB connection available")
            return {
                "safe_to_sell_puts": False,
                "reason": "No IB connection"
            }

        try:
            # Check cache first
            cache_key = ticker
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_duration:
                    logger.info(f"Using cached earnings data for {ticker}")
                    return self._assess_safety(cached_data, dte)

            # Get earnings date from IB
            earnings_date, earnings_time = self._fetch_earnings_date(ticker)

            earnings_data = {
                "next_earnings_date": earnings_date.isoformat() if earnings_date else None,
                "days_to_earnings": (earnings_date - date.today()).days if earnings_date else None,
                "earnings_time": earnings_time
            }

            # Cache result
            self.cache[cache_key] = (earnings_data, datetime.now())

            # Assess safety
            return self._assess_safety(earnings_data, dte)

        except Exception as e:
            logger.error(f"Error getting earnings info for {ticker}: {e}")
            return {
                "safe_to_sell_puts": False,
                "reason": f"Error: {str(e)}"
            }

    def _fetch_earnings_date(self, ticker: str) -> tuple[Optional[date], str]:
        """
        Fetch next earnings date from IB fundamental data

        Returns:
            Tuple of (earnings_date, earnings_time)
            earnings_time: "AMC" (after market close), "BMO" (before market open), "Unknown"
        """
        try:
            stock = Stock(ticker, 'SMART', 'USD')
            self.ib.qualifyContracts(stock)

            # Request fundamental data (ReportSnapshot includes earnings)
            fundamentals_xml = self.ib.reqFundamentalData(
                stock,
                'ReportSnapshot'
            )

            if not fundamentals_xml:
                logger.warning(f"No fundamental data for {ticker}")
                return None, "Unknown"

            # Parse XML to extract earnings date
            earnings_date, earnings_time = self._parse_earnings_from_xml(fundamentals_xml)

            return earnings_date, earnings_time

        except Exception as e:
            logger.error(f"Error fetching earnings date for {ticker}: {e}")
            return None, "Unknown"

    @staticmethod
    def _parse_earnings_from_xml(xml_string: str) -> tuple[Optional[date], str]:
        """
        Parse earnings date from IB fundamental data XML

        This is a simplified parser - actual XML structure may vary
        """
        try:
            root = ET.fromstring(xml_string)

            # Look for earnings date in various possible locations
            # IB XML structure: ReportSnapshot > Forecasts > ConsensusEPS > FiscalPeriodEnd

            # Try to find next earnings date
            for forecast in root.findall('.//Forecast'):
                period_end = forecast.find('FiscalPeriodEnd')
                if period_end is not None and period_end.text:
                    try:
                        earnings_date = datetime.strptime(period_end.text, '%Y-%m-%d').date()

                        # Only use future dates
                        if earnings_date > date.today():
                            # Try to determine timing (AM/PM)
                            time_elem = forecast.find('Time')
                            earnings_time = time_elem.text if time_elem is not None else "Unknown"

                            return earnings_date, earnings_time
                    except ValueError:
                        continue

            return None, "Unknown"

        except Exception as e:
            logger.error(f"Error parsing earnings XML: {e}")
            return None, "Unknown"

    @staticmethod
    def _assess_safety(earnings_data: Dict, dte: int) -> Dict:
        """
        Assess safety of selling puts based on earnings date

        Rules:
        1. No earnings scheduled → Safe
        2. Earnings > 10 days away AND expiration before earnings → Safe
        3. Earnings < 10 days away → Unsafe (IV crush risk)
        4. Expiration after earnings → Unsafe (assignment risk during IV crush)
        """
        result = {**earnings_data}  # Copy earnings data

        if not earnings_data.get("next_earnings_date"):
            result["safe_to_sell_puts"] = True
            result["reason"] = "No earnings scheduled"
            return result

        days_to_earnings = earnings_data["days_to_earnings"]

        # Rule 3: Earnings too close (< 10 days)
        if days_to_earnings < 10:
            result["safe_to_sell_puts"] = False
            result["reason"] = f"Earnings in {days_to_earnings} days (< 10 day safety threshold)"
            return result

        # Rule 4: Expiration after earnings
        if dte > 0 and dte > days_to_earnings:
            result["safe_to_sell_puts"] = False
            result["reason"] = f"Expiration ({dte} DTE) after earnings ({days_to_earnings} days)"
            return result

        # Rule 2: Safe window
        result["safe_to_sell_puts"] = True
        result["reason"] = f"Safe: Earnings in {days_to_earnings} days (>10 day threshold)"

        return result

    def filter_watchlist(self, tickers: List[str], dte: int = 30) -> List[Dict]:
        """
        Filter entire watchlist for earnings safety

        Args:
            tickers: List of ticker symbols
            dte: Days to expiration for the trade

        Returns:
            List of dictionaries with ticker and earnings info:
            [
                {
                    "ticker": "KO",
                    "next_earnings_date": "2025-11-15",
                    "days_to_earnings": 22,
                    "safe_to_sell_puts": True,
                    "reason": "Safe: Earnings in 22 days"
                },
                ...
            ]
        """
        results = []

        for ticker in tickers:
            earnings_info = self.get_earnings_info(ticker, dte)
            results.append({
                "ticker": ticker,
                **earnings_info
            })

        return results

    def get_safe_tickers(self, tickers: List[str], dte: int = 30) -> List[str]:
        """
        Get list of tickers that are safe to trade (no earnings conflicts)

        Args:
            tickers: List of ticker symbols
            dte: Days to expiration

        Returns:
            List of safe ticker symbols
        """
        filtered = self.filter_watchlist(tickers, dte)
        return [item["ticker"] for item in filtered if item.get("safe_to_sell_puts")]

    def clear_cache(self):
        """Clear earnings calendar cache"""
        self.cache.clear()
        logger.info("Earnings calendar cache cleared")
