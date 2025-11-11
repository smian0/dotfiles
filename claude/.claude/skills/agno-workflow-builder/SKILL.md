---
name: agno-workflow-builder
description: Build Agno AI agents and workflows. Use for simple CLI agents (single-agent chat/Q&A) OR complex workflows (multi-step, parallel processing, orchestration). Covers minimal CLI agents (~10 lines) to production workflows with debugging and optimization. Examples: "create a CLI chatbot", "build a research workflow", "add parallel processing".
---

# Agno Agent & Workflow Builder

## Overview

Build Agno AI solutions from simple CLI agents to production-ready workflows. This skill provides idiomatic patterns for:
- **Simple CLI Agents**: Interactive chat, single-purpose assistants (~10 lines)
- **Complex Workflows**: Multi-step orchestration, parallel processing, debugging, optimization

Choose the approach that fits your task complexity.

## CRITICAL: Consult Agno Documentation

**BEFORE implementing any workflow patterns, ALWAYS consult:**

1. **Context7 MCP** - Get up-to-date Agno documentation and examples:
   ```
   Use mcp__context7__resolve-library-id to find agno library
   Use mcp__context7__get-library-docs to get latest workflow patterns, API references, and examples
   ```

2. **Agno Project Source** - Reference the actual agno codebase:
   ```
   Location: /Users/smian/github-smian0/agno-ck/libs/agno/
   Read workflow implementation examples from cookbook/
   Check agno.workflow, agno.agent, agno.models for current APIs
   ```

**Why this matters:**
- Agno has extensive code and documentation that may have patterns not in this skill
- Workflow pipeline patterns, agent configurations, and tool integrations evolve
- Consulting the source ensures idiomatic, up-to-date implementations
- Prevents using deprecated patterns or missing new features

**When to consult:**
- Before creating any new workflow (check latest patterns)
- When implementing parallel processing (verify current Parallel API)
- When using specific model providers (check current model integration)
- When debugging workflow issues (reference actual implementation)
- When uncertain about any pattern (verify against source)

## Decision Guide: CLI Agent vs Workflow

### Use Simple CLI Agent When:
- ✅ Single agent with no multi-step orchestration
- ✅ Interactive chat or single prompt/response pattern
- ✅ No parallel processing needed
- ✅ No custom data transformations between steps
- ✅ **Examples**: "CLI chatbot", "Q&A agent", "simple assistant", "single-task agent"
- ✅ **Result**: ~10-20 lines of code

### Use Complex Workflow When:
- ✅ Multi-step sequential processing (step1 → step2 → step3)
- ✅ Parallel agent execution (research 3 topics simultaneously)
- ✅ Custom data transformations (JSON parsing, file I/O, synthesis)
- ✅ Performance optimization and debugging needed
- ✅ **Examples**: "analyze images then research", "parallel research workflow", "vision → parse → research → synthesize"
- ✅ **Result**: 50-200 lines with full debugging and optimization

**When in doubt:** Start with CLI agent. Upgrade to workflow when complexity grows.

## Quick Start

### Simple CLI Agent (10 Lines)

For single-agent interactive chat or simple tasks:

```bash
# Create single-file CLI agent
cd <project_root>
mkdir -p agno_agents
uv init --script agno_agents/my_agent.py --python 3.12

# Add minimal dependencies
uv add --script agno_agents/my_agent.py ../../libs/agno --editable
uv add --script agno_agents/my_agent.py ollama
```

**Minimal agent code** (`agno_agents/my_agent.py`):

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["agno", "ollama"]
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///

from agno.agent import Agent
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(
        id="glm-4.6:cloud",
        options={"num_ctx": 198000}  # 198K context window - full capacity
    ),
    instructions="You are a helpful AI assistant.",
    markdown=True,
    # Automatic retry with exponential backoff (recommended)
    exponential_backoff=True,
    retries=3,
    delay_between_retries=15,  # With exponential backoff: 15s, 30s, 60s
)

if __name__ == "__main__":
    # Interactive CLI
    agent.cli_app(stream=True)

    # OR single prompt
    # agent.print_response("Your prompt here", stream=True)
