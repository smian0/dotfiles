#!/usr/bin/env python3
"""
Parallel Workflow Template

A workflow that delegates multiple independent tasks to specialized subagents
that execute in parallel, similar to Agno's Parallel() pattern.

Pattern: Input → [Task 1 | Task 2 | Task 3] → Synthesis → Output

Usage:
    python parallel_workflow.py
"""

import asyncio
import sys
from pathlib import Path

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from workflow_helpers import (
    create_base_options,
    create_researcher_agent,
    run_agent_task,
    print_message,
    get_user_input
)
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()


async def main():
    """
    Parallel workflow example: Multiple subagents execute simultaneously.

    Equivalent Agno pattern:
        parallel = Parallel(
            Step(name="Task 1", agent=agent1),
            Step(name="Task 2", agent=agent2),
            Step(name="Task 3", agent=agent3),
            name="Parallel Tasks"
        )
        workflow = Workflow(steps=[parallel, synthesize_step])
    """
    console = Console()

    # ==================================================================
    # Configuration with Subagents
    # ==================================================================

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        permission_mode="acceptEdits",
        setting_sources=["project"],
        allowed_tools=[
            'Read', 'Write', 'Edit', 'Grep', 'Glob',
            'Task',  # REQUIRED for subagent delegation
            'TodoWrite', 'WebSearch', 'WebFetch'
        ],
        # Define specialized subagents for parallel execution
        agents={
            "researcher-1": AgentDefinition(
                description="Specialist focused on the first research angle or subtopic.",
                prompt="""You are a research specialist focused on your assigned angle.
Conduct thorough research on your specific aspect and provide comprehensive findings.
Use WebSearch and WebFetch to gather information.
Write your findings to /docs/research_1.md""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            ),
            "researcher-2": AgentDefinition(
                description="Specialist focused on the second research angle or subtopic.",
                prompt="""You are a research specialist focused on your assigned angle.
Conduct thorough research on your specific aspect and provide comprehensive findings.
Use WebSearch and WebFetch to gather information.
Write your findings to /docs/research_2.md""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            ),
            "researcher-3": AgentDefinition(
                description="Specialist focused on the third research angle or subtopic.",
                prompt="""You are a research specialist focused on your assigned angle.
Conduct thorough research on your specific aspect and provide comprehensive findings.
Use WebSearch and WebFetch to gather information.
Write your findings to /docs/research_3.md""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            )
        }
    )

    console.print("[bold green]Parallel Workflow with Subagents[/bold green]")
    console.print("This workflow delegates tasks to multiple specialists working in parallel.\n")

    # ==================================================================
    # Get User Input
    # ==================================================================

    topic = get_user_input(console, "What topic would you like researched from multiple angles? ")

    if not topic or topic.lower() in ['exit', 'quit']:
        console.print("[yellow]Exiting...[/yellow]")
        return

    # ==================================================================
    # Execute Parallel Workflow
    # ==================================================================

    async with ClaudeSDKClient(options=options) as client:

        # Parallel Phase: Delegate to multiple subagents
        console.print("\n[bold cyan]Phase 1: Parallel Research[/bold cyan]")
        console.print("Delegating to 3 specialized researchers working in parallel...\n")

        parallel_prompt = f"""I need comprehensive research on: {topic}

Please coordinate with the specialized researchers to cover three different angles:
1. Historical context and evolution
2. Current state and key players
3. Future trends and implications

Delegate each angle to a different researcher subagent so they can work in parallel.
Each researcher should save their findings to /docs/research_N.md

Coordinate the parallel research and let me know when all three are complete."""

        parallel_result = await run_agent_task(client, parallel_prompt, show_tools=True, console=console)
        print_message("assistant", parallel_result, console)

        # Synthesis Phase: Combine parallel results
        console.print("\n[bold cyan]Phase 2: Synthesis[/bold cyan]")
        console.print("Combining results from all researchers...\n")

        synthesis_prompt = """Now read all three research reports:
- /docs/research_1.md
- /docs/research_2.md
- /docs/research_3.md

Synthesize them into a comprehensive final report that:
1. Integrates findings from all three angles
2. Identifies connections and patterns across the research
3. Provides a cohesive narrative
4. Includes all key insights

Save the final synthesized report to /docs/final_report.md"""

        synthesis_result = await run_agent_task(client, synthesis_prompt, console=console)
        print_message("assistant", synthesis_result, console)

    console.print("\n[bold green]✓ Parallel Workflow Complete![/bold green]")
    console.print("[dim]Check /docs/final_report.md for the synthesized results[/dim]")


if __name__ == "__main__":
    asyncio.run(main())
