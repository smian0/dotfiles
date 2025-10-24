#!/usr/bin/env python3
"""
Streaming Input Example

Demonstrates:
- Streaming input data to the agent
- Using async generators for incremental data
- Processing streaming responses
"""

import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def message_stream():
    """
    Generator that yields message chunks incrementally.

    Yields:
        Message dictionaries with text content
    """
    yield {"type": "text", "text": "Analyze the following data:"}
    await asyncio.sleep(0.5)
    yield {"type": "text", "text": "\n\nTemperature: 25°C"}
    await asyncio.sleep(0.5)
    yield {"type": "text", "text": "\nHumidity: 60%"}
    await asyncio.sleep(0.5)
    yield {"type": "text", "text": "\nPressure: 1013 hPa"}

async def main():
    """Stream input data to the agent and process responses."""
    print("Streaming input to agent...")

    async with ClaudeSDKClient() as client:
        # Send streaming input
        await client.query(message_stream())

        # Process streaming response
        print("\nAgent response:")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

if __name__ == "__main__":
    asyncio.run(main())
