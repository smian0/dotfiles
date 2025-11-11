#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "agno",
#     "yfinance>=0.2.40",
#     "pandas>=2.0.0",
# ]
# ///
"""
Market Analysis Workflow: Teams + yfinance Tools + Workflow

Demonstrates:
1. Custom yfinance tools for agents
2. Team of specialist analysts (fundamental, technical, risk)
3. Workflow: data gathering → collaborative analysis → report generation
4. Real market data from Yahoo Finance

Pattern: Workflow → [Data Fetch, Team Analysis, Report Generation]
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import yfinance as yf
from typing import Optional
from agno.agent import Agent
from agno.team import Team
from agno.workflow import Workflow, Step, StepOutput
from agno.models.ollama import Ollama
from agno.tools import Toolkit


# ==============================================================================
# Custom yfinance Tools for Agents
# ==============================================================================

class YFinanceTools(Toolkit):
    """Custom tools for stock market analysis using yfinance"""

    def __init__(self):
        super().__init__(name="yfinance_tools")
        self.register(self.get_stock_info)
        self.register(self.get_price_history)
        self.register(self.get_financials)
        self.register(self.get_key_metrics)

    def get_stock_info(self, ticker: str) -> str:
        """Get company info and current market data.

        Args:
            ticker: Stock ticker symbol (e.g., AAPL, MSFT)
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return f"""## {info.get('longName', ticker)} ({ticker})

**Sector**: {info.get('sector', 'N/A')}
**Industry**: {info.get('industry', 'N/A')}
**Market Cap**: ${info.get('marketCap', 0):,.0f}
**Current Price**: ${info.get('currentPrice', 0):.2f}
**52-Week Range**: ${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}
**Average Volume**: {info.get('averageVolume', 0):,.0f}
**P/E Ratio**: {info.get('trailingPE', 'N/A')}
**Dividend Yield**: {info.get('dividendYield', 0) * 100:.2f}%
**Beta**: {info.get('beta', 'N/A')}

**Business Summary**: {info.get('longBusinessSummary', 'N/A')[:500]}...
"""
        except Exception as e:
            return f"Error fetching info for {ticker}: {str(e)}"

    def get_price_history(self, ticker: str, period: str = "3mo") -> str:
        """Get historical price data.

        Args:
            ticker: Stock ticker symbol
            period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                return f"No price history available for {ticker}"

            current = hist['Close'].iloc[-1]
            start = hist['Close'].iloc[0]
            change_pct = ((current - start) / start) * 100

            high = hist['High'].max()
            low = hist['Low'].min()
            avg_volume = hist['Volume'].mean()

            # Calculate volatility (standard deviation of returns)
            returns = hist['Close'].pct_change()
            volatility = returns.std() * 100

            return f"""## Price History ({period})

**Period Return**: {change_pct:+.2f}%
**High**: ${high:.2f}
**Low**: ${low:.2f}
**Current**: ${current:.2f}
**Average Volume**: {avg_volume:,.0f}
**Volatility (Daily)**: {volatility:.2f}%

**Recent 5-Day Prices**:
{hist['Close'].tail().to_string()}
"""
        except Exception as e:
            return f"Error fetching price history for {ticker}: {str(e)}"

    def get_financials(self, ticker: str) -> str:
        """Get latest financial statements.

        Args:
            ticker: Stock ticker symbol
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Key financial metrics from info
            revenue = info.get('totalRevenue', 0)
            net_income = info.get('netIncomeToCommon', 0)
            total_assets = info.get('totalAssets', 0)
            total_debt = info.get('totalDebt', 0)
            free_cash_flow = info.get('freeCashflow', 0)

            return f"""## Financial Overview

**Revenue**: ${revenue:,.0f}
**Net Income**: ${net_income:,.0f}
**Total Assets**: ${total_assets:,.0f}
**Total Debt**: ${total_debt:,.0f}
**Free Cash Flow**: ${free_cash_flow:,.0f}

**Profitability**:
- Profit Margin: {info.get('profitMargins', 0) * 100:.2f}%
- Operating Margin: {info.get('operatingMargins', 0) * 100:.2f}%
- ROE: {info.get('returnOnEquity', 0) * 100:.2f}%
- ROA: {info.get('returnOnAssets', 0) * 100:.2f}%

**Valuation**:
- P/E Ratio: {info.get('trailingPE', 'N/A')}
- Forward P/E: {info.get('forwardPE', 'N/A')}
- P/B Ratio: {info.get('priceToBook', 'N/A')}
- EV/EBITDA: {info.get('enterpriseToEbitda', 'N/A')}
"""
        except Exception as e:
            return f"Error fetching financials for {ticker}: {str(e)}"

    def get_key_metrics(self, ticker: str) -> str:
        """Get key risk and growth metrics.

        Args:
            ticker: Stock ticker symbol
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return f"""## Key Metrics

**Risk Metrics**:
- Beta: {info.get('beta', 'N/A')}
- 52-Week Change: {info.get('52WeekChange', 0) * 100:.2f}%
- Short % of Float: {info.get('shortPercentOfFloat', 0) * 100:.2f}%

**Growth**:
- Revenue Growth: {info.get('revenueGrowth', 0) * 100:.2f}%
- Earnings Growth: {info.get('earningsGrowth', 0) * 100:.2f}%
- Target Price: ${info.get('targetMeanPrice', 0):.2f}

