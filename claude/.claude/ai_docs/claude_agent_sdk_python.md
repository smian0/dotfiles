# Claude Agent SDK for Python

## Overview

The Claude Agent SDK for Python is a powerful library for building interactive AI agents with Claude. It provides high-level abstractions for creating agents that can use tools, maintain conversation context, and handle complex workflows.

**Key Features:**
- Two interaction modes: stateless `query()` and stateful `ClaudeSDKClient`
- Built-in tool support with custom tool creation
- Streaming and non-streaming input modes
- Advanced permission and hook systems
- Real-time progress monitoring
- MCP (Model Context Protocol) server integration

## Installation

```bash
pip install claude-agent-sdk
```

## Core Concepts

### Two Interaction Modes

#### 1. `query()` Function - Stateless Interactions
- Creates a new session for each interaction
- Best for one-off tasks
- Simple, stateless interactions
- Returns an async iterator of messages

**Use when:**
- You need a single-shot agent execution
- No conversation history is needed
- Running independent tasks

#### 2. `ClaudeSDKClient` - Stateful Conversations
- Maintains conversation context across multiple exchanges
- Supports continuous conversations
- Handles interrupts and multi-turn interactions
- Explicit session lifecycle management

**Use when:**
- You need to maintain conversation context
- Building interactive chat applications
- Implementing multi-turn workflows
- Need to interrupt or modify ongoing operations

## Quick Start Examples

### Basic query() Usage

```python
from claude_agent_sdk import query, ClaudeAgentOptions
import asyncio

async def create_project():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode='acceptEdits',
        cwd="/home/user/project"
    )

    async for message in query(
        prompt="Create a Python project structure with setup.py",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Using tool: {block.name}")

asyncio.run(create_project())
```

### ClaudeSDKClient Usage

```python
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock
import asyncio

async def chat_session():
    async with ClaudeSDKClient() as client:
        # First query
        await client.query("What's the capital of France?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up query (maintains context)
        await client.query("What's the population of that city?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

asyncio.run(chat_session())
```

## Tool Creation

### Using the @tool Decorator

Create custom tools that Claude can use during agent execution:

```python
from claude_agent_sdk import tool
from typing import Any

@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    """Greet a user by name."""
    return {
        "content": [{
            "type": "text",
            "text": f"Hello, {args['name']}!"
        }]
    }

@tool("calculate", "Perform mathematical calculations", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a mathematical expression."""
    try:
        result = eval(args["expression"])
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
            }]
        }
```

### Tool Definition Structure

```python
@tool(
    name="tool_name",           # Required: Unique tool identifier
    description="description",  # Required: What the tool does
    input_schema={              # Required: Parameter types
        "param1": str,
        "param2": int,
        "param3": list
    }
)
async def tool_function(args: dict[str, Any]) -> dict[str, Any]:
    # Tool implementation
    return {
        "content": [{
            "type": "text",
            "text": "result"
        }]
    }
```

