#!/usr/bin/env python3
"""
Permission Handler Example

Demonstrates:
- Custom permission control for tool usage
- Allow, deny, and modify behaviors
- Safety checks on file operations
- Command modification for safety
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

async def custom_permission_handler(tool_name: str, input_data: dict, context: dict) -> dict:
    """
    Control which tools can be used and how.

    Args:
        tool_name: Name of the tool being called
        input_data: Parameters passed to the tool
        context: Additional context about the call

    Returns:
        Dictionary with behavior: "allow", "deny", or "modify"
    """
    print(f"\n[Permission Check] Tool: {tool_name}")

    # Block writes to system directories
    if tool_name == "Write":
        file_path = input_data.get("file_path", "")
        if any(path in file_path for path in ["/system/", "/etc/", "/boot/"]):
            print(f"[Permission] Denied: System directory write")
            return {
                "behavior": "deny",
                "message": "Cannot write to system directories for safety"
            }

    # Modify dangerous bash commands
    if tool_name == "Bash":
        command = input_data.get("command", "")
        if command.startswith("rm ") and "-i" not in command:
            modified_command = command.replace("rm ", "rm -i ")
            print(f"[Permission] Modified: Added interactive flag")
            return {
                "behavior": "modify",
                "modified_input": {"command": modified_command},
                "message": "Added safety flag to rm command"
            }

    # Allow all other operations
    print(f"[Permission] Allowed")
    return {"behavior": "allow"}

async def main():
    """Test the permission handler with various operations."""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_handler=custom_permission_handler,
        permission_mode="auto"
    )

    # This will trigger permission checks
    print("Testing permission handler...")
    async for message in query(
        prompt="Read the file /tmp/test.txt if it exists",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\n{block.text}")

if __name__ == "__main__":
    asyncio.run(main())
