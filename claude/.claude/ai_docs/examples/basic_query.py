#!/usr/bin/env python3
"""
Basic Query Example

Demonstrates:
- One-shot query with the query() function
- Tool restrictions (Read, Write, Bash)
- Working directory configuration
- Permission mode settings
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock

async def create_project():
    """Execute a basic query to create a Python project structure."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode='acceptEdits',
        cwd="/tmp/test_project"  # Safe test directory
    )

    async for message in query(
        prompt="Create a Python project structure with setup.py",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Using tool: {block.name}")
                    print(f"Tool input: {block.input}")

if __name__ == "__main__":
    asyncio.run(create_project())
