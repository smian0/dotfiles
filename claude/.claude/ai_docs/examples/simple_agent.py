#!/usr/bin/env python3
"""
Simple Claude Agent SDK Example

This demonstrates:
1. Creating a custom tool
2. Using the agent with both query() and ClaudeSDKClient
3. Permission handling
4. Basic conversation flow
"""

import asyncio
import os
from typing import Any

# Check if SDK is installed
try:
    from claude_agent_sdk import (
        query,
        ClaudeSDKClient,
        ClaudeAgentOptions,
        tool,
        create_sdk_mcp_server,
        AssistantMessage,
        TextBlock,
        ToolUseBlock
    )
except ImportError:
    print("Claude Agent SDK not installed. Install with:")
    print("  pip install claude-agent-sdk")
    exit(1)


# Define a custom tool
@tool(
    "greet_user",
    "Greet a user with a personalized message",
    {"name": str, "language": str}
)
async def greet_user(args: dict[str, Any]) -> dict[str, Any]:
    """Custom greeting tool that supports multiple languages."""
    name = args.get("name", "friend")
    language = args.get("language", "english").lower()

    greetings = {
        "english": f"Hello, {name}! Welcome to the Claude Agent SDK demo!",
        "spanish": f"¡Hola, {name}! ¡Bienvenido a la demostración del SDK de Claude Agent!",
        "french": f"Bonjour, {name}! Bienvenue dans la démo du SDK Claude Agent!",
        "german": f"Hallo, {name}! Willkommen zur Claude Agent SDK Demo!"
    }

    greeting = greetings.get(language, greetings["english"])

    return {
        "content": [{
            "type": "text",
            "text": greeting
        }]
    }


@tool(
    "calculate",
    "Perform basic mathematical calculations",
    {"expression": str}
)
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """Safe calculator tool."""
    try:
        # Simple eval for demo - in production use safer alternatives
        result = eval(args["expression"], {"__builtins__": {}}, {})
        return {
            "content": [{
                "type": "text",
                "text": f"The result of {args['expression']} is: {result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error calculating: {str(e)}"
            }]
        }


# Custom permission handler
async def safety_permission_handler(tool_name: str, input_data: dict, context: dict) -> dict:
    """Demonstrate permission control - blocks certain operations."""
    print(f"\n[Permission Check] Tool: {tool_name}")

    # Allow custom tools
    if tool_name in ["greet_user", "calculate"]:
        return {"behavior": "allow"}

    # Block any file writes to system directories (if using Write tool)
    if tool_name == "Write":
        file_path = input_data.get("file_path", "")
        if "/system" in file_path or "/etc" in file_path:
            return {
                "behavior": "deny",
                "message": "Cannot write to system directories"
            }

    # Allow everything else
    return {"behavior": "allow"}


# Logging hooks
async def pre_tool_hook(input_data: dict, tool_use_id: str, context: dict) -> dict:
    """Log before tool execution."""
    tool_name = context.get("tool_name", "unknown")
    print(f"\n[Pre-Tool] About to execute: {tool_name}")
    return {}


async def post_tool_hook(output_data: dict, tool_use_id: str, context: dict) -> dict:
    """Log after tool execution."""
    tool_name = context.get("tool_name", "unknown")
    print(f"[Post-Tool] Completed: {tool_name}")
    return {}


async def demo_one_shot_query():
    """Demonstrate one-shot query() usage."""
    print("\n" + "=" * 60)
    print("DEMO 1: One-Shot Query with Custom Tools")
    print("=" * 60)

    # Create MCP server with custom tools
    custom_server = create_sdk_mcp_server(
        name="custom_tools",
        version="1.0.0",
        tools=[greet_user, calculate]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"custom_tools": custom_server}
    )

    print("\nPrompt: 'Greet Alice in Spanish, then calculate 15 * 7'")
    print("\nAgent Response:")

    async for message in query(
        prompt="Greet Alice in Spanish, then calculate 15 * 7",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\n{block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[Tool Use] {block.name} with args: {block.input}")


async def demo_stateful_conversation():
    """Demonstrate stateful conversation with ClaudeSDKClient."""
    print("\n" + "=" * 60)
    print("DEMO 2: Stateful Conversation")
    print("=" * 60)

    # Create MCP server with custom tools
    custom_server = create_sdk_mcp_server(
        name="custom_tools",
        version="1.0.0",
        tools=[greet_user, calculate]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"custom_tools": custom_server},
        system_prompt="You are a helpful assistant that uses tools to help users.",
    )

    async with ClaudeSDKClient(options=options) as client:
        # First query
        print("\nQuery 1: 'Hello! What's your name?'")
        print("Agent Response:")
        await client.query("Hello! What's your name?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"{block.text}")

        # Follow-up with context maintained
        print("\n\nQuery 2: 'Can you greet me in French?'")
        print("Agent Response:")
        await client.query("Can you greet me in French? My name is Claude.")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"{block.text}")


async def demo_simple_task():
    """Simplest possible demo."""
    print("\n" + "=" * 60)
    print("DEMO 3: Simplest Task")
    print("=" * 60)

    print("\nPrompt: 'Calculate the sum of 42 + 58'")
    print("Agent Response:")

    # Create MCP server with calculator tool
    calc_server = create_sdk_mcp_server(
        name="calculator",
        version="1.0.0",
        tools=[calculate]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"calculator": calc_server}
    )

    async for message in query(
        prompt="Calculate the sum of 42 + 58",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\n{block.text}")


async def main():
    """Run all demos."""
    print("\n🤖 Claude Agent SDK Demo")
    print("=" * 60)
    print("Using Claude Code authentication (no API key needed!)")
    print("=" * 60)

    try:
        # Run demos
        await demo_simple_task()
        await demo_one_shot_query()
        await demo_stateful_conversation()

        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