**Analyst Ratings**:
- Recommendation: {info.get('recommendationKey', 'N/A').upper()}
- Number of Analysts: {info.get('numberOfAnalystOpinions', 'N/A')}
"""
        except Exception as e:
            return f"Error fetching key metrics for {ticker}: {str(e)}"


# ==============================================================================
# Data Fetching Step (Custom Executor)
# ==============================================================================

def fetch_market_data(step_output):
    """Fetch comprehensive market data for the ticker using yfinance"""

    # Extract ticker from input (format: "AAPL" or "analyze AAPL")
    input_text = step_output.input if hasattr(step_output, 'input') else str(step_output)
    ticker = input_text.strip().upper().split()[-1]

    tools = YFinanceTools()

    # Gather all data
    info = tools.get_stock_info(ticker)
    price_history = tools.get_price_history(ticker, period="3mo")
    financials = tools.get_financials(ticker)
    key_metrics = tools.get_key_metrics(ticker)

    data = f"""# Market Data for {ticker}

{info}

{price_history}

{financials}

{key_metrics}

---
**Data Source**: Yahoo Finance (yfinance)
**Retrieved**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return StepOutput(
        content=data,
    )


# ==============================================================================
# Analyst Team Members
# ==============================================================================

fundamental_analyst = Agent(
    name="Fundamental Analyst",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Analyze financial fundamentals and valuation",
    instructions=[
        "Review the company's financial data, profitability metrics, and valuation ratios.",
        "Assess financial health: revenue, profits, cash flow, debt levels.",
        "Evaluate valuation: Is the stock overvalued, undervalued, or fairly valued?",
        "Identify fundamental strengths and weaknesses.",
        "Provide 3-4 key fundamental insights in 5-6 sentences.",
    ],
    markdown=True,
)

technical_analyst = Agent(
    name="Technical Analyst",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Analyze price trends and technical indicators",
    instructions=[
        "Review price history, volatility, and trading volume.",
        "Identify trends: Is the stock in uptrend, downtrend, or consolidating?",
        "Assess momentum and volatility patterns.",
        "Evaluate risk from technical perspective (52-week range, beta).",
        "Provide 3-4 key technical insights in 5-6 sentences.",
    ],
    markdown=True,
)

risk_analyst = Agent(
    name="Risk Analyst",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Assess investment risks and growth potential",
    instructions=[
        "Review risk metrics: beta, volatility, short interest, analyst consensus.",
        "Evaluate growth metrics: revenue growth, earnings growth, target price.",
        "Identify key risks: market risk, company-specific risks, sector risks.",
        "Assess risk-reward balance and growth sustainability.",
        "Provide 3-4 key risk/reward insights in 5-6 sentences.",
    ],
    markdown=True,
)


# ==============================================================================
# Analysis Team
# ==============================================================================

analysis_team = Team(
    name="Market Analysis Team",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    members=[fundamental_analyst, technical_analyst, risk_analyst],
    instructions=[
        "You coordinate a comprehensive market analysis.",
        "First, ask the Fundamental Analyst to assess financial health and valuation.",
        "Second, ask the Technical Analyst to evaluate price trends and momentum.",
        "Third, ask the Risk Analyst to identify risks and growth potential.",
        "Finally, provide a brief synthesis highlighting the key insights from all three perspectives.",
    ],
    show_members_responses=True,
)


# ==============================================================================
# Report Writer
# ==============================================================================

report_writer = Agent(
    name="Report Writer",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Generate comprehensive market analysis report",
    instructions=[
        "Review the raw market data and the team's collaborative analysis.",
        "Create a professional market analysis report with the following structure:",
        "1. Executive Summary (2-3 sentences)",
        "2. Company Overview (brief, from data)",
        "3. Fundamental Analysis (key points from fundamental analyst)",
        "4. Technical Analysis (key points from technical analyst)",
        "5. Risk Assessment (key points from risk analyst)",
        "6. Investment Thesis (synthesis of all analyses, 3-4 sentences)",
        "7. Key Metrics Table (market cap, P/E, beta, etc.)",
        "Use professional markdown formatting with proper headings and bullet points.",
    ],
    markdown=True,
)


# ==============================================================================
# Market Analysis Workflow
# ==============================================================================

market_analysis_workflow = Workflow(
    name="Market Analysis Workflow",
    description="Comprehensive market analysis using yfinance data and analyst team",
    steps=[
        # Step 1: Fetch market data
        Step(
            name="Fetch Market Data",
            executor=fetch_market_data,
            description="Retrieve comprehensive market data from yfinance",
        ),

        # Step 2: Collaborative analysis by team
        Step(
            name="Analyst Team Review",
            team=analysis_team,
            description="Team of specialists analyzes market data collaboratively",
        ),

        # Step 3: Generate final report
        Step(
            name="Generate Report",
            agent=report_writer,
            description="Create professional market analysis report",
        ),
    ],
)


# ==============================================================================
# CLI Execution
# ==============================================================================

if __name__ == "__main__":
    import sys

    # Get ticker from command line or use default
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"

    print("="*80)
    print(f"Market Analysis Workflow: {ticker}")
    print("="*80 + "\n")

    try:
        result = market_analysis_workflow.run(
            input=ticker,
            stream=False,
        )

        if result and result.content:
            print("\n" + "="*80)
            print("✅ Market Analysis Complete")
            print("="*80 + "\n")
            print(result.content)
        else:
            print("❌ Workflow returned no content")

    except Exception as e:
        print(f"❌ Error during workflow execution: {e}")
        import traceback
        traceback.print_exc()
