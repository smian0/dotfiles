# Agent Execution Artifact Visualization

Generate visual diagrams from orchestration artifacts to understand agent execution flow, timing, and performance characteristics.

## Overview

The `ArtifactVisualizer` utility creates ASCII tree diagrams showing:
- Agent execution hierarchy
- Model configurations and parameters
- Input/output sizes
- Execution timings
- Success/failure status
- Token usage (when available)

## Quick Start

### Programmatic Usage

```python
from orchestration import ArtifactVisualizer
from pathlib import Path

# Load artifacts
visualizer = ArtifactVisualizer(Path("outputs/run/artifacts.json"))

# Generate tree diagram
tree = visualizer.generate_tree(detail_level="normal")
print(tree)

# Generate compact summary
summary = visualizer.generate_compact_summary()
print(summary)

# Generate timeline
timeline = visualizer.generate_timeline()
print(timeline)
```

### Command-Line Usage

```bash
# Tree visualization (default)
python -m orchestration.utils.artifact_visualizer outputs/run/artifacts.json tree

# Compact summary
python -m orchestration.utils.artifact_visualizer outputs/run/artifacts.json compact

# Timeline
python -m orchestration.utils.artifact_visualizer outputs/run/artifacts.json timeline
```

### Using the Example Script

```bash
# Run the comprehensive example
python examples/04_visualize_artifacts.py

# This generates multiple visualizations and saves them to output directories
```

## Visualization Modes

### 1. Tree Visualization

Hierarchical view of agent execution with detailed information.

**Detail Levels:**
- `minimal`: Just agent names and durations
- `normal`: Includes model, timing, and I/O sizes
- `verbose`: Adds timestamps and full details

**Example Output:**

```
================================================================================
🎭 Orchestration Execution Diagram
================================================================================

Orchestrator: PolymarketResearch (deep_research workflow)
Total Duration: 109.34s
Total Agents: 1

Execution Tree:

┌─ PolymarketResearch
│
└── DeepWebResearcherAgent (DeepWebResearcherAgent) ✅
    ├─ Model: claude-sonnet-4 (temp=0.4, max_tokens=8000)
    ├─ Duration: 109.34s
    ├─ Input: 500 chars
    └─ Output: 19,526 chars


================================================================================
```

**For Multi-Agent Systems:**

```
┌─ ResearchOrchestrator
│
├── PlanningAgent (PlanningAgent) ✅
│   ├─ Model: claude-sonnet-4 (temp=0.3, max_tokens=2000)
│   ├─ Duration: 5.23s
│   ├─ Input: 250 chars
│   └─ Output: 1,420 chars
│
├── DataGatheringAgent (DataGatheringAgent) ✅
│   ├─ Model: gpt-oss:120b-cloud (temp=0.5, max_tokens=4000)
│   ├─ Duration: 12.45s
│   ├─ Input: 1,420 chars
│   └─ Output: 8,340 chars
│
└── AnalysisAgent (AnalysisAgent) ✅
    ├─ Model: claude-sonnet-4 (temp=0.4, max_tokens=6000)
    ├─ Duration: 8.72s
    ├─ Input: 8,340 chars
    └─ Output: 15,230 chars
```

### 2. Compact Summary

One-line summary per agent for quick overview.

**Example Output:**

```
🎭 PolymarketResearch (109.34s total)

1. DeepWebResearcherAgent [claude-sonnet-4] 109.34s (500→19,526 chars) ✅
```

**Use Cases:**
- Quick status checks
- Comparing multiple runs
- Progress monitoring
- CI/CD pipeline outputs

### 3. Execution Timeline

Visual timeline showing when each agent ran and for how long.

**Example Output:**

```
================================================================================
⏱️  Execution Timeline: PolymarketResearch
================================================================================

Start: 2025-10-13 15:35:20

DeepWebResearcherAgent ✅
  [0.0s → 109.3s] (109.34s)
  ███████████████████████████████████████████████████████████

Total: 109.34s
================================================================================
```

**Use Cases:**
- Performance analysis
- Identifying bottlenecks
- Parallel execution visualization
- Resource utilization planning

## API Reference

### ArtifactVisualizer Class

#### Constructor

```python
ArtifactVisualizer(artifacts_path: Optional[Path] = None)
```

**Parameters:**
- `artifacts_path`: Path to artifacts.json file (optional, can load later)

#### Methods

##### `generate_tree()`

```python
generate_tree(
    artifacts: Optional[Dict[str, Any]] = None,
    detail_level: str = "normal",
    show_timestamps: bool = False,
    show_token_usage: bool = False
) -> str
```

**Parameters:**
- `artifacts`: Artifacts data (uses loaded data if None)
- `detail_level`: "minimal", "normal", or "verbose"
- `show_timestamps`: Include execution timestamps
- `show_token_usage`: Include token usage info (if available)

**Returns:** ASCII tree diagram as string

##### `generate_compact_summary()`

```python
generate_compact_summary(
    artifacts: Optional[Dict[str, Any]] = None
) -> str
```

