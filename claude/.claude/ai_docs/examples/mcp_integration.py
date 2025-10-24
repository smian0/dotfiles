#!/usr/bin/env python3
"""
MCP Server Integration Example

Demonstrates:
- Connecting to Model Context Protocol servers
- Using tools provided by MCP servers
- Configuring multiple MCP servers
- Accessing external capabilities
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    """Demonstrate using MCP servers with the agent."""

    # Configure agent with MCP servers
    # MCP servers provide additional tools automatically
    options = ClaudeAgentOptions(
        # List of MCP server names to connect to
        # These should match servers configured in your environment
        mcp_servers=["filesystem", "web_search", "database"],

        # You can also use regular tools alongside MCP tools
        allowed_tools=["Read", "Write"],

        system_prompt="You are a helpful assistant with access to filesystem, web search, and database tools via MCP servers."
    )

    async with ClaudeSDKClient(options=options) as client:
        # The agent can now use tools from all configured MCP servers

        # Example 1: Using web search MCP server
        print("Query 1: Search for recent Python news")
        await client.query("Search the web for the latest Python 3.12 features")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}\n")

        # Example 2: Using filesystem MCP server
        print("\nQuery 2: List project files")
        await client.query("What files are in the current project?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

async def mcp_with_custom_tools():
    """Combine MCP servers with custom tools."""
    from claude_agent_sdk import tool
    from typing import Any

    # Define a custom tool
    @tool("analyze_data", "Analyze data from various sources", {"source": str})
    async def analyze_data(args: dict[str, Any]) -> dict[str, Any]:
        return {
            "content": [{
                "type": "text",
                "text": f"Analyzing data from {args['source']}..."
            }]
        }

    options = ClaudeAgentOptions(
        mcp_servers=["filesystem", "web_search"],
        custom_tools=[analyze_data],
        allowed_tools=["analyze_data"]
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Search for data files, then analyze the most recent one"
        )

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

if __name__ == "__main__":
    print("MCP Server Integration Demo")
    print("=" * 60)
    print("Note: This requires MCP servers to be configured")
    print("See: https://modelcontextprotocol.io for setup")
    print("=" * 60)

    # Run the examples
    asyncio.run(main())

    # Uncomment to run custom tools example:
    # asyncio.run(mcp_with_custom_tools())
