"""IB Configuration Management"""

from dataclasses import dataclass
import os

@dataclass
class IBConfig:
    """Interactive Brokers connection configuration"""

    # Connection settings
    host: str = '127.0.0.1'
    port: int = 7497  # TWS paper trading port (7496 for live)
    client_id: int = 1

    # Account settings
    account: str = ''  # Paper trading account
    use_paper: bool = True

    # Data settings
    iv_history_days: int = 252  # 1 year trading days
    cache_ttl: int = 300  # 5 minutes

    # Screening thresholds
    min_iv_rank: float = 50.0
    earnings_safety_days: int = 10
    min_weekly_dte: int = 7
    max_weekly_dte: int = 21

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv('IB_HOST', '127.0.0.1'),
            port=int(os.getenv('IB_PORT', 7497)),
            client_id=int(os.getenv('IB_CLIENT_ID', 1)),
            account=os.getenv('IB_ACCOUNT', ''),
            use_paper=os.getenv('IB_USE_PAPER', 'true').lower() == 'true',
            min_iv_rank=float(os.getenv('MIN_IV_RANK', 50.0)),
            earnings_safety_days=int(os.getenv('EARNINGS_SAFETY_DAYS', 10))
        )

    def get_connection_string(self) -> str:
        """Get human-readable connection string"""
        account_type = "Paper" if self.use_paper else "LIVE"
        return f"{self.host}:{self.port} ({account_type})"


# Port reference for IB connections
IB_PORTS = {
    'tws_paper': 7497,
    'tws_live': 7496,
    'gateway_paper': 4002,
    'gateway_live': 4001
}
