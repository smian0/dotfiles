# Complete Guide: Capturing Agent Responses in Claude SDK Workflows

## Problem: SDK Hooks Don't Capture Agent Outputs

The Claude Agent SDK's hook system (`PreToolUse`, `PostToolUse`) has limitations:

- ✅ **CAN capture**: Tool inputs, timing, context
- ❌ **CANNOT capture**: Agent text responses, sub-agent outputs, actual generated content

This means when you delegate to sub-agents, you see the delegation but not what the sub-agent produced.

## Solution: Dual-System Observability

We use **TWO complementary systems**:

1. **SDK Hooks** → Capture tool execution metadata
2. **Transcript Parser** → Extract agent responses from `.jsonl` files

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Workflow Execution                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SDK Hooks           Transcript File                       │
│  ↓                   ↓                                      │
│  PreToolUse    →     message events                        │
│  PostToolUse   →     tool_use events                       │
│                      tool_result events                    │
│                                                             │
│         ↓                    ↓                              │
│    workflow.log      session-id.jsonl                      │
│         ↓                    ↓                              │
│         └────────┬───────────┘                             │
│                  ↓                                          │
│     Enhanced Tree Visualizer                               │
│     (shows EVERYTHING)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Usage

### Step 1: Enable Debug Logging in Your Workflow

```python
from workflow_helpers import WorkflowLogger, create_debug_hooks

# Create logger
logger = WorkflowLogger("my_workflow")

# Create hooks with verbose mode
hooks = await create_debug_hooks(logger, verbose=True)

# Add hooks to options
options = ClaudeAgentOptions(
    model="claude-sonnet-4-20250514",
    allowed_tools=["Task", "TodoWrite", "Read", "Write"],
    hooks=hooks  # This captures tool metadata
)
```

This generates: `logs/YYYYMMDD_HHMMSS_my_workflow.log`

### Step 2: Get the Transcript File Path

The transcript file is created automatically by the SDK:

```python
async with ClaudeSDKClient(options=options) as client:
    # Run your workflow...
    result = await run_agent_task(client, prompt)

    # Get transcript path from client
    # Usually: ~/.claude/projects/<project-hash>/<session-id>.jsonl
```

