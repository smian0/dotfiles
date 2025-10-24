#!/usr/bin/env python3
"""
Simple Sequential Workflow Template

A basic workflow that processes a task through multiple sequential steps,
similar to Agno's simple workflow pattern but using Claude Agent SDK.

Pattern: Input → Step 1 → Step 2 → Step 3 → Output

Usage:
    python simple_workflow.py
"""

import asyncio
import sys
from pathlib import Path

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from workflow_helpers import (
    create_base_options,
    run_agent_task,
    run_sequential_tasks,
    print_message,
    get_user_input
)
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()


async def main():
    """
    Simple workflow example: Sequential multi-step processing.

    Equivalent Agno pattern:
        workflow = Workflow(
            steps=[
                Step(name="Step 1", agent=agent1),
                Step(name="Step 2", agent=agent2),
                Step(name="Step 3", agent=agent3)
            ]
        )
    """
    console = Console()

    # ==================================================================
    # Configuration
    # ==================================================================

    options = create_base_options(
        model="claude-sonnet-4-20250514",
        allowed_tools=[
            'Read', 'Write', 'Edit', 'Grep', 'Glob',
            'TodoWrite', 'WebSearch', 'WebFetch'
        ],
        permission_mode="acceptEdits"
    )

    console.print("[bold green]Simple Sequential Workflow[/bold green]")
    console.print("This workflow processes tasks through multiple sequential steps.\n")

    # ==================================================================
    # Get User Input
    # ==================================================================

    user_task = get_user_input(console, "What would you like to analyze? ")

    if not user_task or user_task.lower() in ['exit', 'quit']:
        console.print("[yellow]Exiting...[/yellow]")
        return

    # ==================================================================
    # Execute Workflow
    # ==================================================================

    async with ClaudeSDKClient(options=options) as client:

        # Step 1: Research and gather information
        console.print("\n[bold cyan]Step 1: Research[/bold cyan]")
        step1_prompt = f"""Research the following topic and gather key information:
{user_task}

Provide a comprehensive overview with key facts and findings."""

        step1_result = await run_agent_task(client, step1_prompt, console=console)
        print_message("assistant", step1_result, console)

        # Step 2: Analyze the research
        console.print("\n[bold cyan]Step 2: Analysis[/bold cyan]")
        step2_prompt = """Based on your previous research, analyze the key findings:
- Identify the most important insights
- Note any patterns or trends
- Highlight potential implications

Provide a detailed analysis."""

        step2_result = await run_agent_task(client, step2_prompt, console=console)
        print_message("assistant", step2_result, console)

        # Step 3: Generate recommendations
        console.print("\n[bold cyan]Step 3: Recommendations[/bold cyan]")
        step3_prompt = """Based on your research and analysis, provide actionable recommendations:
- What are the key takeaways?
- What should be done next?
- Any best practices to follow?

Create a concise summary with recommendations."""

        step3_result = await run_agent_task(client, step3_prompt, console=console)
        print_message("assistant", step3_result, console)

        # ==================================================================
        # Save Report (Optional)
        # ==================================================================

        console.print("\n[bold cyan]Saving Report[/bold cyan]")
        save_prompt = f"""Create a comprehensive markdown report that combines all previous steps:
1. The research findings
2. The analysis
3. The recommendations

Save the report to /docs/workflow_report.md with proper formatting."""

        save_result = await run_agent_task(client, save_prompt, console=console)
        print_message("system", save_result, console)

    console.print("\n[bold green]✓ Workflow Complete![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
