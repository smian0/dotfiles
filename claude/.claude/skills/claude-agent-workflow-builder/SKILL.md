---
name: claude-agent-workflow-builder
description: Build multi-step AI workflows using Claude Agent SDK with patterns similar to Agno workflows. Use when you need sequential execution, parallel processing, custom tool integration, or complex multi-agent orchestration. Appropriate for "create a research workflow", "add parallel subagents", or "integrate custom tools with agents".
---

# Claude Agent Workflow Builder

Build production-ready Claude Agent SDK workflows with patterns inspired by Agno's workflow system. Create sequential, parallel, and hybrid workflows with specialized subagents, custom tools, and comprehensive orchestration.

## Overview

This skill helps you build workflows using Claude Agent SDK that mirror Agno's workflow patterns while leveraging Claude-specific features like deep file integration, IDE support, and extended context windows.

**Key capabilities:**
- Sequential multi-step workflows
- Parallel subagent execution
- Custom tool integration via MCP
- Hybrid workflows (sequential + parallel)
- Helper functions to reduce boilerplate
- Message parsing utilities
- Ready-to-use templates

## Quick Start

### Creating a Simple Workflow

```bash
# Use the simple workflow template
cp ~/.claude/skills/claude-agent-workflow-builder/templates/simple_workflow.py my_workflow.py

# Run it
python my_workflow.py
```

### Pattern Overview

| Pattern | Use When | Agno Equivalent |
|---------|----------|-----------------|
| **Simple Sequential** | Linear multi-step tasks | `Workflow(steps=[step1, step2, step3])` |
| **Parallel** | Independent tasks | `Parallel(step1, step2, step3)` |
| **Custom Tools** | Need specialized functions | `Agent(tools=[custom_tool])` |
| **Hybrid** | Complex multi-phase workflows | Sequential + Parallel steps |

## Authentication

The Claude Agent SDK supports two authentication methods:

### Option 1: Claude Code Authentication (Recommended)

**If you have Claude Code installed and authenticated, no additional setup is needed!**

The SDK automatically uses your Claude Code session. Generated workflows will run immediately without requiring an API key.

