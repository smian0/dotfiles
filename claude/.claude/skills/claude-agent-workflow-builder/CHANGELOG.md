# Changelog

## 2025-10-17 - Debug Mode and Tree Visualization

### Added

**Debugging Infrastructure:**
- `WorkflowLogger` class for dual-output logging (console + file)
- `create_debug_hooks()` function for pre/post tool use hooks
- Automatic timestamped log files in `logs/` directory
- Color-coded console output with Rich formatting
- Persistent file logs with detailed input/output data

**Tree Visualization:**
- `WorkflowTreeVisualizer` class for ASCII tree rendering
- `visualize_workflow()` convenience function
- Support for both log files and JSONL transcripts
- Metrics summary showing tool usage statistics
- Timeline view for chronological execution
- Verbose mode with detailed input/output

**Helper Utilities:**
- `TranscriptViewer` for JSONL transcript analysis
- CLI interfaces for all debugging tools
- Demo scripts showing best practices

**Documentation:**
- `DEBUGGING.md` - Complete debugging guide
- Updated `README.md` with debug mode examples
- Code examples and usage patterns

### Features

1. **Debug Mode**
   - Enable with `debug=True` in `create_base_options()`
   - Automatically logs all tool calls with timing
   - Captures full input/output data
   - Writes to both console and log file

2. **Tree Visualization**
   - Display workflow execution as ASCII tree
   - Shows tool calls hierarchically
   - Includes timing information
   - Supports verbose mode for detailed view
   - Metrics table with tool usage counts

3. **Log File Format**
   - Timestamped entries: `[HH:MM:SS.mmm] [LEVEL] message`
   - Color-coded levels: INFO, DEBUG, WARNING, ERROR, TOOL
   - JSON input/output formatting
   - Header with workflow metadata

### Files Added

```
helpers/
├── workflow_helpers.py (updated)
│   ├── WorkflowLogger class
│   ├── create_debug_hooks()
│   └── Updated create_base_options()
├── workflow_tree_visualizer.py (new)
│   ├── WorkflowTreeVisualizer class
│   ├── visualize_workflow()
│   └── CLI interface
└── trace_viewer.py (new)
    ├── TranscriptViewer class
    └── JSONL analysis tools

test_workflow.py (updated)
├── Debug mode enabled
└── Verbose output

demo_tree_visualizer.py (new)
└── Complete demo showing debug + visualization

DEBUGGING.md (new)
└── Complete debugging documentation

CHANGELOG.md (new)
└── This file
```

### Usage Example

```python
from workflow_helpers import create_base_options, run_agent_task
from workflow_tree_visualizer import visualize_workflow

# Enable debug mode
options = await create_base_options(
    debug=True,
    verbose=True,
    workflow_name="my_workflow"
)

# Run workflow
async with ClaudeSDKClient(options=options) as client:
    result = await run_agent_task(client, "Research topic...")

# Visualize execution
visualize_workflow(
    log_file="logs/20251017_123456_my_workflow.log",
    verbose=True,
    show_metrics=True,
    show_timeline=True
)
```

### CLI Commands

```bash
# View workflow tree
python -m helpers.workflow_tree_visualizer --log logs/my_workflow.log --verbose

# Run demo
python demo_tree_visualizer.py

# View transcript
python helpers/trace_viewer.py transcript.jsonl
```

### Inspiration

Tree visualization patterns inspired by Agno's workflow debugger:
- ASCII tree structure with Rich library
- Hierarchical display of tool calls
- Metrics and timing analysis
- Verbose mode for detailed inspection

### Technical Details

**Hook Format:**
```python
{
    'PreToolUse': [HookMatcher(hooks=[pre_tool_hook])],
    'PostToolUse': [HookMatcher(hooks=[post_tool_hook])]
}
```

**Log File Naming:**
```
logs/YYYYMMDD_HHMMSS_{workflow_name}.log
```

**Hook Function Signature:**
```python
async def hook(input_data: dict, tool_use_id: str, context: dict) -> dict:
    # Process tool call
    return {}  # Optional modifications
```

### Known Limitations

1. Tool names show as "unknown" - SDK doesn't expose tool name in hook context
2. Very large outputs are truncated in logs (500 chars)
3. JSON parsing requires exact formatting in log files
4. JSONL transcript support is basic (no nested events)

### Future Enhancements

- [ ] Enhanced JSONL parsing for nested workflow events
- [ ] Cost tracking and token usage analysis
- [ ] Export to HTML/Markdown formats
- [ ] Integration with workflow optimizer suggestions
- [ ] Real-time streaming visualization
- [ ] Support for parallel execution visualization
- [ ] Context window tracking
- [ ] Critical path analysis

---

**Compatibility:** Claude Agent SDK 0.1.0+
