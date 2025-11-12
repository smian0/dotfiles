#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "ollama",
# ]
#
# [tool.uv.sources]
# agno = { path = "/Users/smian/github-smian0/agno-ck/libs/agno", editable = true }
# ///

"""
Agno with MCP Tools Example

Demonstrates using Agno with Context7 MCP tools for documentation lookup.
Tests if glm-4.6:cloud can actually invoke MCP tools through Agno.

Run:
   python examples/07_agno_mcp.py
"""

# Disable Agno telemetry before importing agno modules
import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools


async def async_main():
    """Async entry point for MCP workflow execution"""

    print("=== Agno with Context7 MCP Tools ===")
    print("Model: glm-4.6:cloud (Ollama)")
    print("Testing: MCP tool invocation\n")

    # Initialize Context7 MCP tools
    mcp_tools = MCPTools(
        command="npx -y @upstash/context7-mcp",
        transport="stdio",
    )

    # CRITICAL: Use async context manager
    async with mcp_tools:
        # Initialize tools within the session
        await mcp_tools.initialize()

        print(f"✓ MCP tools initialized")
        print(f"  Available tools: {list(mcp_tools.functions.keys())}\n")

        # Create agent with initialized MCP tools
        agent = Agent(
            name="Documentation Assistant",
            model=Ollama(
                id="glm-4.6:cloud",
                options={"num_ctx": 198000}
            ),
            tools=[mcp_tools],
            instructions=[
                "You are a documentation assistant with access to Context7 MCP tools.",
                "You MUST use the available MCP tools to fetch real-time documentation.",
                "NEVER answer from your training data when MCP tools are available.",
                "Always use resolve-library-id first to find the library, then get-library-docs to fetch documentation.",
            ],
            markdown=True,
            exponential_backoff=True,
            retries=3,
            delay_between_retries=15,
        )

        # Test queries
        queries = [
            "What is React and what are its key features?",
            "Explain Atomic Agents agent chaining patterns",
        ]

        print("="*60 + "\n")

        for query in queries:
            print(f"Query: {query}")
            print("-" * 60)

            try:
                # Execute agent with MCP tools
                response = await agent.arun(query)

                print(f"\n{response.content}\n")
                print("="*60 + "\n")

            except Exception as e:
                print(f"Error: {e}\n")
                import traceback
                traceback.print_exc()
                continue

    # MCP session closes automatically when exiting context manager


def main():
    """Synchronous entry point that runs async workflow"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
