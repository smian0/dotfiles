# Claude Agent SDK Examples

This directory contains working examples of the Claude Agent SDK for Python.

## Examples Overview

All examples are fully documented and executable. They're organized from beginner to advanced.

### Beginner Examples (Start Here!)

#### 1. `simple_agent_mock.py` - Structure Demo ⭐ (No API Required)
**Run this first!** Demonstrates agent patterns without requiring API calls.

```bash
python3 simple_agent_mock.py
```

**What it shows:**
- ✅ Custom tool creation with `@tool` decorator
- ✅ Permission handlers (allow/deny/modify)
- ✅ Pre/post tool execution hooks
- ✅ Error handling
- ✅ Agent configuration patterns

#### 2. `basic_query.py` - One-Shot Query
Simplest real SDK example using `query()` function.

```bash
export ANTHROPIC_API_KEY='your-key'
python3 basic_query.py
```

**Demonstrates:**
- One-shot query pattern
- Tool restrictions
- Working directory configuration
- Permission modes

#### 3. `custom_tool_calculator.py` - Custom Tool Creation
Learn how to create and use custom tools.

```bash
python3 custom_tool_calculator.py
```

**Shows:**
- `@tool` decorator syntax
- Input validation
- Error handling in tools
- Using custom tools with agents

### Intermediate Examples

#### 4. `conversation_session.py` - Stateful Conversations
Maintain context across multiple queries.

```bash
python3 conversation_session.py
```

**Demonstrates:**
- ClaudeSDKClient usage
- Context preservation
- Multi-turn interactions
- Message processing

#### 5. `permission_handler.py` - Permission Control
Implement fine-grained security controls.

```bash
python3 permission_handler.py
```

**Shows:**
- Allow/deny/modify behaviors
- File path validation
- Command safety modifications
- Custom permission logic

#### 6. `hooks_logging.py` - Hooks & Monitoring
Monitor and log agent behavior.

```bash
python3 hooks_logging.py
```

**Demonstrates:**
- Pre-tool hooks
- Post-tool hooks
- Error hooks
- Execution monitoring

### Advanced Examples

#### 7. `streaming_input.py` - Streaming Input
Stream data to the agent incrementally.

```bash
python3 streaming_input.py
```

**Shows:**
- Async generators
- Incremental data streaming
- Real-time processing

#### 8. `interrupt_handling.py` - Task Interruption
Cancel long-running operations gracefully.

```bash
python3 interrupt_handling.py
```

**Demonstrates:**
- Interrupting tasks
- Graceful cancellation
- Background task management

#### 9. `mcp_integration.py` - MCP Servers
Integrate with Model Context Protocol servers.

```bash
python3 mcp_integration.py
```

**Shows:**
- MCP server configuration
- Using external tools
- Combining MCP with custom tools

#### 10. `multi_tool_agent.py` - Complex Workflows
Real-world agent with multiple tools working together.

```bash
python3 multi_tool_agent.py
```

**Demonstrates:**
- Multiple tool coordination
- Complex workflows
- Data flow between tools
- Interactive agent mode

#### 11. `simple_agent.py` - Complete Full Demo
Comprehensive demo with all features.

```bash
export ANTHROPIC_API_KEY='your-key'
python3 simple_agent.py
```

**Includes:**
- Three different demos
- Multiple tools and permissions
- Hooks and logging
- Full agent lifecycle

## Installation

```bash
# Install the SDK
pip install claude-agent-sdk

# Verify installation
python3 -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"
```

## Quick Start

### Creating a Custom Tool

```python
from claude_agent_sdk import tool

@tool("tool_name", "Tool description", {"param": str})
async def my_tool(args):
    result = process(args["param"])
    return {
        "content": [{
            "type": "text",
            "text": f"Result: {result}"
        }]
    }
```

### Using the Agent

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    allowed_tools=["tool_name"],
    custom_tools=[my_tool]
)

async for msg in query("Your prompt", options):
    # Process messages
    pass
```

## Key Concepts Demonstrated

### 1. Tool Creation
- Using `@tool` decorator
- Input schemas with type validation
- Returning properly formatted results
- Error handling in tools

### 2. Permission Handlers
```python
async def permission_handler(tool_name, input_data, context):
    # Return: {"behavior": "allow"}
    # Or: {"behavior": "deny", "message": "reason"}
    # Or: {"behavior": "modify", "modified_input": {...}}
    pass
```

**Three behaviors:**
- **allow**: Permit tool execution
- **deny**: Block with message
- **modify**: Change input parameters

### 3. Hooks
```python
hooks = {
    'pre_tool_use': async_func,   # Before tool execution
    'post_tool_use': async_func,  # After tool execution
    'on_error': async_func        # On error
}
```

**Use cases:**
- Logging and monitoring
- Input validation
- Output transformation
- Error recovery

### 4. Two Interaction Modes

**One-shot (`query`):**
```python
async for msg in query("task", options):
    pass
