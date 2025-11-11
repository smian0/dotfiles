#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "fastapi>=0.118.0",
#   "ollama",
#   "sqlalchemy",
#   "ddgs>=8.1.1",
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///
# NOTE: This format is portable and works from any agno_workflows/* directory
# uv resolves the relative path ../../libs/agno from the script location

"""
Agno Workflow Template

This template demonstrates idiomatic Agno workflow patterns including:
- Agent creation with tools and caching
- Custom executor steps
- Parallel processing
- File saving
- Debug configuration
- Optimization analysis

Usage:
    uv run workflow_template.py
"""

from pathlib import Path
from datetime import datetime

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow import Workflow
from agno.workflow.parallel import Parallel
from agno.workflow.step import Step
from agno.workflow.types import StepOutput, StepInput
from agno.utils.workflow_config import configure_workflow_debug

# ============================================================================
# Configuration
# ============================================================================

ENABLE_CACHE = True
CACHE_TTL = 3600  # 1 hour

# Debug configuration (enabled by default for all workflows)
SHOW_DEBUG_TREE = True      # Display ASCII tree in console after execution
EXPORT_DEBUG_MARKDOWN = True  # Export detailed debug report to markdown
DEBUG_TREE_VERBOSE = True   # Include detailed metrics and timing

# ============================================================================
# Tools Setup
# ============================================================================

# Create tools with caching
ddg_tools = DuckDuckGoTools()
for func in ddg_tools.functions.values():
    func.cache_results = ENABLE_CACHE
    func.cache_ttl = CACHE_TTL

# ============================================================================
# Agents
# ============================================================================

# Main agent with tools
main_agent = Agent(
    name="Main Agent",
    model=Ollama(id="glm-4.6:cloud"),
    tools=[ddg_tools],
    instructions="""You are a professional assistant.

    Use the available tools to search for information when needed.
    Provide well-structured, comprehensive responses.""",
    markdown=True,
)

# Specialized agent factory (for parallel steps)
def create_specialized_agent(task_name: str) -> Agent:
    """Create an agent for a specific parallel task"""
    # Clone tools with caching
    task_tools = DuckDuckGoTools()
    for func in task_tools.functions.values():
        func.cache_results = ENABLE_CACHE
        func.cache_ttl = CACHE_TTL

    return Agent(
        name=f"{task_name} Specialist",
        model=Ollama(id="glm-4.6:cloud"),
        tools=[task_tools],
        instructions=f"""You specialize in {task_name}.

        Focus only on {task_name} in your research and analysis.""",
        markdown=True,
    )

# ============================================================================
# Steps
# ============================================================================

# Step 1: Agent step
step1 = Step(
    name="Initial Analysis",
    agent=main_agent,
)

# Step 2: Custom executor for data processing
def parse_data(step_input: StepInput) -> StepOutput:
    """Parse and process data from previous step"""
    import json
    import re

    content = step_input.previous_step_content or ""

    # Example: Extract structured data
    # TODO: Implement your parsing logic here
    parsed = {
        "summary": content[:200],
        "length": len(content),
    }

    return StepOutput(
        step_name="parse_data",
        content=json.dumps(parsed, indent=2),
        success=True,
    )

step2 = Step(
    name="Parse Data",
    executor=parse_data,
    description="Extract structured data from analysis",
)

# Step 3: Parallel processing
# Create specialized agents for each parallel task
agent_a = create_specialized_agent("Task A")
agent_b = create_specialized_agent("Task B")
agent_c = create_specialized_agent("Task C")

# Create parallel steps
parallel_step_a = Step(name="Task A", agent=agent_a)
parallel_step_b = Step(name="Task B", agent=agent_b)
parallel_step_c = Step(name="Task C", agent=agent_c)

# Wrap in Parallel
parallel_step = Parallel(
    parallel_step_a,
    parallel_step_b,
    parallel_step_c,
    name="Parallel Processing"
)

# Step 4: Synthesize parallel results
def synthesize_results(step_input: StepInput) -> StepOutput:
    """Combine results from parallel steps"""
    # Get all parallel step outputs
    parallel_results = step_input.get_step_content("Parallel Processing")

    if not parallel_results or not isinstance(parallel_results, dict):
        return StepOutput(
            step_name="synthesize",
            content="Error: Could not retrieve parallel results",
            success=False,
        )

    # Combine results
    report = "# Combined Results\n\n"
    for step_name, content in parallel_results.items():
        report += f"## {step_name}\n\n{content}\n\n---\n\n"

    return StepOutput(
        step_name="synthesize",
        content=report,
        success=True,
    )

step4 = Step(
    name="Synthesize Results",
    executor=synthesize_results,
    description="Combine parallel processing results",
)

# Step 5: Save to file
def save_report(step_input: StepInput) -> StepOutput:
    """Save the final report to a markdown file"""
    try:
        content = step_input.previous_step_content or ""

        # Get run_id for deterministic pairing with debug export
        run_id = None
        if step_input.workflow_session and step_input.workflow_session.runs:
            current_run = step_input.workflow_session.runs[-1]
            run_id = current_run.run_id

        # Create reports directory
        reports_dir = Path(__file__).parent.joinpath("reports")
        reports_dir.mkdir(exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if run_id:
            filename = f"report_{timestamp}_{run_id[:8]}.md"
        else:
            filename = f"report_{timestamp}.md"

        filepath = reports_dir / filename
        filepath.write_text(content, encoding="utf-8")

        return StepOutput(
            step_name="save_report",
            content=f"✓ Report saved to: {filepath}",
            success=True
        )
    except Exception as e:
        return StepOutput(
            step_name="save_report",
            content=f"✗ Failed to save: {e}",
            success=False
        )

step5 = Step(
    name="Save Report",
    executor=save_report,
    description="Save final report to file",
)

# ============================================================================
# Workflow
# ============================================================================

workflow = Workflow(
    name="My Workflow",
    description="Template workflow with all idiomatic patterns",
    steps=[
        step1,           # Initial analysis
        step2,           # Parse data
        parallel_step,   # Parallel processing
        step4,           # Synthesize results
        step5,           # Save report
    ],
    store_events=True,  # REQUIRED for debugging
    debug_mode=False,   # Clean console output
    db=SqliteDb(db_file="tmp/workflow.db"),  # REQUIRED
)

# Configure automatic debug export (enabled by default)
# This wraps print_response to automatically show debug tree and export markdown
configure_workflow_debug(
    workflow,
    show_console_tree=SHOW_DEBUG_TREE,       # ASCII tree in console
    export_markdown=EXPORT_DEBUG_MARKDOWN,   # Markdown debug report
    reports_dir=str(Path(__file__).parent / "reports"),
    report_pattern="report_*.md",            # Match report files for pairing
    verbose=DEBUG_TREE_VERBOSE,              # Detailed metrics
    include_analysis=True,                    # Optimization analysis
)

# ============================================================================
# Execution
# ============================================================================

if __name__ == "__main__":
    result = workflow.print_response(
        input="Your workflow input prompt here...",
        # images=[Image(content=base64_image_content)],  # Optional
        markdown=True,
        stream=True,  # CRITICAL for event capture
        stream_intermediate_steps=True,
    )

    # Debug export happens automatically!
