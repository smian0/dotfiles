"""
Institutional-Grade Technical Indicators for Wheel Strategy

Includes indicators commonly used by hedge funds and proprietary trading desks:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)
- Bollinger Bands (volatility and mean reversion)
- Volume Analysis (OBV, Volume Profile)
- Moving Averages (SMA, EMA, Golden/Death Cross)
- Relative Strength vs SPY (institutional favorite)
- VWAP (Volume Weighted Average Price)
- Support/Resistance (pivot points)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class TechnicalAnalysis:
    """Complete technical analysis results"""
    ticker: str

    # Momentum Indicators
    rsi: Optional[float] = None
    rsi_signal: str = ""

    macd: Optional[float] = None
    macd_signal_line: Optional[float] = None
    macd_histogram: Optional[float] = None
    macd_crossover: str = ""

    # Trend Indicators
    adx: Optional[float] = None
    adx_signal: str = ""

    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None

    golden_cross: bool = False  # SMA 50 crosses above SMA 200
    death_cross: bool = False   # SMA 50 crosses below SMA 200

    # Volatility Indicators
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width: Optional[float] = None
    bb_position: Optional[float] = None  # Where price is in BB (0-1)
    bb_squeeze: bool = False  # Low volatility, potential breakout

    # Volume Indicators
    obv: Optional[float] = None
    obv_trend: str = ""  # rising, falling, neutral
    volume_sma: Optional[float] = None
    volume_ratio: Optional[float] = None  # Current vol vs average

    vwap: Optional[float] = None
    vwap_distance: Optional[float] = None  # % from VWAP

    # Relative Strength
    rs_spy: Optional[float] = None  # Relative strength vs SPY
    rs_spy_trend: str = ""  # outperforming, underperforming, neutral

    # Support/Resistance
    current_price: Optional[float] = None
    pivot_point: Optional[float] = None
    support_1: Optional[float] = None
    support_2: Optional[float] = None
    resistance_1: Optional[float] = None
    resistance_2: Optional[float] = None
    distance_to_support: Optional[float] = None  # %
    distance_to_resistance: Optional[float] = None  # %

    # Composite Scores
    technical_score: int = 0  # 0-100
    momentum_score: int = 0   # 0-100
    trend_score: int = 0      # 0-100
    volatility_score: int = 0 # 0-100
    volume_score: int = 0     # 0-100

    # Overall Signal
    overall_signal: str = ""  # STRONG_BUY, BUY, NEUTRAL, AVOID, STRONG_AVOID
    confidence: str = ""      # HIGH, MEDIUM, LOW

    # Institutional Insights
    institutional_signal: str = ""
    entry_recommendation: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'ticker': self.ticker,
            'rsi': self.rsi,
            'rsi_signal': self.rsi_signal,
            'macd': {
                'macd': self.macd,
                'signal': self.macd_signal_line,
                'histogram': self.macd_histogram,
                'crossover': self.macd_crossover
            },
            'adx': self.adx,
            'adx_signal': self.adx_signal,
            'moving_averages': {
                'sma_20': self.sma_20,
                'sma_50': self.sma_50,
                'sma_200': self.sma_200,
                'ema_12': self.ema_12,
                'ema_26': self.ema_26,
                'golden_cross': self.golden_cross,
                'death_cross': self.death_cross
            },
            'bollinger_bands': {
                'upper': self.bb_upper,
                'middle': self.bb_middle,
                'lower': self.bb_lower,
                'width': self.bb_width,
                'position': self.bb_position,
                'squeeze': self.bb_squeeze
            },
            'volume': {
                'obv': self.obv,
                'obv_trend': self.obv_trend,
                'volume_ratio': self.volume_ratio,
                'vwap': self.vwap,
                'vwap_distance': self.vwap_distance
            },
            'relative_strength': {
                'rs_spy': self.rs_spy,
                'trend': self.rs_spy_trend
            },
            'support_resistance': {
                'current_price': self.current_price,
                'pivot': self.pivot_point,
                'support_1': self.support_1,
                'support_2': self.support_2,
                'resistance_1': self.resistance_1,
                'resistance_2': self.resistance_2,
                'distance_to_support': self.distance_to_support,
                'distance_to_resistance': self.distance_to_resistance
            },
            'scores': {
                'technical': self.technical_score,
                'momentum': self.momentum_score,
                'trend': self.trend_score,
                'volatility': self.volatility_score,
                'volume': self.volume_score
            },
            'signals': {
                'overall': self.overall_signal,
                'confidence': self.confidence,
                'institutional': self.institutional_signal,
                'entry_recommendation': self.entry_recommendation
            }
        }


class InstitutionalTechnicalAnalyzer:
    """
    Institutional-grade technical analysis for wheel strategy timing

    Uses indicators that hedge funds and prop desks rely on:
    - Price action and momentum (RSI, MACD)
    - Trend following (ADX, MAs, Golden/Death Cross)
    - Volatility (Bollinger Bands, squeeze detection)
    - Volume confirmation (OBV, VWAP, volume profile)
    - Relative strength vs market (RS vs SPY)
    """

    def __init__(self):
        self.spy_cache = None
        self.spy_cache_time = None

    def analyze(self, ticker: str, include_spy_comparison: bool = True) -> TechnicalAnalysis:
        """
        Run complete technical analysis on ticker

        Args:
            ticker: Stock symbol
            include_spy_comparison: Compare relative strength vs SPY (slower)

        Returns:
            TechnicalAnalysis object with all indicators
        """
        analysis = TechnicalAnalysis(ticker=ticker)

        try:
            # Fetch historical data
            stock = yf.Ticker(ticker)
            hist = stock.history(period='6mo')  # 6 months for comprehensive analysis

            if len(hist) < 50:
                return analysis  # Not enough data

            # Calculate all indicators
            self._calculate_rsi(hist, analysis)
            self._calculate_macd(hist, analysis)
            self._calculate_adx(hist, analysis)
            self._calculate_moving_averages(hist, analysis)
            self._calculate_bollinger_bands(hist, analysis)
            self._calculate_volume_indicators(hist, analysis)
            self._calculate_vwap(hist, analysis)
            self._calculate_support_resistance(hist, analysis)

            # Relative strength vs SPY (institutional favorite)
            if include_spy_comparison:
                self._calculate_relative_strength_spy(ticker, hist, analysis)

            # Calculate composite scores
            self._calculate_scores(analysis)

            # Generate signals and recommendations
            self._generate_signals(analysis)

        except Exception as e:
            print(f"Technical analysis error for {ticker}: {e}")

        return analysis

    def _calculate_rsi(self, hist: pd.DataFrame, analysis: TechnicalAnalysis, period: int = 14):
        """Calculate RSI and generate signal"""
        try:
            delta = hist['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            analysis.rsi = float(rsi.iloc[-1])

            # Generate signal
            if analysis.rsi < 30:
                analysis.rsi_signal = "EXTREMELY_OVERSOLD"
            elif analysis.rsi < 40:
                analysis.rsi_signal = "OVERSOLD"
            elif analysis.rsi < 50:
                analysis.rsi_signal = "SLIGHT_PULLBACK"
            elif analysis.rsi < 60:
                analysis.rsi_signal = "NEUTRAL"
            elif analysis.rsi < 70:
                analysis.rsi_signal = "OVERBOUGHT"
            else:
                analysis.rsi_signal = "EXTREMELY_OVERBOUGHT"

        except Exception as e:
            print(f"RSI calculation error: {e}")

    def _calculate_macd(self, hist: pd.DataFrame, analysis: TechnicalAnalysis):
        """Calculate MACD and detect crossovers"""
        try:
            ema_12 = hist['Close'].ewm(span=12, adjust=False).mean()
            ema_26 = hist['Close'].ewm(span=26, adjust=False).mean()

            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line

            analysis.macd = float(macd_line.iloc[-1])
            analysis.macd_signal_line = float(signal_line.iloc[-1])
            analysis.macd_histogram = float(histogram.iloc[-1])

            # Detect crossovers (compare last 2 periods)
            if len(histogram) >= 2:
                current_hist = histogram.iloc[-1]
                prev_hist = histogram.iloc[-2]

                if current_hist > 0 and prev_hist <= 0:
                    analysis.macd_crossover = "BULLISH"
                elif current_hist < 0 and prev_hist >= 0:
                    analysis.macd_crossover = "BEARISH"
                elif current_hist > 0:
                    analysis.macd_crossover = "BULLISH_MOMENTUM"
                elif current_hist < 0:
                    analysis.macd_crossover = "BEARISH_MOMENTUM"
                else:
                    analysis.macd_crossover = "NEUTRAL"

        except Exception as e:
            print(f"MACD calculation error: {e}")

    def _calculate_adx(self, hist: pd.DataFrame, analysis: TechnicalAnalysis, period: int = 14):
        """Calculate ADX (Average Directional Index) - trend strength"""
        try:
            high_low = hist['High'] - hist['Low']
            high_close = np.abs(hist['High'] - hist['Close'].shift())
            low_close = np.abs(hist['Low'] - hist['Close'].shift())

            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

            high_diff = hist['High'].diff()
            low_diff = -hist['Low'].diff()

            pos_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
            neg_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

            atr = tr.rolling(window=period).mean()
            pos_di = 100 * (pos_dm.rolling(window=period).mean() / atr)
            neg_di = 100 * (neg_dm.rolling(window=period).mean() / atr)

            dx = 100 * np.abs(pos_di - neg_di) / (pos_di + neg_di)
            adx = dx.rolling(window=period).mean()

            analysis.adx = float(adx.iloc[-1])

            # Generate signal
            if analysis.adx < 20:
                analysis.adx_signal = "RANGE_BOUND"  # Ideal for wheel strategy
            elif analysis.adx < 30:
                analysis.adx_signal = "WEAK_TREND"
            elif analysis.adx < 40:
                analysis.adx_signal = "MODERATE_TREND"
            else:
                analysis.adx_signal = "STRONG_TREND"  # Caution for wheel

        except Exception as e:
            print(f"ADX calculation error: {e}")

    def _calculate_moving_averages(self, hist: pd.DataFrame, analysis: TechnicalAnalysis):
        """Calculate moving averages and detect golden/death crosses"""
        try:
            analysis.current_price = float(hist['Close'].iloc[-1])

            # Simple Moving Averages
            analysis.sma_20 = float(hist['Close'].rolling(window=20).mean().iloc[-1])
            analysis.sma_50 = float(hist['Close'].rolling(window=50).mean().iloc[-1])

            if len(hist) >= 200:
                analysis.sma_200 = float(hist['Close'].rolling(window=200).mean().iloc[-1])

            # Exponential Moving Averages
            analysis.ema_12 = float(hist['Close'].ewm(span=12, adjust=False).mean().iloc[-1])
            analysis.ema_26 = float(hist['Close'].ewm(span=26, adjust=False).mean().iloc[-1])

            # Detect golden/death cross
            if analysis.sma_50 and analysis.sma_200:
                sma_50_series = hist['Close'].rolling(window=50).mean()
                sma_200_series = hist['Close'].rolling(window=200).mean()

                if len(sma_50_series) >= 2 and len(sma_200_series) >= 2:
                    # Golden cross: SMA 50 crosses above SMA 200
                    if sma_50_series.iloc[-1] > sma_200_series.iloc[-1] and \
                       sma_50_series.iloc[-2] <= sma_200_series.iloc[-2]:
                        analysis.golden_cross = True

                    # Death cross: SMA 50 crosses below SMA 200
                    elif sma_50_series.iloc[-1] < sma_200_series.iloc[-1] and \
                         sma_50_series.iloc[-2] >= sma_200_series.iloc[-2]:
                        analysis.death_cross = True

        except Exception as e:
            print(f"Moving averages calculation error: {e}")

    def _calculate_bollinger_bands(self, hist: pd.DataFrame, analysis: TechnicalAnalysis, period: int = 20):
        """Calculate Bollinger Bands and detect squeeze (low volatility)"""
        try:
            sma = hist['Close'].rolling(window=period).mean()
            std = hist['Close'].rolling(window=period).std()

            analysis.bb_upper = float(sma.iloc[-1] + (std.iloc[-1] * 2))
            analysis.bb_middle = float(sma.iloc[-1])
            analysis.bb_lower = float(sma.iloc[-1] - (std.iloc[-1] * 2))

            current_price = hist['Close'].iloc[-1]

            # BB Width (volatility measure)
            analysis.bb_width = float((analysis.bb_upper - analysis.bb_lower) / analysis.bb_middle * 100)

            # BB Position (where price is within bands, 0=lower, 0.5=middle, 1=upper)
            if analysis.bb_upper != analysis.bb_lower:
                analysis.bb_position = float(
                    (current_price - analysis.bb_lower) / (analysis.bb_upper - analysis.bb_lower)
                )

            # BB Squeeze detection (Bollinger Band width in lowest 10th percentile)
            bb_width_series = (sma + 2*std - (sma - 2*std)) / sma * 100
            percentile_10 = bb_width_series.quantile(0.10)
            analysis.bb_squeeze = analysis.bb_width < percentile_10

        except Exception as e:
            print(f"Bollinger Bands calculation error: {e}")

    def _calculate_volume_indicators(self, hist: pd.DataFrame, analysis: TechnicalAnalysis):
        """Calculate OBV and volume profile"""
        try:
            # On-Balance Volume (OBV)
            obv = [0]
            for i in range(1, len(hist)):
                if hist['Close'].iloc[i] > hist['Close'].iloc[i-1]:
                    obv.append(obv[-1] + hist['Volume'].iloc[i])
                elif hist['Close'].iloc[i] < hist['Close'].iloc[i-1]:
                    obv.append(obv[-1] - hist['Volume'].iloc[i])
                else:
                    obv.append(obv[-1])

            analysis.obv = float(obv[-1])

            # OBV trend (compare to 20-period SMA of OBV)
            if len(obv) >= 20:
                obv_sma = pd.Series(obv).rolling(window=20).mean().iloc[-1]
                if analysis.obv > obv_sma * 1.05:
                    analysis.obv_trend = "RISING"
                elif analysis.obv < obv_sma * 0.95:
                    analysis.obv_trend = "FALLING"
                else:
                    analysis.obv_trend = "NEUTRAL"

            # Volume ratio (current volume vs 20-day average)
            if len(hist) >= 20:
                analysis.volume_sma = float(hist['Volume'].rolling(window=20).mean().iloc[-1])
                analysis.volume_ratio = float(hist['Volume'].iloc[-1] / analysis.volume_sma)

        except Exception as e:
            print(f"Volume indicators calculation error: {e}")

    def _calculate_vwap(self, hist: pd.DataFrame, analysis: TechnicalAnalysis):
        """Calculate VWAP (Volume Weighted Average Price) - institutional execution benchmark"""
        try:
            # Use last 20 trading days for VWAP
            recent = hist.tail(20)

            typical_price = (recent['High'] + recent['Low'] + recent['Close']) / 3
            vwap = (typical_price * recent['Volume']).sum() / recent['Volume'].sum()

            analysis.vwap = float(vwap)

            # Distance from VWAP (% above or below)
            if analysis.current_price:
                analysis.vwap_distance = float(
                    (analysis.current_price - analysis.vwap) / analysis.vwap * 100
                )

        except Exception as e:
            print(f"VWAP calculation error: {e}")

    def _calculate_support_resistance(self, hist: pd.DataFrame, analysis: TechnicalAnalysis):
        """Calculate support/resistance using pivot points"""
        try:
            # Use recent 20-day high/low for pivot calculation
            recent = hist.tail(20)
            high = recent['High'].max()
            low = recent['Low'].min()
            close = hist['Close'].iloc[-1]

            # Pivot point
            pivot = (high + low + close) / 3
            analysis.pivot_point = float(pivot)

            # Support and Resistance levels
            analysis.resistance_1 = float((2 * pivot) - low)
            analysis.support_1 = float((2 * pivot) - high)

            analysis.resistance_2 = float(pivot + (high - low))
            analysis.support_2 = float(pivot - (high - low))

            # Distance to nearest support/resistance
            if analysis.current_price:
                analysis.distance_to_support = float(
                    (analysis.current_price - analysis.support_1) / analysis.current_price * 100
                )
                analysis.distance_to_resistance = float(
                    (analysis.resistance_1 - analysis.current_price) / analysis.current_price * 100
                )

        except Exception as e:
            print(f"Support/Resistance calculation error: {e}")

    def _calculate_relative_strength_spy(self, ticker: str, hist: pd.DataFrame, analysis: TechnicalAnalysis):
        """
        Calculate relative strength vs SPY (S&P 500)

        Institutional traders focus heavily on this - stocks outperforming SPY
        are stronger candidates for bullish strategies
        """
        try:
            # Cache SPY data to avoid repeated API calls
            if self.spy_cache is None or \
               self.spy_cache_time is None or \
               datetime.now() - self.spy_cache_time > timedelta(hours=1):
                spy = yf.Ticker('SPY')
                self.spy_cache = spy.history(period='6mo')
                self.spy_cache_time = datetime.now()

            spy_hist = self.spy_cache

            # Align dates
            common_dates = hist.index.intersection(spy_hist.index)
            if len(common_dates) < 50:
                return

            stock_returns = hist.loc[common_dates, 'Close'].pct_change()
            spy_returns = spy_hist.loc[common_dates, 'Close'].pct_change()

            # Calculate relative strength (stock returns / SPY returns)
            # Values > 1 = outperforming, < 1 = underperforming
            stock_cumulative = (1 + stock_returns).cumprod().iloc[-1]
            spy_cumulative = (1 + spy_returns).cumprod().iloc[-1]

            analysis.rs_spy = float(stock_cumulative / spy_cumulative)

            # Trend (compare recent 20-day RS vs 50-day RS)
            if len(common_dates) >= 50:
                recent_20 = common_dates[-20:]
                recent_50 = common_dates[-50:]

                rs_20 = (1 + stock_returns.loc[recent_20]).cumprod().iloc[-1] / \
                        (1 + spy_returns.loc[recent_20]).cumprod().iloc[-1]
                rs_50 = (1 + stock_returns.loc[recent_50]).cumprod().iloc[-1] / \
                        (1 + spy_returns.loc[recent_50]).cumprod().iloc[-1]

                if rs_20 > rs_50 * 1.05:
                    analysis.rs_spy_trend = "ACCELERATING_OUTPERFORMANCE"
                elif rs_20 > rs_50:
                    analysis.rs_spy_trend = "OUTPERFORMING"
                elif rs_20 < rs_50 * 0.95:
                    analysis.rs_spy_trend = "ACCELERATING_UNDERPERFORMANCE"
                else:
                    analysis.rs_spy_trend = "NEUTRAL"

        except Exception as e:
            print(f"Relative strength calculation error: {e}")

    def _calculate_scores(self, analysis: TechnicalAnalysis):
        """Calculate composite scores (0-100)"""

        # Momentum Score (RSI, MACD)
        momentum_score = 50  # Start neutral

        if analysis.rsi is not None:
            if analysis.rsi < 30:
                momentum_score += 30
            elif analysis.rsi < 40:
                momentum_score += 20
            elif analysis.rsi < 50:
                momentum_score += 10
            elif analysis.rsi > 70:
                momentum_score -= 20
            elif analysis.rsi > 60:
                momentum_score -= 10

        if analysis.macd_crossover == "BULLISH":
            momentum_score += 20
        elif analysis.macd_crossover == "BEARISH":
            momentum_score -= 20
        elif analysis.macd_crossover == "BULLISH_MOMENTUM":
            momentum_score += 10

        analysis.momentum_score = max(0, min(100, momentum_score))

        # Trend Score (ADX, MAs, Golden/Death Cross)
        trend_score = 50

        if analysis.adx is not None:
            if analysis.adx < 20:
                trend_score += 20  # Range-bound, ideal for wheel
            elif analysis.adx > 40:
                trend_score -= 15  # Strong trend, risky

        if analysis.golden_cross:
            trend_score += 25
        elif analysis.death_cross:
            trend_score -= 25

        # Price above key MAs is bullish
        if analysis.current_price and analysis.sma_50:
            if analysis.current_price > analysis.sma_50:
                trend_score += 10

        if analysis.current_price and analysis.sma_200:
            if analysis.current_price > analysis.sma_200:
                trend_score += 15

        analysis.trend_score = max(0, min(100, trend_score))

        # Volatility Score (Bollinger Bands)
        volatility_score = 50

        if analysis.bb_position is not None:
            if analysis.bb_position < 0.3:
                volatility_score += 25  # Near lower band, oversold
            elif analysis.bb_position > 0.7:
                volatility_score -= 20  # Near upper band, overbought

        if analysis.bb_squeeze:
            volatility_score += 15  # Squeeze = potential breakout

        analysis.volatility_score = max(0, min(100, volatility_score))

        # Volume Score (OBV, volume ratio, VWAP)
        volume_score = 50

        if analysis.obv_trend == "RISING":
            volume_score += 20
        elif analysis.obv_trend == "FALLING":
            volume_score -= 20

        if analysis.volume_ratio is not None:
            if analysis.volume_ratio > 1.5:
                volume_score += 15  # High volume confirmation
            elif analysis.volume_ratio < 0.5:
                volume_score -= 10  # Low volume, weak signal

        if analysis.vwap_distance is not None:
            if abs(analysis.vwap_distance) < 1:
                volume_score += 10  # Price near institutional VWAP

        analysis.volume_score = max(0, min(100, volume_score))

        # Technical Score (weighted average of all scores)
        analysis.technical_score = int(
            analysis.momentum_score * 0.30 +
            analysis.trend_score * 0.25 +
            analysis.volatility_score * 0.20 +
            analysis.volume_score * 0.25
        )

    def _generate_signals(self, analysis: TechnicalAnalysis):
        """Generate overall signal and recommendations"""

        score = analysis.technical_score

        # Overall Signal
        if score >= 70:
            analysis.overall_signal = "STRONG_BUY"
            analysis.confidence = "HIGH"
        elif score >= 55:
            analysis.overall_signal = "BUY"
            analysis.confidence = "MEDIUM"
        elif score >= 40:
            analysis.overall_signal = "NEUTRAL"
            analysis.confidence = "MEDIUM"
        elif score >= 25:
            analysis.overall_signal = "AVOID"
            analysis.confidence = "MEDIUM"
        else:
            analysis.overall_signal = "STRONG_AVOID"
            analysis.confidence = "HIGH"

        # Institutional Signal (considers RS vs SPY)
        if analysis.rs_spy is not None:
            if analysis.rs_spy > 1.1 and analysis.rs_spy_trend in ["OUTPERFORMING", "ACCELERATING_OUTPERFORMANCE"]:
                analysis.institutional_signal = "INSTITUTIONAL_BUY"
            elif analysis.rs_spy < 0.9 and analysis.rs_spy_trend in ["ACCELERATING_UNDERPERFORMANCE"]:
                analysis.institutional_signal = "INSTITUTIONAL_AVOID"
            else:
                analysis.institutional_signal = "NEUTRAL"

        # Entry Recommendation for Wheel Strategy
        if score >= 70:
            analysis.entry_recommendation = "🟢 EXCELLENT - Full position size"
        elif score >= 55:
            analysis.entry_recommendation = "🟢 GOOD - Standard position size"
        elif score >= 40:
            analysis.entry_recommendation = "🟡 MODERATE - Reduced position (50%)"
        elif score >= 25:
            analysis.entry_recommendation = "🔴 POOR - Wait for better setup"
        else:
            analysis.entry_recommendation = "🔴 AVOID - Do not enter"


# Convenience function
def analyze_ticker(ticker: str, include_spy_comparison: bool = True) -> TechnicalAnalysis:
    """
    Quick analysis of a ticker with all institutional indicators

    Usage:
        ta = analyze_ticker('AAPL')
        print(f"Technical Score: {ta.technical_score}/100")
        print(f"Signal: {ta.overall_signal}")
        print(f"Entry: {ta.entry_recommendation}")
    """
    analyzer = InstitutionalTechnicalAnalyzer()
    return analyzer.analyze(ticker, include_spy_comparison)