```

**Run it:**

```bash
chmod +x agno_agents/my_agent.py
./agno_agents/my_agent.py
```

**That's it!** See `assets/simple_cli_agent.py` for the complete template.

For complex multi-step workflows, continue to the section below.

### Creating a New Workflow

Create workflows as single-file `uv` scripts with inline dependencies:

```bash
# Navigate to project root
cd <project_root>

# Create workflow directory
mkdir -p agno_workflows/my_workflow

# Initialize the workflow script with uv
uv init --script agno_workflows/my_workflow/workflow.py --python 3.12

# Add agno dependencies (from local forked source + required runtime dependencies)
# uv automatically uses the correct portable format with tool.uv.sources
uv add --script agno_workflows/my_workflow/workflow.py ../../libs/agno --editable
uv add --script agno_workflows/my_workflow/workflow.py fastapi ollama sqlalchemy
```

This creates a workflow script with inline metadata:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "fastapi>=0.118.0",
#   "ollama",
#   "sqlalchemy",
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///

from pathlib import Path
from agno.agent import Agent
from agno.workflow import Workflow, Step
from agno.models.ollama import Ollama
from agno.db.sqlite import SqliteDb
from agno.utils.workflow_config import configure_workflow_debug

# Create agent
agent = Agent(
    name="Assistant",
    model=Ollama(
        id="glm-4.6:cloud",
        options={"num_ctx": 198000}
    ),
    instructions="Your agent instructions here...",
    exponential_backoff=True,
    retries=3,
    delay_between_retries=15,
)

# Create workflow
workflow = Workflow(
    name="My Workflow",
    steps=[Step(name="Process", agent=agent)],
    store_events=True,
    db=SqliteDb(db_file="tmp/workflow.db"),
)

# Configure debug (enabled by default for all workflows)
configure_workflow_debug(
    workflow,
    show_console_tree=True,
    export_markdown=True,
    reports_dir=str(Path(__file__).parent / "reports"),
    verbose=True,
    include_analysis=True,
)

# Execute
if __name__ == "__main__":
    result = workflow.print_response(
        input="Your prompt...",
        stream=True,
        stream_intermediate_steps=True,
    )
    # Debug tree and report generated automatically!
```

### Running the Workflow

```bash
# Run with uv (automatically manages dependencies)
uv run agno_workflows/my_workflow/workflow.py

# Or make executable and run directly
chmod +x agno_workflows/my_workflow/workflow.py
./agno_workflows/my_workflow/workflow.py
```

For complete examples, see `assets/simple_workflow.py` (minimal) or `assets/workflow_template.py` (comprehensive).

## Building Workflows

### 1. Choosing Workflow Structure

Determine the appropriate structure based on the task:

**Single Agent Sequential**
- One agent processes input step-by-step
- Use when tasks are simple or inherently sequential
- Example: analyze → summarize → save

**Multi-Agent Sequential**
- Different specialized agents for each step
- Use when each step requires different expertise/models
- Example: vision analysis → text extraction → research → synthesis

**Parallel Processing**
- Multiple agents execute simultaneously
- Use when tasks are independent and can run concurrently
- Example: research 3 companies in parallel, then synthesize
- **Key benefit**: 3x speedup for 3 parallel branches

**Hybrid (Recommended Pattern)**
- Combine sequential and parallel steps
- Example: vision → parse → parallel research → synthesize → save
- See reference workflow: `qwen_vision_workflow.py`

### 2. Creating Agents

#### Basic Agent

```python
from agno.agent import Agent
from agno.models.ollama import Ollama

agent = Agent(
    name="Agent Name",
    model=Ollama(id="glm-4.6:cloud"),
    instructions="Clear, specific instructions...",
    markdown=True,
    # Automatic retry with exponential backoff (recommended for production)
    exponential_backoff=True,
    retries=3,
    delay_between_retries=15,
)
```

**Retry configuration (recommended):**
- `exponential_backoff=True` - Enables automatic retries with exponential backoff
- `retries=3` - Number of retry attempts (3 retries = up to 4 total attempts)
- `delay_between_retries=15` - Initial delay in seconds (with exponential backoff: 15s, 30s, 60s)

This handles transient model provider errors automatically, with the third retry occurring at ~1 minute.

#### Context Window Configuration (CRITICAL)

**⚠️ WARNING:** Ollama defaults to only **2048 tokens (2K)** for `num_ctx`, which is extremely low.

