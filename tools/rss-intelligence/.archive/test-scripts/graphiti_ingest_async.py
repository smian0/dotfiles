#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
# ]
#
# [tool.uv.sources]
# agno = { path = "/Users/smian/github-smian0/agno-ck/libs/agno", editable = true }
# ///

"""
Async Graphiti Episode Ingestion

Ingests prepared RSS intelligence episodes into Graphiti knowledge graph
using proper async MCP Tools pattern from Agno.

This follows the pattern from agno-workflow-builder/examples/agno_mcp.py
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
import json
from pathlib import Path

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools


async def async_main():
    """Async entry point for Graphiti MCP ingestion"""

    print("=" * 80)
    print("Graphiti Knowledge Graph Ingestion")
    print("=" * 80)
    print()

    # Load episodes from JSON file
    episodes_file = Path("graphiti_episodes_pending.json")
    if not episodes_file.exists():
        print("❌ No episodes file found. Run the RSS workflow first.")
        return 1

    with open(episodes_file) as f:
        episodes = json.load(f)

    print(f"📊 Found {len(episodes)} episodes to ingest")
    print(f"🎯 Target group: rss-intelligence\n")

    # Initialize Graphiti MCP tools
    print("🔧 Initializing Graphiti MCP tools...")
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=60,
    )

    # CRITICAL: Use async context manager
    async with graphiti_mcp:
        # Initialize tools within the session
        await graphiti_mcp.initialize()

        print(f"✓ MCP tools initialized")
        print(f"  Available tools: {list(graphiti_mcp.functions.keys())}\n")

        # Create agent with initialized MCP tools
        agent = Agent(
            name="Knowledge Graph Ingestion Agent",
            model=Ollama(id="glm-4.6:cloud"),
            tools=[graphiti_mcp],
            instructions="""
            You are responsible for ingesting news articles into the Graphiti knowledge graph.

            For EACH episode provided:
            1. Use add_memory tool with:
               - name: The episode name (already formatted)
               - episode_body: The JSON body (already formatted)
               - source: "json"
               - group_id: "rss-intelligence"

            2. Graphiti will automatically:
               - Extract entities (people, organizations, locations, events)
               - Build relationship graphs
               - Enable temporal tracking

            3. Report progress after each successful ingestion

            IMPORTANT: Call add_memory for EACH episode. Do not skip any.
            """,
            markdown=False,
        )

        print("=" * 80)
        print("Starting ingestion...")
        print("=" * 80)
        print()

        # Prepare the prompt with all episodes
        episodes_text = "\n\n".join([
            f"Episode {i+1}:\n"
            f"Name: {ep['name']}\n"
            f"Body: {ep['body'][:200]}...\n"
            f"[Full body available in data]"
            for i, ep in enumerate(episodes)
        ])

        prompt = f"""Please ingest these {len(episodes)} news articles into Graphiti:

{episodes_text}

Use the add_memory tool for each episode with:
- name: (as shown above)
- episode_body: (the full JSON body from the data)
- source: "json"
- group_id: "rss-intelligence"

Report progress as you go."""

        try:
            # Execute agent with MCP tools
            response = await agent.arun(prompt)

            print(f"\n{response.content}\n")
            print("=" * 80)
            print("✅ Ingestion complete!")
            print("=" * 80)

            # Archive the episodes file
            archived = episodes_file.with_suffix('.json.completed')
            episodes_file.rename(archived)
            print(f"\n📦 Episodes file archived to: {archived.name}")

            return 0

        except Exception as e:
            print(f"\n❌ Error during ingestion: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # MCP session closes automatically when exiting context manager


def main():
    """Synchronous entry point that runs async workflow"""
    return asyncio.run(async_main())


if __name__ == "__main__":
    exit(main())
