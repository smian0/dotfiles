#!/usr/bin/env python3
"""Manual test of Knowledge Graph search to replicate the user's scenario."""

import asyncio
from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama


async def test_iran_search():
    """Test searching for Iran - the exact scenario the user wants."""
    print("=" * 80)
    print("MANUAL TEST: Searching for 'Iran' in Knowledge Graph")
    print("=" * 80)

    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=60,
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()
        print("✓ Connected to Graphiti MCP\n")

        agent = Agent(
            name="Entity Search Test",
            model=Ollama(id="glm-4.6:cloud"),
            tools=[graphiti_mcp],
            instructions="Execute the search_nodes tool and return ONLY valid JSON. No extra text.",
            markdown=False,
        )

        print("Searching for entities matching 'Iran'...")
        result = await agent.arun(
            "search_nodes(query='Iran', group_ids=['rss-intelligence'], max_nodes=10)"
        )

        print(f"\nAgent Response (first 500 chars):\n{result.content[:500]}\n")
        print("=" * 80)

        # Try to parse it
        import json
        import re

        try:
            # Try direct parse
            data = json.loads(result.content)
            print("✅ Direct JSON parse successful")
        except json.JSONDecodeError:
            print("⚠️  Direct parse failed, trying extraction...")

            # Try extraction
            json_match = re.search(r'\{.*\}|\[.*\]', result.content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Fix trailing commas
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

                try:
                    data = json.loads(json_str)
                    print("✅ Extracted and parsed JSON successfully")
                except Exception as e:
                    print(f"❌ Extraction also failed: {e}")
                    print(f"\nExtracted JSON (first 500 chars):\n{json_str[:500]}")
                    return

        # Show results
        nodes = data.get('nodes', [])
        print(f"\n✅ Found {len(nodes)} entities:\n")

        for i, node in enumerate(nodes[:5], 1):
            print(f"{i}. {node.get('name')}")
            print(f"   UUID: {node.get('uuid', 'N/A')[:16]}...")
            print(f"   Summary: {node.get('summary', 'N/A')[:80]}...")
            print()


if __name__ == "__main__":
    asyncio.run(test_iran_search())