**Requirements:**
- Claude Code installed: `npm install -g @anthropic-ai/claude-code`
- Authenticated via `claude` command (already done if you're using Claude Code)

**How it works:**
```python
# No API key needed - SDK automatically uses Claude Code auth
async with ClaudeSDKClient(options=options) as client:
    result = await run_agent_task(client, "Your prompt")
```

### Option 2: Anthropic API Key

If you're not using Claude Code or want to use a specific API key:

```bash
# Get API key from console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-api01-..."

# Make persistent (add to ~/.zshrc or ~/.bashrc)
echo 'export ANTHROPIC_API_KEY="sk-ant-api01-..."' >> ~/.zshrc
source ~/.zshrc
```

Or create a `.env` file in your workflow directory:
```bash
ANTHROPIC_API_KEY=sk-ant-api01-...
```

**Authentication priority:**
1. `ANTHROPIC_API_KEY` environment variable (if set)
2. Claude Code authentication (if available)
3. `.env` file in current directory

### Verification

Test your authentication with any generated workflow:
```bash
cd <project_root>/claude_workflows/my_workflow
python workflow.py
```

If authentication succeeds, the workflow will start. If not, you'll see an authentication error.

## Workflow Generation

The skill includes a workflow generator that creates properly structured workflows in your project's `claude_workflows/` directory, similar to how Agno creates workflows in `agno_workflows/`.

### Using the Workflow Generator

**Create workflow from template:**
```python
from workflow_generator import create_workflow_from_template

# Create a new workflow from template
result = create_workflow_from_template(
    template="simple",                    # or: parallel, custom_tool, hybrid
    workflow_name="my_research",
    description="Research workflow for AI topics"
)

print(f"Created: {result['workflow_path']}")
# Output: <project_root>/claude_workflows/my_research/workflow.py
```

**Interactive CLI:**
```bash
cd ~/.claude/skills/claude-agent-workflow-builder/helpers
python workflow_generator.py
```

### Generated Structure

The generator creates:
```
<project_root>/claude_workflows/my_research/
├── workflow.py              # Main executable workflow
├── docs/                    # Output directory for reports
└── README.md                # Usage instructions
```

**Example generated workflow.py:**
```python
#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Helpers automatically referenced
sys.path.insert(0, "/path/to/skill/helpers")

from claude_agent_sdk import ClaudeSDKClient
from workflow_helpers import create_base_options, run_agent_task
# ... rest of workflow code
```

### Available Functions

**Find project root:**
```python
from workflow_generator import get_project_root

root = get_project_root()  # Finds .git, pyproject.toml, etc.
```

**Get workflows directory:**
```python
from workflow_generator import get_workflows_dir

workflows_dir = get_workflows_dir()  # <project_root>/claude_workflows/
```

**List existing workflows:**
```python
from workflow_generator import list_workflows

workflows = list_workflows()
for wf in workflows:
    print(f"{wf['name']}: {wf['path']}")
```

**Copy template to project:**
```python
from workflow_generator import copy_template_to_project

path = copy_template_to_project("parallel", "multi_angle_research")
# Creates claude_workflows/multi_angle_research/workflow.py
```

### Template Selection Guide

| Template | Best For | Typical Use Case |
|----------|----------|------------------|
| `simple` | Linear pipelines | Research → Analysis → Report |
| `parallel` | Independent tasks | Multi-perspective research |
| `custom_tool` | Specialized functions | API integration, data processing |
| `hybrid` | Multi-phase workflows | Prep → Parallel → Synthesis |

### Integration with IDEs

The generated workflows work seamlessly with:
- **Claude Code**: Use `claude-agent run workflow.py` or Claude Code SDK
- **VS Code**: Standard Python execution
- **Command Line**: `python workflow.py` (with proper environment)

## Workflow Patterns

### 1. Sequential Workflow

Process tasks through multiple sequential steps.

**When to use:**
- Tasks depend on previous results
- Linear processing pipeline
- Step-by-step analysis

**Template:** `templates/simple_workflow.py`

**Key concepts:**
```python
async with ClaudeSDKClient(options=options) as client:
    # Step 1: Research
    result1 = await run_agent_task(client, "Research...")

    # Step 2: Analyze (builds on Step 1)
    result2 = await run_agent_task(client, "Analyze based on previous research...")

    # Step 3: Recommend (builds on Step 2)
    result3 = await run_agent_task(client, "Recommend based on analysis...")
```

**Equivalent Agno:**
```python
workflow = Workflow(
    steps=[
        Step(name="Research", agent=agent),
        Step(name="Analyze", agent=agent),
        Step(name="Recommend", agent=agent)
    ]
)
```

### 2. Parallel Workflow

Execute multiple independent tasks simultaneously via subagents.

**When to use:**
- Tasks are independent
- Multiple perspectives needed
- Speed optimization (N tasks in parallel)

**Template:** `templates/parallel_workflow.py`

**Key concepts:**
```python
options = ClaudeAgentOptions(
    allowed_tools=['Task'],  # Required!
    agents={
        "researcher-1": AgentDefinition(...),
        "researcher-2": AgentDefinition(...),
        "researcher-3": AgentDefinition(...)
    }
)

async with ClaudeSDKClient(options=options) as client:
    # Main agent delegates to subagents in parallel
    await client.query("Coordinate research across 3 specialists...")
```

**Equivalent Agno:**
```python
parallel = Parallel(
    Step(name="Research 1", agent=agent1),
    Step(name="Research 2", agent=agent2),
    Step(name="Research 3", agent=agent3)
)
workflow = Workflow(steps=[parallel, synthesize_step])
```

### 3. Custom Tool Workflow

Integrate custom functions via MCP servers.

**When to use:**
- Need specialized computations
- External API integration
- Custom data processing

**Template:** `templates/custom_tool_workflow.py`

**Key concepts:**
```python
# 1. Define custom tool
@tool("analyze_sentiment", "Analyze sentiment", {"text": str})
async def analyze_sentiment(args):
    result = {...}  # Your logic
    return {"content": [{"type": "text", "text": json.dumps(result)}]}

# 2. Create MCP server
server = create_sdk_mcp_server(
    name="analysis",
    tools=[analyze_sentiment]
)

# 3. Configure agent
options = ClaudeAgentOptions(
    mcp_servers={"analysis": server},
    allowed_tools=['mcp__analysis__analyze_sentiment']
)
```

**Equivalent Agno:**
```python
@tool()
def analyze_sentiment(text: str) -> str:
    return result

agent = Agent(tools=[analyze_sentiment])
```

### 4. Hybrid Workflow

Combine sequential and parallel patterns.

**When to use:**
- Complex multi-phase workflows
- Need prep → parallel → synthesis pattern
- Optimize specific phases for speed

**Template:** `templates/hybrid_workflow.py`

**Pattern:**
```
Phase 1 (Sequential): Prepare/Plan
         ↓
Phase 2 (Parallel): [Task 1 | Task 2 | Task 3]
         ↓
Phase 3 (Sequential): Synthesize Results
         ↓
Phase 4 (Sequential): Save/Format Output
```

**Equivalent Agno:**
```python
workflow = Workflow(
    steps=[
        Step(name="Prep", agent=prep_agent),
        Parallel(step1, step2, step3),
        Step(name="Synthesize", executor=synthesize),
        Step(name="Save", executor=save)
    ]
)
```

## Helper Functions

The skill provides helper functions in `helpers/workflow_helpers.py` to reduce boilerplate.

### Message Parsing

```python
from workflow_helpers import extract_text_from_message, extract_tool_uses

# Extract text from any message
text = extract_text_from_message(message)

# Extract tool usage information
tools = extract_tool_uses(message)
for tool in tools:
    print(f"Tool: {tool['name']}")
```

### Workflow Execution

```python
from workflow_helpers import run_agent_task, run_sequential_tasks

# Run single task
response = await run_agent_task(client, "Your prompt", show_tools=True)

# Run multiple sequential tasks
tasks = ["Task 1", "Task 2", "Task 3"]
results = await run_sequential_tasks(client, tasks, console)
```

### Subagent Creation

```python
from workflow_helpers import (
    create_researcher_agent,
    create_analyst_agent,
    create_code_reviewer_agent
)

# Pre-configured subagent definitions
agents = {
    "researcher": create_researcher_agent(),
    "analyst": create_analyst_agent(),
    "reviewer": create_code_reviewer_agent()
}
```

### Display Utilities

```python
from workflow_helpers import print_message, print_tool_use

# Pretty-print messages
print_message("user", "Hello!", console)
print_message("assistant", "Hi there!", console)

# Display tool usage
print_tool_use("search_web", {"query": "AI agents"}, console)
```

### Interactive Helpers

```python
from workflow_helpers import run_conversation_loop

# Run interactive conversation
async with ClaudeSDKClient(options=options) as client:
    await run_conversation_loop(client, console, show_tools=True)
```

## Creating Custom Workflows

### Step-by-Step Guide

**Recommended: Use Workflow Generator**

1. **Choose Pattern**
   - Sequential: Linear pipeline
   - Parallel: Independent tasks
   - Custom Tools: Specialized functions
   - Hybrid: Combination

2. **Generate Workflow** (RECOMMENDED)
   ```python
   from workflow_generator import create_workflow_from_template

   result = create_workflow_from_template(
       template="simple",           # or: parallel, custom_tool, hybrid
       workflow_name="my_analysis",
       description="Custom analysis workflow"
   )
   # Creates: <project_root>/claude_workflows/my_analysis/
   ```

3. **Customize Generated Workflow**
   ```bash
   cd <project_root>/claude_workflows/my_analysis
   # Edit workflow.py to customize
   ```

**Alternative: Manual Template Copy**

2. **Copy Template Manually**
   ```bash
   cp ~/.claude/skills/claude-agent-workflow-builder/templates/<pattern>_workflow.py my_workflow.py
   ```

3. **Configure Options**
   ```python
   options = ClaudeAgentOptions(
       model="claude-sonnet-4-20250514",
       allowed_tools=[...],
       agents={...}  # If using subagents
   )
   ```

4. **Implement Steps**
   - Define your workflow logic
   - Use helper functions
   - Handle errors gracefully

5. **Test**
   ```bash
   python my_workflow.py
   ```

### Best Practices

**1. Use Helper Functions**
```python
# Instead of manual message parsing
async for message in client.receive_response():
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)

# Use helper
response = await run_agent_task(client, prompt, console=console)
```

**2. Configure Subagents Properly**
```python
# Good: Clear description
AgentDefinition(
    description="Analyzes code security vulnerabilities and generates reports",
    prompt="You are a security expert...",
    tools=['Read', 'Write', 'Grep']
)

# Bad: Vague description
AgentDefinition(
    description="A helper agent",  # Main agent won't know when to use this
    ...
)
```

**3. Handle Async Properly**
```python
# Good: Proper async handling
async def main():
    async with ClaudeSDKClient(options=options) as client:
        result = await run_agent_task(client, prompt)

if __name__ == "__main__":
    asyncio.run(main())
```

**4. Use Rich for Better UX**
```python
from rich.console import Console

console = Console()
console.print("[bold green]Starting workflow...[/bold green]")
print_message("assistant", result, console)
```

**5. Error Handling**
```python
try:
    result = await run_agent_task(client, prompt)
except Exception as e:
    console.print(f"[red]Error: {e}[/red]")
    # Handle error
```

## Subagent Design

### Creating Effective Subagents

**Single Responsibility:**
```python
# Good: Focused specialty
"security-reviewer": AgentDefinition(
    description="Reviews code for security vulnerabilities only",
    ...
)

# Bad: Too broad
"helper": AgentDefinition(
    description="Does various tasks",
    ...
)
```

**Minimal Tools:**
```python
# Good: Only what's needed
tools=['Read', 'Write', 'Grep']

# Bad: Unnecessary access
tools=['Read', 'Write', 'Bash', 'Delete', 'Edit']  # Too many!
```

**Clear Instructions:**
```python
prompt="""You are a data analyst.

When analyzing data:
1. Read the data file
2. Calculate key statistics
3. Identify patterns
4. Generate visualizations if helpful
5. Write report to /docs

Task complete when:
- Report is saved
- All metrics are documented
- Visualizations are included
"""
```

### Pre-Built Subagent Templates

```python
from workflow_helpers import (
    create_researcher_agent,      # Web research specialist
    create_analyst_agent,          # Data analysis specialist
    create_code_reviewer_agent     # Code review specialist
)

agents = {
    "researcher": create_researcher_agent(
        tools=['Read', 'Write', 'WebSearch', 'WebFetch'],
        model="sonnet"
    ),
    "analyst": create_analyst_agent(),
    "reviewer": create_code_reviewer_agent()
}
```

## Custom Tools

### Three-Step Integration

**1. Define Tool:**
```python
@tool("tool_name", "Description", {"param": type})
async def my_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    result = process(args['param'])
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result)
        }]
    }
```

**2. Create MCP Server:**
```python
server = create_sdk_mcp_server(
    name="my_server",
    version="1.0.0",
    tools=[my_tool]
)
```

**3. Configure Agent:**
```python
options = ClaudeAgentOptions(
    mcp_servers={"my_server": server},
    allowed_tools=['mcp__my_server__tool_name']
)
```

### Tool Naming Convention

Format: `mcp__<server_name>__<tool_name>`

Examples:
- `mcp__analysis__analyze_sentiment`
- `mcp__data__calculate_stats`
- `mcp__search__find_documents`

## Agno vs Claude SDK

### Code Comparison

**Agno (35 lines):**
```python
from agno.agent import Agent
from agno.workflow import Workflow, Step
from agno.models.ollama import Ollama

agent = Agent(model=Ollama(id="llama3.1:8b"))
workflow = Workflow(steps=[
    Step(name="Research", agent=agent),
    Step(name="Analyze", agent=agent)
])
result = workflow.run(input="Query")
print(result.content)
```

**Claude SDK (45 lines with helpers):**
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from workflow_helpers import run_sequential_tasks

async def main():
    options = ClaudeAgentOptions(model="claude-sonnet-4-20250514")

    async with ClaudeSDKClient(options=options) as client:
        tasks = ["Research...", "Analyze..."]
        results = await run_sequential_tasks(client, tasks)
        print(results[-1])

asyncio.run(main())
```

### When to Use Each

**Use Agno When:**
- ✅ Code simplicity is priority
- ✅ Multi-model flexibility needed (GPT/Claude/Ollama)
- ✅ Prototyping quickly
- ✅ 30-60% less code desired

**Use Claude SDK When:**
- ✅ Building coding agents (file/bash integration)
- ✅ Want IDE integration (Claude Code)
- ✅ Using Claude Code auth (no API key)
- ✅ Need extended context windows
- ✅ Want CLAUDE.md project memory

## Examples

### Example 1: Research Workflow

```python
#!/usr/bin/env python3
"""Multi-perspective research workflow"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from workflow_helpers import run_agent_task, print_message
from rich.console import Console

async def main():
    console = Console()

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        allowed_tools=['Task', 'Read', 'Write', 'WebSearch', 'WebFetch'],
        agents={
            "history-researcher": AgentDefinition(
                description="Researches historical context and evolution",
                prompt="Focus on historical development and key milestones",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch']
            ),
            "current-researcher": AgentDefinition(
                description="Researches current state and trends",
                prompt="Focus on current state, key players, recent developments",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch']
            )
        }
    )

    async with ClaudeSDKClient(options=options) as client:
        # Parallel research
        prompt = """Research AI agents from two angles:
1. Historical evolution (delegate to history-researcher)
2. Current landscape (delegate to current-researcher)

Then synthesize into comprehensive report."""

        result = await run_agent_task(client, prompt, console=console)
        print_message("assistant", result, console)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Data Analysis Pipeline

```python
#!/usr/bin/env python3
"""Sequential data analysis workflow"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient
from workflow_helpers import create_base_options, run_sequential_tasks
from rich.console import Console

async def main():
    console = Console()
    options = create_base_options(allowed_tools=['Read', 'Write', 'Edit'])

    tasks = [
        "Read data from /data/metrics.csv and provide summary",
        "Identify top 3 patterns in the data",
        "Calculate statistics and trends",
        "Generate insights report in /docs/analysis.md"
    ]

    async with ClaudeSDKClient(options=options) as client:
        results = await run_sequential_tasks(client, tasks, console)

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Common Issues

**Issue: Authentication errors / "Invalid API key"**
- **Cause**: No authentication configured
- **Solution**: Either:
  1. Use Claude Code authentication (recommended - see Authentication section)
  2. Set `ANTHROPIC_API_KEY` environment variable
  3. Create `.env` file with API key
- **Verification**: Run `python workflow.py` - if it starts, auth is working

**Issue: "Task tool not found"**
- **Cause**: Task tool not in allowed_tools
- **Solution**: Add `'Task'` to allowed_tools list

**Issue: "Subagent 'xyz' not found"**
- **Cause**: Typo in agent name
- **Solution**: Verify exact name (case-sensitive)

**Issue: Message parsing errors**
- **Cause**: Manual parsing of complex message types
- **Solution**: Use `extract_text_from_message()` helper

**Issue: Subagent can't access tools**
- **Cause**: Tools not specified in subagent definition
- **Solution**: Add required tools to subagent's `tools` list

**Issue: MCP tools not working**
- **Cause**: Incorrect tool naming
- **Solution**: Use exact format: `mcp__<server>__<tool>`

**Issue: Workflow hangs or doesn't respond**
- **Cause**: Authentication issue or network problem
- **Solution**:
  1. Check authentication (see above)
  2. Verify internet connection
  3. Try with simpler prompt first

### Debug Tips

**1. Show Tool Usage:**
```python
result = await run_agent_task(client, prompt, show_tools=True)
```

**2. Check Available Tools:**
```python
options = ClaudeAgentOptions(allowed_tools=[...])
print(options.allowed_tools)
```

**3. Monitor Subagent Calls:**
```python
tools = extract_tool_uses(message)
for tool in tools:
    if tool['name'] == 'Task':
        print(f"Delegating to: {tool['input']}")
```

**4. Use Rich Console:**
```python
from rich.console import Console
console = Console()
console.print("[yellow]Debug info[/yellow]")
```

## Debugging & Tracing

The skill includes comprehensive debugging capabilities for tracing workflow execution, tool usage, and troubleshooting issues.

### Debug Mode

Enable debug mode to log all tool calls to both console and file:

```python
from workflow_helpers import create_base_options

# Enable debugging with dual output (console + file)
options = await create_base_options(
    debug=True,              # Enable debug mode
    verbose=True,            # Show detailed input/output
    workflow_name="my_workflow"  # Name for log files
)

async with ClaudeSDKClient(options=options) as client:
    # All tool calls will be logged automatically
    result = await run_agent_task(client, "Your prompt")
```

**What gets logged:**
- Every tool call with timestamp
- Tool inputs (full JSON when verbose=True)
- Tool outputs (truncated if > 500 chars)
- Errors with context
- Execution flow

**Output locations:**
- **Console**: Real-time colored output with Rich formatting
- **File**: `logs/YYYYMMDD_HHMMSS_<workflow_name>.log`

### Trace Viewer

View JSONL transcript files created by Claude Code in human-readable format:

```bash
# View full transcript summary
python ~/.claude/skills/claude-agent-workflow-builder/helpers/trace_viewer.py transcript.jsonl

# Show only tool calls
python trace_viewer.py transcript.jsonl --tools-only

# Show detailed tool input/output
python trace_viewer.py transcript.jsonl --tools-only --verbose

# Show conversation flow
python trace_viewer.py transcript.jsonl --conversation

# Export to markdown
python trace_viewer.py transcript.jsonl --export report.md
```

**Trace viewer features:**
- Summary statistics (messages, tool calls, timing)
- Tool usage breakdown by type
- Conversation flow with timestamps
- Detailed tool call inspection
- Markdown export for documentation

### WorkflowLogger

Direct access to logging for custom workflows:

```python
from workflow_helpers import WorkflowLogger

# Create logger
logger = WorkflowLogger(workflow_name="custom_workflow", log_dir="my_logs")

# Log messages (console + file)
logger.log("Starting phase 1", level="INFO")
logger.log("Processing data...", level="DEBUG")
logger.log("Critical error!", level="ERROR")
logger.log("Tool call: WebSearch", level="TOOL")

# Check log file location
print(f"Logs: {logger.log_file}")
```

**Log levels:**
- `INFO`: General information (cyan)
- `DEBUG`: Detailed debugging info (blue)
- `WARNING`: Warning messages (yellow)
- `ERROR`: Error messages (red)
- `TOOL`: Tool usage (magenta)

### Custom Debug Hooks

Create custom pre/post tool hooks for advanced debugging:

```python
from workflow_helpers import create_debug_hooks, WorkflowLogger

# Create logger and hooks
logger = WorkflowLogger("advanced_workflow")
hooks = await create_debug_hooks(logger, verbose=True)

# Use with options
options = ClaudeAgentOptions(
    hooks=hooks,
    # ... other options
)
```

**Hook capabilities:**
- `pre_tool_use`: Called before each tool execution
- `post_tool_use`: Called after each tool execution
- `on_error`: Called when errors occur

### Debugging Examples

**Example 1: Debug a slow workflow**
```python
# Enable debug mode to see exactly what's happening
options = await create_base_options(
    debug=True,
    verbose=True,
    workflow_name="slow_research"
)

async with ClaudeSDKClient(options=options) as client:
    result = await run_agent_task(client, "Research AI trends")

# Check logs/YYYYMMDD_HHMMSS_slow_research.log to see:
# - Which tools took the longest
# - What data was being processed
# - Where the workflow is spending time
```

**Example 2: Trace subagent delegation**
```python
# Enable verbose logging to see subagent calls
options = await create_base_options(
    debug=True,
    verbose=True,
    allowed_tools=['Task'],  # Include Task for subagents
    agents={
        "researcher": create_researcher_agent()
    }
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Delegate research to researcher subagent")

# Log will show:
# [TOOL] Using tool: Task
# [DEBUG] Input: {"agent": "researcher", "prompt": "..."}
```

**Example 3: Analyze completed workflow**
```bash
# After workflow completes, analyze the trace
cd logs
python ../helpers/trace_viewer.py 20251017_143052_my_workflow.log --tools-only --verbose

# Export detailed report
python ../helpers/trace_viewer.py 20251017_143052_my_workflow.log --export analysis.md
```

### Debugging Best Practices

**1. Start with debug mode ON for new workflows:**
```python
# During development
options = await create_base_options(debug=True, verbose=True)
```

**2. Use trace viewer to understand execution flow:**
```bash
# After running workflow
python trace_viewer.py logs/latest.jsonl --conversation
```

**3. Check logs for errors:**
```bash
# Search for errors in log files
grep -i "error" logs/*.log
```

**4. Monitor tool usage patterns:**
```bash
# See which tools are being called most
python trace_viewer.py transcript.jsonl --tools-only | grep "Using tool"
```

**5. Disable debug mode in production:**
```python
# Production: no debugging overhead
options = await create_base_options(debug=False)
```

### Log File Management

Debug logs are automatically created in the `logs/` directory:

```
logs/
├── 20251017_143052_workflow1.log
├── 20251017_150334_workflow2.log
└── 20251017_162145_workflow3.log
```

**Cleanup old logs:**
```bash
# Remove logs older than 7 days
find logs/ -name "*.log" -mtime +7 -delete
```

**Archive logs:**
```bash
# Archive all logs
tar -czf workflow_logs_$(date +%Y%m%d).tar.gz logs/
```

## Performance Optimization

### Model Selection

| Model | Use For | Cost | Speed |
|-------|---------|------|-------|
| Haiku | Simple tasks, summaries | Low | Fast |
| Sonnet | Most workflows | Medium | Balanced |
| Opus | Complex reasoning | High | Slower |

### Parallelization

```python
# Sequential: 3x time
tasks = [task1, task2, task3]
await run_sequential_tasks(client, tasks)  # 30 seconds

# Parallel: ~1x time
# Delegate to 3 subagents simultaneously
await client.query("Coordinate 3 parallel analyses")  # 10 seconds
```

### Tool Caching

For repeated operations, cache results:

```python
# In custom tools
@tool("cached_search", "Search with cache", {"query": str})
async def cached_search(args):
    cache_key = f"search_{args['query']}"
    if cache_key in cache:
        return cache[cache_key]

    result = perform_search(args['query'])
    cache[cache_key] = result
    return result
```

## References

### Official Documentation

- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/python)
- [Subagents Guide](https://docs.claude.com/en/api/agent-sdk/subagents)
- [Custom Tools](https://docs.claude.com/en/api/agent-sdk/custom-tools)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)

### Templates

- `templates/simple_workflow.py` - Sequential workflow
- `templates/parallel_workflow.py` - Parallel subagents
- `templates/custom_tool_workflow.py` - Custom MCP tools
- `templates/hybrid_workflow.py` - Sequential + parallel

### Helper Modules

- `helpers/workflow_helpers.py` - Workflow utilities, execution helpers, and debugging tools
- `helpers/workflow_generator.py` - Workflow generation and project management
- `helpers/trace_viewer.py` - JSONL transcript viewer and analysis tool

## When to Use This Skill

Use this skill when:
- Creating multi-step Claude Agent SDK workflows
- Need patterns similar to Agno workflows
- Building sequential or parallel agent orchestration
- Integrating custom tools with agents
- Want to reduce SDK boilerplate
- Need workflow templates and patterns

The skill provides Agno-like workflow patterns while leveraging Claude's unique advantages.
