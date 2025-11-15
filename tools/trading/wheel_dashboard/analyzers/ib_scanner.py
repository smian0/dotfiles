"""
IB Gateway Scanner Integration
Professional-grade options flow scanning using Interactive Brokers API

Provides 762 scan codes including:
- High IV stocks (HIGH_OPT_IMP_VOLAT)
- Unusual options volume (OPT_VOLUME_MOST_ACTIVE)
- Institutional flow (TOP_STOCK_BUY_IMBALANCE_ADV_RATIO)
- Put/Call ratio extremes
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class IBScannerConfig:
    """Configuration for IB Gateway scanner"""
    host: str = '127.0.0.1'
    port: int = 4001  # IB Gateway port (TWS uses 7497)
    client_id: int = 1
    timeout: int = 30


class IBScanner:
    """
    Interactive Brokers market scanner for options flow detection

    Requires:
    - IB Gateway or TWS running
    - ib_insync library installed
    - Valid IB account (paper trading OK)
    """

    def __init__(self, config: Optional[IBScannerConfig] = None):
        self.config = config or IBScannerConfig()
        self.ib = None
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to IB Gateway/TWS

        Returns:
            bool: True if connected successfully
        """
        try:
            from ib_insync import IB

            self.ib = IB()
            self.ib.connect(
                self.config.host,
                self.config.port,
                clientId=self.config.client_id,
                timeout=self.config.timeout
            )
            self.connected = True
            logger.info("✅ Connected to IB Gateway")
            return True

        except ImportError:
            logger.warning("⚠️ ib_insync not installed - install with: pip install ib_insync")
            return False
        except Exception as e:
            logger.warning(f"⚠️ IB Gateway connection failed: {e}")
            logger.info("💡 Make sure IB Gateway/TWS is running")
            return False

    def disconnect(self):
        """Disconnect from IB Gateway"""
        if self.ib and self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IB Gateway")

    def get_high_iv_stocks(self, max_results: int = 50) -> List[str]:
        """
        Scan for stocks with high implied volatility (best for premium collection)

        Args:
            max_results: Maximum number of results (default: 50)

        Returns:
            List of ticker symbols
        """
        if not self.connected:
            logger.warning("Not connected to IB Gateway")
            return []

        try:
            from ib_insync import ScannerSubscription, TagValue

            # High IV scanner
            sub = ScannerSubscription(
                instrument='STK',
                locationCode='STK.US.MAJOR',
                scanCode='HIGH_OPT_IMP_VOLAT'  # Built-in high IV scanner
            )

            # Add filters for wheel strategy
            filters = [
                TagValue("priceAbove", "10"),         # Min price $10
                TagValue("priceBelow", "500"),        # Max price $500
                TagValue("avgVolumeAbove", "500000"), # High liquidity
                TagValue("optVolumeAbove", "5000")    # Options liquidity
            ]

            results = self.ib.reqScannerData(sub, [], filters)
            tickers = [r.contractDetails.contract.symbol for r in results[:max_results]]

            logger.info(f"📊 IB scanner found {len(tickers)} high IV stocks")
            return tickers

        except Exception as e:
            logger.error(f"IB scanner error: {e}")
            return []

    def get_unusual_options_volume(self, max_results: int = 50) -> List[str]:
        """
        Scan for stocks with unusual options volume

        Args:
            max_results: Maximum number of results

        Returns:
            List of ticker symbols
        """
        if not self.connected:
            logger.warning("Not connected to IB Gateway")
            return []

        try:
            from ib_insync import ScannerSubscription, TagValue

            sub = ScannerSubscription(
                instrument='STK',
                locationCode='STK.US.MAJOR',
                scanCode='OPT_VOLUME_MOST_ACTIVE'  # Unusual volume
            )

            filters = [
                TagValue("priceAbove", "10"),
                TagValue("avgVolumeAbove", "500000")
            ]

            results = self.ib.reqScannerData(sub, [], filters)
            tickers = [r.contractDetails.contract.symbol for r in results[:max_results]]

            logger.info(f"⚡ IB scanner found {len(tickers)} stocks with unusual options volume")
            return tickers

        except Exception as e:
            logger.error(f"IB scanner error: {e}")
            return []

    def get_institutional_flow(self, max_results: int = 50, flow_type: str = 'buy') -> List[str]:
        """
        Scan for stocks with institutional buying or selling pressure

        Args:
            max_results: Maximum number of results
            flow_type: 'buy' or 'sell'

        Returns:
            List of ticker symbols
        """
        if not self.connected:
            logger.warning("Not connected to IB Gateway")
            return []

        try:
            from ib_insync import ScannerSubscription

            scan_code = (
                'TOP_STOCK_BUY_IMBALANCE_ADV_RATIO' if flow_type == 'buy'
                else 'TOP_STOCK_SELL_IMBALANCE_ADV_RATIO'
            )

            sub = ScannerSubscription(
                instrument='STK',
                locationCode='STK.US.MAJOR',
                scanCode=scan_code
            )

            results = self.ib.reqScannerData(sub)
            tickers = [r.contractDetails.contract.symbol for r in results[:max_results]]

            logger.info(f"🏢 IB scanner found {len(tickers)} stocks with institutional {flow_type} flow")
            return tickers

        except Exception as e:
            logger.error(f"IB scanner error: {e}")
            return []

    def get_wheel_candidates(self, max_results: int = 100) -> List[str]:
        """
        Get comprehensive list of wheel strategy candidates using multiple IB scanners

        Combines:
        - High IV stocks
        - Unusual options volume
        - Institutional buying pressure

        Returns:
            List of unique ticker symbols
        """
        if not self.connected:
            logger.warning("Not connected to IB Gateway - attempting to connect...")
            if not self.connect():
                return []

        candidates = set()

        # Scan 1: High IV (best for premium collection)
        high_iv = self.get_high_iv_stocks(max_results=50)
        candidates.update(high_iv)

        # Scan 2: Unusual options volume
        unusual_volume = self.get_unusual_options_volume(max_results=50)
        candidates.update(unusual_volume)

        # Scan 3: Institutional buying (quality signal)
        institutional = self.get_institutional_flow(max_results=30, flow_type='buy')
        candidates.update(institutional)

        result = list(candidates)[:max_results]
        logger.info(f"🎯 Combined IB scans found {len(result)} unique wheel candidates")

        return result


