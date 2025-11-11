# Workflow Debugging and Optimization Guide

This guide covers how to configure automatic debugging, optimization analysis, and performance monitoring for Agno workflows.

## Quick Setup (Idiomatic Pattern)

```python
from agno.workflow import Workflow
from agno.db.sqlite import SqliteDb
from cookbook.utils.workflow_config import configure_workflow_debug
from pathlib import Path

# Create workflow with event storage
workflow = Workflow(
    name="My Workflow",
    description="Workflow description",
    steps=[...],
    store_events=True,  # REQUIRED for debugging
    debug_mode=False,   # False for clean output
    db=SqliteDb(db_file="tmp/workflow.db"),  # REQUIRED
)

# Configure automatic debug export
configure_workflow_debug(
    workflow,
    show_console_tree=True,       # Show ASCII tree after execution
    export_markdown=True,          # Export detailed debug report
    reports_dir="./reports",       # Where to save reports
    report_pattern="output_*.md",  # Pattern to match output files
    verbose=True,                  # Include detailed metrics
    include_analysis=True,         # Include optimization analysis
)

# Execute workflow
result = workflow.print_response(
    input="...",
    stream=True,  # CRITICAL for event capture
    stream_intermediate_steps=True,
)

# Debug export happens automatically!
```

## Debug Output Components

When `configure_workflow_debug()` is enabled, you get:

### 1. Console Tree (if `show_console_tree=True`)

```
🌳 My Workflow
├─ ✓ 0: Step 1
│   ├─ Model: glm-4.6:cloud (Ollama)
│   ├─ 🔧 tool_name() (0.64s) → ~1,510 tokens
│      📊 6,737↓ 1,114↑ ⏱️ 9.87s
├─ ✓ 1: Step 2 (Parallel)
│   ├─ ✓ 1.0: Subtask A (11.00s)
│   ├─ ✓ 1.1: Subtask B (9.25s)
│   └─ ✓ 1.2: Subtask C (7.48s)
└─ ✓ 2: Synthesize
```

### 2. Markdown Debug Report (if `export_markdown=True`)

Exported to `{reports_dir}/{workflow_name}_{timestamp}_{run_id}_debug.md`:

- **Execution Tree**: Visual representation of all steps
- **Workflow Summary**: Total tokens, tool calls, duration, cost
- **Optimization Analysis**: Bottleneck detection, parallel efficiency, cost opportunities
- **Tool Timing Analysis**: Per-tool execution times
- **Context Window Summary**: Token usage tracking
- **LLM Insights**: AI-powered optimization recommendations

### 3. Paired Reports

The debug export automatically pairs with your output file:
```
reports/
├── output_20251017_112533_a1b2c3d4.md         # Your workflow output
└── output_20251017_112533_a1b2c3d4_debug.md   # Paired debug report
```

The `run_id` suffix ensures deterministic pairing between output and debug files.

## Configuration Options

### show_console_tree (boolean)

```python
show_console_tree=True  # Print ASCII tree to console after workflow
```

Shows a compact ASCII tree in the console immediately after workflow execution. Great for quick debugging.

### export_markdown (boolean)

```python
export_markdown=True  # Export detailed markdown debug report
```

Exports a comprehensive markdown report with metrics, optimization analysis, and recommendations.

### reports_dir (string)

```python
reports_dir="./reports"  # Directory to save debug reports
```

Where debug markdown files are saved. Created automatically if it doesn't exist.

### report_pattern (string)

```python
report_pattern="output_*.md"  # Glob pattern for matching output files
```

Used to find your workflow's output file for deterministic pairing with the debug report. The pattern should match the filenames created by your save step.

### verbose (boolean)

```python
verbose=True  # Include detailed metrics in debug output
```

When True, includes:
- Tool execution times per call
- Token usage per step
- Model information
- Context window tracking
- Result previews

When False, shows minimal output (just the tree structure).

### include_analysis (boolean)

```python
include_analysis=True  # Include optimization analysis section
```

When True, includes:
- **Bottleneck Detection**: Steps taking >40% of workflow time
- **Parallel Efficiency**: Load balancing and speedup metrics
- **Cost Opportunities**: Model selection and pricing analysis
- **Cache Opportunities**: Repeated operations that could be cached
- **Tool Timing Analysis**: Slow tool calls (>1.0s threshold)
- **LLM Insights**: AI-powered optimization recommendations (requires model)

When False, skips optimization analysis (faster export).

## Optimization Analysis Details

### Analysis Types

1. **Bottleneck Detection**
   - Identifies steps taking >40% of total workflow time
   - Suggests faster models, task simplification, or caching

2. **Parallel Efficiency**
   - Measures load imbalance across parallel branches
   - Calculates efficiency: `efficiency = total_work / (num_branches * longest_branch_time)`
   - Suggests rebalancing or using faster models for slow branches

