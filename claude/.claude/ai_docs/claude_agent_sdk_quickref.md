# Claude Agent SDK - Quick Reference

## Installation
```bash
pip install claude-agent-sdk
```

## Basic Usage

### One-Shot Query
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for msg in query("Your prompt here", ClaudeAgentOptions(
    allowed_tools=["Read", "Write"],
    cwd="/path/to/project"
)):
    # Process message
    pass
```

### Stateful Conversation
```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient() as client:
    await client.query("First question")
    async for msg in client.receive_response():
        # Process response
        pass

    # Context is maintained
    await client.query("Follow-up question")
```

## Tool Creation
```python
from claude_agent_sdk import tool

@tool("tool_name", "Description", {"param": str})
async def my_tool(args):
    return {
        "content": [{
            "type": "text",
            "text": f"Result: {args['param']}"
        }]
    }
```

## Common Options

```python
ClaudeAgentOptions(
    # Tools
    allowed_tools=["Read", "Write", "Bash", "Edit"],
    custom_tools=[my_tool],

    # System
    system_prompt="Custom system prompt",
    model="claude-sonnet-4",
    cwd="/working/directory",

    # Permissions
    permission_mode='auto',  # 'auto', 'prompt', 'acceptEdits'
    permission_handler=handler_function,

    # Hooks
    hooks={
        'pre_tool_use': pre_hook,
        'post_tool_use': post_hook,
        'on_error': error_hook
    }
)
```

## Permission Handler
```python
async def permission_handler(tool_name, input_data, context):
    # Deny
    if condition:
        return {"behavior": "deny", "message": "Reason"}

    # Modify
    if other_condition:
        return {
            "behavior": "modify",
            "modified_input": {...},
            "message": "Modified"
        }

    # Allow
    return {"behavior": "allow"}
```

## Hooks Pattern
```python
async def pre_hook(input_data, tool_use_id, context):
    # Log or modify before tool use
    return {}  # Can return modifications

async def post_hook(output_data, tool_use_id, context):
    # Log or modify after tool use
    return {}  # Can return modifications

async def error_hook(error, context):
    # Handle errors
    return {"continue": True}  # Continue or stop
```

## Message Types

### Processing Assistant Messages
```python
from claude_agent_sdk import AssistantMessage, TextBlock, ToolUseBlock

async for message in client.receive_response():
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
            elif isinstance(block, ToolUseBlock):
                print(f"Using: {block.name}")
```

## Common Patterns

### File Processing
```python
async for msg in query(
    "Process all Python files",
    ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Glob"],
        cwd="/project"
    )
):
    pass
```

### Interactive Assistant
```python
async with ClaudeSDKClient(
    options=ClaudeAgentOptions(permission_mode='prompt')
) as client:
    while True:
        task = input("Task: ")
        await client.query(task)
        async for msg in client.receive_response():
            # Show response
            pass
```

### With Custom Tools
```python
options = ClaudeAgentOptions(
    allowed_tools=["my_tool"],
    custom_tools=[my_tool_function]
)

async for msg in query("Use my custom tool", options):
    pass
```

## Error Handling

```python
try:
    async with ClaudeSDKClient() as client:
        await client.query("Task")
        async for msg in client.receive_response():
            # Process
            pass
except Exception as e:
    print(f"Error: {e}")
```

## Debugging Tips

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Tool Calls
```python
async def debug_hook(input_data, tool_use_id, context):
    print(f"Tool: {context['tool_name']}")
    print(f"Input: {input_data}")
    return {}
```

### Check Configuration
```python
print(f"Tools: {options.allowed_tools}")
print(f"CWD: {options.cwd}")
print(f"Mode: {options.permission_mode}")
```

## Quick Decision Guide

| Need | Use |
|------|-----|
| Single task | `query()` |
| Conversation | `ClaudeSDKClient` |
| Custom capability | `@tool` decorator |
| Control tool usage | `permission_handler` |
| Monitor execution | `hooks` |
| Integrate external tools | `mcp_servers` |

## Authentication

```bash
# Set environment variable
export ANTHROPIC_API_KEY="your-api-key"

# Or pass in code
ClaudeSDKClient(api_key="your-api-key")
```

---

*For full documentation, see: claude_agent_sdk_python.md*
