"""
Market-Wide Discovery Scanner

Automatically scans thousands of stocks to find hidden gem opportunities based on:
- Unusual options volume vs historical baseline
- IV rank surges and volatility explosions
- Large block trades and institutional flow
- Smart money indicators (aggressive buying at ask)
- Price action + options activity divergence
- Undervalued opportunities in emerging sectors

Designed to surface opportunities you wouldn't find manually.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from ib_insync import IB, Stock, Option
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import data quality validator for institutional-grade metrics
from analyzers.data_quality_fixes import DataQualityValidator


@dataclass
class DiscoverySignal:
    """Represents an unusual activity signal"""
    ticker: str
    signal_type: str  # 'unusual_volume', 'iv_surge', 'block_trade', 'sweep', 'oi_surge'
    severity: str  # 'low', 'medium', 'high', 'extreme'
    score: float  # 0-100
    details: Dict
    timestamp: datetime


@dataclass
class HiddenGem:
    """A discovered opportunity with aggregated signals"""
    ticker: str
    company_name: str
    price: float
    market_cap: float
    sector: str

    # Discovery metrics
    discovery_score: float  # 0-100 composite score
    signals: List[DiscoverySignal]

    # Options metrics
    iv_percentile: float
    iv_change_pct: float
    unusual_volume_ratio: float  # Today's volume / 30-day avg
    put_call_ratio: float
    oi_change_pct: float

    # Smart money indicators
    block_trades_count: int
    sweep_count: int
    aggressive_buy_pct: float

    # Fundamentals (for context)
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    analyst_coverage: int  # Number of analysts (low = hidden)

    # News catalysts
    recent_news: List[Dict]  # Last 7 days of news with sentiment
    news_sentiment: str  # 'positive', 'negative', 'neutral', 'mixed'
    catalyst_score: float  # 0-100, boost for positive catalysts

    # PRIORITY 1: Advanced options metrics (IV/HV analysis)
    iv_hv_ratio: float  # IV/HV ratio (>1.5 = premium selling opportunity)
    hv_30d: float  # 30-day historical volatility
    iv_skew: float  # Put IV - Call IV (sentiment indicator)
    atm_call_iv: float  # ATM strike call IV
    atm_put_iv: float  # ATM strike put IV
    vol_oi_ratio_calls: float  # Call volume/OI ratio
    vol_oi_ratio_puts: float  # Put volume/OI ratio
    iv_hv_interpretation: str  # Trading signal interpretation

    # PRIORITY 2: Fundamental quality metrics
    quality_score: float  # 0-100 composite quality score
    short_interest_pct: float  # % of float (>20% = squeeze candidate)
    days_to_cover: float  # Short squeeze timing
    roe: float  # Return on equity (>15% = quality)
    profit_margin: float  # Profitability
    debt_to_equity: float  # Financial health (<1.0 = conservative)
    free_cash_flow: float  # Real earnings (in billions)
    insider_ownership_pct: float  # Insider skin in the game
    institutional_pct: float  # Institutional backing
    analyst_target_upside: float  # % to mean price target

    # PRIORITY 3: Insider trading sentiment (EDGAR/yfinance)
    insider_buys_90d: int  # Number of insider buys in last 90 days
    insider_sells_90d: int  # Number of insider sells in last 90 days
    insider_sentiment: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    insider_confidence_boost: float  # -15 to +15 discovery score boost

    # Technical Analysis (all indicators from yfinance/IB Gateway)
    technical_score: float  # 0-100 composite technical score
    rsi: Optional[float]  # Relative Strength Index (0-100)
    rsi_signal: str  # OVERSOLD, NEUTRAL, OVERBOUGHT
    macd_histogram: Optional[float]  # MACD histogram
    macd_signal: str  # BULLISH, BEARISH, NEUTRAL
    adx: Optional[float]  # Average Directional Index (trend strength)
    bb_position: Optional[float]  # Bollinger Band position (0-1)
    volume_ratio: Optional[float]  # Current volume vs 20-day avg
    rs_vs_spy: Optional[float]  # Relative strength vs SPY (>1 = outperforming)
    sma_20: Optional[float]  # 20-day SMA
    sma_50: Optional[float]  # 50-day SMA
    price_vs_sma50_pct: Optional[float]  # % above/below SMA 50
    entry_timing_signal: str  # Technical entry recommendation

    # Why it's a gem
    discovery_reasons: List[str]


class StockUniverse:
    """Manages different stock universes for scanning"""

    @staticmethod
    def get_sp500() -> List[str]:
        """Get S&P 500-like stocks using yfinance screener as primary scanner"""
        try:
            import yfinance as yf
            from yfinance import EquityQuery

            print("📊 Using yfinance screener for large cap stocks...")

            # Query for large cap, liquid stocks (S&P 500-equivalent criteria)
            query = EquityQuery('and', [
                EquityQuery('gt', ['intradaymarketcap', 10000000000]),  # Market cap > $10B
                EquityQuery('gt', ['avgdailyvol3m', 500000]),            # Volume > 500K
                EquityQuery('is-in', ['exchange', 'NYQ', 'NMS'])        # NYSE or NASDAQ
            ])

            screener = yf.Screener()
            screener.set_default_body(query)
            response = screener.response

            if response and 'quotes' in response:
                tickers = [quote['symbol'] for quote in response['quotes'][:500]]
                print(f"✅ yfinance screener found {len(tickers)} large cap stocks")
                return tickers
            else:
                print("⚠️ yfinance screener returned no results")
                return []

        except Exception as e:
            print(f"❌ yfinance screener error: {e}")
            # Fallback: Curated 100 large cap stocks (works with current yfinance version)
            print("🔄 Using curated large cap fallback list...")
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'V', 'UNH',
                'JNJ', 'WMT', 'JPM', 'MA', 'PG', 'HD', 'CVX', 'MRK', 'ABBV', 'KO',
                'PEP', 'COST', 'AVGO', 'TMO', 'MCD', 'ABT', 'DHR', 'VZ', 'CSCO', 'ACN',
                'CRM', 'ADBE', 'TXN', 'NEE', 'NKE', 'QCOM', 'ORCL', 'LIN', 'PM', 'AMD',
                'INTC', 'BA', 'DIS', 'IBM', 'GE', 'CAT', 'RTX', 'UPS', 'NOW', 'SBUX',
                'LOW', 'SPGI', 'BLK', 'GS', 'AXP', 'HON', 'BKNG', 'SYK', 'MDLZ', 'GILD',
                'CVS', 'USB', 'BMY', 'C', 'PLD', 'ISRG', 'DE', 'CB', 'AMT', 'MMC',
                'TJX', 'SO', 'BDX', 'CI', 'SCHW', 'MO', 'DUK', 'BSX', 'ZTS', 'ITW',
                'REGN', 'PNC', 'EOG', 'CL', 'APD', 'WM', 'SHW', 'TT', 'FIS', 'COP',
                'CME', 'NOC', 'HUM', 'EQIX', 'ICE', 'PSX', 'NSC', 'MCO', 'AON', 'GD'
            ]

    @staticmethod
    def get_russell2000() -> List[str]:
        """Get Russell 2000 tickers (small caps - more hidden gems)"""
        # TODO: Implement Russell 2000 fetch
        # For now, return empty - would need data source
        return []

    @staticmethod
    def get_nasdaq100() -> List[str]:
        """Get NASDAQ 100 stocks using yfinance screener"""
        try:
            import yfinance as yf
            from yfinance import EquityQuery

            print("📊 Using yfinance screener for NASDAQ stocks...")

            # Query for NASDAQ-listed tech/growth stocks
            query = EquityQuery('and', [
                EquityQuery('gt', ['intradaymarketcap', 5000000000]),   # Market cap > $5B
                EquityQuery('gt', ['avgdailyvol3m', 500000]),            # Volume > 500K
                EquityQuery('eq', ['exchange', 'NMS'])                   # NASDAQ only
            ])

            screener = yf.Screener()
            screener.set_default_body(query)
            response = screener.response

            if response and 'quotes' in response:
                tickers = [quote['symbol'] for quote in response['quotes'][:150]]
                print(f"✅ yfinance screener found {len(tickers)} NASDAQ stocks")
                return tickers
            else:
                print("⚠️ yfinance screener returned no results")
                return []

        except Exception as e:
            print(f"❌ yfinance screener error: {e}")
            # Fallback: Curated NASDAQ 100 stocks (works with current yfinance version)
            print("🔄 Using curated NASDAQ fallback list...")
            return [
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'COST',
                'ASML', 'PEP', 'AZN', 'TMUS', 'CSCO', 'ADBE', 'AMD', 'NFLX', 'INTC', 'CMCSA',
                'TXN', 'QCOM', 'INTU', 'AMGN', 'HON', 'AMAT', 'ARM', 'BKNG', 'ISRG', 'ADP',
                'VRTX', 'SBUX', 'GILD', 'ADI', 'MU', 'PANW', 'LRCX', 'REGN', 'MDLZ', 'MELI',
                'PDD', 'SNPS', 'CDNS', 'KLAC', 'PYPL', 'CRWD', 'MRVL', 'MAR', 'ABNB', 'CSX',
                'ORLY', 'FTNT', 'DASH', 'ADSK', 'WDAY', 'NXPI', 'MNST', 'ROP', 'PCAR', 'CEG',
                'CHTR', 'CPRT', 'PAYX', 'ROST', 'AEP', 'ODFL', 'FAST', 'KDP', 'EA', 'MCHP',
                'DXCM', 'VRSK', 'BKR', 'XEL', 'CTSH', 'GEHC', 'TEAM', 'EXC', 'KHC', 'LULU',
                'TTD', 'IDXX', 'CCEP', 'FANG', 'ZS', 'ON', 'CTAS', 'ANSS', 'CDW', 'WBD',
                'MDB', 'MRNA', 'BIIB', 'DDOG', 'GFS', 'ILMN', 'WBA', 'SMCI', 'ALGN', 'DLTR'
            ]

    @staticmethod
    def get_custom_universe(min_price: float = 5.0, max_price: float = 500.0,
                           min_volume: int = 100000) -> List[str]:
        """Get a custom filtered universe based on criteria"""
        # Start with S&P 500 + NASDAQ 100 as base
        base = list(set(StockUniverse.get_sp500() + StockUniverse.get_nasdaq100()))

        # Filter by price and volume (placeholder - would need real-time data)
        return base

    @staticmethod
    def get_high_iv_universe() -> List[str]:
        """Get stocks with historically high IV (better for premium selling)"""
        # Placeholder - would query options data
        return []


class MarketDiscoveryScanner:
    """
    Scans entire market for hidden gem opportunities

    Workflow:
    1. Load stock universe (500-2000 tickers)
    2. Quick filter: Remove stocks without options or low volume
    3. Fetch recent options activity for remaining stocks
    4. Calculate discovery signals (unusual volume, IV surges, etc.)
    5. Score and rank opportunities
    6. Return top N hidden gems
    """

    def __init__(self, ib: Optional[IB] = None):
        self.ib = ib
        self.use_ib = ib is not None
        self._cache = {}
        self._cache_ttl = timedelta(minutes=15)
        # Initialize data quality validator for institutional-grade metrics
        self.validator = DataQualityValidator()

    async def discover_gems(
        self,
        universe: str = 'sp500',  # 'sp500', 'nasdaq100', 'russell2000', 'custom'
        min_discovery_score: float = 60.0,
        max_results: int = 20,
        signals_required: int = 2,  # Minimum number of signals to qualify
        prefer_small_caps: bool = True,  # Favor under-the-radar stocks
        prefer_low_analyst_coverage: bool = True  # Favor less-followed stocks
    ) -> List[HiddenGem]:
        """
        Main discovery method - scans market for hidden gems

        Args:
            universe: Which stock universe to scan
            min_discovery_score: Minimum score to qualify as a gem
            max_results: Maximum number of results to return
            signals_required: Minimum unusual signals needed
            prefer_small_caps: Boost scores for smaller market caps
            prefer_low_analyst_coverage: Boost scores for less-followed stocks

        Returns:
            List of HiddenGem objects, sorted by discovery_score
        """
        print(f"🔍 Starting market-wide discovery scan...")
        print(f"📊 Universe: {universe.upper()}")

        # 1. Get stock universe
        tickers = self._get_universe(universe)
        print(f"📈 Scanning {len(tickers)} stocks...")

        # 2. Quick filter - remove unsuitable stocks
        filtered = await self._quick_filter(tickers)
        print(f"✅ {len(filtered)} stocks passed initial filter")

        # 3. Scan for signals (parallel processing)
        gems = await self._parallel_scan(
            filtered,
            min_discovery_score,
            signals_required,
            prefer_small_caps,
            prefer_low_analyst_coverage
        )

        # 4. Sort by discovery score and return top N
        gems.sort(key=lambda x: x.discovery_score, reverse=True)
        top_gems = gems[:max_results]

        print(f"💎 Found {len(top_gems)} hidden gems!")
        return top_gems

    def _get_universe(self, universe: str) -> List[str]:
        """Get the specified stock universe"""
        if universe == 'sp500':
            return StockUniverse.get_sp500()
        elif universe == 'nasdaq100':
            return StockUniverse.get_nasdaq100()
        elif universe == 'russell2000':
            return StockUniverse.get_russell2000()
        elif universe == 'custom':
            return StockUniverse.get_custom_universe()
        else:
            # Default to S&P 500
            return StockUniverse.get_sp500()

    async def _quick_filter(self, tickers: List[str]) -> List[str]:
        """
        Quick filter to remove unsuitable stocks before deep analysis

        Filters out:
        - Stocks with no options
        - Stocks with very low volume (< 100k shares/day)
        - Stocks outside price range ($5-$500)
        - Stocks with broken data
        """
        filtered = []

        # Use ThreadPoolExecutor for parallel yfinance calls
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ticker = {
                executor.submit(self._check_ticker_suitable, ticker): ticker
                for ticker in tickers
            }

            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    is_suitable = future.result()
                    if is_suitable:
                        filtered.append(ticker)
                except Exception as e:
                    print(f"Error checking {ticker}: {e}")
                    continue

        return filtered

    def _check_ticker_suitable(self, ticker: str) -> bool:
        """Check if ticker meets basic criteria for scanning"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Check price range
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not price or price < 5 or price > 500:
                return False

            # Check volume
            volume = info.get('volume') or info.get('regularMarketVolume')
            if not volume or volume < 100000:
                return False

            # Check if options exist
            try:
                exp_dates = stock.options
                if not exp_dates or len(exp_dates) == 0:
                    return False
            except:
                return False

            return True

        except Exception:
            return False

    async def _parallel_scan(
        self,
        tickers: List[str],
        min_score: float,
        signals_required: int,
        prefer_small_caps: bool,
        prefer_low_coverage: bool
    ) -> List[HiddenGem]:
        """Scan tickers in parallel for discovery signals"""
        gems = []

        # Use ThreadPoolExecutor for parallel scanning
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ticker = {
                executor.submit(
                    self._scan_single_ticker,
                    ticker,
                    prefer_small_caps,
                    prefer_low_coverage
                ): ticker
                for ticker in tickers
            }

            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    gem = future.result()
                    if gem and gem.discovery_score >= min_score and len(gem.signals) >= signals_required:
                        gems.append(gem)
                        print(f"  💎 {ticker}: Score {gem.discovery_score:.1f} ({len(gem.signals)} signals)")
                except Exception as e:
                    print(f"  ❌ {ticker}: {e}")
                    continue

        return gems

    def _scan_single_ticker(
        self,
        ticker: str,
        prefer_small_caps: bool,
        prefer_low_coverage: bool
    ) -> Optional[HiddenGem]:
        """
        Deep scan of a single ticker for discovery signals

        Returns HiddenGem if signals detected, None otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Get basic info
            price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            market_cap = info.get('marketCap', 0)
            company_name = info.get('shortName', ticker)
            sector = info.get('sector', 'Unknown')

            # Detect signals
            signals = self._detect_signals(stock, ticker)

            if not signals:
                return None

            # Calculate discovery score
            discovery_score = self._calculate_discovery_score(
                signals,
                market_cap,
                prefer_small_caps,
                prefer_low_coverage,
                info
            )

            # Get options metrics
            iv_percentile, iv_change = self._calculate_iv_metrics(stock)
            unusual_vol_ratio = self._calculate_unusual_volume(stock)
            put_call_ratio = self._calculate_put_call_ratio(stock)
            oi_change = self._calculate_oi_change(stock)

            # Smart money indicators
            block_trades = sum(1 for s in signals if s.signal_type == 'block_trade')
            sweeps = sum(1 for s in signals if s.signal_type == 'sweep')
            aggressive_buy = self._calculate_aggressive_buying(stock)

            # Discovery reasons
            reasons = self._generate_discovery_reasons(signals, info)

            # Fetch news and analyze sentiment
            recent_news = self._fetch_recent_news(stock, days=7)
            news_sentiment, catalyst_score, news_reasons = self._analyze_news_sentiment(recent_news)

            # Add news reasons to discovery reasons
            if news_reasons:
                reasons.extend(news_reasons)

            # Boost discovery score for positive catalysts
            if catalyst_score > 0:
                discovery_score = min(100, discovery_score + catalyst_score * 0.15)  # Max 15 point boost

            # PRIORITY 1: Get advanced options metrics (IV/HV analysis)
            try:
                advanced_opts = self.validator.get_advanced_options_metrics(stock)
            except Exception as e:
                # If fails, use defaults
                advanced_opts = {
                    'iv_hv_ratio': 0.0,
                    'hv_30d': 0.0,
                    'iv_skew': 0.0,
                    'atm_call_iv': 0.0,
                    'atm_put_iv': 0.0,
                    'vol_oi_ratio_calls': 0.0,
                    'vol_oi_ratio_puts': 0.0,
                    'interpretation': 'N/A'
                }

            # PRIORITY 2: Get fundamental quality metrics
            try:
                quality_metrics = self.validator.get_fundamental_quality_metrics(stock)
            except Exception as e:
                # If fails, use defaults
                quality_metrics = {
                    'quality_score': 0.0,
                    'short_interest_pct': 0.0,
                    'days_to_cover': 0.0,
                    'roe': 0.0,
                    'profit_margin': 0.0,
                    'debt_to_equity': 0.0,
                    'free_cash_flow': 0.0,
                    'insider_ownership_pct': 0.0,
                    'institutional_pct': 0.0,
                    'analyst_target_upside': 0.0
                }

            # Add IV/HV discovery reasons
            if advanced_opts['iv_hv_ratio'] > 1.5:
                reasons.append(f"💰 IV/HV ratio {advanced_opts['iv_hv_ratio']:.2f} - Premium selling opportunity!")

            # Add quality-based discovery reasons
            if quality_metrics['quality_score'] > 60:
                reasons.append(f"⭐ High-quality company (score: {quality_metrics['quality_score']:.0f}/100)")
            if quality_metrics['roe'] > 15:
                reasons.append(f"📈 Strong ROE: {quality_metrics['roe']:.1f}%")

            # PRIORITY 3: Get insider sentiment
            try:
                insider_data = self.validator.get_insider_sentiment(stock)
            except Exception as e:
                # If fails, use defaults
                insider_data = {
                    'insider_buys_90d': 0,
                    'insider_sells_90d': 0,
                    'net_sentiment': 'NEUTRAL',
                    'confidence_boost': 0
                }

            # Add insider-based discovery reasons
            if insider_data['net_sentiment'] == 'BULLISH':
                reasons.append(f"👔 Insider buying: {insider_data['insider_buys_90d']} buys vs {insider_data['insider_sells_90d']} sells")
            elif insider_data['net_sentiment'] == 'BEARISH':
                reasons.append(f"⚠️ Insider selling: {insider_data['insider_sells_90d']} sells vs {insider_data['insider_buys_90d']} buys")

            # Apply insider confidence boost to discovery score
            if insider_data['confidence_boost'] != 0:
                discovery_score = min(100, max(0, discovery_score + insider_data['confidence_boost']))

            # TECHNICAL ANALYSIS: Calculate all technical indicators from yfinance data
            from analyzers.technical_indicators import InstitutionalTechnicalAnalyzer

            tech_analyzer = InstitutionalTechnicalAnalyzer()
            try:
                ta = tech_analyzer.analyze(ticker, include_spy_comparison=True)

                # Extract key technical metrics
                technical_score = ta.technical_score
                rsi = ta.rsi
                rsi_signal = ta.rsi_signal
                macd_histogram = ta.macd_histogram
                macd_signal = ta.macd_crossover if ta.macd_crossover else "NEUTRAL"
                adx = ta.adx
                bb_position = ta.bb_position
                volume_ratio = ta.volume_ratio
                rs_vs_spy = ta.rs_spy
                sma_20 = ta.sma_20
                sma_50 = ta.sma_50

                # Calculate % from SMA 50
                price_vs_sma50_pct = None
                if sma_50:
                    price_vs_sma50_pct = (price / sma_50 - 1) * 100

                # Entry timing signal
                entry_timing_signal = ta.entry_recommendation

                # Add technical reasons to discovery reasons
                if rsi and rsi < 40:
                    reasons.append(f"📉 RSI {rsi:.0f} - Oversold (good entry timing)")
                if rs_vs_spy and rs_vs_spy > 1.05:
                    reasons.append(f"🏛️ Outperforming SPY by {(rs_vs_spy-1)*100:.1f}% (institutional support)")
                if adx and adx < 25:
                    reasons.append(f"📊 ADX {adx:.0f} - Range-bound (ideal for wheel strategy)")

            except Exception as e:
                # If technical analysis fails, use defaults
                technical_score = 50
                rsi = None
                rsi_signal = "UNKNOWN"
                macd_histogram = None
                macd_signal = "UNKNOWN"
                adx = None
                bb_position = None
                volume_ratio = None
                rs_vs_spy = None
                sma_20 = None
                sma_50 = None
                price_vs_sma50_pct = None
                entry_timing_signal = "UNKNOWN"

            return HiddenGem(
                ticker=ticker,
                company_name=company_name,
                price=price,
                market_cap=market_cap,
                sector=sector,
                discovery_score=discovery_score,
                signals=signals,
                iv_percentile=iv_percentile,
                iv_change_pct=iv_change,
                unusual_volume_ratio=unusual_vol_ratio,
                put_call_ratio=put_call_ratio,
                oi_change_pct=oi_change,
                block_trades_count=block_trades,
                sweep_count=sweeps,
                aggressive_buy_pct=aggressive_buy,
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                analyst_coverage=info.get('numberOfAnalystOpinions', 0),
                recent_news=recent_news,
                news_sentiment=news_sentiment,
                catalyst_score=catalyst_score,
                # PRIORITY 1: Advanced options metrics
                iv_hv_ratio=advanced_opts['iv_hv_ratio'],
                hv_30d=advanced_opts['hv_30d'],
                iv_skew=advanced_opts['iv_skew'],
                atm_call_iv=advanced_opts['atm_call_iv'],
                atm_put_iv=advanced_opts['atm_put_iv'],
                vol_oi_ratio_calls=advanced_opts['vol_oi_ratio_calls'],
                vol_oi_ratio_puts=advanced_opts['vol_oi_ratio_puts'],
                iv_hv_interpretation=advanced_opts['interpretation'],
                # PRIORITY 2: Fundamental quality metrics
                quality_score=quality_metrics['quality_score'],
                short_interest_pct=quality_metrics['short_interest_pct'],
                days_to_cover=quality_metrics['days_to_cover'],
                roe=quality_metrics['roe'],
                profit_margin=quality_metrics['profit_margin'],
                debt_to_equity=quality_metrics['debt_to_equity'],
                free_cash_flow=quality_metrics['free_cash_flow'],
                insider_ownership_pct=quality_metrics['insider_ownership_pct'],
                institutional_pct=quality_metrics['institutional_pct'],
                analyst_target_upside=quality_metrics['analyst_target_upside'],
                # PRIORITY 3: Insider trading sentiment
                insider_buys_90d=insider_data['insider_buys_90d'],
                insider_sells_90d=insider_data['insider_sells_90d'],
                insider_sentiment=insider_data['net_sentiment'],
                insider_confidence_boost=insider_data['confidence_boost'],
                # Technical Analysis (from yfinance data)
                technical_score=technical_score,
                rsi=rsi,
                rsi_signal=rsi_signal,
                macd_histogram=macd_histogram,
                macd_signal=macd_signal,
                adx=adx,
                bb_position=bb_position,
                volume_ratio=volume_ratio,
                rs_vs_spy=rs_vs_spy,
                sma_20=sma_20,
                sma_50=sma_50,
                price_vs_sma50_pct=price_vs_sma50_pct,
                entry_timing_signal=entry_timing_signal,
                discovery_reasons=reasons
            )

        except Exception as e:
            raise Exception(f"Scan failed: {e}")

    def _detect_signals(self, stock: yf.Ticker, ticker: str) -> List[DiscoverySignal]:
        """Detect all unusual activity signals for a ticker"""
        signals = []

        # 1. Unusual Volume Signal
        vol_signal = self._detect_unusual_volume(stock, ticker)
        if vol_signal:
            signals.append(vol_signal)

        # 2. IV Surge Signal
        iv_signal = self._detect_iv_surge(stock, ticker)
        if iv_signal:
            signals.append(iv_signal)

        # 3. OI Surge Signal
        oi_signal = self._detect_oi_surge(stock, ticker)
        if oi_signal:
            signals.append(oi_signal)

        # 4. Put/Call Ratio Extreme
        pc_signal = self._detect_pc_ratio_extreme(stock, ticker)
        if pc_signal:
            signals.append(pc_signal)

        # Note: Block trades and sweeps require tick data (IB)
        # We'll add those when IB is connected

        return signals

    def _detect_unusual_volume(self, stock: yf.Ticker, ticker: str) -> Optional[DiscoverySignal]:
        """Detect unusual options volume vs historical average"""
        try:
            # Get recent options data
            exp_dates = stock.options
            if not exp_dates:
                return None

            # Use nearest expiration
            opt_chain = stock.option_chain(exp_dates[0])

            # Calculate total volume
            total_volume = (
                opt_chain.calls['volume'].sum() +
                opt_chain.puts['volume'].sum()
            )

            # Calculate average open interest as proxy for normal volume
            total_oi = (
                opt_chain.calls['openInterest'].sum() +
                opt_chain.puts['openInterest'].sum()
            )

            if total_oi == 0:
                return None

            # Volume/OI ratio > 1.0 indicates unusual activity
            vol_oi_ratio = total_volume / total_oi if total_oi > 0 else 0

            if vol_oi_ratio > 0.5:  # Significant activity
                severity = self._classify_severity(vol_oi_ratio, [0.5, 1.0, 2.0, 3.0])
                score = min(100, vol_oi_ratio * 30)

                return DiscoverySignal(
                    ticker=ticker,
                    signal_type='unusual_volume',
                    severity=severity,
                    score=score,
                    details={
                        'volume': int(total_volume),
                        'open_interest': int(total_oi),
                        'vol_oi_ratio': round(vol_oi_ratio, 2)
                    },
                    timestamp=datetime.now()
                )
        except Exception:
            pass

        return None

    def _detect_iv_surge(self, stock: yf.Ticker, ticker: str) -> Optional[DiscoverySignal]:
        """Detect IV percentile surge (volatility explosion)"""
        try:
            exp_dates = stock.options
            if not exp_dates or len(exp_dates) < 2:
                return None

            # Get ATM options from first two expirations
            info = stock.info
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))

            ivs = []
            for exp_date in exp_dates[:2]:
                opt_chain = stock.option_chain(exp_date)

                # Find ATM strike
                calls = opt_chain.calls
                if not calls.empty:
                    atm_call = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:1]]
                    if not atm_call.empty and 'impliedVolatility' in atm_call.columns:
                        iv = atm_call['impliedVolatility'].iloc[0]
                        if iv and iv > 0:
                            ivs.append(iv)

            if not ivs:
                return None

            avg_iv = np.mean(ivs)

            # High IV indicates unusual activity (>50% = elevated, >80% = extreme)
            if avg_iv > 0.5:
                severity = self._classify_severity(avg_iv, [0.5, 0.8, 1.2, 1.5])
                score = min(100, avg_iv * 60)

                return DiscoverySignal(
                    ticker=ticker,
                    signal_type='iv_surge',
                    severity=severity,
                    score=score,
                    details={
                        'implied_volatility': round(avg_iv * 100, 1),
                        'iv_percentile': 'High' if avg_iv > 0.8 else 'Elevated'
                    },
                    timestamp=datetime.now()
                )
        except Exception:
            pass

        return None

    def _detect_oi_surge(self, stock: yf.Ticker, ticker: str) -> Optional[DiscoverySignal]:
        """Detect large open interest changes (institutional positioning)"""
        try:
            exp_dates = stock.options
            if not exp_dates:
                return None

            opt_chain = stock.option_chain(exp_dates[0])

            # Look for strikes with very high OI relative to volume
            calls_oi = opt_chain.calls['openInterest'].sum()
            puts_oi = opt_chain.puts['openInterest'].sum()
            total_oi = calls_oi + puts_oi

            if total_oi > 10000:  # Significant OI threshold
                score = min(100, (total_oi / 1000) * 5)
                severity = self._classify_severity(total_oi, [10000, 50000, 100000, 200000])

                return DiscoverySignal(
                    ticker=ticker,
                    signal_type='oi_surge',
                    severity=severity,
                    score=score,
                    details={
                        'total_oi': int(total_oi),
                        'calls_oi': int(calls_oi),
                        'puts_oi': int(puts_oi)
                    },
                    timestamp=datetime.now()
                )
        except Exception:
            pass

        return None

    def _detect_pc_ratio_extreme(self, stock: yf.Ticker, ticker: str) -> Optional[DiscoverySignal]:
        """Detect extreme put/call ratios (sentiment extremes)"""
        try:
            exp_dates = stock.options
            if not exp_dates:
                return None

            opt_chain = stock.option_chain(exp_dates[0])

            calls_vol = opt_chain.calls['volume'].sum()
            puts_vol = opt_chain.puts['volume'].sum()

            if calls_vol == 0 or puts_vol == 0:
                return None

            pc_ratio = puts_vol / calls_vol

            # Extreme ratios: < 0.3 (very bullish) or > 3.0 (very bearish)
            if pc_ratio < 0.3 or pc_ratio > 3.0:
                score = min(100, abs(np.log(pc_ratio)) * 40)

                if pc_ratio < 0.3:
                    severity = 'high'
                    sentiment = 'Extremely Bullish'
                else:
                    severity = 'high'
                    sentiment = 'Extremely Bearish'

                return DiscoverySignal(
                    ticker=ticker,
                    signal_type='pc_ratio_extreme',
                    severity=severity,
                    score=score,
                    details={
                        'put_call_ratio': round(pc_ratio, 2),
                        'sentiment': sentiment,
                        'puts_volume': int(puts_vol),
                        'calls_volume': int(calls_vol)
                    },
                    timestamp=datetime.now()
                )
        except Exception:
            pass

        return None

    def _classify_severity(self, value: float, thresholds: List[float]) -> str:
        """Classify severity based on value and thresholds"""
        if value < thresholds[0]:
            return 'low'
        elif value < thresholds[1]:
            return 'medium'
        elif value < thresholds[2]:
            return 'high'
        else:
            return 'extreme'

    def _calculate_discovery_score(
        self,
        signals: List[DiscoverySignal],
        market_cap: float,
        prefer_small_caps: bool,
        prefer_low_coverage: bool,
        info: Dict
    ) -> float:
        """
        Calculate composite discovery score (0-100)

        Combines:
        - Signal scores (weighted)
        - Market cap adjustment (prefer smaller caps)
        - Analyst coverage adjustment (prefer less followed)
        """
        # Base score from signals
        signal_score = sum(s.score for s in signals) / len(signals) if signals else 0

        # Market cap adjustment
        cap_bonus = 0
        if prefer_small_caps and market_cap > 0:
            if market_cap < 2e9:  # < $2B = small cap
                cap_bonus = 15
            elif market_cap < 10e9:  # < $10B = mid cap
                cap_bonus = 10
            elif market_cap < 50e9:  # < $50B
                cap_bonus = 5

        # Analyst coverage adjustment
        coverage_bonus = 0
        if prefer_low_coverage:
            analyst_count = info.get('numberOfAnalystOpinions', 0)
            if analyst_count < 5:
                coverage_bonus = 15
            elif analyst_count < 10:
                coverage_bonus = 10
            elif analyst_count < 20:
                coverage_bonus = 5

        # Combine (ensure 0-100 range)
        total_score = min(100, signal_score + cap_bonus + coverage_bonus)
        return round(total_score, 1)

    def _calculate_iv_metrics(self, stock: yf.Ticker) -> Tuple[float, float]:
        """Calculate IV percentile and change"""
        # Placeholder - would need historical IV data
        return (0.0, 0.0)

    def _calculate_unusual_volume(self, stock: yf.Ticker) -> float:
        """Calculate volume ratio vs average"""
        try:
            info = stock.info
            current_vol = info.get('volume', 0)
            avg_vol = info.get('averageVolume', 0)

            if avg_vol > 0:
                return round(current_vol / avg_vol, 2)
        except:
            pass
        return 1.0

    def _calculate_put_call_ratio(self, stock: yf.Ticker) -> float:
        """Calculate put/call ratio"""
        try:
            exp_dates = stock.options
            if exp_dates:
                opt_chain = stock.option_chain(exp_dates[0])
                puts_vol = opt_chain.puts['volume'].sum()
                calls_vol = opt_chain.calls['volume'].sum()

                if calls_vol > 0:
                    return round(puts_vol / calls_vol, 2)
        except:
            pass
        return 0.0

    def _calculate_oi_change(self, stock: yf.Ticker) -> float:
        """Calculate OI change percentage"""
        # Placeholder - would need historical OI data
        return 0.0

    def _calculate_aggressive_buying(self, stock: yf.Ticker) -> float:
        """Calculate percentage of volume at ask (requires tick data)"""
        # Placeholder - requires IB tick data
        return 0.0

    def _generate_discovery_reasons(self, signals: List[DiscoverySignal], info: Dict) -> List[str]:
        """Generate human-readable reasons why this is a hidden gem"""
        reasons = []

        for signal in signals:
            if signal.signal_type == 'unusual_volume':
                ratio = signal.details.get('vol_oi_ratio', 0)
                reasons.append(f"📈 Unusual options volume ({ratio:.1f}x normal)")

            elif signal.signal_type == 'iv_surge':
                iv = signal.details.get('implied_volatility', 0)
                reasons.append(f"⚡ High implied volatility ({iv:.1f}%)")

            elif signal.signal_type == 'oi_surge':
                oi = signal.details.get('total_oi', 0)
                reasons.append(f"🏢 Large open interest ({oi:,} contracts)")

            elif signal.signal_type == 'pc_ratio_extreme':
                sentiment = signal.details.get('sentiment', '')
                reasons.append(f"🎯 {sentiment} sentiment")

        # Add market cap context
        market_cap = info.get('marketCap', 0)
        if market_cap < 2e9:
            reasons.append("💎 Small cap (under-the-radar)")

        # Add analyst coverage
        analysts = info.get('numberOfAnalystOpinions', 0)
        if analysts < 5:
            reasons.append(f"🔍 Limited analyst coverage ({analysts} analysts)")

        return reasons[:5]  # Limit to top 5 reasons

    def _fetch_recent_news(self, stock: yf.Ticker, days: int = 7) -> List[Dict]:
        """
        Fetch recent news for the ticker from yfinance

        Returns list of news items with:
        - title: str
        - link: str
        - publisher: str
        - timestamp: datetime
        """
        try:
            news_items = []
            raw_news = stock.news

            if not raw_news:
                return []

            cutoff_date = datetime.now() - timedelta(days=days)

            for item in raw_news:
                # Handle nested content structure
                content = item.get('content', {})

                # Parse timestamp (ISO format from pubDate)
                pub_date = content.get('pubDate', '')
                if pub_date:
                    try:
                        from dateutil import parser
                        timestamp = parser.parse(pub_date)
                        # Convert to naive datetime for comparison
                        if timestamp.tzinfo is not None:
                            timestamp = timestamp.replace(tzinfo=None)
                    except:
                        # Fallback: try providerPublishTime
                        timestamp = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                else:
                    timestamp = datetime.fromtimestamp(item.get('providerPublishTime', 0))

                # Skip if timestamp is invalid (epoch 0)
                if timestamp.year < 2000:
                    continue

                if timestamp >= cutoff_date:
                    # Get provider info
                    provider = content.get('provider', {})

                    # Get canonical URL
                    canonical = content.get('canonicalUrl', {})

                    news_items.append({
                        'title': content.get('title', ''),
                        'link': canonical.get('url', ''),
                        'publisher': provider.get('displayName', 'Unknown'),
                        'timestamp': timestamp
                    })

            # Sort by timestamp descending
            news_items.sort(key=lambda x: x['timestamp'], reverse=True)

            return news_items[:10]  # Limit to 10 most recent

        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def _analyze_news_sentiment(self, news_items: List[Dict]) -> Tuple[str, float, List[str]]:
        """
        Analyze news sentiment and generate catalyst score with firm-specific weighting

        Returns:
            (sentiment, catalyst_score, reasons)
            sentiment: 'positive', 'negative', 'neutral', 'mixed'
            catalyst_score: 0-100
            reasons: List of catalyst explanations
        """
        if not news_items:
            return 'neutral', 0.0, []

        # Tier-1 analyst firms (higher weight for upgrades/downgrades)
        tier1_firms = [
            'goldman sachs', 'goldman', 'gs',
            'morgan stanley', 'ms',
            'jpmorgan', 'jp morgan', 'jpm',
            'bank of america', 'bofa', 'bac',
            'citi', 'citigroup',
            'wells fargo', 'barclays',
            'deutsche bank', 'credit suisse',
            'ubs', 'jefferies'
        ]

        # TIER 1: High-confidence catalysts (weighted 30 points base)
        tier1_positive = [
            'beat', 'beats', 'exceeded', 'exceeds',
            'raised guidance', 'raises guidance',
            'insider buying', 'insider purchase', 'ceo bought', 'director bought',
            'buyback', 'share repurchase',
            'dividend increase', 'dividend raised',
            'stock split', 'share split'
        ]

        tier1_negative = [
            'miss', 'misses', 'missed',
            'lowered guidance', 'lowers guidance', 'guidance cut',
            'insider selling', 'insider sale',
            'dividend cut', 'dividend suspended',
            'sec investigation', 'doj probe', 'antitrust'
        ]

        # TIER 2: Medium-confidence catalysts (weighted 20 points base)
        tier2_positive = [
            'upgrade', 'upgraded', 'raises price target',
            'approval', 'approved', 'fda approval',
            'acquisition', 'merger', 'partnership',
            'buy rating', 'initiated with buy', 'outperform'
        ]

        tier2_negative = [
            'downgrade', 'downgraded', 'lowers price target',
            'lawsuit', 'recall', 'investigation',
            'sell rating', 'underperform',
            'bankruptcy', 'chapter 11'
        ]

        # TIER 3: Low-confidence catalysts (weighted 10 points base)
        tier3_positive = [
            'strong earnings', 'strong revenue', 'strong growth',
            'expansion', 'contract win', 'award'
        ]

        tier3_negative = [
            'weak', 'decline', 'concern', 'warning', 'risk'
        ]

        # Volatility keywords (separate tracking)
        volatility_keywords = [
            'earnings call', 'earnings report',
            'ceo change', 'cfo change', 'executive transition',
            'restructuring', 'turnaround plan',
            'trial results', 'clinical trial', 'fda decision'
        ]

        positive_score = 0.0
        negative_score = 0.0
        volatility_count = 0
        reasons = []

        for news in news_items:
            title_lower = news['title'].lower()

            # Check for tier-1 analyst firm
            is_tier1_firm = any(firm in title_lower for firm in tier1_firms)
            firm_multiplier = 1.5 if is_tier1_firm else 1.0

            # Check TIER 1 positive catalysts (30 points base)
            for keyword in tier1_positive:
                if keyword in title_lower:
                    points = 30 * firm_multiplier
                    positive_score += points
                    if len(reasons) < 3:
                        prefix = "⭐" if is_tier1_firm else "📰"
                        reasons.append(f"{prefix} {news['title'][:75]}...")
                    break

            # Check TIER 1 negative catalysts (30 points base)
            for keyword in tier1_negative:
                if keyword in title_lower:
                    points = 30 * firm_multiplier
                    negative_score += points
                    if len(reasons) < 3:
                        prefix = "🚨" if is_tier1_firm else "⚠️"
                        reasons.append(f"{prefix} {news['title'][:75]}...")
                    break

            # Check TIER 2 positive catalysts (20 points base)
            for keyword in tier2_positive:
                if keyword in title_lower:
                    points = 20 * firm_multiplier
                    positive_score += points
                    if len(reasons) < 3:
                        prefix = "⭐" if is_tier1_firm else "📰"
                        reasons.append(f"{prefix} {news['title'][:75]}...")
                    break

            # Check TIER 2 negative catalysts (20 points base)
            for keyword in tier2_negative:
                if keyword in title_lower:
                    points = 20 * firm_multiplier
                    negative_score += points
                    if len(reasons) < 3:
                        reasons.append(f"⚠️ {news['title'][:75]}...")
                    break

            # Check TIER 3 positive catalysts (10 points base)
            for keyword in tier3_positive:
                if keyword in title_lower:
                    positive_score += 10
                    if len(reasons) < 3:
                        reasons.append(f"📈 {news['title'][:75]}...")
                    break

            # Check TIER 3 negative catalysts (10 points base)
            for keyword in tier3_negative:
                if keyword in title_lower:
                    negative_score += 10
                    if len(reasons) < 3:
                        reasons.append(f"📉 {news['title'][:75]}...")
                    break

            # Check volatility keywords (adds context)
            for keyword in volatility_keywords:
                if keyword in title_lower:
                    volatility_count += 1
                    break

        # Determine overall sentiment
        if positive_score == 0 and negative_score == 0:
            sentiment = 'neutral'
            catalyst_score = 0.0
        elif positive_score > negative_score * 1.3:
            sentiment = 'positive'
            catalyst_score = min(100, positive_score + (volatility_count * 5))
        elif negative_score > positive_score * 1.3:
            sentiment = 'negative'
            catalyst_score = -min(100, negative_score)
        else:
            sentiment = 'mixed'
            catalyst_score = positive_score - negative_score

        return sentiment, catalyst_score, reasons