Or extract from log file (it's logged in input_data):
```bash
grep "transcript_path" logs/my_workflow.log
```

### Step 3: Visualize with Agent Responses

```python
from helpers.workflow_tree_visualizer_enhanced import visualize_workflow_enhanced

visualize_workflow_enhanced(
    log_file="logs/20251017_180100_my_workflow.log",
    transcript_file="/path/to/session-id.jsonl",  # KEY!
    show_all_inputs=True,
    show_context=True,
    show_timing=True,
    show_agent_responses=True,  # Shows agent text!
    show_metrics=True
)
```

Or via CLI:
```bash
python helpers/workflow_tree_visualizer_enhanced.py \
    logs/my_workflow.log \
    --transcript /path/to/session-id.jsonl
```

---

## What You Get

### Before (Hooks Only)

```
🌳 Workflow
├── 1. 🔧 Task @ 18:01:12.652 ⏱️ 45.3s
│   ├── 📥 INPUT:
│   │   {
│   │     "prompt": "Research Python...",
│   │     "subagent_type": "general-purpose"
│   │   }
│   └── [No visibility into what sub-agent did or returned]
```

### After (Hooks + Transcript)

```
🌳 Workflow
├── 1. 🔧 Task @ 18:01:12.652 ⏱️ 45.3s
│   ├── 📥 INPUT:
│   │   {
│   │     "prompt": "Research Python...",
│   │     "subagent_type": "general-purpose"
│   │   }
│   └── 💬 Agent Response:
│       📝 Python is a high-level programming language...
│
│       Key features:
│       - Simple and readable syntax
│       - Extensive standard library
│       - Dynamic typing
│
│       Primary use cases:
│       - Web development (Django, Flask)
│       - Data science (NumPy, Pandas)
│       - Machine learning (TensorFlow, PyTorch)
│       ...
│
│       🔧 Tool Calls in Response: 3
│       • WebSearch (id: toolu_abc123)
│       • WebFetch (id: toolu_def456)
│       • TodoWrite (id: toolu_ghi789)
```

---

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete workflow with agent response logging.
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from workflow_helpers import WorkflowLogger, create_debug_hooks, run_agent_task
from workflow_tree_visualizer_enhanced import visualize_workflow_enhanced

async def main():
    # Step 1: Set up logging
    logger = WorkflowLogger("research_workflow")
    hooks = await create_debug_hooks(logger, verbose=True)

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        allowed_tools=["Task", "WebSearch", "WebFetch", "TodoWrite"],
        hooks=hooks
    )

    # Step 2: Run workflow
    transcript_path = None
    async with ClaudeSDKClient(options=options) as client:
        # Extract transcript path from first tool call
        result = await run_agent_task(
            client,
            "Research Python programming language comprehensively"
        )

        # Get transcript path from log
        with open(logger.log_file) as f:
            for line in f:
                if "transcript_path" in line:
                    import json
                    import re
                    match = re.search(r'"transcript_path":\s*"([^"]+)"', line)
                    if match:
                        transcript_path = match.group(1)
                        break

    print(f"\n✅ Workflow complete!")
    print(f"📄 Log: {logger.log_file}")
    print(f"📜 Transcript: {transcript_path}")

    # Step 3: Visualize with agent responses
    if transcript_path:
        print("\n" + "="*80)
        print("Visualizing with agent responses...")
        print("="*80 + "\n")

        visualize_workflow_enhanced(
            log_file=str(logger.log_file),
            transcript_file=transcript_path,
            show_all_inputs=True,
            show_agent_responses=True,
            show_timing=True
        )
    else:
        print("⚠️  Transcript path not found, showing tool calls only")
        visualize_workflow_enhanced(
            log_file=str(logger.log_file),
            show_all_inputs=True,
            show_timing=True
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Transcript Parser Standalone Usage

You can also use the transcript parser independently:

```python
from helpers.transcript_parser import TranscriptParser, parse_and_enhance

# Parse transcript
parser = TranscriptParser("session-id.jsonl")
parser.parse()

# Get agent responses
for msg in parser.get_agent_responses():
    print(f"Agent: {msg.text}")

# Get tool executions
for tool in parser.get_tool_executions():
    print(f"Tool: {tool.tool_name}")
    print(f"  Input: {tool.tool_input}")
    print(f"  Result: {tool.tool_result}")

# Export enhanced log
parser.export_to_enhanced_log("enhanced_workflow.log")
```

Or via CLI:
```bash
python helpers/transcript_parser.py session-id.jsonl output.log
```

---

## API Reference

### `visualize_workflow_enhanced()`

```python
def visualize_workflow_enhanced(
    log_file: str,
    transcript_file: Optional[str] = None,  # Path to .jsonl transcript
    show_all_inputs: bool = True,           # Show complete tool inputs
    show_context: bool = True,              # Show context data
    show_timing: bool = True,               # Show execution timing
    show_output: bool = False,              # Show output data (large!)
    show_agent_responses: bool = True,      # Show agent text responses
    show_metrics: bool = True               # Show metrics table
)
```

### `TranscriptParser`

```python
class TranscriptParser:
    def __init__(self, transcript_path: str)
    def parse(self) -> None
    def get_agent_responses(self) -> List[AgentMessage]
    def get_tool_executions(self) -> List[ToolExecution]
    def get_workflow_summary(self) -> Dict[str, Any]
    def export_to_enhanced_log(self, output_path: Optional[Path] = None)
```

---

## Troubleshooting

### Issue: "Transcript file not found"

**Cause**: Transcript path not extracted correctly

**Solution**:
```bash
# Find transcript in log
grep "transcript_path" logs/my_workflow.log

# Or search Claude projects directory
find ~/.claude/projects -name "*.jsonl" -mtime -1
```

### Issue: "No agent responses shown"

**Cause**: Transcript file not provided or empty

**Solution**:
1. Verify transcript file exists and has content
2. Check that `show_agent_responses=True` is set
3. Verify transcript has `message` events with `role: assistant`

### Issue: "Agent responses but no tool calls visible"

**Cause**: Log file doesn't have hook data

**Solution**: Ensure hooks are registered in `ClaudeAgentOptions`:
```python
options = ClaudeAgentOptions(
    hooks=await create_debug_hooks(logger, verbose=True)
)
```

---

## Comparison with Agno Workflow Debugger

| Feature | Our Implementation | Agno |
|---------|-------------------|------|
| Tool inputs | ✅ Complete | ✅ |
| Tool outputs | ✅ Via transcript | ✅ |
| Agent responses | ✅ Via transcript | ✅ |
| Sub-agent visibility | ⚠️ Limited | ✅ Full |
| Timing/metrics | ✅ | ✅ |
| Parallel execution viz | ⚠️ Coming soon | ✅ |
| Interactive debugging | ❌ | ✅ |

---

## Next Steps

1. ✅ SDK hooks capture tool metadata
2. ✅ Transcript parser extracts agent responses
3. ✅ Enhanced visualizer combines both
4. ⏳ **TODO**: Nested sub-agent visualization
5. ⏳ **TODO**: Parallel execution timeline
6. ⏳ **TODO**: Interactive debugging mode

---

## Summary

**The complete observability strategy:**

1. **Use SDK hooks** (`create_debug_hooks`) → Captures tool metadata
2. **Parse transcript files** (`TranscriptParser`) → Extracts agent responses
3. **Visualize combined data** (`visualize_workflow_enhanced`) → See everything!

This gives you **full visibility** into:
- What tools were called ✅
- What inputs were provided ✅
- **What agents responded** ✅ (NEW!)
- **What sub-agents generated** ✅ (NEW!)
- Tool execution timing ✅

You now have observability comparable to Agno's workflow debugger!
