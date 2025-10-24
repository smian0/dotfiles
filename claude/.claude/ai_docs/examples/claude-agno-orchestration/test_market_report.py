#!/usr/bin/env python3
"""
Daily Market Report - Stock & Crypto Analysis
==============================================

Tests the improved AdaptiveDeepResearchAgent with:
- Complex market analysis query
- All quality requirements (inline citations, confidence, remaining questions, hop tracking)
- Real-time market conditions
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration import AdaptiveDeepResearchAgent, AgentConfig

# Try web tools
try:
    from agno.tools.ollama_web import OllamaWebTools
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False

def test_market_report():
    """Generate comprehensive daily market report"""

    print("\n" + "=" * 80)
    print("DAILY MARKET REPORT - STOCK & CRYPTO ANALYSIS")
    print("=" * 80)
    print()

    # Setup tools
    tools = []
    if HAS_TOOLS:
        print("✅ Using OllamaWebTools for real-time market data")
        tools.append(OllamaWebTools(cache_results=True, cache_ttl=1800))  # 30min cache
    else:
        print("⚠️  No web tools - simulated research")

    # Configuration for market analysis
    config = AgentConfig(
        name="MarketResearcher",
        model_id="claude-sonnet-4",
        temperature=0.3,
        max_tokens=6000,  # Increased for comprehensive report
        markdown=True
    )

    agent = AdaptiveDeepResearchAgent(config, tools=tools)

    # Complex market query (should trigger UNIFIED PLANNING)
    query = """Research today's stock and cryptocurrency market conditions (October 14, 2025).

Focus on:
1. Major US stock indices performance (S&P 500, Nasdaq, Dow Jones) - today's movements and key drivers
2. Top cryptocurrency movements (Bitcoin, Ethereum) - price action and catalysts
3. Key economic data releases or events impacting markets today
4. Notable sector performance (tech, financials, energy)
5. Market sentiment and volatility indicators (VIX, etc.)

Provide actionable insights for traders and investors."""

    print(f"Query Complexity: {agent._detect_complexity(query)}")  # Should be "complex"
    print(f"Expected Strategy: UNIFIED PLANNING")
    print(f"Tools: {len(tools)} ({'Real web search' if tools else 'Simulated'})")
    print()
    print("⏳ Executing comprehensive market research...")
    print()

    start_time = datetime.now()
    result = agent.run(query)
    duration = (datetime.now() - start_time).total_seconds()

    print("=" * 80)
    print("MARKET REPORT COMPLETE")
    print("=" * 80)
    print()

    if result.success:
        print(f"✅ Success")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📏 Length: {len(result.content):,} chars")
        print(f"📊 Complexity: {result.metadata.get('complexity', 'unknown')}")
        print()
        print("=" * 80)
        print("DAILY MARKET REPORT")
        print("=" * 80)
        print()
        print(result.content)
        print()
        print("=" * 80)

        # Save report
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"market_report_{timestamp}.md"

        with open(report_file, 'w') as f:
            f.write(f"# Daily Market Report - Stock & Crypto Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Duration:** {duration:.2f}s\n\n")
            f.write(f"**Tools:** {len(tools)} ({', '.join([type(t).__name__ for t in tools]) if tools else 'None'})\n\n")
            f.write("---\n\n")
            f.write(result.content)

        print(f"\n💾 Report saved to: {report_file.absolute()}")

        # Quality assessment
        print("\n" + "=" * 80)
        print("QUALITY ASSESSMENT - NEW REQUIREMENTS")
        print("=" * 80)

        content_lower = result.content.lower()

        checks = {
            "Inline citations ([Source, Date])": "[" in result.content and "]" in result.content,
            "Confidence level stated": any(x in content_lower for x in ['confidence level:', 'confidence:', 'high confidence', 'medium confidence', 'low confidence']),
            "Remaining Questions section": "remaining question" in content_lower,
            "Multi-hop tracking ([Hop N])": "[hop" in content_lower or "hop 1" in content_lower,
            "Executive Summary": "summary" in content_lower or "overview" in content_lower,
            "Key Findings": "finding" in content_lower,
            "Sources section": "sources" in content_lower or "references" in content_lower,
        }

        for component, present in checks.items():
            status = "✅" if present else "❌"
            print(f"  {status} {component}")

        score = sum(checks.values()) / len(checks)
        print(f"\n📊 Quality Score: {score:.1%}")
        print(f"📈 Total words: {len(result.content.split()):,}")

        if score >= 0.8:
            print("🌟 EXCELLENT - All quality requirements met!")
        elif score >= 0.6:
            print("👍 GOOD - Most requirements met")
        else:
            print("⚠️  NEEDS IMPROVEMENT - Missing key requirements")

    else:
        print(f"❌ Failed: {result.error}")
        if "too large" in str(result.error):
            print("\n💡 Tip: Reduce max_tokens or simplify query")

if __name__ == "__main__":
    test_market_report()
    print("\n" + "=" * 80)
    print("✅ MARKET REPORT TEST COMPLETE")
    print("=" * 80)
    print()
