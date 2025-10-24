#!/usr/bin/env python3
"""
Hooks Example

Demonstrates:
- Pre-tool hook for logging/validation
- Post-tool hook for logging/transformation
- Error hook for error handling
- Using hooks for monitoring
"""

import asyncio
import json
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

# Global counters for demo
tool_calls = 0
errors = 0

async def pre_tool_hook(input_data: dict, tool_use_id: str, context: dict) -> dict:
    """
    Called before each tool execution.

    Args:
        input_data: Tool input parameters
        tool_use_id: Unique ID for this tool use
        context: Additional context including tool name

    Returns:
        Dictionary with optional modifications
    """
    global tool_calls
    tool_calls += 1

    tool_name = context.get('tool_name', 'unknown')
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"\n[{timestamp}] [Pre-Tool #{tool_calls}] {tool_name}")
    print(f"  Input: {json.dumps(input_data, indent=2)[:100]}...")

    # Can return modifications here
    return {}

async def post_tool_hook(output_data: dict, tool_use_id: str, context: dict) -> dict:
    """
    Called after each tool execution.

    Args:
        output_data: Tool output
        tool_use_id: Unique ID for this tool use
        context: Additional context including tool name

    Returns:
        Dictionary with optional modifications
    """
    tool_name = context.get('tool_name', 'unknown')
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"[{timestamp}] [Post-Tool] {tool_name} completed")

    # Extract text from content
    content = output_data.get('content', [])
    if content and isinstance(content, list):
        text = content[0].get('text', '')
        print(f"  Output: {text[:80]}...")

    # Can return modifications here
    return {}

async def error_hook(error: Exception, context: dict) -> dict:
    """
    Called when an error occurs.

    Args:
        error: The exception that occurred
        context: Context about where the error occurred

    Returns:
        Dictionary with continue flag
    """
    global errors
    errors += 1

    print(f"\n[Error Hook] Error #{errors}: {type(error).__name__}")
    print(f"  Message: {str(error)}")
    print(f"  Context: {context}")

    # Return True to continue execution despite error
    return {"continue": True}

async def main():
    """Demonstrate hooks with a simple agent task."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write"],
        hooks={
            'pre_tool_use': pre_tool_hook,
            'post_tool_use': post_tool_hook,
            'on_error': error_hook
        }
    )

    print("Running agent with hooks enabled...")
    print("=" * 60)

    async for message in query(
        prompt="List files in /tmp directory",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\nFinal response:\n{block.text}")

    print("\n" + "=" * 60)
    print(f"Summary: {tool_calls} tool calls, {errors} errors")

if __name__ == "__main__":
    asyncio.run(main())
