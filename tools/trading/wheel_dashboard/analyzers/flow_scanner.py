"""
Real-Time Options Flow Scanner for Interactive Brokers

Detects institutional-grade unusual options activity:
- Large block trades (>100 contracts)
- Aggressive buying/selling (bid/ask aggressor)
- Multi-exchange sweeps
- Unusual volume spikes

Requires:
- Active IB connection
- Market data subscription for options
"""

from ib_insync import IB, Stock, Option
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass


@dataclass
class FlowAlert:
    """Structured flow alert"""
    timestamp: datetime
    ticker: str
    strike: float
    right: str  # 'C' or 'P'
    alert_type: str  # 'BLOCK', 'SWEEP', 'AGGRESSIVE_BUY'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    size: int
    premium_flow: float
    details: str


class FlowScanner:
    """
    Real-time options flow scanner using IB market data

    Detects:
    1. Block trades: Single trades >100 contracts (institutional size)
    2. Sweeps: Aggressive buying across multiple exchanges simultaneously
    3. Aggressive buyers: Traders hitting the ask (willing to pay up)
    """

    def __init__(self, ib: IB):
        """
        Initialize flow scanner

        Args:
            ib: Active IB connection
        """
        self.ib = ib
        self.block_threshold = 100  # contracts
        self.sweep_window_seconds = 2  # Time window for sweep detection
        self.aggressive_threshold = 0.65  # 65% of volume at ask = aggressive

    def scan_option_flow(
        self,
        ticker: str,
        max_expirations: int = 3,
        lookback_trades: int = 1000
    ) -> Dict:
        """
        Scan recent options flow for unusual activity

        Args:
            ticker: Stock ticker symbol
            max_expirations: Number of expirations to scan (default: 3)
            lookback_trades: Number of recent trades to analyze per option (default: 1000)

        Returns:
            Dictionary with detected flow:
            {
                'block_trades': [...],
                'sweeps': [...],
                'aggressive_buys': [...],
                'flow_stats': {...},
                'alerts': [...]
            }
        """
        print(f"\n{'='*60}")
        print(f"🔍 Scanning Options Flow for {ticker}")
        print(f"{'='*60}\n")

        # Qualify stock contract
        stock = Stock(ticker, 'SMART', 'USD')
        qualified_stock = self.ib.qualifyContracts(stock)

        if not qualified_stock:
            print(f"❌ Could not find stock: {ticker}")
            return self._empty_result()

        stock = qualified_stock[0]

        # Get current market price
        ticker_data = self.ib.reqTickers(stock)[0]
        current_price = ticker_data.marketPrice()

        # Fallback to close if market price not available (nan, None, or <= 0)
        import math
        if not current_price or math.isnan(current_price) or current_price <= 0:
            current_price = ticker_data.close
            print(f"💰 Using close price: ${current_price:.2f} (market closed)")
        else:
            print(f"💰 Current price: ${current_price:.2f}")

        # Get option chain parameters
        chains = self.ib.reqSecDefOptParams(
            stock.symbol, '', stock.secType, stock.conId
        )

        if not chains:
            print(f"❌ No option chains found for {ticker}")
            return self._empty_result()

        # Use first exchange that has options
        chain = chains[0]
        print(f"📊 Found {len(chain.expirations)} expirations on {chain.exchange}")

        # Limit expirations to scan
        expirations_to_scan = sorted(chain.expirations)[:max_expirations]

        unusual_flow = {
            'block_trades': [],
            'sweeps': [],
            'aggressive_buys': [],
            'flow_stats': {
                'total_premium_flow': 0,
                'put_flow': 0,
                'call_flow': 0,
                'total_contracts': 0
            },
            'alerts': []
        }

        # Scan each expiration
        options_processed = 0
        start_time = datetime.now()

        for exp_idx, expiration in enumerate(expirations_to_scan):
            print(f"\n📅 Scanning expiration {exp_idx + 1}/{len(expirations_to_scan)}: {expiration}")

            # Get strikes near ATM (within 5% for faster scanning)
            strikes_to_scan = self._get_atm_strikes(chain.strikes, current_price, range_pct=5)
            total_options = len(strikes_to_scan) * 2 * len(expirations_to_scan)  # strikes × 2 rights × expirations
            print(f"   Analyzing {len(strikes_to_scan)} strikes near ATM (~{total_options} total options)")

            for strike_idx, strike in enumerate(strikes_to_scan):
                for right in ['P', 'C']:
                    options_processed += 1

                    # Show progress every 10 options
                    if options_processed % 10 == 0:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        rate = options_processed / elapsed if elapsed > 0 else 1
                        remaining = total_options - options_processed
                        eta_seconds = remaining / rate if rate > 0 else 0
                        print(f"   ⏱️  Progress: {options_processed}/{total_options} options ({options_processed/total_options*100:.0f}%) - ETA: {int(eta_seconds)}s")
                    # Create option contract
                    option = Option(
                        ticker,
                        expiration,
                        strike,
                        right,
                        chain.exchange
                    )

                    # Qualify contract
                    qualified = self.ib.qualifyContracts(option)

                    if not qualified:
                        continue

                    option = qualified[0]

                    # Get recent trades
                    try:
                        # IB API requires 2 of 3 params: startDateTime, endDateTime, numberOfTicks
                        # Using endDateTime='now' + numberOfTicks to get most recent trades
                        from datetime import datetime as dt
                        ticks = self.ib.reqHistoricalTicks(
                            option,
                            startDateTime='',
                            endDateTime=dt.now(),
                            numberOfTicks=lookback_trades,
                            whatToShow='TRADES',
                            useRth=True
                        )
                    except Exception as e:
                        # Market data might not be available for all options
                        continue

                    if not ticks:
                        continue

                    # Analyze tick data
                    flow_data = self._analyze_ticks(ticks, ticker, strike, right, expiration)

                    # Update stats
                    unusual_flow['flow_stats']['total_contracts'] += flow_data['total_volume']

                    if right == 'P':
                        unusual_flow['flow_stats']['put_flow'] += flow_data['premium_flow']
                    else:
                        unusual_flow['flow_stats']['call_flow'] += flow_data['premium_flow']

                    unusual_flow['flow_stats']['total_premium_flow'] += flow_data['premium_flow']

                    # Collect unusual activity
                    if flow_data['block_trade']:
                        unusual_flow['block_trades'].append(flow_data)
                        print(f"   🎯 BLOCK: {right} {strike} - {flow_data['largest_trade']} contracts")

                    if flow_data['is_sweep']:
                        unusual_flow['sweeps'].append(flow_data)
                        print(f"   💥 SWEEP: {right} {strike} - {flow_data['sweep_exchanges']} exchanges")

                    if flow_data['aggressive_buy']:
                        unusual_flow['aggressive_buys'].append(flow_data)
                        print(f"   🔥 AGGRESSIVE: {right} {strike} - {flow_data['aggressive_ratio']:.0%} at ask")

        # Generate alerts
        unusual_flow['alerts'] = self._generate_alerts(unusual_flow, ticker)

        # Print completion time
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"\n⏱️  Scan completed in {total_time:.1f} seconds ({options_processed} options scanned)")

        # Print summary
        self._print_summary(unusual_flow, ticker)

        return unusual_flow

    def _get_atm_strikes(self, all_strikes: List[float], current_price: float, range_pct: float = 10) -> List[float]:
        """Get strikes within range_pct of current price"""
        if not current_price or current_price <= 0:
            return sorted(all_strikes)[:10]  # Just take first 10 if no price

        lower_bound = current_price * (1 - range_pct / 100)
        upper_bound = current_price * (1 + range_pct / 100)

        atm_strikes = [s for s in all_strikes if lower_bound <= s <= upper_bound]

        return sorted(atm_strikes)

    def _analyze_ticks(
        self,
        ticks: List,
        ticker: str,
        strike: float,
        right: str,
        expiration: str
    ) -> Dict:
        """
        Analyze tick data for unusual patterns

        Returns:
            Dictionary with flow metrics and flags
        """
        if not ticks:
            return self._empty_tick_result()

        # Convert to DataFrame for analysis
        tick_data = []
        for t in ticks:
            tick_data.append({
                'time': t.time,
                'price': t.price,
                'size': t.size,
                'exchange': getattr(t, 'exchange', 'UNKNOWN'),
            })

        df = pd.DataFrame(tick_data)

        if df.empty:
            return self._empty_tick_result()

        # Calculate metrics
        total_volume = df['size'].sum()
        largest_trade = df['size'].max()
        avg_trade_size = df['size'].mean()
        total_trades = len(df)

        # Premium flow (approximate)
        avg_price = df['price'].mean()
        premium_flow = avg_price * total_volume * 100  # Contract multiplier

        # 1. Block trade detection (single trade >100 contracts)
        has_block = largest_trade >= self.block_threshold

        # 2. Sweep detection (multiple exchanges within time window)
        df['time_rounded'] = pd.to_datetime(df['time']).dt.floor(f'{self.sweep_window_seconds}S')
        exchanges_per_window = df.groupby('time_rounded')['exchange'].nunique()
        max_exchanges = exchanges_per_window.max() if len(exchanges_per_window) > 0 else 0
        has_sweep = max_exchanges > 1

        # 3. Aggressive buying (price trending up = hitting ask)
        df_sorted = df.sort_values('time')
        df_sorted['price_change'] = df_sorted['price'].diff()

        # Count volume at higher prices (aggressive buys)
        aggressive_volume = df_sorted[df_sorted['price_change'] > 0]['size'].sum()
        aggressive_ratio = aggressive_volume / total_volume if total_volume > 0 else 0
        is_aggressive = aggressive_ratio >= self.aggressive_threshold

        return {
            'ticker': ticker,
            'strike': strike,
            'right': right,
            'expiration': expiration,
            'total_volume': int(total_volume),
            'largest_trade': int(largest_trade),
            'avg_trade_size': float(avg_trade_size),
            'total_trades': total_trades,
            'premium_flow': float(premium_flow),
            'block_trade': has_block,
            'is_sweep': has_sweep,
            'sweep_exchanges': int(max_exchanges),
            'aggressive_buy': is_aggressive,
            'aggressive_ratio': float(aggressive_ratio),
            'last_trade_time': df['time'].max()
        }

    def _generate_alerts(self, flow_data: Dict, ticker: str) -> List[Dict]:
        """Generate actionable alerts from flow data"""
        alerts = []
        stats = flow_data['flow_stats']

        # Alert 1: Large put block trades (bearish institutional)
        put_blocks = [b for b in flow_data['block_trades'] if b['right'] == 'P']
        if put_blocks:
            total_put_contracts = sum(b['largest_trade'] for b in put_blocks)
            total_put_premium = sum(b['premium_flow'] for b in put_blocks)

            if total_put_premium > 500000:  # $500k+
                alerts.append({
                    'type': 'WARNING',
                    'severity': 'HIGH',
                    'title': '🚨 INSTITUTIONAL PUT BLOCKS',
                    'message': f"{len(put_blocks)} large put blocks totaling {total_put_contracts:,} contracts",
                    'premium': f"${total_put_premium:,.0f}",
                    'recommendation': f"🛑 AVOID selling puts on {ticker} - Institutions hedging/betting on downside",
                    'timestamp': datetime.now()
                })

        # Alert 2: Put sweeps (very aggressive bearish)
        put_sweeps = [s for s in flow_data['sweeps'] if s['right'] == 'P']
        if put_sweeps:
            alerts.append({
                'type': 'WARNING',
                'severity': 'CRITICAL',
                'title': '💥 PUT SWEEP ALERT',
                'message': f"{len(put_sweeps)} put sweeps detected (multi-exchange aggressive buying)",
                'recommendation': f"🚨 URGENT: Do not sell puts on {ticker} - Smart money expecting sharp drop",
                'timestamp': datetime.now()
            })

        # Alert 3: Heavy call flow (IV expansion opportunity)
        call_flow = stats['call_flow']
        if call_flow > 1000000:  # $1M+
            alerts.append({
                'type': 'INFO',
                'severity': 'MEDIUM',
                'title': '💡 HEAVY CALL FLOW',
                'message': f"${call_flow:,.0f} in call premium flow detected",
                'recommendation': f"IV likely to expand on {ticker} - Wait for higher covered call premiums",
                'timestamp': datetime.now()
            })

        # Alert 4: Extreme put/call imbalance
        if stats['put_flow'] > 0 and stats['call_flow'] > 0:
            put_call_ratio = stats['put_flow'] / stats['call_flow']

            if put_call_ratio > 3.0:
                alerts.append({
                    'type': 'WARNING',
                    'severity': 'HIGH',
                    'title': '⚠️ BEARISH FLOW DOMINANCE',
                    'message': f"Put flow is {put_call_ratio:.1f}x call flow",
                    'recommendation': f"Strong bearish positioning on {ticker} - Reduce put-selling exposure",
                    'timestamp': datetime.now()
                })

        # Alert 5: All clear
        if not alerts:
            alerts.append({
                'type': 'SUCCESS',
                'severity': 'LOW',
                'title': '✅ NO UNUSUAL ACTIVITY',
                'message': 'Normal options flow detected',
                'recommendation': f"No red flags for selling puts on {ticker}",
                'timestamp': datetime.now()
            })

        return alerts

    def _print_summary(self, flow_data: Dict, ticker: str):
        """Print flow analysis summary"""
        stats = flow_data['flow_stats']

        print(f"\n{'='*60}")
        print(f"📊 FLOW ANALYSIS SUMMARY: {ticker}")
        print(f"{'='*60}")
        print(f"\n💰 Premium Flow:")
        print(f"   Total: ${stats['total_premium_flow']:,.0f}")
        print(f"   Puts:  ${stats['put_flow']:,.0f}")
        print(f"   Calls: ${stats['call_flow']:,.0f}")

        print(f"\n📈 Volume:")
        print(f"   Total Contracts: {stats['total_contracts']:,}")

        print(f"\n🎯 Unusual Activity:")
        print(f"   Block Trades: {len(flow_data['block_trades'])}")
        print(f"   Sweeps: {len(flow_data['sweeps'])}")
        print(f"   Aggressive Buys: {len(flow_data['aggressive_buys'])}")

        print(f"\n🚨 ALERTS ({len(flow_data['alerts'])}):")
        for alert in flow_data['alerts']:
            severity_emoji = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }.get(alert['severity'], '⚪')

            print(f"\n{severity_emoji} {alert['title']}")
            print(f"   {alert['message']}")
            print(f"   → {alert['recommendation']}")

        print(f"\n{'='*60}\n")

    def _empty_result(self) -> Dict:
        """Return empty flow result"""
        return {
            'block_trades': [],
            'sweeps': [],
            'aggressive_buys': [],
            'flow_stats': {
                'total_premium_flow': 0,
                'put_flow': 0,
                'call_flow': 0,
                'total_contracts': 0
            },
            'alerts': []
        }

    def _empty_tick_result(self) -> Dict:
        """Return empty tick analysis result"""
        return {
            'total_volume': 0,
            'largest_trade': 0,
            'avg_trade_size': 0,
            'total_trades': 0,
            'premium_flow': 0,
            'block_trade': False,
            'is_sweep': False,
            'sweep_exchanges': 0,
            'aggressive_buy': False,
            'aggressive_ratio': 0
        }
