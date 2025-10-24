#!/usr/bin/env python3
"""
Custom Tool Creation Example

Demonstrates:
- Creating a custom tool with @tool decorator
- Input validation and error handling
- Returning properly formatted results
- Using the tool with an agent
"""

import asyncio
from typing import Any
from claude_agent_sdk import tool, query, ClaudeAgentOptions, create_sdk_mcp_server, AssistantMessage, TextBlock

@tool("calculate", "Perform mathematical calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate mathematical expressions safely.

    Args:
        args: Dictionary with 'expression' key containing math expression

    Returns:
        Result dictionary with content
    """
    try:
        # Evaluate with restricted builtins for safety
        result = eval(args["expression"], {"__builtins__": {}}, {})
        return {
            "content": [{
                "type": "text",
                "text": f"Result: {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: {str(e)}"
            }],
            "is_error": True
        }

async def main():
    """Use the calculator tool in an agent."""
    # Create MCP server with calculator tool
    calc_server = create_sdk_mcp_server(
        name="calculator",
        version="1.0.0",
        tools=[calculate]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"calculator": calc_server}
    )

    print("Query: Calculate 42 * 58 + 100")
    async for message in query(prompt="Calculate 42 * 58 + 100", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Result: {block.text}")

if __name__ == "__main__":
    asyncio.run(main())