For `glm-4.6:cloud` with 198K capacity, you must explicitly set `num_ctx` or risk **silent context truncation**:

```python
agent = Agent(
    name="Agent Name",
    model=Ollama(
        id="glm-4.6:cloud",
        options={
            "num_ctx": 198000,  # 198K - USE THIS BY DEFAULT
            "temperature": 0.6,
        }
    ),
    instructions="Clear, specific instructions...",
    markdown=True,
    exponential_backoff=True,
    retries=3,
    delay_between_retries=15,
)
```

**Context window recommendations for glm-4.6:cloud:**
- **Recommended**: 198000 (198K tokens) - **USE THIS BY DEFAULT** for full capacity
- **Minimum**: 65536 (64K tokens) - only for simple, short operations if needed

**Why this matters:**
- Ollama **silently discards leading context** when limit exceeded
- You won't know your conversation history is being truncated
- Default 2K is only 1% of glm-4.6's actual capacity
- Essential for agents with long conversations or large prompts

**Always set `num_ctx`** in the `options` dict for production agents.

#### Agent with Tools and Caching

```python
from agno.tools.duckduckgo import DuckDuckGoTools

# Create and configure tools
tools = DuckDuckGoTools()
for func in tools.functions.values():
    func.cache_results = True
    func.cache_ttl = 3600  # 1 hour

agent = Agent(
    name="Research Agent",
    model=Ollama(
        id="glm-4.6:cloud",
        options={"num_ctx": 198000}
    ),
    tools=[tools],
    instructions="Use duckduckgo_news to search for recent information...",
    markdown=True,
    exponential_backoff=True,
    retries=3,
    delay_between_retries=15,
)
```

**When to use caching:**
- API rate limits (e.g., DuckDuckGo)
- Repeated searches across parallel branches
- Development/testing (instant re-runs)

#### Agent Factory (for Parallel Steps)

```python
def create_specialized_agent(task_name: str) -> Agent:
    """Create an agent for a specific parallel task"""
    tools = DuckDuckGoTools()
    for func in tools.functions.values():
        func.cache_results = True
        func.cache_ttl = 3600

    return Agent(
        name=f"{task_name} Specialist",
        model=Ollama(
            id="glm-4.6:cloud",
            options={"num_ctx": 198000}
        ),
        tools=[tools],
        instructions=f"Focus exclusively on {task_name}...",
        markdown=True,
        exponential_backoff=True,
        retries=3,
        delay_between_retries=15,
    )
```

Use this pattern when creating multiple similar agents with different specializations.

### 2.5. Human-in-the-Loop (User Confirmation)

Add user confirmation for sensitive operations using Agno's built-in `requires_confirmation` pattern.

#### Tool with Confirmation Required

```python
from agno.tools import tool
from rich.console import Console
from rich.prompt import Prompt

console = Console()

@tool(requires_confirmation=True)
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email (requires user confirmation)"""
    # Email sending logic here
    return f"Email sent to {recipient}"

agent = Agent(
    model=Ollama(
        id="glm-4.6:cloud",
        options={"num_ctx": 198000}
    ),
    tools=[send_email],
    instructions="Help the user with email tasks, but always ask for confirmation.",
    markdown=True,
    exponential_backoff=True,
    retries=3,
    delay_between_retries=15,
)
```

#### Handling Confirmation Flow

```python
# Run the agent
run_response = agent.run("Send an email to john@example.com about the meeting")

# Check if paused for confirmation
if run_response.is_paused:
    for tool in run_response.tools_requiring_confirmation:
        # Show tool details to user
        console.print(
            f"Tool [bold blue]{tool.tool_name}({tool.tool_args})[/] requires confirmation."
        )

        # Prompt for confirmation
        message = Prompt.ask(
            "Do you want to continue?",
            choices=["y", "n"],
            default="y"
        ).strip().lower()

        if message == "n":
            tool.confirmed = False
            tool.confirmation_note = "User declined this operation"
        else:
            tool.confirmed = True

    # Continue execution
    run_response = agent.continue_run(run_response=run_response)

# Print final response
from agno.utils import pprint
pprint.pprint_run_response(run_response)
```

#### Multiple Tools with Confirmation

