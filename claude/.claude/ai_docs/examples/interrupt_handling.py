#!/usr/bin/env python3
"""
Interrupt Handling Example

Demonstrates:
- Interrupting long-running agent operations
- Graceful task cancellation
- Handling interrupted state
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def interruptible_task():
    """Demonstrate interrupting a long-running agent task."""
    options = ClaudeAgentOptions(
        allowed_tools=["Bash"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        print("Starting long-running task...")
        await client.query("Count from 1 to 100 slowly, with a pause between each number")

        # Start processing in background
        response_task = asyncio.create_task(process_responses(client))

        # Wait 2 seconds then interrupt
        await asyncio.sleep(2)
        print("\n\nInterrupting task...")
        await client.interrupt("User requested cancellation")

        # Wait for graceful shutdown
        await response_task

async def process_responses(client):
    """Process responses until interrupted."""
    try:
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end='', flush=True)
    except asyncio.CancelledError:
        print("\n\nTask was interrupted")
    except Exception as e:
        print(f"\n\nError: {e}")

if __name__ == "__main__":
    asyncio.run(interruptible_task())
