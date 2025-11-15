#!/usr/bin/env python3
"""Test intelligence analysis with fixed agent"""

import asyncio
import os
from pathlib import Path

os.environ["AGNO_TELEMETRY"] = "false"

from agno.tools.mcp import MCPTools
from agents.intelligence_analyst import create_intelligence_analyst


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
        
        # Create intelligence analyst with fixed config
        analyst = create_intelligence_analyst(graphiti_mcp)
        
        print("🔍 Running Phase 1 Enhanced Intelligence Analysis...\n")
        
        result = await analyst.arun(
            "Analyze the rss-intelligence knowledge graph with Phase 1 enhancements"
        )
        
        print("\n" + "=" * 80)
        print("INTELLIGENCE BRIEF")
        print("=" * 80)
        print()
        print(result.content)
        print()
        print("=" * 80)
        
        # Save to file
        output_file = Path("intelligence_brief_$(date +%Y%m%d_%H%M%S).md")
        with open(output_file, "w") as f:
            f.write(result.content)
        
        print(f"\n✅ Analysis saved to: {output_file.name}")
        
        return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
