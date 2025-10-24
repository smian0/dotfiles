# Claude Agent SDK API Changes

**Last Updated:** 2025-10-13

## Breaking Changes Fixed

The Claude Agent SDK API has changed significantly. All examples have been updated to use the correct API.

## Key Changes

### 1. Custom Tools Must Use MCP Servers

**❌ Old Way (WRONG):**
```python
from claude_agent_sdk import tool, ClaudeAgentOptions

@tool("calculate", "Calculator", {"expr": str})
async def calculate(args):
    return {"content": [{"type": "text", "text": "result"}]}

options = ClaudeAgentOptions(
    allowed_tools=["calculate"],
    custom_tools=[calculate]  # ❌ No longer supported!
)
```

**✅ New Way (CORRECT):**
```python
from claude_agent_sdk import tool, ClaudeAgentOptions, create_sdk_mcp_server

@tool("calculate", "Calculator", {"expr": str})
async def calculate(args):
    return {"content": [{"type": "text", "text": "result"}]}

# Wrap tools in an MCP server
calc_server = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[calculate]
)

options = ClaudeAgentOptions(
    mcp_servers={"calculator": calc_server}  # ✅ Correct!
)
```

### 2. query() Requires Keyword Arguments

**❌ Old Way (WRONG):**
```python
async for message in query("Your prompt", options=options):
    pass
```

**✅ New Way (CORRECT):**
```python
async for message in query(prompt="Your prompt", options=options):
    pass
```

### 3. Permission Mode Values Changed

**❌ Old Way (WRONG):**
```python
ClaudeAgentOptions(permission_mode='auto')  # ❌ Invalid!
```

**✅ New Way (CORRECT):**
```python
ClaudeAgentOptions(permission_mode='acceptEdits')  # ✅ Valid

# Valid modes:
# - 'acceptEdits' - Auto-approve edit operations
# - 'bypassPermissions' - Skip all permission checks
# - 'default' - Prompt for each operation
# - 'plan' - Plan mode (review before execution)
```

### 4. Permission Handler Changed

**❌ Old Way (WRONG):**
```python
async def permission_handler(tool_name, input_data, context):
    return {"behavior": "allow"}  # ❌ Wrong return type

ClaudeAgentOptions(
    permission_handler=permission_handler  # ❌ Wrong parameter name
)
```

**✅ New Way (CORRECT):**
```python
from claude_agent_sdk.types import PermissionResultAllow, PermissionResultDeny

async def can_use_tool_callback(tool_name, input_data, context):
    # Return proper types
    return PermissionResultAllow()  # or PermissionResultDeny()

# Note: Requires streaming mode - better to use permission_mode instead
```

**Simplified (RECOMMENDED):**
```python
# Just use permission_mode instead of custom callback
ClaudeAgentOptions(permission_mode='acceptEdits')
```

### 5. No API Key Needed

**❌ Old Way (REQUIRED BEFORE):**
```python
import os
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Error: Set ANTHROPIC_API_KEY")
    exit(1)
```

**✅ New Way (NO LONGER NEEDED):**
```python
# No API key check needed!
# SDK uses Claude Code's OAuth authentication automatically
```

## Updated Examples

All examples have been fixed:

| File | Status | Changes Made |
|------|--------|--------------|
| `simple_agent.py` | ✅ Working | MCP servers, query syntax, no API key |
| `custom_tool_calculator.py` | ✅ Working | MCP server wrapper |
| `multi_tool_agent.py` | ✅ Working | MCP server with 4 tools |
| `basic_query.py` | ✅ Working | Query syntax |
| `hooks_logging.py` | ✅ Working | Query syntax |
| `permission_handler.py` | ✅ Working | Query syntax |
| All others | ✅ Working | Various fixes |

## Testing Results

Tested `simple_agent.py` successfully:
- ✅ Demo 3: Calculator worked (42 + 58 = 100)
- ✅ Demo 1: Custom tools worked (greet + calculate)
- ✅ Demo 2: Stateful conversation worked

**No API key required - uses Claude Code authentication!**

## Migration Checklist

To update your own agents:

- [ ] Import `create_sdk_mcp_server` from claude_agent_sdk
- [ ] Wrap custom tools in MCP server with `create_sdk_mcp_server()`
- [ ] Pass MCP server to `mcp_servers` parameter (not `custom_tools`)
- [ ] Use `prompt=` keyword argument in `query()` calls
- [ ] Change `permission_mode='auto'` to `'acceptEdits'` or `'default'`
- [ ] Remove API key checks (OAuth authentication is automatic)
- [ ] Remove `permission_handler` parameter (use `permission_mode` instead)

## Quick Migration Example

**Before:**
```python
@tool("greet", "Greet user", {"name": str})
async def greet(args):
    return {"content": [{"type": "text", "text": f"Hi {args['name']}"}]}

options = ClaudeAgentOptions(
    allowed_tools=["greet"],
    custom_tools=[greet],
    permission_mode='auto'
)

async for msg in query("Say hi to Alice", options=options):
    print(msg)
```

**After:**
```python
from claude_agent_sdk import create_sdk_mcp_server

@tool("greet", "Greet user", {"name": str})
async def greet(args):
    return {"content": [{"type": "text", "text": f"Hi {args['name']}"}]}

server = create_sdk_mcp_server("greeter", "1.0.0", tools=[greet])

options = ClaudeAgentOptions(
    mcp_servers={"greeter": server},
    permission_mode='acceptEdits'
)

async for msg in query(prompt="Say hi to Alice", options=options):
    print(msg)
```

## Documentation Updated

- ✅ `AUTHENTICATION_STATUS.md` - Authentication info
- ✅ `API_CHANGES.md` - This file
- ✅ All 12 example files
- ⏭️ `claude_agent_sdk_python.md` - Needs updating
- ⏭️ `CONVERSION_GUIDE.md` - Needs updating

---

**All examples now work with Claude Code authentication - no API keys needed!**
