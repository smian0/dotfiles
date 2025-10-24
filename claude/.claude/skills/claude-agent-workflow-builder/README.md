# Claude Agent Workflow Builder Skill

Build Agno-style workflows using Claude Agent SDK with patterns for sequential execution, parallel processing, custom tools, and multi-agent orchestration.

## Quick Start

### View Skill Documentation

```bash
# Open the skill in Claude Code
@claude-agent-workflow-builder

# Ask for help
"Help me create a workflow that researches a topic from multiple angles in parallel"
```

### Use Templates

```bash
# Simple sequential workflow
cp ~/.claude/skills/claude-agent-workflow-builder/templates/simple_workflow.py my_workflow.py

# Parallel subagent workflow
cp ~/.claude/skills/claude-agent-workflow-builder/templates/parallel_workflow.py my_workflow.py

# Custom tools workflow
cp ~/.claude/skills/claude-agent-workflow-builder/templates/custom_tool_workflow.py my_workflow.py

# Hybrid workflow (sequential + parallel)
cp ~/.claude/skills/claude-agent-workflow-builder/templates/hybrid_workflow.py my_workflow.py
```

### Run Examples

```bash
# Complete research workflow example
python ~/.claude/skills/claude-agent-workflow-builder/examples/research_workflow.py
```

## What's Included

### Templates (`templates/`)

- **simple_workflow.py** - Sequential multi-step processing
- **parallel_workflow.py** - Parallel subagent execution
- **custom_tool_workflow.py** - Custom MCP tool integration
- **hybrid_workflow.py** - Sequential + parallel combination

### Helper Functions (`helpers/workflow_helpers.py`)

**Debugging and Tracing:**
- `WorkflowLogger` - Dual-output logger (console + file)
- `create_debug_hooks()` - Pre/post tool use hooks for debugging
- `visualize_workflow()` - ASCII tree visualization of workflow execution

**Message Parsing:**
- `extract_text_from_message()` - Extract text from any message
- `extract_tool_uses()` - Get tool usage information
- `collect_full_response()` - Collect streaming response

**Workflow Execution:**
- `run_agent_task()` - Execute single agent task
- `run_sequential_tasks()` - Run multiple tasks in sequence
- `run_conversation_loop()` - Interactive conversation mode

**Subagent Creation:**
- `create_researcher_agent()` - Pre-configured research specialist
- `create_analyst_agent()` - Data analysis specialist
- `create_code_reviewer_agent()` - Code review specialist

**Display Utilities:**
- `print_message()` - Pretty-print messages with roles
- `print_tool_use()` - Display tool usage information
- `get_user_input()` - Styled user input prompt

**Configuration:**
- `create_base_options()` - Base agent configuration with optional debug mode

### Examples (`examples/`)

- **research_workflow.py** - Comprehensive research workflow
  - Topic analysis
  - Parallel research (3 specialists)
  - Synthesis
  - Report generation

## Usage Patterns

### Debug Mode and Tree Visualization

```python
from workflow_helpers import create_base_options
from workflow_tree_visualizer import visualize_workflow

# Enable debug mode to log all tool calls
options = await create_base_options(
    debug=True,
    verbose=True,
    workflow_name="my_workflow"
)

async with ClaudeSDKClient(options=options) as client:
    # Run your workflow...
    result = await run_agent_task(client, "Research topic...")

# Visualize execution as ASCII tree
visualize_workflow(
    log_file="logs/20251017_123456_my_workflow.log",
    verbose=True,
    show_metrics=True,
    show_timeline=True
)
```

### Sequential Workflow

```python
from workflow_helpers import run_agent_task

async with ClaudeSDKClient(options=options) as client:
    # Step 1
    result1 = await run_agent_task(client, "Research topic...")

    # Step 2 (builds on Step 1)
    result2 = await run_agent_task(client, "Analyze findings...")

    # Step 3 (builds on Step 2)
    result3 = await run_agent_task(client, "Generate recommendations...")
```

### Parallel Workflow

```python
options = ClaudeAgentOptions(
    allowed_tools=['Task'],  # Required!
    agents={
        "specialist-1": AgentDefinition(...),
        "specialist-2": AgentDefinition(...),
        "specialist-3": AgentDefinition(...)
    }
)

async with ClaudeSDKClient(options=options) as client:
    # Delegates to all 3 specialists in parallel
    await client.query("Coordinate analysis across all specialists...")
```

### Custom Tools

```python
@tool("my_tool", "Description", {"param": type})
async def my_tool(args):
    result = process(args['param'])
    return {"content": [{"type": "text", "text": json.dumps(result)}]}

server = create_sdk_mcp_server(name="my_server", tools=[my_tool])
options = ClaudeAgentOptions(
    mcp_servers={"my_server": server},
    allowed_tools=['mcp__my_server__my_tool']
)
```

## Agno vs Claude SDK

### When to Use Agno

✅ Code simplicity (30-60% less code)
✅ Multi-model flexibility (GPT/Claude/Ollama)
✅ Fast prototyping
✅ Rich built-in tools

### When to Use Claude SDK

✅ Coding agents (file/bash operations)
✅ IDE integration (Claude Code)
✅ No API key needed (Claude Code auth)
✅ Extended context windows
✅ CLAUDE.md project memory

## Installation

The skill uses standard Claude Agent SDK:

```bash
# Install dependencies
pip install claude-agent-sdk python-dotenv rich

# Optional: Set up API key
# (Not needed if using Claude Code auth)
echo "ANTHROPIC_API_KEY=your_key" > .env
```

## Documentation

- **SKILL.md** - Complete skill documentation
- **templates/** - Ready-to-use workflow templates
- **examples/** - Practical workflow examples
- **helpers/** - Utility functions

## Common Tasks

**Create a simple sequential workflow:**
```bash
cp templates/simple_workflow.py my_workflow.py
# Edit my_workflow.py with your steps
python my_workflow.py
```

**Create a parallel research workflow:**
```bash
cp templates/parallel_workflow.py my_workflow.py
# Customize subagent definitions
python my_workflow.py
```

**Add custom tools:**
```bash
cp templates/custom_tool_workflow.py my_workflow.py
# Add your custom tool functions
python my_workflow.py
```

## Tips

1. **Start with templates** - Don't write from scratch
2. **Use helper functions** - Reduce boilerplate
3. **Enable debug mode** - Track tool calls with `debug=True` in options
4. **Visualize execution** - Use `visualize_workflow()` to see tool call tree
5. **Configure subagents properly** - Clear descriptions, minimal tools
6. **Handle async correctly** - Use `asyncio.run(main())`
7. **Add Rich console** - Better user experience

## Resources

- [Claude Agent SDK Docs](https://docs.claude.com/en/api/agent-sdk/python)
- [Subagents Guide](https://docs.claude.com/en/api/agent-sdk/subagents)
- [Custom Tools](https://docs.claude.com/en/api/agent-sdk/custom-tools)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)

## Contributing

This is a personal skill - feel free to:
- Modify templates for your needs
- Add new patterns
- Create specialized subagents
- Build custom tools

---

**Last Updated:** 2025-10-17