**Returns:** Compact one-line summary per agent

##### `generate_timeline()`

```python
generate_timeline(
    artifacts: Optional[Dict[str, Any]] = None
) -> str
```

**Returns:** Timeline diagram showing execution flow

##### `save_visualization()`

```python
save_visualization(
    output_path: Path,
    mode: str = "tree",
    **kwargs
)
```

**Parameters:**
- `output_path`: Path to save visualization
- `mode`: "tree", "compact", or "timeline"
- `**kwargs`: Additional arguments for visualization method

### Convenience Function

```python
visualize_artifacts(
    artifacts_path: Path,
    mode: str = "tree",
    output_path: Optional[Path] = None,
    **kwargs
) -> str
```

**Parameters:**
- `artifacts_path`: Path to artifacts.json
- `mode`: "tree", "compact", or "timeline"
- `output_path`: Optional path to save output
- `**kwargs`: Additional visualization options

**Returns:** Visualization string

## Integration with Output Manager

The `ResearchOutputManager` automatically saves artifacts.json with each research run. These can be visualized immediately:

```python
from orchestration import ResearchOutputManager, ArtifactVisualizer
from pathlib import Path

# After a research run
output_manager = ResearchOutputManager()
run_dir = output_manager.save_full_run(
    run_name="my_research",
    query=query,
    report_content=report,
    artifacts_data=artifacts_dict
)

# Visualize artifacts
visualizer = ArtifactVisualizer(run_dir / "artifacts.json")
tree = visualizer.generate_tree(detail_level="verbose")
print(tree)

# Save visualization alongside other outputs
visualizer.save_visualization(
    run_dir / "execution_diagram.txt",
    mode="tree",
    detail_level="normal"
)
```

## Use Cases

### 1. Debugging Performance Issues

```python
# Generate timeline to identify bottlenecks
timeline = visualizer.generate_timeline()

# Look for agents with unexpectedly long durations
# Check if agents are running sequentially when they could be parallel
```

### 2. Comparing Research Runs

```bash
# Compare two runs side by side
python -m orchestration.utils.artifact_visualizer outputs/run1/artifacts.json compact
python -m orchestration.utils.artifact_visualizer outputs/run2/artifacts.json compact
```

### 3. Documentation and Presentations

```python
# Generate minimal tree for clean presentation slides
tree = visualizer.generate_tree(detail_level="minimal")

# Save to file
with open("presentation_diagram.txt", "w") as f:
    f.write(tree)
```

### 4. Audit and Compliance

```python
# Generate verbose tree with all details
tree = visualizer.generate_tree(
    detail_level="verbose",
    show_timestamps=True,
    show_token_usage=True
)

# Save to audit trail
with open("audit_trail.txt", "w") as f:
    f.write(tree)
```

### 5. CI/CD Integration

```bash
#!/bin/bash
# In your CI pipeline

# Run research
python examples/03_polymarket_research.py

# Generate compact summary for logs
python -m orchestration.utils.artifact_visualizer \
    outputs/latest/artifacts.json \
    compact
```

## Advanced Features

### Custom Formatting

The visualizer uses Unicode box-drawing characters for clean output:
- `├──` for branches
- `└──` for last items
- `│` for vertical lines
- `─` for horizontal lines

### Status Icons

- ✅ Success
- ❌ Failure

### Performance Metrics

For each agent, the visualizer shows:
- **Duration**: Total execution time
- **Input size**: Characters in the input prompt
- **Output size**: Characters in the agent's response
- **Model**: AI model used (e.g., claude-sonnet-4)
- **Temperature**: Model temperature setting
- **Max tokens**: Token limit

## Troubleshooting

### Empty or Missing Artifacts

**Problem:** `No artifacts data available`

**Solution:** Ensure the orchestrator is configured to capture artifacts:

```python
# Orchestrator automatically captures artifacts
result = orchestrator.run(query)

# Check if artifacts are present
if result.artifacts:
    print("Artifacts available")
else:
    print("No artifacts captured")
```

### Incorrect Timestamps

**Problem:** Timestamps show wrong timezone

**Solution:** Timestamps are stored in ISO format with timezone info. The visualizer formats them to local time.

### Visualization Too Wide

**Problem:** Timeline bars exceed terminal width

**Solution:** The timeline automatically scales to 60 characters. For longer runs, the bars compress proportionally.

## Examples

See `examples/04_visualize_artifacts.py` for comprehensive examples of all visualization modes.

## Future Enhancements

Potential future features:
- Graphviz/DOT format export
- Mermaid diagram generation
- Interactive HTML visualization
- Cost analysis (token usage × model pricing)
- Parallel execution visualization
- Agent dependency graphs

## Related Documentation

- [Output Management](./OUTPUT_MANAGEMENT.md)
- [Orchestration Patterns](./ORCHESTRATION_PATTERNS.md)
- [Research Workflows](./RESEARCH_WORKFLOWS.md)

---

Last Updated: 2025-10-13
