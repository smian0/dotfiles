# Debugging Claude Agent SDK Workflows

Quick reference for debugging and visualizing workflow execution.

## Enable Debug Mode

Add `debug=True` when creating options:

```python
from workflow_helpers import create_base_options

options = await create_base_options(
    debug=True,              # Enable debug hooks
    verbose=True,            # Show detailed input/output
    workflow_name="my_workflow"  # Used in log filename
)
```

This automatically:
- Creates timestamped log files in `logs/` directory
- Logs every tool call with input/output
- Writes to both console (colored) and file (persistent)

## Log File Location

Logs are saved with timestamps:
```
logs/20251017_123456_my_workflow.log
```

Format: `YYYYMMDD_HHMMSS_{workflow_name}.log`

## Visualize Execution Tree

Display workflow execution as an ASCII tree:

```python
from workflow_tree_visualizer import visualize_workflow

# Basic visualization
visualize_workflow(log_file="logs/20251017_123456_my_workflow.log")

# Verbose mode with metrics
visualize_workflow(
    log_file="logs/20251017_123456_my_workflow.log",
    verbose=True,
    show_metrics=True,
    show_timeline=True
)
```

### CLI Usage

```bash
# Basic tree view
python -m helpers.workflow_tree_visualizer --log logs/my_workflow.log

# Verbose with metrics
python -m helpers.workflow_tree_visualizer --log logs/my_workflow.log --verbose --metrics

# With timeline
python -m helpers.workflow_tree_visualizer --log logs/my_workflow.log --timeline

# From JSONL transcript
python -m helpers.workflow_tree_visualizer --transcript transcript.jsonl --verbose
```

## Example Output

```
📊 Workflow Execution Tree
Started: 2025-10-17 17:32:52
Total tool calls: 1

🌳 tech_comparison
└── 🔧 TodoWrite (17:33:01.278)
    ├── ID: toolu_01DKNb9egHowLX...
    └── Input: todos: 5 items

📈 Metrics Summary

    Tool Usage
┏━━━━━━━━━━━┳━━━━━━━┓
┃ Tool      ┃ Calls ┃
┡━━━━━━━━━━━╇━━━━━━━┩
│ TodoWrite │     1 │
└───────────┴───────┘
```

## WorkflowLogger API

Direct usage of the logger:

```python
from workflow_helpers import WorkflowLogger

# Create logger
logger = WorkflowLogger(workflow_name="my_workflow")

# Log messages
logger.log("Starting workflow", level="INFO")
logger.log("Processing step 1", level="DEBUG")
logger.log("Task completed", level="TOOL")

# Log file location
print(logger.log_file)
```

### Log Levels

- `INFO` - General information (cyan)
- `DEBUG` - Detailed debugging (blue)
- `WARNING` - Warnings (yellow)
- `ERROR` - Errors (red)
- `TOOL` - Tool usage (magenta)

## Debug Hooks

Create custom hooks for advanced debugging:

```python
from workflow_helpers import create_debug_hooks, WorkflowLogger

# Create logger
logger = WorkflowLogger("my_workflow")

# Create hooks
hooks = await create_debug_hooks(logger, verbose=True)

# Use in options
options = ClaudeAgentOptions(
    model="claude-sonnet-4-20250514",
    hooks=hooks
)
```

Hook events:
- `PreToolUse` - Called before each tool use
- `PostToolUse` - Called after each tool use

## Trace Viewer (JSONL)

View Claude Code transcripts:

```python
from trace_viewer import TranscriptViewer

viewer = TranscriptViewer("transcript.jsonl")

# Get tool calls
tools = viewer.get_tool_calls()

# Display summary
viewer.display_summary()

# Show conversation
viewer.display_conversation()

# Export to JSON
viewer.export_summary("summary.json")
```

CLI:
```bash
# View transcript
python helpers/trace_viewer.py transcript.jsonl

# Show only tools
python helpers/trace_viewer.py transcript.jsonl --tools-only

# Show conversation
python helpers/trace_viewer.py transcript.jsonl --conversation

# Export summary
python helpers/trace_viewer.py transcript.jsonl --export summary.json
```

## Complete Example

```python
#!/usr/bin/env python3
import asyncio
from claude_agent_sdk import ClaudeSDKClient
from workflow_helpers import create_base_options, run_agent_task
from workflow_tree_visualizer import visualize_workflow
from rich.console import Console

async def main():
    console = Console()

    # Enable debug mode
    options = await create_base_options(
        debug=True,
        verbose=True,
        workflow_name="debug_demo"
    )

    # Run workflow
    async with ClaudeSDKClient(options=options) as client:
        result = await run_agent_task(
            client,
            "Create a todo list for this project",
            console=console
        )

    # Find log file
    from pathlib import Path
    logs = sorted(Path("logs").glob("*_debug_demo.log"))
    latest_log = logs[-1]

    # Visualize
    console.print(f"\n[bold cyan]Visualizing: {latest_log}[/bold cyan]\n")
    visualize_workflow(
        log_file=str(latest_log),
        verbose=True,
        show_metrics=True
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### No log files created

Check that debug mode is enabled:
```python
options = await create_base_options(debug=True)
```

### Tools not captured

Ensure hooks are properly configured. The `create_base_options()` with `debug=True` handles this automatically.

### JSON parsing errors in logs

This is normal for very verbose mode with large outputs. The tree visualizer handles truncation automatically.

### Cannot import visualizer

Make sure you're running from the skill directory or add it to path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "helpers"))
```

## Tips

1. **Always use debug mode during development** - Helps track tool calls and diagnose issues
2. **Check log files for detailed input/output** - More detail than console output
3. **Use tree visualization to understand execution flow** - Easy to spot issues
4. **Enable verbose mode for complex workflows** - Shows full input/output data
5. **Keep logs directory clean** - Old logs can accumulate quickly

---

**Last Updated:** 2025-10-17
