#!/usr/bin/env python3
"""
Conversation Session Example

Demonstrates:
- Using ClaudeSDKClient for stateful conversations
- Maintaining context across multiple queries
- Processing different message types
- Multi-turn interactions
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def main():
    """Run a multi-turn conversation with context maintained."""
    async with ClaudeSDKClient() as client:
        # First question
        print("User: What's the capital of France?")
        await client.query("What's the capital of France?")

        # Process response
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up question - Claude remembers the previous context
        print("\nUser: What's the population of that city?")
        await client.query("What's the population of that city?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

if __name__ == "__main__":
    asyncio.run(main())
