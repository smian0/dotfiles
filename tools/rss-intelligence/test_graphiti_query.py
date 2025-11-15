#!/usr/bin/env python3
"""Test Graphiti MCP tools to understand data structure for visualization."""

import asyncio
from agno.tools.mcp import MCPTools

async def test_graphiti_queries():
    """Query Graphiti to see what data is available and its structure."""
    from agno.agent import Agent
    from agno.models.ollama import Ollama
    import json

    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=60,
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()
        print("✓ Graphiti MCP tools initialized\n")

        # Create agent for tool calling (MCP requires agent pattern)
        agent = Agent(
            name="Graphiti Query Agent",
            model=Ollama(id="glm-4.6:cloud"),
            tools=[graphiti_mcp],
            instructions="Execute the requested Graphiti tool and return the raw JSON result.",
            markdown=False,
        )

        # Test 1: Get episodes
        print("=" * 80)
        print("TEST 1: Get Episodes")
        print("=" * 80)
        try:
            result = await agent.arun(
                "get_episodes(group_ids=['rss-intelligence'], max_episodes=5)"
            )
            print(f"Result:\n{result.content[:1500]}\n")
        except Exception as e:
            print(f"Error: {e}")

        # Test 2: Search nodes
        print("\n" + "=" * 80)
        print("TEST 2: Search Nodes (Entities)")
        print("=" * 80)
        try:
            result = await agent.arun(
                "search_nodes(query='Iran', group_ids=['rss-intelligence'], max_nodes=10)"
            )
            print(f"Result:\n{result.content[:1500]}\n")
        except Exception as e:
            print(f"Error: {e}")

        # Test 3: Search memory facts (relationships)
        print("\n" + "=" * 80)
        print("TEST 3: Search Memory Facts (Relationships)")
        print("=" * 80)
        try:
            result = await agent.arun(
                "search_memory_facts(query='Iran tanker', group_ids=['rss-intelligence'], max_facts=10)"
            )
            print(f"Result:\n{result.content[:1500]}\n")
        except Exception as e:
            print(f"Error: {e}")

        # Test 4: Get status
        print("\n" + "=" * 80)
        print("TEST 4: Get Graphiti Status")
        print("=" * 80)
        try:
            result = await agent.arun("get_status()")
            print(f"Result:\n{result.content}\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_graphiti_queries())
