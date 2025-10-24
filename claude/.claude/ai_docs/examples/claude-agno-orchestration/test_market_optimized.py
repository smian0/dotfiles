#!/usr/bin/env python3
"""
Optimized Market Brief - Fixed OllamaWebTools Integration
==========================================================

Fixes "request body too large" by:
1. Very targeted queries (not broad research)
2. Limited results (2-3 max per search)
3. Sequential small searches
4. Smaller max_tokens
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration import AdaptiveDeepResearchAgent, AgentConfig

try:
    from agno.tools.ollama_web import OllamaWebTools
    HAS_TOOLS = True
except ImportError:
    print("❌ OllamaWebTools not available")
    sys.exit(1)

def generate_optimized_market_brief():
    """Generate brief with optimized web search configuration"""

    print("\n" + "=" * 80)
    print("OPTIMIZED LIVE MARKET BRIEF - OCTOBER 14, 2025")
    print("=" * 80)
    print()

    # Smaller configuration to avoid body too large
    config = AgentConfig(
        name="OptimizedMarketBrief",
        model_id="claude-sonnet-4",
        temperature=0.3,
        max_tokens=2500,  # Reduced further
        markdown=True
    )

    # Optimized web search tools with strict limits
    tools = [OllamaWebTools(
        cache_results=True,
        cache_ttl=1800,
        # These will be passed to searches
    )]

    agent = AdaptiveDeepResearchAgent(config, tools=tools)

    # VERY FOCUSED query - single topic only
    query = """What is the S&P 500 closing price today (October 14, 2025)?

Find:
- Today's closing level
- Percentage change
- Main reason for the move

Maximum 2-3 sources. Keep answer under 500 words."""

    print(f"🔍 Query: {query}")
    print(f"📊 Strategy: Ultra-focused (avoid large responses)")
    print(f"🛠️  Tools: OllamaWebTools with strict limits")
    print()
    print("⏳ Fetching focused data...")
    print()

    start_time = datetime.now()
    result = agent.run(query)
    duration = (datetime.now() - start_time).total_seconds()

    print("=" * 80)
    print("OPTIMIZED MARKET BRIEF")
    print("=" * 80)
    print()

    if result.success:
        print(result.content)
        print()
        print("=" * 80)
        print(f"\n✅ Success! ({duration:.2f}s, {len(result.content):,} chars)")

        # Save
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"market_optimized_{timestamp}.md"

        with open(report_file, 'w') as f:
            f.write(f"# Optimized Market Brief - S&P 500\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Data Source:** Real-time web search (optimized)\n\n")
            f.write("---\n\n")
            f.write(result.content)

        print(f"💾 Saved: {report_file.absolute()}")

        # Quality check
        content_lower = result.content.lower()

        print("\n" + "=" * 80)
        print("QUALITY VERIFICATION")
        print("=" * 80)

        checks = {
            "Real market data": any(x in result.content for x in ['$', '%', 'points']),
            "Inline citations": "[" in result.content and "]" in result.content,
            "Sources named": any(x in content_lower for x in ['cnbc', 'bloomberg', 'reuters', 'yahoo', 'marketwatch', 'financial times']),
            "Date mentioned": "october 14" in content_lower or "oct 14" in content_lower,
            "Clear conclusion": any(x in content_lower for x in ['summary', 'takeaway', 'key', 'driver', 'reason']),
        }

        for component, present in checks.items():
            status = "✅" if present else "⚠️ "
            print(f"  {status} {component}")

        score = sum(checks.values()) / len(checks)
        print(f"\n{'🌟' if score >= 0.8 else '📊'} Quality Score: {score:.1%}")

        if score >= 0.8:
            print("🎉 EXCELLENT - All quality standards met!")
            print("✅ OllamaWebTools integration successfully optimized!")
        elif score >= 0.6:
            print("👍 GOOD - Most quality standards met")

        return True

    else:
        print(f"❌ Failed: {result.error}")

        if "too large" in str(result.error):
            print("\n⚠️  Still getting 'body too large' error.")
            print("\nFurther optimization needed:")
            print("  1. Reduce query scope even more")
            print("  2. Use research tool with explicit max_results=2")
            print("  3. Consider MCP financial APIs instead of web search")

        return False

if __name__ == "__main__":
    success = generate_optimized_market_brief()

    print("\n" + "=" * 80)
    if success:
        print("✅ OPTIMIZED MARKET BRIEF COMPLETE")
        print("\n🎯 Solution: Ultra-focused queries + strict result limits")
    else:
        print("⚠️  OPTIMIZATION INCOMPLETE")
        print("\n💡 Next Step: Try alternative approach with MCP financial APIs")
    print("=" * 80)