### Using Custom Tools with Agents

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def agent_with_tools():
    options = ClaudeAgentOptions(
        allowed_tools=["greet", "calculate"],  # Your custom tools
        custom_tools=[greet, calculate]        # Pass tool functions
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Calculate 15 * 7, then greet Alice")
        async for message in client.receive_response():
            # Process response
            pass
```

## Configuration Options

### ClaudeAgentOptions

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    # Tool Configuration
    allowed_tools=["Read", "Write", "Bash", "Edit"],
    custom_tools=[my_tool1, my_tool2],

    # System Configuration
    system_prompt="You are a helpful coding assistant.",
    model="claude-sonnet-4",
    cwd="/path/to/working/directory",

    # Permission Control
    permission_mode='acceptEdits',  # 'auto', 'prompt', 'acceptEdits'
    permission_handler=custom_permission_handler,

    # Hooks
    hooks={
        'pre_tool_use': pre_tool_logger,
        'post_tool_use': post_tool_logger,
        'on_error': error_handler
    },

    # MCP Integration
    mcp_servers=["server1", "server2"],

    # Output Control
    max_tokens=4096,
    temperature=0.7
)
```

### Permission Modes

- **`'auto'`**: Agent uses tools automatically without asking
- **`'prompt'`**: Ask user before using each tool
- **`'acceptEdits'`**: Automatically accept edit operations, prompt for others

## Advanced Patterns

### Custom Permission Handler

Control tool usage with fine-grained permission logic:

```python
async def custom_permission_handler(tool_name: str, input_data: dict, context: dict) -> dict:
    """
    Control which tools can be used and with what parameters.

    Returns:
        {
            "behavior": "allow" | "deny" | "modify",
            "message": "Optional user message",
            "modified_input": {...}  # Only if behavior is "modify"
        }
    """
    # Deny writes to system directories
    if tool_name == "Write" and "/system/" in input_data.get("file_path", ""):
        return {
            "behavior": "deny",
            "message": "System directory write not allowed"
        }

    # Modify bash commands to add safety flags
    if tool_name == "Bash":
        command = input_data.get("command", "")
        if command.startswith("rm"):
            return {
                "behavior": "modify",
                "modified_input": {
                    "command": f"{command} -i"  # Add interactive flag
                },
                "message": "Added safety flag to rm command"
            }

    # Allow all other operations
    return {"behavior": "allow"}

# Use in options
options = ClaudeAgentOptions(
    permission_handler=custom_permission_handler
)
```

### Hooks for Behavior Modification

Intercept and modify agent behavior at various stages:

```python
async def pre_tool_logger(input_data: dict, tool_use_id: str, context: dict) -> dict:
    """Called before each tool use."""
    print(f"About to use tool: {context.get('tool_name')}")
    print(f"Input: {input_data}")
    return {}  # Can return modifications

async def post_tool_logger(output_data: dict, tool_use_id: str, context: dict) -> dict:
    """Called after each tool use."""
    print(f"Tool completed: {context.get('tool_name')}")
    print(f"Output: {output_data}")
    return {}  # Can return modifications

async def error_handler(error: Exception, context: dict) -> dict:
    """Called when an error occurs."""
    print(f"Error occurred: {error}")
    print(f"Context: {context}")
    return {"continue": True}  # Continue execution despite error

# Configure hooks
options = ClaudeAgentOptions(
    hooks={
        'pre_tool_use': pre_tool_logger,
        'post_tool_use': post_tool_logger,
        'on_error': error_handler
    }
)
```

### Streaming Input

Stream input data to the agent in real-time:

```python
async def message_stream():
    """Generator that yields message chunks."""
    yield {"type": "text", "text": "Analyze the following data:"}
    await asyncio.sleep(0.5)
    yield {"type": "text", "text": "Temperature: 25°C"}
    await asyncio.sleep(0.5)
    yield {"type": "text", "text": "Humidity: 60%"}

async def stream_example():
    async with ClaudeSDKClient() as client:
        await client.query(message_stream())
        async for message in client.receive_response():
            # Process streaming response
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end='', flush=True)
```

### Handling Interrupts

Interrupt ongoing agent operations:

```python
async def interruptible_agent():
    async with ClaudeSDKClient() as client:
        # Start long-running task
        await client.query("Analyze all files in this large directory")

        # Begin receiving response
        response_task = asyncio.create_task(
            consume_response(client)
        )

        # Wait for user input or timeout
        await asyncio.sleep(5)

        # Interrupt if needed
        await client.interrupt("User requested cancellation")

        # Wait for graceful shutdown
        await response_task

async def consume_response(client):
    try:
        async for message in client.receive_response():
            # Process messages
            pass
    except InterruptedError:
        print("Operation was interrupted")
```

## MCP Server Integration

Integrate with Model Context Protocol servers:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def use_mcp_servers():
    options = ClaudeAgentOptions(
        mcp_servers=["filesystem", "database", "web_search"],
        # MCP servers provide additional tools automatically
    )

    async with ClaudeSDKClient(options=options) as client:
        # Agent can now use tools from MCP servers
        await client.query("Search the web for Python tutorials")
        async for message in client.receive_response():
            # Process response
            pass
```

## Best Practices

### 1. Choose the Right Interaction Mode

```python
# Use query() for one-off tasks
async for msg in query("Create README.md", options):
    process(msg)

# Use ClaudeSDKClient for conversations
async with ClaudeSDKClient() as client:
    while True:
        user_input = input("You: ")
        await client.query(user_input)
        async for msg in client.receive_response():
            print_response(msg)
```

### 2. Define Clear Tool Descriptions

```python
# Good: Clear, actionable description
@tool(
    "fetch_weather",
    "Fetch current weather data for a specific city using OpenWeather API",
    {"city": str, "units": str}
)

# Bad: Vague description
@tool(
    "get_data",
    "Gets some data",
    {"param": str}
)
```

### 3. Handle Errors Gracefully

```python
async def robust_tool(args: dict[str, Any]) -> dict[str, Any]:
    try:
        result = perform_operation(args)
        return {
            "content": [{
                "type": "text",
                "text": f"Success: {result}"
            }]
        }
    except ValueError as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Invalid input: {str(e)}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error occurred: {str(e)}"
            }]
        }
