#!/usr/bin/env python3
"""Run intelligence analysis on Graphiti knowledge graph"""

import asyncio
import os
from pathlib import Path

os.environ["AGNO_TELEMETRY"] = "false"

from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama


async def main():
    print("=" * 80)
    print("Knowledge Graph Intelligence Analysis")
    print("=" * 80)
    print()
    
    # Initialize Graphiti MCP
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=120,
    )
    
    async with graphiti_mcp:
        await graphiti_mcp.initialize()
        print("✓ MCP tools initialized")
        print(f"  Available: {list(graphiti_mcp.functions.keys())}\n")
        
        # Create intelligence analyst agent
        analyst = Agent(
            name="Intelligence Analyst",
            model=Ollama(id="deepseek-v3.1:671b-cloud"),  # Best reasoning model
            tools=[graphiti_mcp],
            instructions="""You are an intelligence analyst with access to a knowledge graph of news articles.

Use search_memory_facts and search_nodes to:
1. Identify cross-cutting themes and patterns
2. Find connections between seemingly unrelated events
3. Detect emerging trends and escalating situations
4. Highlight geopolitical implications

Query the graph systematically and provide strategic intelligence insights.""",
            markdown=True,
        )
        
        print("🔍 Querying knowledge graph for intelligence patterns...\n")
        
        prompt = """Analyze the knowledge graph and provide strategic intelligence insights:

1. Search for key geopolitical entities and events
2. Identify cross-cutting themes (conflicts, elections, human rights, climate)
3. Find connections between different regions/actors
4. Detect escalating situations or emerging crises

Provide a concise intelligence brief with:
- Key patterns discovered
- Critical connections between events
- Strategic implications
- Hidden signals or trends

Be specific - reference actual entities and facts from the graph."""

        result = await analyst.arun(prompt)
        
        print("\n" + "=" * 80)
        print("INTELLIGENCE BRIEF")
        print("=" * 80)
        print()
        print(result.content)
        print()
        print("=" * 80)
        
        # Save to file
        output_file = Path("intelligence_analysis_manual.md")
        with open(output_file, "w") as f:
            f.write(f"# Intelligence Analysis - {Path().absolute().name}\n\n")
            f.write(result.content)
        
        print(f"\n✅ Analysis saved to: {output_file.name}")
        
        return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