```python
from agno.tools.wikipedia import WikipediaTools

agent = Agent(
    model=Ollama(
        id="glm-4.6:cloud",
        options={"num_ctx": 198000}
    ),
    tools=[
        send_email,  # Custom tool with @tool(requires_confirmation=True)
        WikipediaTools(requires_confirmation_tools=["search_wikipedia"]),
    ],
    markdown=True,
)

# The confirmation loop handles ALL tools requiring confirmation
run_response = agent.run("Search Wikipedia and email me the results")
while run_response.is_paused:
    for tool in run_response.tools_requiring_confirmation:
        console.print(f"Confirm: {tool.tool_name}({tool.tool_args})")
        tool.confirmed = Prompt.ask("Continue?", choices=["y", "n"]) == "y"
    run_response = agent.continue_run(run_response=run_response)
```

**When to use:**
- Sensitive operations (sending emails, making purchases, deleting data)
- External API calls that cost money
- Operations that modify important data
- Any action requiring explicit user approval

**Dependencies:** `pip install rich` (for console prompts)

#### Async Version

```python
import asyncio

# Async agent execution with confirmation
run_response = asyncio.run(agent.arun("Send an email..."))
if run_response.is_paused:
    for tool in run_response.tools_requiring_confirmation:
        console.print(f"Confirm: {tool.tool_name}({tool.tool_args})")
        tool.confirmed = Prompt.ask("Continue?", choices=["y", "n"]) == "y"
    run_response = asyncio.run(agent.acontinue_run(run_response=run_response))
```

Use `agent.arun()` and `agent.acontinue_run()` for async workflows.

### 3. Creating Steps

#### Agent Step (Direct Execution)

```python
from agno.workflow.step import Step

step = Step(
    name="Step Name",
    agent=agent,
)
```

**Use when:** The agent should process input and produce output directly.

**Captures:** All agent events, tool calls, and metrics automatically.

#### Custom Executor Step (Python Function)

```python
from agno.workflow.types import StepInput, StepOutput

def process_data(step_input: StepInput) -> StepOutput:
    """Process data with Python code"""
    # Get previous step content
    content = step_input.previous_step_content or ""

    # Get specific step by name
    other = step_input.get_step_content("Other Step")

    # Process...
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

**Use when:** Need deterministic Python logic (parsing, file I/O, data transformation).

**Important:** Set `stream=True` in workflow execution to capture nested agent events.

#### Parallel Step

```python
from agno.workflow.parallel import Parallel

# Create parallel sub-steps
step1 = Step(name="Task 1", agent=agent1)
step2 = Step(name="Task 2", agent=agent2)
step3 = Step(name="Task 3", agent=agent3)

# Wrap in Parallel
parallel = Parallel(step1, step2, step3, name="Parallel Tasks")
```

**Key Points:**
- All parallel steps receive the SAME input from previous step
- Use agent instructions to guide each to focus on specific aspects
- Significant speedup: N parallel steps ≈ N× faster than sequential

#### Synthesizing Parallel Results

```python
def synthesize_parallel(step_input: StepInput) -> StepOutput:
    """Combine results from parallel execution"""
    # Get all parallel outputs as dict
    results = step_input.get_step_content("Parallel Tasks")

    if not results or not isinstance(results, dict):
        return StepOutput(
            step_name="synthesize",
            content="Error: No parallel results",
            success=False,
        )

    # Combine
    report = ""
    for name, content in results.items():
        report += f"## {name}\n{content}\n\n"

    return StepOutput(
        step_name="synthesize",
        content=report,
        success=True,
    )
```

### 4. Assembling the Workflow

```python
from agno.workflow import Workflow
from agno.db.sqlite import SqliteDb

workflow = Workflow(
    name="Workflow Name",
    description="Brief description",
    steps=[
        step1,
        step2,
        parallel_step,
        synthesize_step,
    ],
    store_events=True,  # REQUIRED for debugging
    debug_mode=False,   # False for clean output
    db=SqliteDb(db_file="tmp/workflow.db"),  # REQUIRED
)
```

**Critical Configuration:**
- `store_events=True` - Captures all events for debugging and optimization
- `db=SqliteDb(...)` - Required when store_events=True
- `debug_mode=False` - Keep False for clean console output

### 5. Configuring Debug Export (ENABLED BY DEFAULT)

Debug tree and optimization analysis are **automatically enabled** for all workflows created with this skill:

```python
from agno.utils.workflow_config import configure_workflow_debug
from pathlib import Path

