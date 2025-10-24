#!/usr/bin/env python3
"""
Multi-Tool Agent Example

Demonstrates:
- Creating multiple custom tools
- Using tools together in an agent
- Complex workflows with multiple capabilities
- Real-world agent patterns
"""

import asyncio
from typing import Any
from claude_agent_sdk import tool, query, ClaudeAgentOptions, create_sdk_mcp_server, AssistantMessage, TextBlock
import json

# Define multiple custom tools

@tool("fetch_user_data", "Fetch user information from database", {"user_id": str})
async def fetch_user_data(args: dict[str, Any]) -> dict[str, Any]:
    """Mock user data fetcher."""
    # In real implementation, this would query a database
    user_id = args["user_id"]

    mock_data = {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
        "status": "active",
        "credits": 150
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(mock_data, indent=2)
        }]
    }

@tool("calculate_discount", "Calculate discount based on user credits", {"credits": int, "price": float})
async def calculate_discount(args: dict[str, Any]) -> dict[str, Any]:
    """Calculate discount percentage based on credits."""
    credits = args["credits"]
    price = args["price"]

    # 1 credit = 1% discount, max 50%
    discount_percent = min(credits, 50)
    discount_amount = price * (discount_percent / 100)
    final_price = price - discount_amount

    result = {
        "original_price": price,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "final_price": final_price
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }

@tool("send_notification", "Send notification to user", {"user_id": str, "message": str})
async def send_notification(args: dict[str, Any]) -> dict[str, Any]:
    """Mock notification sender."""
    user_id = args["user_id"]
    message = args["message"]

    # In real implementation, this would send an actual notification
    print(f"\n[Notification Sent to {user_id}]: {message}")

    return {
        "content": [{
            "type": "text",
            "text": f"Notification sent successfully to user {user_id}"
        }]
    }

@tool("format_report", "Format data into a readable report", {"data": str})
async def format_report(args: dict[str, Any]) -> dict[str, Any]:
    """Format data into a nice report."""
    data = args["data"]

    # Simple formatting
    report = f"""
╔══════════════════════════════════════╗
║         TRANSACTION REPORT           ║
╚══════════════════════════════════════╝

{data}

Generated: {asyncio.get_event_loop().time()}
    """

    return {
        "content": [{
            "type": "text",
            "text": report
        }]
    }

async def main():
    """Run a multi-tool agent for a complex workflow."""

    # Create MCP server with all custom tools
    tools_server = create_sdk_mcp_server(
        name="business_tools",
        version="1.0.0",
        tools=[
            fetch_user_data,
            calculate_discount,
            send_notification,
            format_report
        ]
    )

    # Configure agent with all tools
    options = ClaudeAgentOptions(
        mcp_servers={"business_tools": tools_server}
    )

    # Complex task requiring multiple tools
    task = """
    Process a purchase for user 'user_123':
    1. Fetch the user's data
    2. Calculate their discount for a $100 product
    3. Create a formatted report of the transaction
    4. Send a notification to the user with the final price
    """

    print("Multi-Tool Agent Demo")
    print("=" * 60)
    print(f"Task: {task}")
    print("=" * 60)

    async for message in query(prompt=task, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\n{block.text}")

async def interactive_agent():
    """Run an interactive multi-tool agent."""
    from claude_agent_sdk import ClaudeSDKClient

    # Create MCP server with all custom tools
    tools_server = create_sdk_mcp_server(
        name="business_tools",
        version="1.0.0",
        tools=[
            fetch_user_data,
            calculate_discount,
            send_notification,
            format_report
        ]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"business_tools": tools_server},
        system_prompt="You are a helpful sales assistant with access to user data and pricing tools."
    )

    async with ClaudeSDKClient(options=options) as client:
        print("\nInteractive Agent (type 'exit' to quit)")
        print("=" * 60)

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                break

            await client.query(user_input)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"Agent: {block.text}")

if __name__ == "__main__":
    # Run single-task demo
    asyncio.run(main())

    # Uncomment for interactive mode:
    # asyncio.run(interactive_agent())