def get_ib_scanner_tickers(scanner_type: str = 'wheel', max_results: int = 100) -> List[str]:
    """
    Convenience function to get tickers from IB Gateway scanner

    Args:
        scanner_type: 'wheel', 'high_iv', 'unusual_volume', or 'institutional'
        max_results: Maximum number of results

    Returns:
        List of ticker symbols (empty list if IB Gateway not available)
    """
    scanner = IBScanner()

    if not scanner.connect():
        logger.info("📊 IB Gateway not available - use scan presets or yfinance fallback")
        return []

    try:
        if scanner_type == 'wheel':
            return scanner.get_wheel_candidates(max_results)
        elif scanner_type == 'high_iv':
            return scanner.get_high_iv_stocks(max_results)
        elif scanner_type == 'unusual_volume':
            return scanner.get_unusual_options_volume(max_results)
        elif scanner_type == 'institutional':
            return scanner.get_institutional_flow(max_results, flow_type='buy')
        else:
            logger.warning(f"Unknown scanner type: {scanner_type}")
            return []
    finally:
        scanner.disconnect()


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print("🧪 Testing IB Gateway scanner integration...")
    print("=" * 70)

    # Test connection
    scanner = IBScanner()
    if scanner.connect():
        print("✅ Connected to IB Gateway")

        # Test high IV scan
        print("\n1️⃣ Testing high IV scanner...")
        high_iv = scanner.get_high_iv_stocks(max_results=10)
        print(f"   Found {len(high_iv)} stocks: {high_iv[:5]}")

        # Test unusual volume scan
        print("\n2️⃣ Testing unusual volume scanner...")
        unusual = scanner.get_unusual_options_volume(max_results=10)
        print(f"   Found {len(unusual)} stocks: {unusual[:5]}")

        # Test wheel candidates
        print("\n3️⃣ Testing combined wheel scanner...")
        candidates = scanner.get_wheel_candidates(max_results=20)
        print(f"   Found {len(candidates)} candidates: {candidates[:10]}")

        scanner.disconnect()
        print("\n✅ All IB scanner tests passed!")
    else:
        print("❌ IB Gateway not available")
        print("💡 To use IB scanners:")
        print("   1. Install: pip install ib_insync")
        print("   2. Start IB Gateway or TWS")
        print("   3. Enable API connections in settings")