# Debug configuration (enabled by default in all workflows)
configure_workflow_debug(
    workflow,
    show_console_tree=True,        # ASCII tree in console after execution
    export_markdown=True,           # Detailed debug report in markdown
    reports_dir="./reports",        # Where to save debug reports
    report_pattern="output_*.md",   # Pattern to match output files for pairing
    verbose=True,                   # Include detailed metrics and timing
    include_analysis=True,          # Optimization analysis and recommendations
)
```

**What you automatically get with every workflow:**
- **Console Tree**: Visual ASCII tree showing step execution, timing, and token usage
- **Markdown Report**: Comprehensive debug file (`output_*_debug.md`) paired with your output
- **Optimization Analysis**:
  - Bottleneck detection (steps taking >40% of time)
  - Parallel efficiency analysis (load balancing)
  - Cost opportunities (model selection optimization)
  - Tool timing analysis (slow tool calls >1.0s)
  - Cache recommendations
- **LLM Insights**: AI-powered recommendations using expert models (can be disabled with `AGNO_WORKFLOW_LLM_ANALYSIS=false`)
- **Paired Reports**: Debug file automatically paired with output file using run_id

**To disable debug (not recommended):**
```python
# Only disable if you have specific performance needs
configure_workflow_debug(
    workflow,
    show_console_tree=False,
    export_markdown=False,
)
```

See `references/debug_guide.md` for complete documentation.

### 6. Executing the Workflow

```python
result = workflow.print_response(
    input="Your workflow prompt...",
    # images=[Image(content=base64_content)],  # Optional
    markdown=True,
    stream=True,  # CRITICAL for event capture
    stream_intermediate_steps=True,
)

# Debug export happens automatically!
```

**Important:**
- `stream=True` is CRITICAL for capturing tool calls and nested events
- `stream_intermediate_steps=True` shows real-time progress
- Debug export is automatic (no manual code needed)

### 7. Creating and Running Tests

Always create a test script to validate your workflow:

```bash
# Create test script in the same directory
uv init --script agno_workflows/my_workflow/test_workflow.py --python 3.12

# Add test dependencies (same as workflow + pytest)
uv add --script agno_workflows/my_workflow/test_workflow.py ../../libs/agno --editable
uv add --script agno_workflows/my_workflow/test_workflow.py fastapi ollama sqlalchemy 'pytest>=7.0.0'
```

**Test Script Template:**

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "fastapi>=0.118.0",
#   "ollama",
#   "sqlalchemy",
#   "pytest>=7.0.0",
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///
# NOTE: Uses portable format with tool.uv.sources

"""Test script for My Workflow"""

from pathlib import Path
import sys

# Add workflow directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_workflow_basic():
    """Test basic workflow execution"""
    # Import workflow from the same directory
    from workflow import workflow

    # Execute with test input
    result = workflow.run(
        input="Test prompt for validation",
        stream=False,  # Disable streaming for tests
    )

    # Validate results
    assert result is not None, "Workflow returned None"
    assert result.content, "Workflow returned empty content"
    print(f"✓ Workflow executed successfully")
    print(f"  Output length: {len(result.content)} chars")

    return True

def test_workflow_steps():
    """Test that all steps execute"""
    from workflow import workflow

    # Check workflow configuration
    assert workflow.steps, "Workflow has no steps"
    assert workflow.store_events, "Event storage not enabled"
    assert workflow.db, "Database not configured"

    print(f"✓ Workflow configuration valid")
    print(f"  Steps: {len(workflow.steps)}")
    print(f"  Event storage: enabled")

    return True

if __name__ == "__main__":
    print("Running workflow tests...\n")

    try:
        # Run tests
        test_workflow_steps()
        print()
        test_workflow_basic()

        print("\n✅ All tests passed!")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

**Running Tests:**

```bash
# Run test script with uv
uv run agno_workflows/my_workflow/test_workflow.py

# Or make executable
chmod +x agno_workflows/my_workflow/test_workflow.py
./agno_workflows/my_workflow/test_workflow.py
```

**Expected Output:**

```
Running workflow tests...

