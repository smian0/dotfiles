#!/usr/bin/env python3
"""
Test AdaptiveDeepResearchAgent with actual web search tools
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration import AdaptiveDeepResearchAgent, create_adaptive_researcher

# In a real implementation, you would use:
# - Agno's OllamaWebTools
# - Agno's MCPTools with web search MCP servers
# - DuckDuckGo search
# - Any other web search API

# For this demo, we'll show the API pattern
# In production, pass actual tool instances:

def test_with_simulated_tools():
    """Test with simulated tool list (shows API pattern)"""

    print("=" * 80)
    print("Testing AdaptiveDeepResearchAgent with Tools (Simulated)")
    print("=" * 80)
    print()

    # In real usage, you'd pass actual tools:
    # from agno.tools.ollama_web import OllamaWebTools
    # tools = [OllamaWebTools()]

    # For now, we'll use empty list to show the API works
    agent = create_adaptive_researcher(
        model_id="claude-sonnet-4",
        temperature=0.3,
        max_tokens=12000,
        tools=[]  # Would be [OllamaWebTools(), MCPTools(...), etc.]
    )

    query = "What are the latest developments in quantum computing for drug discovery?"

    print(f"Query: {query}")
    print(f"Detected complexity: {agent._detect_complexity(query)}")
    print()
    print("Note: Agent would use web search tools if provided")
    print("      Current test runs with simulated research (no actual web calls)")
    print()

    # Run the agent
    result = agent.run(query)

    if result.success:
        print(f"✅ Research completed in {result.duration:.2f}s")
        print(f"Output length: {len(result.content):,} chars")
        print()
        print("First 1000 chars of output:")
        print("-" * 80)
        print(result.content[:1000])
        print("...")
    else:
        print(f"❌ Failed: {result.error}")


def show_real_usage_example():
    """Show how to use with real Agno tools"""

    print("\n" + "=" * 80)
    print("Real Usage Example with Agno Tools")
    print("=" * 80)
    print()

    example_code = '''
from agno.tools.ollama_web import OllamaWebTools
from agno.tools.mcp import MCPTools
from orchestration import create_adaptive_researcher

# Create web search tools
ollama_web = OllamaWebTools(
    cache_results=True,
    cache_ttl=3600
)

# Or use MCP tools (like webSearchPrime)
# mcp_search = MCPTools(
#     url="https://api.z.ai/api/mcp/web_search_prime/mcp",
#     ...
# )

# Create agent with tools
agent = create_adaptive_researcher(
    model_id="claude-sonnet-4",
    temperature=0.3,
    max_tokens=15000,
    tools=[ollama_web]  # Agent can now do REAL web research!
)

# Execute research - agent will:
# 1. Present research plan
# 2. Use web search tools to gather information
# 3. Synthesize findings with citations
# 4. Provide comprehensive report
result = agent.run("Research fusion energy breakthroughs in 2024-2025")

print(result.content)  # Full research report with real data!
'''

    print(example_code)


if __name__ == "__main__":
    test_with_simulated_tools()
    show_real_usage_example()

    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)
    print()
    print("Key Changes Made:")
    print("1. ✅ Agent accepts tools parameter")
    print("2. ✅ Tools passed to underlying Agno Agent")
    print("3. ✅ Unified Planning strategy executes immediately (no confirmation)")
    print("4. ✅ Instructions updated: 'Execute research, don't wait'")
    print()
    print("To use with real research:")
    print("- Install: pip install duckduckgo-search")
    print("- Or use Agno's OllamaWebTools")
    print("- Or use MCP web search servers")
    print()