```

### 4. Use Permission Handlers for Safety

```python
async def safe_permission_handler(tool_name, input_data, context):
    # Prevent dangerous operations
    dangerous_patterns = ['/system/', '/boot/', '/etc/']

    if tool_name in ["Write", "Bash", "Edit"]:
        path = input_data.get("file_path") or input_data.get("command", "")
        if any(pattern in path for pattern in dangerous_patterns):
            return {
                "behavior": "deny",
                "message": f"Operation on {path} blocked for safety"
            }

    return {"behavior": "allow"}
```

### 5. Log Tool Usage for Debugging

```python
import logging

async def logging_hook(input_data, tool_use_id, context):
    logging.info(f"Tool: {context['tool_name']}, Input: {input_data}")
    return {}

options = ClaudeAgentOptions(
    hooks={'pre_tool_use': logging_hook}
)
```

## Common Patterns

### File Processing Agent

```python
async def file_processor():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Glob"],
        cwd="/path/to/project"
    )

    async for message in query(
        "Find all Python files and add docstrings to functions",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
```

### Interactive Code Assistant

```python
async def code_assistant():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit", "Bash"],
        system_prompt="You are an expert Python developer.",
        permission_mode='prompt'
    )

    async with ClaudeSDKClient(options=options) as client:
        while True:
            task = input("What would you like me to do? ")
            if task.lower() == 'exit':
                break

            await client.query(task)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"\n{block.text}\n")
```

### Automated Testing Agent

```python
@tool("run_tests", "Run test suite", {"test_path": str})
async def run_tests(args):
    import subprocess
    result = subprocess.run(
        ["pytest", args["test_path"]],
        capture_output=True,
        text=True
    )
    return {
        "content": [{
            "type": "text",
            "text": f"Tests: {result.stdout}\nErrors: {result.stderr}"
        }]
    }

async def test_agent():
    options = ClaudeAgentOptions(
        custom_tools=[run_tests],
        allowed_tools=["Read", "run_tests"]
    )

    async for msg in query("Run tests and analyze failures", options):
        # Process results
        pass
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```python
# Ensure SDK is installed
pip install claude-agent-sdk

# Verify installation
python -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"
```

#### 2. Authentication Issues
```python
# Set API key as environment variable
export ANTHROPIC_API_KEY="your-api-key"

# Or pass explicitly
from claude_agent_sdk import ClaudeSDKClient

client = ClaudeSDKClient(api_key="your-api-key")
```

#### 3. Tool Not Found Errors
```python
# Ensure tools are properly registered
options = ClaudeAgentOptions(
    allowed_tools=["my_tool"],      # Tool name in allowed list
    custom_tools=[my_tool_function] # Actual function reference
)
```

#### 4. Context Not Maintained
```python
# Use ClaudeSDKClient (not query) for conversations
async with ClaudeSDKClient() as client:  # ✓ Maintains context
    await client.query("First question")
    await client.query("Follow-up question")

# This loses context between calls
await query("First question")  # ✗ New session
await query("Follow-up question")  # ✗ New session, no context
```

## API Reference Summary

### Main Classes
- **`ClaudeSDKClient`**: Stateful agent client
- **`ClaudeAgentOptions`**: Configuration object
- **`AssistantMessage`**: Claude's response messages
- **`ToolUseBlock`**: Tool usage information
- **`TextBlock`**: Text content blocks

### Main Functions
- **`query(prompt, options)`**: Execute stateless query
- **`@tool(name, description, schema)`**: Define custom tool

### Message Types
- **`AssistantMessage`**: Messages from Claude
- **`UserMessage`**: Messages from user
- **`ToolResultMessage`**: Tool execution results

## Additional Resources

- **Documentation**: https://docs.claude.com/en/api/agent-sdk/python
- **GitHub**: Check for official repository and examples
- **API Reference**: Full API documentation at claude.com/api
- **Community**: Anthropic Discord and forums

## Version Compatibility

This documentation is based on the latest version of the Claude Agent SDK for Python. Always check the official documentation for the most up-to-date information and version-specific features.

---

*Last Updated: 2025-10-11*
*For Claude Code AI Assistant Reference*
