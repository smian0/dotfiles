# Agno Workflow Patterns Reference

This document covers idiomatic patterns for building Agno workflows with proper debugging, optimization, and parallel processing.

## Import Structure

```python
from pathlib import Path
from datetime import datetime

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.media import Image
from agno.models.ollama import Ollama  # or OpenAI, Anthropic, etc.
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow import Workflow
from agno.workflow.parallel import Parallel
from agno.workflow.step import Step
from agno.workflow.types import StepOutput, StepInput
```

## Agent Creation Patterns

### Basic Agent with Tools

```python
# Create tools with caching
ddg_tools = DuckDuckGoTools()
for func in ddg_tools.functions.values():
    func.cache_results = True
    func.cache_ttl = 3600  # 1 hour

agent = Agent(
    name="Research Analyst",
    model=Ollama(id="gpt-oss:120b-cloud"),
    tools=[ddg_tools],
    instructions="Clear, specific instructions for the agent...",
    markdown=True,
    debug_mode=False,  # Set to True for verbose output
)
```

### Agent Factory Pattern (for Parallel Steps)

```python
def create_specialized_agent(task_name: str, config: dict) -> Agent:
    """Create an agent for a specific task

    Args:
        task_name: The specific task this agent handles
        config: Configuration dictionary with model, tools, etc.
    """
    # Clone tools with caching
    tools = DuckDuckGoTools()
    for func in tools.functions.values():
        func.cache_results = config.get('enable_cache', True)
        func.cache_ttl = config.get('cache_ttl', 3600)

    return Agent(
        name=f"{task_name} Specialist",
        model=config.get('model', Ollama(id="gpt-oss:120b-cloud")),
        tools=[tools],
        instructions=f"You specialize in {task_name}. {config.get('extra_instructions', '')}",
        markdown=True,
    )
```

## Step Patterns

### Agent Step (Direct Agent Execution)

```python
# Simple step using an agent
step = Step(
    name="Research Step",
    agent=research_agent,
)
```

**Use when:** The agent should process the input and produce output directly.

### Custom Executor Step (Python Function)

```python
def process_data(step_input: StepInput) -> StepOutput:
    """Process data from previous step"""
    # Get previous step content
    content = step_input.previous_step_content or ""

    # Get specific step content by name
    other_content = step_input.get_step_content("Other Step Name")

    # Process data
    result = f"Processed: {content}"

    return StepOutput(
        step_name="process_data",
        content=result,
        success=True,
    )

step = Step(
    name="Process Data",
    executor=process_data,
    description="Process data from previous step",
)
```

**Use when:** You need deterministic Python logic (parsing, file I/O, data transformation).

### Parallel Steps

```python
# Create parallel steps
step1 = Step(name="Task 1", agent=agent1)
step2 = Step(name="Task 2", agent=agent2)
step3 = Step(name="Task 3", agent=agent3)

# Wrap in Parallel
parallel_step = Parallel(
    step1,
    step2,
    step3,
    name="Parallel Tasks"
)
```

**Key Points:**
- All parallel steps receive the SAME input from the previous step
- Use agent instructions to guide each agent to focus on specific aspects
- Access results via `step_input.get_step_content("Parallel Tasks")` which returns a dict

### Accessing Parallel Results

```python
def synthesize_parallel_results(step_input: StepInput) -> StepOutput:
    """Combine results from parallel execution"""
    # Get all parallel step outputs as a dict
    parallel_results = step_input.get_step_content("Parallel Tasks")

    if not parallel_results or not isinstance(parallel_results, dict):
        return StepOutput(
            step_name="synthesize",
            content="Error: Could not retrieve parallel results",
            success=False,
        )

    # Combine results
    combined = ""
    for step_name, content in parallel_results.items():
        combined += f"\n## {step_name}\n{content}\n"

    return StepOutput(
        step_name="synthesize",
        content=combined,
        success=True,
    )
```

## Workflow Configuration

### Complete Workflow Setup

