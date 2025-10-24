"""IB Connection Manager with graceful fallback"""

from typing import Optional, Tuple
import logging

try:
    from ib_insync import IB
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False

from .ib_config import IBConfig

logger = logging.getLogger(__name__)


class IBManager:
    """Manages Interactive Brokers connection with graceful degradation"""

    def __init__(self, config: IBConfig):
        self.config = config
        self.ib: Optional[IB] = None
        self.connected = False

        if not IB_AVAILABLE:
            logger.warning("ib_insync not installed - IB features disabled")

    def connect(self) -> Tuple[bool, str]:
        """
        Connect to IB Gateway or TWS

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not IB_AVAILABLE:
            return False, "ib_insync package not installed"

        try:
            self.ib = IB()
            self.ib.connect(
                host=self.config.host,
                port=self.config.port,
                clientId=self.config.client_id,
                readonly=True,  # Read-only for screening
                account=self.config.account if self.config.account else None
            )

            self.connected = True
            account_type = "Paper" if self.config.use_paper else "Live"
            return True, f"Connected to IB ({account_type})"

        except Exception as e:
            self.connected = False
            logger.error(f"IB connection failed: {e}")
            return False, f"Connection failed: {str(e)}"

    def disconnect(self):
        """Disconnect from IB"""
        if self.connected and self.ib:
            try:
                self.ib.disconnect()
                self.connected = False
                logger.info("Disconnected from IB")
            except Exception as e:
                logger.error(f"Disconnect error: {e}")

    def is_connected(self) -> bool:
        """Check if connection is active"""
        if not IB_AVAILABLE:
            return False
        return self.connected and self.ib and self.ib.isConnected()

    def get_connection(self) -> Optional[IB]:
        """
        Get IB connection object

        Returns:
            IB connection or None if not connected
        """
        if not self.is_connected():
            success, msg = self.connect()
            if not success:
                logger.warning(f"Auto-connect failed: {msg}")
                return None

        return self.ib

    def reconnect(self) -> Tuple[bool, str]:
        """Reconnect to IB"""
        self.disconnect()
        return self.connect()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
