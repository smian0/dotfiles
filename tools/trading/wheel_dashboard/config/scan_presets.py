"""
Curated Scan Presets for Different Wheel Strategy Risk Profiles

Each preset is optimized for specific trading goals:
- Conservative: Maximize safety, accept lower premiums
- Balanced: Mix of stability and premium income
- Aggressive: Maximize premiums, accept higher risk
"""

from typing import Dict, List


class ScanPresets:
    """Predefined ticker lists and settings for different wheel strategies"""

    PRESETS: Dict[str, Dict] = {
        # Conservative - Stable Blue Chips
        'conservative_wheel': {
            'name': '🛡️ Conservative Wheel',
            'description': 'Stable dividend aristocrats with low volatility',
            'risk_profile': 'LOW',
            'expected_premium': '1-2% monthly',
            'beta_range': '0.5-0.8',
            'tickers': [
                # Consumer Defensive
                'WMT', 'PG', 'KO', 'PEP', 'COST', 'TGT', 'CL', 'CLX',
                # Healthcare Stable
                'JNJ', 'ABBV', 'MRK', 'BMY', 'LLY',
                # Utilities
                'NEE', 'DUK', 'SO', 'D', 'AEP',
                # Telecom
                'VZ', 'T',
                # Industrials (Stable)
                'MMM', 'HON', 'UPS', 'FDX'
            ],
            'settings': {
                'min_discovery_score': 50,
                'signals_required': 1,
                'prefer_small_caps': False,
                'prefer_low_analyst_coverage': False
            }
        },

        # Mega Cap Tech - FAANG + Microsoft
        'mega_cap_tech': {
            'name': '📱 Mega Cap Tech',
            'description': 'FAANG + MSFT - Tech stability with decent premiums',
            'risk_profile': 'MEDIUM',
            'expected_premium': '1.5-3% monthly',
            'beta_range': '0.9-1.3',
            'tickers': [
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NFLX',
                # Other mega caps
                'NVDA', 'TSLA', 'V', 'MA', 'PYPL',
                # Stable tech
                'CSCO', 'ORCL', 'IBM', 'INTC', 'QCOM'
            ],
            'settings': {
                'min_discovery_score': 45,
                'signals_required': 1,
                'prefer_small_caps': False,
                'prefer_low_analyst_coverage': False
            }
        },

        # High Premium Tech
        'high_premium_tech': {
            'name': '⚡ High Premium Tech',
            'description': 'AI, semiconductors, cloud - High IV, high premiums',
            'risk_profile': 'HIGH',
            'expected_premium': '3-5% monthly',
            'beta_range': '1.5-2.5',
            'tickers': [
                # AI Pure Plays
                'NVDA', 'AMD', 'PLTR', 'AI', 'SNOW', 'NET', 'DDOG', 'CRWD',
                # Cloud/SaaS
                'CRM', 'NOW', 'WDAY', 'PANW', 'ZS', 'OKTA', 'DDOG',
                # Semiconductors
                'AVGO', 'QCOM', 'MU', 'LRCX', 'AMAT', 'KLAC', 'MCHP', 'ADI',
                # Cyber Security
                'FTNT', 'S', 'CRWD', 'ZS'
            ],
            'settings': {
                'min_discovery_score': 40,
                'signals_required': 1,
                'prefer_small_caps': False,
                'prefer_low_analyst_coverage': False
            }
        },

        # Quantum Computing
        'quantum_computing': {
            'name': '🔬 Quantum Computing',
            'description': 'Emerging quantum tech - Extreme volatility, huge premiums',
            'risk_profile': 'EXTREME',
            'expected_premium': '5-10% monthly',
            'beta_range': '2.0-3.5',
            'tickers': [
                # Pure play quantum
                'IONQ', 'RGTI', 'QUBT',
                # Quantum-adjacent
                'IBM', 'GOOGL', 'MSFT', 'AMZN',  # Have quantum divisions
                # Quantum enabling tech
                'NVDA', 'AMD'  # Supply chips for quantum research
            ],
            'settings': {
                'min_discovery_score': 35,
                'signals_required': 1,
                'prefer_small_caps': True,
                'prefer_low_analyst_coverage': True
            }
        },

        # Biotech Volatility
        'biotech_volatility': {
            'name': '🧬 Biotech High Vol',
            'description': 'Gene editing, pharma - Binary events, huge moves',
            'risk_profile': 'EXTREME',
            'expected_premium': '4-8% monthly',
            'beta_range': '1.8-3.0',
            'tickers': [
                # Gene Editing (CRISPR)
                'CRSP', 'EDIT', 'NTLA', 'BEAM',
                # Vaccine/Immunotherapy
                'MRNA', 'BNTX', 'NVAX',
                # Oncology
                'SGEN', 'EXEL', 'VRTX', 'REGN',
                # Emerging Biotech
                'ARKG'  # ETF for diversification
            ],
            'settings': {
                'min_discovery_score': 35,
                'signals_required': 1,
                'prefer_small_caps': True,
                'prefer_low_analyst_coverage': True
            }
        },

        # Clean Energy
        'clean_energy': {
            'name': '🔋 Clean Energy',
            'description': 'Solar, EV infrastructure - Policy-driven volatility',
            'risk_profile': 'HIGH',
            'expected_premium': '3-6% monthly',
            'beta_range': '1.5-2.5',
            'tickers': [
                # Solar
                'ENPH', 'SEDG', 'FSLR', 'RUN', 'NOVA',
                # EVs
                'TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV',
                # Charging Infrastructure
                'CHPT', 'BLNK', 'EVGO',
                # Batteries
                'ALB', 'LAC', 'MP'
            ],
            'settings': {
                'min_discovery_score': 35,
                'signals_required': 1,
                'prefer_small_caps': False,
                'prefer_low_analyst_coverage': False
            }
        },

        # Financial Tech
        'fintech_volatility': {
            'name': '💰 Fintech Volatility',
            'description': 'Digital finance, crypto exposure - Regulatory risk',
            'risk_profile': 'HIGH',
            'expected_premium': '4-7% monthly',
            'beta_range': '1.8-2.8',
            'tickers': [
                # Payments
                'SQ', 'PYPL', 'AFRM', 'SOFI',
                # Crypto Exposure
                'COIN', 'MSTR', 'RIOT', 'MARA',
                # Lending Tech
                'UPST', 'LC', 'SOFI',
                # Trading Platforms
                'HOOD'
            ],
            'settings': {
                'min_discovery_score': 35,
                'signals_required': 1,
                'prefer_small_caps': False,
                'prefer_low_analyst_coverage': False
            }
        },

        # Industrial Cyclicals
        'industrial_cyclicals': {
            'name': '🏭 Industrial Cyclicals',
            'description': 'Economy-linked - Volatility during macro changes',
            'risk_profile': 'MEDIUM',
            'expected_premium': '2-4% monthly',
            'beta_range': '1.2-1.8',
            'tickers': [
                # Heavy Equipment
                'CAT', 'DE', 'CMI',
                # Aerospace
                'BA', 'GE', 'RTX', 'LMT', 'NOC',
                # Industrials
                'HON', 'MMM', 'EMR', 'ITW',
                # Shipping/Logistics
                'UPS', 'FDX', 'XPO'
            ],
            'settings': {
                'min_discovery_score': 45,
                'signals_required': 1,
                'prefer_small_caps': False,
                'prefer_low_analyst_coverage': False
            }
        },

        # Dividend Aristocrats
        'dividend_aristocrats': {
            'name': '👑 Dividend Aristocrats',
            'description': '25+ years of dividend growth - Ultra safe',
            'risk_profile': 'VERY LOW',
            'expected_premium': '0.8-1.5% monthly',
            'beta_range': '0.4-0.7',
            'tickers': [
                # Classic aristocrats
                'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'TGT', 'LOW', 'HD',
                'MMM', 'CAT', 'GD', 'ITW', 'SWK', 'TROW',
                'BEN', 'AFL', 'ADP', 'CB', 'TRV',
                # REITs (high dividend)
                'O', 'SPG', 'VTR'
            ],
            'settings': {
                'min_discovery_score': 55,
                'signals_required': 1,
                'prefer_small_caps': False,
                'prefer_low_analyst_coverage': False
            }
        },

        # Earnings Season Special
        'earnings_season': {
            'name': '📊 Earnings Season Plays',
            'description': 'High IV around earnings - Premium spikes',
            'risk_profile': 'MEDIUM-HIGH',
            'expected_premium': '2-5% monthly',
            'beta_range': '1.0-2.0',
            'tickers': [
                # These are placeholders - would be populated based on upcoming earnings
                # For now, include stocks with quarterly options
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
                'NFLX', 'AMD', 'CRM', 'ADBE', 'SNOW', 'PLTR'
            ],
            'settings': {
                'min_discovery_score': 40,
                'signals_required': 2,  # Want multiple signals for earnings plays
                'prefer_small_caps': False,
                'prefer_low_analyst_coverage': False
            }
        }
    }

    @classmethod
    def get_preset(cls, preset_key: str) -> Dict:
        """Get a specific preset by key"""
        return cls.PRESETS.get(preset_key, None)

    @classmethod
    def list_presets(cls) -> List[Dict]:
        """Get list of all presets with metadata"""
        return [
            {
                'key': key,
                'name': preset['name'],
                'description': preset['description'],
                'risk_profile': preset['risk_profile'],
                'expected_premium': preset['expected_premium'],
                'ticker_count': len(preset['tickers'])
            }
            for key, preset in cls.PRESETS.items()
        ]

    @classmethod
    def get_preset_tickers(cls, preset_key: str) -> List[str]:
        """Get just the ticker list for a preset"""
        preset = cls.get_preset(preset_key)
        return preset['tickers'] if preset else []

    @classmethod
    def get_preset_settings(cls, preset_key: str) -> Dict:
        """Get scanner settings for a preset"""
        preset = cls.get_preset(preset_key)
        return preset['settings'] if preset else {}


# Quick access for common presets
CONSERVATIVE_TICKERS = ScanPresets.get_preset_tickers('conservative_wheel')
HIGH_VOL_TICKERS = ScanPresets.get_preset_tickers('high_premium_tech')
QUANTUM_TICKERS = ScanPresets.get_preset_tickers('quantum_computing')
BIOTECH_TICKERS = ScanPresets.get_preset_tickers('biotech_volatility')