```python
workflow = Workflow(
    name="My Workflow",
    description="Brief description of what this workflow does",
    steps=[
        step1,
        step2,
        parallel_step,
        synthesize_step,
    ],
    store_events=True,  # REQUIRED for debugging and optimization
    debug_mode=False,  # Set to True for verbose console output
    db=SqliteDb(db_file="tmp/workflow.db"),  # REQUIRED when store_events=True
)
```

**Key Configuration:**
- `store_events=True` - Captures all events for debugging (CRITICAL for optimization analysis)
- `db=SqliteDb(...)` - Required when store_events=True
- `debug_mode=False` - Keep False for clean output, True for verbose debugging

### Workflow Execution

```python
result = workflow.print_response(
    input="Your prompt here...",
    images=[Image(content=base64_image_content)],  # Optional
    markdown=True,
    stream=True,  # CRITICAL for capturing nested agent events
    stream_intermediate_steps=True,  # Show progress for each step
)
```

**Key Points:**
- `stream=True` is CRITICAL for capturing nested agent.run() events from custom executors
- `stream_intermediate_steps=True` provides real-time progress updates
- Use `workflow.run()` instead of `print_response()` if you need programmatic access to results

## File Saving Pattern

### Option 1: Dedicated Save Step (Idiomatic)

```python
def save_to_file(step_input: StepInput) -> StepOutput:
    """Save workflow output to a file"""
    try:
        content = step_input.previous_step_content or ""

        # Get run_id for deterministic file naming (pairs with debug export)
        run_id = None
        if step_input.workflow_session and step_input.workflow_session.runs:
            current_run = step_input.workflow_session.runs[-1]
            run_id = current_run.run_id

        # Create output directory
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp and run_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if run_id:
            filename = f"output_{timestamp}_{run_id[:8]}.md"
        else:
            filename = f"output_{timestamp}.md"

        filepath = output_dir / filename
        filepath.write_text(content, encoding="utf-8")

        return StepOutput(
            step_name="save_file",
            content=f"✓ Saved to: {filepath}",
            success=True
        )
    except Exception as e:
        return StepOutput(
            step_name="save_file",
            content=f"✗ Failed: {e}",
            success=False
        )

save_step = Step(
    name="Save Report",
    executor=save_to_file,
    description="Save output to file",
)
```

### Option 2: Manual Save After Workflow

```python
result = workflow.run(input="...")

# Save result manually
output_path = Path("reports/output.md")
output_path.write_text(result.content)
```

## Common Patterns

### Pattern: Parsing Structured Data

```python
def parse_json_output(step_input: StepInput) -> StepOutput:
    """Parse JSON from agent output"""
    import json
    import re

    content = step_input.previous_step_content or ""

    # Extract JSON from markdown code blocks if needed
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = content

    try:
        data = json.loads(json_str)
        return StepOutput(
            step_name="parse_json",
            content=json.dumps(data, indent=2),
            success=True,
        )
    except json.JSONDecodeError as e:
        return StepOutput(
            step_name="parse_json",
            content=f"Failed to parse JSON: {e}",
            success=False,
        )
```

### Pattern: Image Handling

```python
import base64

# Load image and encode as base64
image_path = Path("path/to/image.png")
with open(image_path, "rb") as f:
    image_bytes = f.read()
    image_content = base64.b64encode(image_bytes).decode("utf-8")

# Pass to workflow
result = workflow.print_response(
    input="Analyze this image...",
    images=[Image(content=image_content)],
    stream=True,
)
```

**Note:** Workflows require base64-encoded image content (not filepath or raw bytes) because images need to be serialized between workflow steps.

### Pattern: Configuration Section

```python
# Configuration constants at top of file
NUM_ITEMS = 5
ENABLE_CACHE = True
CACHE_TTL = 3600
SHOW_DEBUG_TREE = True
DEBUG_TREE_VERBOSE = True
AGENT_DEBUG = False
```

This makes the workflow easily configurable without editing code deep in the file.