3. **Cost Opportunities**
   - Compares model costs across steps
   - Suggests cheaper alternatives (e.g., gpt-4o-mini vs gpt-4o)
   - Shows potential savings

4. **Cache Opportunities**
   - Detects repeated operations (same step run multiple times)
   - Suggests prompt caching or result caching
   - Estimates time/cost savings

5. **Tool Timing Analysis**
   - Identifies tool calls taking >1.0s
   - Shows what % of step time is spent in tools vs LLM processing
   - Suggests tool optimization strategies (caching, parallel execution, faster APIs)

6. **LLM Insights** (optional)
   - Uses an AI model to analyze the workflow holistically
   - Identifies cross-step optimization opportunities
   - Provides domain-specific recommendations
   - Validates suggestions with quality metrics

### Disabling LLM Analysis

By default, LLM analysis uses Kimi K2 1T or GPT-OSS 120B models. To disable:

```bash
export AGNO_WORKFLOW_LLM_ANALYSIS=false
```

This skips the AI-powered insights and uses only rule-based analysis (faster, no API calls).

## Event Storage Requirements

For debugging and optimization to work, you MUST enable event storage:

```python
workflow = Workflow(
    ...
    store_events=True,  # REQUIRED
    db=SqliteDb(db_file="tmp/workflow.db"),  # REQUIRED
)
```

Without `store_events=True`, no events are captured and debugging will be empty.

## Streaming Requirements

For capturing nested agent events (especially in custom executors), use streaming:

```python
result = workflow.print_response(
    input="...",
    stream=True,  # CRITICAL for event capture
    stream_intermediate_steps=True,
)
```

Without `stream=True`, tool calls and nested agent executions may not be captured.

## Tool Timing

Tool timing is automatically extracted from `ToolCallStartedEvent` and `ToolCallCompletedEvent` events. Each event has a `created_at` timestamp (Unix seconds).

The debug export shows:
- Individual tool call durations
- Total tool time per step
- % of step time spent in tools vs LLM processing

Example in execution tree:
```
├─ ✓ 2.0: OpenAI Research
│   ├─ 🔧 duckduckgo_news() (0.64s) → ~1,510 tokens
│   ├─ 🔧 duckduckgo_news() (0.61s) → ~1,394 tokens
│      📊 6,737↓ 1,114↑ ⏱️ 9.87s
```

This shows:
- Two tool calls: 0.64s and 0.61s
- Total step time: 9.87s
- Tool time: 1.25s (13% of step time)
- LLM time: 8.62s (87% of step time)

## Complete Example

```python
#!/usr/bin/env python3
from pathlib import Path
from agno.workflow import Workflow
from agno.db.sqlite import SqliteDb
from cookbook.utils.workflow_config import configure_workflow_debug

# Configuration
SHOW_DEBUG_TREE = True
DEBUG_TREE_VERBOSE = True

# Create workflow
workflow = Workflow(
    name="My Workflow",
    description="Description",
    steps=[...],
    store_events=True,
    debug_mode=False,
    db=SqliteDb(db_file="tmp/workflow.db"),
)

# Configure debug export
configure_workflow_debug(
    workflow,
    show_console_tree=SHOW_DEBUG_TREE,
    export_markdown=SHOW_DEBUG_TREE,
    reports_dir=str(Path(__file__).parent / "reports"),
    report_pattern="output_*.md",
    verbose=DEBUG_TREE_VERBOSE,
    include_analysis=True,
)

# Execute
result = workflow.print_response(
    input="...",
    stream=True,
    stream_intermediate_steps=True,
)

# Debug export happens automatically!
```

## Troubleshooting

**Problem:** Debug tree is empty or shows no events

**Solutions:**
- Ensure `store_events=True` in Workflow
- Ensure `db=SqliteDb(...)` is configured
- Ensure `stream=True` in workflow.print_response()

**Problem:** Tool calls not showing in debug tree

**Solutions:**
- Ensure agents are added as Step(agent=...), not custom executors wrapping agent.run()
- Ensure `stream=True` in workflow.print_response()
- Check that tools are actually being called (not just available)

**Problem:** Optimization analysis is missing

**Solutions:**
- Ensure `include_analysis=True` in configure_workflow_debug()
- Check that events were captured (tree should show steps)
- Check logs for any analysis errors

**Problem:** LLM insights are empty

**Solutions:**
- Ensure AGNO_WORKFLOW_LLM_ANALYSIS env var is not set to "false"
- Ensure Ollama is running and models are available
- Check console output for fallback messages
- Set `export AGNO_WORKFLOW_LLM_ANALYSIS=false` to skip LLM analysis
