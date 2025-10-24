#!/usr/bin/env python3
"""
Full Research Test with AdaptiveDeepResearchAgent
=================================================

Tests the agent with real web search tools and generates a complete research report.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration import AdaptiveDeepResearchAgent

# Try to import web search tools
try:
    from agno.tools.ollama_web import OllamaWebTools
    HAS_OLLAMA_WEB = True
except ImportError:
    HAS_OLLAMA_WEB = False
    print("⚠️  OllamaWebTools not available")

try:
    from duckduckgo_search import DDGS
    HAS_DUCKDUCKGO = True
except ImportError:
    HAS_DUCKDUCKGO = False
    print("⚠️  DuckDuckGo not available")


def create_simple_ddg_tool():
    """Create a simple DuckDuckGo search tool for Agno"""
    class SimpleDDGTool:
        def __name__(self):
            return "web_search"

        def search(self, query: str, max_results: int = 5):
            """Search using DuckDuckGo"""
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_results))

                    # Format results
                    formatted = []
                    for r in results:
                        formatted.append({
                            'title': r.get('title', ''),
                            'url': r.get('href', ''),
                            'snippet': r.get('body', ''),
                        })
                    return formatted
            except Exception as e:
                return [{'error': str(e)}]

    return SimpleDDGTool()


def test_full_research():
    """Run complete research with tools"""

    print("\n" + "=" * 80)
    print("FULL RESEARCH TEST - AdaptiveDeepResearchAgent")
    print("=" * 80)
    print()

    # Setup tools
    tools = []

    if HAS_OLLAMA_WEB:
        print("✅ Using OllamaWebTools for research")
        ollama_web = OllamaWebTools(
            cache_results=True,
            cache_ttl=3600
        )
        tools.append(ollama_web)
    elif HAS_DUCKDUCKGO:
        print("✅ Using DuckDuckGo for research")
        ddg_tool = create_simple_ddg_tool()
        tools.append(ddg_tool)
    else:
        print("⚠️  No web search tools available")
        print("    Installing: pip install duckduckgo-search")
        print("    Or: Configure Agno with OllamaWebTools")
        print()
        print("    Running without tools (simulated research)...")
        print()

    # Create agent
    agent = AdaptiveDeepResearchAgent(tools=tools)

    # Research query
    query = """Research the current state of fusion energy development in 2024-2025.

Focus on:
1. Major breakthrough announcements (NIF net energy gain follow-up, etc.)
2. Commercial viability timeline
3. Key players (ITER, Commonwealth Fusion, TAE, Helion)
4. Investment trends
5. Technical challenges remaining
"""

    print("Research Query:")
    print("-" * 80)
    print(query)
    print("-" * 80)
    print()

    # Detect complexity
    complexity = agent._detect_complexity(query)
    print(f"📊 Detected Complexity: {complexity}")
    print(f"🔧 Strategy: {'UNIFIED PLANNING' if complexity == 'complex' else complexity.upper()}")
    print(f"🛠️  Tools Available: {len(tools)}")
    print()

    if tools:
        print("🔍 Agent will execute REAL web research using provided tools")
    else:
        print("⚠️  Agent will simulate research (no actual web calls)")

    print()
    print("⏳ Executing research (may take 30-60 seconds)...")
    print()

    # Execute
    start_time = datetime.now()
    result = agent.run(query)
    duration = (datetime.now() - start_time).total_seconds()

    print("=" * 80)
    print("RESEARCH COMPLETE")
    print("=" * 80)
    print()

    if result.success:
        print(f"✅ Success: True")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📏 Output Length: {len(result.content):,} chars")
        print(f"🎯 Complexity: {result.metadata.get('complexity', 'unknown')}")
        print(f"🔢 Max Hops: {result.metadata.get('max_hops', 'unknown')}")
        print()
        print("=" * 80)
        print("FULL RESEARCH REPORT")
        print("=" * 80)
        print()
        print(result.content)
        print()
        print("=" * 80)
        print("END OF REPORT")
        print("=" * 80)

        # Save to file
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"fusion_energy_research_{timestamp}.md"

        with open(report_file, 'w') as f:
            f.write(f"# Fusion Energy Research Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Duration:** {duration:.2f}s\n\n")
            f.write(f"**Complexity:** {complexity}\n\n")
            f.write(f"**Tools Used:** {len(tools)} ({', '.join([type(t).__name__ for t in tools]) if tools else 'None'})\n\n")
            f.write("---\n\n")
            f.write(result.content)

        print()
        print(f"💾 Report saved to: {report_file.absolute()}")

        return result
    else:
        print(f"❌ Failed: {result.error}")
        return None


def analyze_report_quality(result):
    """Analyze the quality of the generated report"""

    if not result or not result.success:
        print("\n❌ Cannot analyze - research failed")
        return

    print("\n" + "=" * 80)
    print("QUALITY ANALYSIS")
    print("=" * 80)
    print()

    content = result.content

    # Check for key components
    checks = {
        "Executive Summary": any(x in content.lower() for x in ['executive summary', '## summary', '# summary']),
        "Research Methodology": any(x in content.lower() for x in ['methodology', 'research approach', 'strategy']),
        "Key Findings": any(x in content.lower() for x in ['findings', 'results', 'discoveries']),
        "Citations/Sources": '[' in content and ']' in content,  # Inline citations
        "Sources Section": any(x in content.lower() for x in ['## sources', '# sources', 'references', 'bibliography']),
        "Confidence Level": any(x in content.lower() for x in ['confidence:', 'confidence level', 'high confidence', 'medium confidence', 'low confidence']),
        "Limitations/Gaps": any(x in content.lower() for x in ['limitation', 'gap', 'remaining question', 'unknown']),
        "Conclusions": any(x in content.lower() for x in ['conclusion', 'summary', 'recommendation']),
        "Multi-Hop Evidence": any(x in content.lower() for x in ['hop 1', 'hop 2', 'first', 'second', 'then', 'subsequently']),
        "Structured Format": '##' in content or '#' in content,  # Markdown headers
    }

    print("Report Structure:")
    print("-" * 80)
    for component, present in checks.items():
        status = "✅" if present else "❌"
        print(f"  {status} {component}")

    # Count metrics
    print()
    print("Content Metrics:")
    print("-" * 80)
    print(f"  Total Characters: {len(content):,}")
    print(f"  Total Words: {len(content.split()):,}")
    print(f"  Total Lines: {content.count(chr(10)):,}")
    print(f"  Sections (##): {content.count('##')}")
    print(f"  Citations ([...]): ~{content.count('[')}")

    # Estimate confidence
    confidence = sum(checks.values()) / len(checks)
    print()
    print(f"Overall Quality Score: {confidence:.1%}")
    print()

    if confidence >= 0.8:
        print("🌟 Excellent - Report has most expected components")
    elif confidence >= 0.6:
        print("👍 Good - Report covers main areas")
    elif confidence >= 0.4:
        print("⚠️  Fair - Some components missing")
    else:
        print("❌ Poor - Major components missing")

    print()


if __name__ == "__main__":
    result = test_full_research()

    if result:
        analyze_report_quality(result)

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print()
