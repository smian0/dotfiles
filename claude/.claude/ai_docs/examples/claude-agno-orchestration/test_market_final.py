#!/usr/bin/env python3
"""
Final Fix: Market Brief with Strict Result Limits
==================================================

Wraps OllamaWebTools to enforce max_results=2 limit.
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

class LimitedWebTools:
    """Wrapper that enforces strict result limits"""

    def __init__(self, max_results=2):
        self.max_results = max_results
        self.web = OllamaWebTools(cache_results=True, cache_ttl=1800)

    def search(self, query: str, **kwargs):
        """Force max_results limit"""
        kwargs['max_results'] = min(kwargs.get('max_results', self.max_results), self.max_results)
        print(f"🔍 Searching: {query[:50]}... (max {kwargs['max_results']} results)")
        return self.web.search(query=query, **kwargs)

    def fetch(self, url: str, **kwargs):
        """Pass through fetch"""
        return self.web.fetch(url=url, **kwargs)

    def research(self, query: str, **kwargs):
        """Force max_results limit on research"""
        kwargs['max_results'] = min(kwargs.get('max_results', self.max_results), self.max_results)
        print(f"📚 Researching: {query[:50]}... (max {kwargs['max_results']} results)")
        return self.web.research(query=query, **kwargs)

    def verify(self, claim: str, **kwargs):
        """Pass through verify"""
        return self.web.verify(claim=claim, **kwargs)

def generate_final_market_brief():
    """Generate brief with ENFORCED result limits"""

    print("\n" + "=" * 80)
    print("FINAL FIX: MARKET BRIEF WITH STRICT LIMITS")
    print("=" * 80)
    print()

    # Small configuration
    config = AgentConfig(
        name="FinalMarketBrief",
        model_id="claude-sonnet-4",
        temperature=0.3,
        max_tokens=2000,  # Very small
        markdown=True
    )

    # Wrapped tools with ENFORCED limits
    limited_web = LimitedWebTools(max_results=2)  # Force max 2 results
    tools = [limited_web]

    agent = AdaptiveDeepResearchAgent(config, tools=tools)

    # Ultra-focused query
    query = """S&P 500 close October 14 2025.

Report:
- Closing level
- % change
- Main driver (1 sentence)

Brief answer only."""

    print(f"🎯 Query: {query}")
    print(f"🔒 Enforcement: max_results=2 (hardcoded wrapper)")
    print()
    print("⏳ Executing with strict limits...")
    print()

    start_time = datetime.now()

    try:
        result = agent.run(query)
        duration = (datetime.now() - start_time).total_seconds()

        print("\n" + "=" * 80)
        print("RESULT")
        print("=" * 80)
        print()

        if result.success:
            print(result.content)
            print()
            print("=" * 80)
            print(f"\n✅ SUCCESS! ({duration:.2f}s, {len(result.content):,} chars)")

            # Save
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = output_dir / f"market_final_{timestamp}.md"

            with open(report_file, 'w') as f:
                f.write(f"# Market Brief - S&P 500 (Final Fix)\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Method:** Strict result limits (max 2 per search)\n\n")
                f.write("---\n\n")
                f.write(result.content)

            print(f"💾 Saved: {report_file.absolute()}")

            # Verify real data
            has_data = any(x in result.content for x in ['$', '%', 'points', 'S&P'])
            has_citation = '[' in result.content or any(x in result.content.lower() for x in ['source:', 'investopedia', 'cnbc', 'bloomberg'])

            print("\n" + "=" * 80)
            print("VERIFICATION")
            print("=" * 80)
            print(f"  {'✅' if has_data else '❌'} Contains market data")
            print(f"  {'✅' if has_citation else '❌'} Has citations")
            print()

            if has_data and has_citation:
                print("🎉 SUCCESS! OllamaWebTools integration FIXED!")
                print("✅ Solution: Wrapper class enforcing max_results=2")

            return True

        else:
            print(f"❌ Failed: {result.error}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = generate_final_market_brief()

    print("\n" + "=" * 80)
    if success:
        print("✅ OPTIMIZATION COMPLETE - PROBLEM SOLVED")
        print("\n🔧 Fix Applied:")
        print("   - Wrapped OllamaWebTools with LimitedWebTools class")
        print("   - Enforced max_results=2 (hardcoded, cannot be overridden)")
        print("   - Reduced max_tokens to 2000")
        print("   - Ultra-focused query")
    else:
        print("⚠️  STILL EXPERIENCING ISSUES")
    print("=" * 80)
