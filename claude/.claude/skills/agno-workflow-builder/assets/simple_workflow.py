#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno>=2.2.10",
#   "fastapi>=0.118.0",
#   "ollama",
#   "sqlalchemy",
#   "click",
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///
# NOTE: This format is portable and works from any agno_workflows/* directory
# uv resolves the relative path ../../libs/agno from the script location

"""
Simple Agno Workflow Example with Click CLI

Demonstrates the minimal idiomatic pattern for an Agno workflow with debugging
and Click command-line interface.

Usage:
    ./simple_workflow.py run "Your prompt here"
    ./simple_workflow.py run --prompt "Custom prompt"
    ./simple_workflow.py run --help
"""

# Disable Agno telemetry before importing agno modules
import os
os.environ["AGNO_TELEMETRY"] = "false"

import click
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
    # debug_mode=True,          # Uncomment for agent-level debugging
    # debug_level=1,            # 1=basic, 2=detailed
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

# Click CLI
@click.group()
def cli():
    """Simple Workflow CLI"""
    pass


@cli.command()
@click.argument('prompt', required=False)
@click.option('--prompt', '-p', 'prompt_opt', help='Prompt for workflow')
@click.option('--stream/--no-stream', default=True, help='Stream output')
def run(prompt, prompt_opt, stream):
    """Execute workflow with a prompt"""
    input_prompt = prompt or prompt_opt or "What are the key benefits of using workflows?"

    workflow.print_response(
        input=input_prompt,
        stream=stream,
        stream_intermediate_steps=stream,
    )


if __name__ == "__main__":
    cli()