✓ Workflow configuration valid
  Steps: 3
  Event storage: enabled

✓ Workflow executed successfully
  Output length: 1234 chars

✅ All tests passed!
```

### Workflow Directory Structure

```
<project_root>/
└── agno_workflows/
    └── my_workflow/
        ├── workflow.py          # Main workflow script
        ├── test_workflow.py     # Test script
        └── reports/             # Output reports (auto-created)
            ├── output_*.md
            └── output_*_debug.md
```

## Common Patterns

### File Saving

Add a save step at the end of your workflow:

```python
from datetime import datetime

def save_report(step_input: StepInput) -> StepOutput:
    """Save output to file"""
    content = step_input.previous_step_content or ""

    # Get run_id for pairing with debug export
    run_id = None
    if step_input.workflow_session and step_input.workflow_session.runs:
        run_id = step_input.workflow_session.runs[-1].run_id

    # Create output directory
    Path("reports").mkdir(exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output_{timestamp}_{run_id[:8]}.md" if run_id else f"output_{timestamp}.md"

    # Save
    Path("reports") / filename).write_text(content)

    return StepOutput(
        step_name="save_report",
        content=f"✓ Saved to: reports/{filename}",
        success=True
    )
```

The run_id ensures the output file pairs with its debug report.

### Image Processing

```python
import base64
from agno.media import Image

# Load and encode image
image_path = Path("image.png")
image_bytes = image_path.read_bytes()
image_content = base64.b64encode(image_bytes).decode("utf-8")

# Pass to workflow
result = workflow.print_response(
    input="Analyze this image...",
    images=[Image(content=image_content)],
    stream=True,
)
```

**Note:** Workflows require base64-encoded content (not filepath).

### JSON Parsing

```python
import json
import re

def parse_json(step_input: StepInput) -> StepOutput:
    """Extract JSON from agent output"""
    content = step_input.previous_step_content or ""

    # Extract from markdown code block
    match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
    json_str = match.group(1) if match else content

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
            content=f"Parse error: {e}",
            success=False,
        )
```

## Optimization Analysis

When `include_analysis=True` in debug configuration, workflows automatically analyze:

1. **Bottleneck Detection** - Steps taking >40% of workflow time
2. **Parallel Efficiency** - Load balancing across parallel branches
3. **Cost Opportunities** - Model selection and pricing optimization
4. **Cache Opportunities** - Repeated operations that could be cached
5. **Tool Timing Analysis** - Slow tool calls (>1.0s threshold)
6. **LLM Insights** - AI-powered recommendations from expert models

Example optimization output:

```
### 🟠 Slow tool call: duckduckgo_news in Research Step
Tool call takes 1.25s (15% of step time)
Impact: Could save 1.25s with caching or parallel execution
Action: Consider caching tool results or running tools in parallel
```

See `references/debug_guide.md` for detailed documentation on all analysis types.

## References

- **workflow_patterns.md** - Complete pattern reference with code examples
- **debug_guide.md** - Debugging, optimization, and performance monitoring guide

## Templates

**CLI Agents:**
- **simple_cli_agent.py** - Minimal CLI agent (~15 lines) for interactive chat or single-task execution

**Workflows:**
- **simple_workflow.py** - Minimal workflow example (single agent) with uv inline dependencies
- **workflow_template.py** - Comprehensive template with all patterns (agents, parallel, custom executors, debugging) with uv inline dependencies
- **test_workflow_template.py** - Complete test suite template for workflow validation

## Workflow Creation Process

When creating a new workflow, follow these steps:

### 1. Create Workflow Directory

```bash
cd <project_root>
mkdir -p agno_workflows/<workflow_name>
```

### 2. Initialize Workflow Script

```bash
# Create workflow.py with uv
uv init --script agno_workflows/<workflow_name>/workflow.py --python 3.12

# Add Agno dependencies using relative paths (portable format)
# uv automatically creates the tool.uv.sources format
uv add --script agno_workflows/<workflow_name>/workflow.py ../../libs/agno --editable
uv add --script agno_workflows/<workflow_name>/workflow.py fastapi ollama sqlalchemy

