#!/usr/bin/env python3
"""
Example 2: Deep Web Research
=============================

Demonstrates using the DeepWebResearcherAgent for comprehensive research tasks.

Scenario:
  User asks: "Research the latest developments in quantum computing"

  The DeepWebResearcherAgent:
    1. Simulates multi-source research methodology
    2. Provides structured research reports
    3. Includes source credibility assessment
    4. Notes confidence levels

This shows:
  ✓ Advanced single-agent use case
  ✓ Structured output formatting
  ✓ Research methodology simulation
  ✓ Extensibility (can add real web search tools)

Usage:
  python examples/02_deep_web_research.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestration import DeepWebResearcherAgent


def main():
    print("\n" + "="*80)
    print("Example 2: Deep Web Research Agent")
    print("="*80)

    print("\n📦 Setup: Creating Deep Web Researcher Agent...\n")

    # Create the research agent
    researcher = DeepWebResearcherAgent()

    print(f"✅ Agent created: {researcher.config.name}")
    print(f"   Model: {researcher.config.model_id}")
    print(f"   Max tokens: {researcher.config.max_tokens}")

    # Research topics
    research_topics = [
        "Research the latest developments in quantum computing in 2024",
        "Compare Vue.js vs React vs Angular for enterprise applications",
        "Investigate the impact of AI on software development practices"
    ]

    for i, topic in enumerate(research_topics, 1):
        print("\n" + "="*80)
        print(f"Research Topic {i}")
        print("="*80)
        print(f"Query: {topic}")
        print("="*80)

        # Execute research
        print("\n🔍 Researching... (this may take 5-10 seconds)\n")

        result = researcher.run(topic)

        if result.success:
            print(f"✅ Research completed in {result.duration:.2f}s")
            print("\n" + "="*80)
            print("📊 RESEARCH REPORT")
            print("="*80)
            print(result.content)
            print("="*80)

            # Show metadata
            print("\n📈 Research Metadata:")
            print(f"   Agent: {result.metadata.get('agent_name')}")
            print(f"   Duration: {result.duration:.2f}s")
            print(f"   Execution #{result.metadata.get('execution_count')}")

        else:
            print(f"❌ Research failed: {result.error}")

        print("\n" + "-"*80)

    # Show agent statistics
    print("\n" + "="*80)
    print("📊 Agent Statistics")
    print("="*80)

    stats = researcher.stats
    print(f"Total research queries: {stats['execution_count']}")
    print(f"Total research time: {stats['total_duration']:.2f}s")
    print(f"Average time per query: {stats['average_duration']:.2f}s")

    # Demonstrate extended research method
    print("\n" + "="*80)
    print("🔬 Extended Research Method")
    print("="*80)

    print("\nTesting research_with_sources() method...")

    advanced_query = "Research ethical considerations in AI development"
    research_data = researcher.research_with_sources(
        query=advanced_query,
        max_sources=5
    )

    print(f"\nQuery: {research_data['query']}")
    print(f"Success: {research_data['success']}")
    print(f"Duration: {research_data['metadata']['duration']:.2f}s")
    print(f"Max sources: {research_data['metadata']['max_sources']}")
    print("\nFindings:")
    print(research_data['findings'])

    print("\n" + "="*80)
    print("✅ Example Complete!")
    print("="*80)
    print("""
What happened:
  1. Created DeepWebResearcherAgent with specialized research instructions
  2. Executed comprehensive research on multiple topics
  3. Agent provided structured reports with:
     • Executive summary
     • Key findings
     • Analysis
     • Sources (simulated)
     • Confidence levels
  4. Demonstrated extended research_with_sources() method

Key Takeaways:
  • DeepWebResearcherAgent follows research methodology
  • Structured output makes it easy to parse
  • Can be extended with real web search tools:
    - Claude Agent SDK WebSearch tool
    - web-search-prime MCP
    - Custom search APIs
  • Perfect for literature reviews, market research, competitive analysis

Extending with Real Web Search:
  1. Add MCP tool integration:
     from claude_agent_sdk import tool, create_sdk_mcp_server

     @tool("web_search", "Search the web", {"query": "string"})
     async def web_search(args):
         # Use web-search-prime or custom API
         return {"content": [{"type": "text", "text": results}]}

  2. Give tool to agent:
     # This would require modifying the agent to accept tools
     # or wrapping it in an MCP orchestrator

  3. Agent can now access real-time web data!

Next: Try creating a custom agent or workflow!
    """)


if __name__ == "__main__":
    main()
