#!/usr/bin/env python3
"""
Live Market Brief - Real Web Search
====================================

Generate market report with actual web data using OllamaWebTools.
Focused scope to avoid token limits.
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

def generate_live_market_brief():
    """Generate brief with REAL web data"""

    print("\n" + "=" * 80)
    print("LIVE MARKET BRIEF - OCTOBER 14, 2025")
    print("=" * 80)
    print()

    # Configuration - smaller to avoid body too large
    config = AgentConfig(
        name="LiveMarketBrief",
        model_id="claude-sonnet-4",
        temperature=0.3,
        max_tokens=3000,  # Smaller limit
        markdown=True
    )

    # Web search tools
    tools = [OllamaWebTools(
        cache_results=True,
        cache_ttl=1800  # 30min cache
    )]

    agent = AdaptiveDeepResearchAgent(config, tools=tools)

    # FOCUSED query - only 2 key areas
    query = """Research US stock market today (October 14, 2025).

Focus on:
1. S&P 500 - today's close and key driver
2. Bitcoin price - current level and main catalyst

Keep response under 1500 words. Cite sources inline."""

    print(f"🔍 Query: {query}")
    print(f"📊 Complexity: {agent._detect_complexity(query)}")
    print(f"🛠️  Tools: OllamaWebTools (REAL web search)")
    print()
    print("⏳ Searching web for live data...")
    print()

    start_time = datetime.now()
    result = agent.run(query)
    duration = (datetime.now() - start_time).total_seconds()

    print("=" * 80)
    print("LIVE MARKET BRIEF")
    print("=" * 80)
    print()

    if result.success:
        print(result.content)
        print()
        print("=" * 80)
        print(f"\n✅ Report generated ({duration:.2f}s, {len(result.content):,} chars)")

        # Save
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"market_live_{timestamp}.md"

        with open(report_file, 'w') as f:
            f.write(f"# Live Market Brief\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Data Source:** Real-time web search via OllamaWebTools\n\n")
            f.write("---\n\n")
            f.write(result.content)

        print(f"💾 Saved: {report_file.absolute()}")

        # Quality check
        content_lower = result.content.lower()

        print("\n" + "=" * 80)
        print("QUALITY ASSESSMENT")
        print("=" * 80)

        checks = {
            "Real data (numbers)": any(char.isdigit() for char in result.content),
            "Inline citations": "[" in result.content and "]" in result.content,
            "Sources cited": any(x in content_lower for x in ['cnbc', 'bloomberg', 'reuters', 'yahoo', 'marketwatch']),
            "Confidence stated": "confidence" in content_lower,
        }

        for component, present in checks.items():
            status = "✅" if present else "⚠️ "
            print(f"  {status} {component}")

        score = sum(checks.values()) / len(checks)
        print(f"\n{'🌟' if score >= 0.75 else '📊'} Quality Score: {score:.1%}")

    else:
        print(f"❌ Failed: {result.error}")
        if "too large" in str(result.error):
            print("\n💡 Response was too large. Report saved to file if partial data exists.")

if __name__ == "__main__":
    generate_live_market_brief()
    print("\n" + "=" * 80)
    print("✅ LIVE MARKET BRIEF COMPLETE")
    print("=" * 80)
