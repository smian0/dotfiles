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
# NOTE: This format is portable and works from any agno_workflows/* directory
# uv resolves the relative path ../../libs/agno from the script location

"""
Simple Agno Workflow Example

Demonstrates the minimal idiomatic pattern for an Agno workflow with debugging.

Usage:
    uv run simple_workflow.py
"""

from pathlib import Path
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama
from agno.workflow import Workflow
from agno.workflow.step import Step
from agno.utils.workflow_config import configure_workflow_debug

# Debug configuration (enabled by default)
SHOW_DEBUG_TREE = True
EXPORT_DEBUG_MARKDOWN = True
DEBUG_VERBOSE = True

# Create agent
agent = Agent(
    name="Assistant",
    model=Ollama(id="glm-4.6:cloud"),
    instructions="You are a helpful assistant. Provide clear, concise responses.",
    markdown=True,
)

# Create step
step = Step(
    name="Process Request",
    agent=agent,
)

# Create workflow
workflow = Workflow(
    name="Simple Workflow",
    description="A minimal workflow example",
    steps=[step],
    store_events=True,
    debug_mode=False,
    db=SqliteDb(db_file="tmp/workflow.db"),
)

# Configure debug export (enabled by default)
configure_workflow_debug(
    workflow,
    show_console_tree=SHOW_DEBUG_TREE,        # ASCII tree in console
    export_markdown=EXPORT_DEBUG_MARKDOWN,    # Markdown debug report
    reports_dir=str(Path(__file__).parent / "reports"),
    report_pattern="simple_output_*.md",
    verbose=DEBUG_VERBOSE,                    # Detailed metrics
    include_analysis=True,                     # Optimization analysis
)

# Execute workflow
if __name__ == "__main__":
    result = workflow.print_response(
        input="What are the key benefits of using workflows?",
        stream=True,
        stream_intermediate_steps=True,
    )
