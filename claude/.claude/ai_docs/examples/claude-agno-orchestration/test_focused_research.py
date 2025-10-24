#!/usr/bin/env python3
"""
Focused Research Test - Simplified query to avoid token limits
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

def test_focused_research():
    """Run focused research with smaller scope"""

    print("\n" + "=" * 80)
    print("FOCUSED FUSION ENERGY RESEARCH")
    print("=" * 80)
    print()

    # Setup tools
    tools = []
    if HAS_TOOLS:
        print("✅ Using OllamaWebTools")
        tools.append(OllamaWebTools(cache_results=True, cache_ttl=3600))
    else:
        print("⚠️  No web tools - simulated research")

    # Simpler configuration with shorter output
    config = AgentConfig(
        name="FocusedResearcher",
        model_id="claude-sonnet-4",
        temperature=0.3,
        max_tokens=4000,  # Reduced to avoid body too large
        markdown=True
    )

    agent = AdaptiveDeepResearchAgent(config, tools=tools)

    # FOCUSED query (not 5 topics, just 2)
    query = """Research recent fusion energy breakthroughs in 2024-2025.

Focus on:
1. NIF (National Ignition Facility) net energy gain status
2. Commonwealth Fusion Systems progress

Keep response under 3000 words."""

    print(f"Query: {query}")
    print(f"Complexity: {agent._detect_complexity(query)}")
    print()
    print("⏳ Executing focused research...")
    print()

    result = agent.run(query)

    print("=" * 80)
    print("RESULT")
    print("=" * 80)
    print()

    if result.success:
        print(f"✅ Success")
        print(f"⏱️  Duration: {result.duration:.2f}s")
        print(f"📏 Length: {len(result.content):,} chars")
        print()
        print("=" * 80)
        print("REPORT")
        print("=" * 80)
        print()
        print(result.content)
        print()
        print("=" * 80)

        # Save
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"fusion_focused_{timestamp}.md"

        with open(report_file, 'w') as f:
            f.write(f"# Focused Fusion Energy Research\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Duration:** {result.duration:.2f}s\n\n")
            f.write(f"**Tools:** {len(tools)} ({', '.join([type(t).__name__ for t in tools]) if tools else 'None'})\n\n")
            f.write("---\n\n")
            f.write(result.content)

        print(f"\n💾 Saved to: {report_file.absolute()}")

        # Quick quality check
        has_structure = '##' in result.content
        has_citations = '[' in result.content and ']' in result.content
        has_findings = 'finding' in result.content.lower() or 'result' in result.content.lower()

        print("\n" + "=" * 80)
        print("QUALITY CHECK")
        print("=" * 80)
        status = "✅" if has_structure else "❌"
        print(f"  {status} Structured format (headings)")
        status = "✅" if has_citations else "❌"
        print(f"  {status} Citations present")
        status = "✅" if has_findings else "❌"
        print(f"  {status} Findings/results")
        print(f"  📊 Total words: {len(result.content.split()):,}")

    else:
        print(f"❌ Failed: {result.error}")
        print("\nError likely due to:")
        print("- Request body too large (reduce max_tokens or simplify query)")
        print("- Network timeout")
        print("- Model availability")

if __name__ == "__main__":
    test_focused_research()
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print()