```
- New session each time
- No context maintained
- Best for independent tasks

**Stateful (`ClaudeSDKClient`):**
```python
async with ClaudeSDKClient(options) as client:
    await client.query("first")
    await client.query("follow-up")  # Context maintained
```
- Maintains conversation history
- Multi-turn interactions
- Best for chatbots and assistants

## Example Output

When you run `simple_agent_mock.py`, you'll see:

```
🤖 Claude Agent SDK Structure Demo (Mock Version)
======================================================================

DEMO: Tool Execution with Hooks and Permissions
======================================================================

Test Case 1:
----------------------------------------------------------------------
[Permission Check] Tool: greet_user
[Permission] ✓ Allowed

[Pre-Tool Hook] Executing: greet_user
[Pre-Tool Hook] Input: {'name': 'Alice', 'language': 'spanish'}
[Post-Tool Hook] Completed: greet_user

✅ Result:
   ¡Hola, Alice! ¡Bienvenido a la demostración del SDK de Claude Agent!
```

## Troubleshooting

### ModuleNotFoundError
```bash
pip install claude-agent-sdk
```

### API Key Not Set
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### Permission Errors
Make the script executable:
```bash
chmod +x simple_agent.py
```

## Next Steps

1. **Run the mock demo** to understand the structure
2. **Get an API key** from https://console.anthropic.com
3. **Run the full demo** with your API key
4. **Modify the examples** to create your own agents
5. **Read the docs** in `../claude_agent_sdk_python.md`

## Documentation

- **Full Guide**: `../claude_agent_sdk_python.md`
- **Quick Reference**: `../claude_agent_sdk_quickref.md`
- **Index**: `../README.md`

## Example Use Cases

These examples can be adapted for:
- **Code assistants**: Read/Write/Edit file operations
- **Data processors**: Transform and analyze data
- **Automation tools**: Execute tasks with safety checks
- **Interactive bots**: Multi-turn conversations
- **Testing frameworks**: Validate system behavior

## Quick Reference Table

| Example | API Required | Tools | Hooks | Permissions | MCP | Level |
|---------|-------------|-------|-------|-------------|-----|-------|
| `simple_agent_mock.py` | ❌ No | ✅ | ✅ | ✅ | ❌ | Beginner |
| `basic_query.py` | ✅ Yes | ✅ | ❌ | ❌ | ❌ | Beginner |
| `custom_tool_calculator.py` | ✅ Yes | ✅ | ❌ | ❌ | ❌ | Beginner |
| `conversation_session.py` | ✅ Yes | ❌ | ❌ | ❌ | ❌ | Intermediate |
| `permission_handler.py` | ✅ Yes | ✅ | ❌ | ✅ | ❌ | Intermediate |
| `hooks_logging.py` | ✅ Yes | ✅ | ✅ | ❌ | ❌ | Intermediate |
| `streaming_input.py` | ✅ Yes | ❌ | ❌ | ❌ | ❌ | Advanced |
| `interrupt_handling.py` | ✅ Yes | ✅ | ❌ | ❌ | ❌ | Advanced |
| `mcp_integration.py` | ✅ Yes | ✅ | ❌ | ❌ | ✅ | Advanced |
| `multi_tool_agent.py` | ✅ Yes | ✅ | ❌ | ❌ | ❌ | Advanced |
| `simple_agent.py` | ✅ Yes | ✅ | ✅ | ✅ | ❌ | Complete |

## Learning Path

**Complete Beginner:**
```bash
# Start here - no API key needed!
python3 simple_agent_mock.py

# Then get API key and run:
python3 basic_query.py
python3 custom_tool_calculator.py
```

**Building Real Agents:**
```bash
python3 conversation_session.py  # Learn stateful conversations
python3 permission_handler.py     # Add security
python3 hooks_logging.py          # Add monitoring
```

**Advanced Patterns:**
```bash
python3 streaming_input.py        # Real-time data
python3 interrupt_handling.py     # Task control
python3 multi_tool_agent.py       # Complex workflows
```

## Pattern Examples

Want to see more? Check out these patterns demonstrated in the examples:

1. **File Processing Agent**: Uses Read/Write/Glob tools → see `multi_tool_agent.py`
2. **Interactive Assistant**: Multi-turn conversations → see `conversation_session.py`
3. **Monitored Execution**: Logging and tracking → see `hooks_logging.py`
4. **Secure Operations**: Permission control → see `permission_handler.py`

## Contributing

To add new examples:
1. Follow the naming convention: `{name}_agent.py`
2. Include docstrings explaining the purpose
3. Add error handling
4. Update this README

---

*Last Updated: 2025-10-11*
*Part of Claude Code AI Documentation*