# Add optional tool dependencies as needed
# Example: uv add --script agno_workflows/<workflow_name>/workflow.py 'ddgs>=8.1.1'
```

### 3. Implement Workflow

Copy from `assets/simple_workflow.py` (minimal) or `assets/workflow_template.py` (comprehensive) and customize:
- Update agent instructions
- Configure steps (sequential, parallel, or hybrid)
- Add tool integrations if needed
- Configure debug settings

### 4. Create Test Script

```bash
# Create test_workflow.py
uv init --script agno_workflows/<workflow_name>/test_workflow.py --python 3.12

# Add test dependencies (same as workflow + pytest)
uv add --script agno_workflows/<workflow_name>/test_workflow.py ../../libs/agno --editable
uv add --script agno_workflows/<workflow_name>/test_workflow.py fastapi ollama sqlalchemy 'pytest>=7.0.0'
```

Copy from `assets/test_workflow_template.py` and customize test cases.

### 5. Run Tests

```bash
# Execute test script
uv run agno_workflows/<workflow_name>/test_workflow.py
```

Verify all tests pass before using the workflow.

### 6. Run Workflow

```bash
# Execute workflow
uv run agno_workflows/<workflow_name>/workflow.py
```

Debug reports are automatically generated in `agno_workflows/<workflow_name>/reports/`.

## Troubleshooting

### Understanding tool.uv.sources Format

**The `tool.uv.sources` format is CORRECT and recommended** (not a bug or workaround).

Since uv v0.4.10 (Sept 2024), the proper format for local package dependencies uses `tool.uv.sources`:

```python
# ✅ CORRECT - Portable format that works across machines
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "fastapi>=0.118.0",
#   "ollama",
#   "sqlalchemy",
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///
```

**Why this format?**
- **Portable**: Relative paths work from any machine without modification
- **Clean separation**: "What packages" (dependencies) vs "Where to get them" (tool.uv.sources)
- **Standard**: Matches pyproject.toml conventions
- **Editable mode**: Changes to local package are immediately reflected

**How it works:**
- The `dependencies` list declares package names (like requirements.txt)
- The `[tool.uv.sources]` table specifies where to find local packages
- Relative paths are resolved from the script file location
- Path `../../libs/agno` works from any `agno_workflows/*/` directory

**Commands that generate this format:**
```bash
# This automatically creates the correct tool.uv.sources format
uv add --script workflow.py ../../libs/agno --editable
```

### Missing Dependencies

If you see import errors:
- `ImportError: sqlalchemy not installed`
- `ModuleNotFoundError: No module named 'fastapi'`
- `ModuleNotFoundError: No module named 'ollama'`

**Solution:** Ensure all required dependencies are listed:
```python
# dependencies = [
#   "agno",              # Main package
#   "fastapi>=0.118.0",  # Required for workflow types
#   "ollama",            # Required for Ollama model
#   "sqlalchemy",        # Required for SQLite database
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
```

**Add dependencies with:**
```bash
uv add --script workflow.py fastapi ollama sqlalchemy
```

**Optional dependencies:**
- `"ddgs>=8.1.1"` - For DuckDuckGo search tools
- `"pytest>=7.0.0"` - For test scripts only

### Path Resolution Issues

If you see errors like "package not found" when running from different directories:

**Problem:** The relative path `../../libs/agno` is resolved from the script file location, not the current working directory.

**Solution:** Always structure workflows under `agno_workflows/*/`:
```
<project_root>/
├── libs/
│   └── agno/          # Local package here
└── agno_workflows/
    └── my_workflow/
        └── workflow.py  # From here, ../../libs/agno works
```

**Verify path from script location:**
```bash
cd agno_workflows/my_workflow
ls ../../libs/agno  # Should show the agno package
```

## When to Use This Skill

Use this skill when:

**For Simple CLI Agents:**
- Creating interactive chatbots or Q&A agents
- Single-agent tasks with no orchestration
- Quick prototypes or simple assistants

**For Complex Workflows:**
- Creating multi-step workflows from scratch
- Adding parallel processing to existing workflows
- Implementing debugging and optimization analysis
- Setting up tool caching for rate-limited APIs
- Building complex multi-agent orchestration
- Optimizing workflow performance

The skill provides idiomatic patterns for both minimal CLI agents (~10 lines) and production workflows with `uv`-based dependency management, automatic testing, and comprehensive debugging.
