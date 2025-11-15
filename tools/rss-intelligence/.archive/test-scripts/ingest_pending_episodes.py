#!/usr/bin/env python3
"""Ingest the 10 pending episodes from graphiti_episodes_pending.json"""

import asyncio
import json
import os
from pathlib import Path

os.environ["AGNO_TELEMETRY"] = "false"

from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama


async def main():
    episodes_file = Path("graphiti_episodes_pending.json")
    if not episodes_file.exists():
        print("❌ No pending episodes file found")
        return 1
    
    with open(episodes_file) as f:
        episodes = json.load(f)
    
    print(f"📊 Ingesting {len(episodes)} pending episodes into Graphiti...\n")
    
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=120,
    )
    
    ingested_count = 0
    failed_count = 0
    
    async with graphiti_mcp:
        await graphiti_mcp.initialize()
        print("✓ Graphiti MCP tools initialized\n")
        
        agent = Agent(
            name="Graphiti Ingestor",
            model=Ollama(id="glm-4.6:cloud"),
            tools=[graphiti_mcp],
            instructions="Use add_memory tool with provided parameters. Return only 'OK' on success.",
            markdown=False,
        )
        
        for i, episode in enumerate(episodes):
            episode_name = episode["name"]
            episode_body = episode["body"]
            
            try:
                print(f"  [{i+1}/{len(episodes)}] {episode_name[:55]}...", end=" ", flush=True)
                
                result = await agent.arun(
                    f"add_memory(name={repr(episode_name)}, episode_body={repr(episode_body)}, "
                    f"source='json', source_description='RSS news article', group_id='rss-intelligence')"
                )
                
                ingested_count += 1
                print("✅")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ {str(e)[:40]}")
        
        print(f"\n{'='*80}")
        print(f"✅ Successfully ingested: {ingested_count}/{len(episodes)} episodes")
        print(f"❌ Failed: {failed_count}/{len(episodes)} episodes")
        print(f"{'='*80}\n")
    
    if ingested_count == len(episodes):
        archived = episodes_file.with_suffix('.json.completed')
        episodes_file.rename(archived)
        print(f"📦 Pending file archived to: {archived.name}")
        return 0
    else:
        print("⚠️ Some episodes failed - keeping pending file")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
