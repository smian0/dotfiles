#!/usr/bin/env python3
"""
Hybrid Workflow Template

A comprehensive workflow combining sequential and parallel execution patterns,
similar to Agno's hybrid workflow (sequential → parallel → sequential).

Pattern: Prep → [Parallel Tasks] → Synthesis → Save

Usage:
    python hybrid_workflow.py
"""

import asyncio
import sys
from pathlib import Path

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from workflow_helpers import (
    run_agent_task,
    print_message,
    get_user_input
)
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()


async def main():
    """
    Hybrid workflow: Sequential → Parallel → Sequential

    Equivalent Agno pattern:
        workflow = Workflow(
            steps=[
                Step(name="Prep", agent=prep_agent),
                Parallel(
                    Step(name="Task 1", agent=agent1),
                    Step(name="Task 2", agent=agent2),
                    Step(name="Task 3", agent=agent3)
                ),
                Step(name="Synthesize", agent=synth_agent),
                Step(name="Save", executor=save_function)
            ]
        )
    """
    console = Console()

    # ==================================================================
    # Configuration with Multiple Specialized Subagents
    # ==================================================================

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        permission_mode="acceptEdits",
        setting_sources=["project"],
        allowed_tools=[
            'Read', 'Write', 'Edit', 'Grep', 'Glob',
            'Task',  # Required for subagent delegation
            'TodoWrite', 'WebSearch', 'WebFetch'
        ],
        agents={
            # Specialized subagents for different analysis types
            "technical-analyst": AgentDefinition(
                description="Technical expert analyzing technical aspects, architecture, and implementation details.",
                prompt="""You are a technical analyst specializing in architecture and implementation.
Focus on technical aspects: architecture, tech stack, implementation patterns, scalability.
Use WebSearch for technical details and best practices.
Save findings to /docs/technical_analysis.md""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            ),
            "business-analyst": AgentDefinition(
                description="Business expert analyzing market fit, use cases, and business value.",
                prompt="""You are a business analyst specializing in market analysis and business strategy.
Focus on business aspects: market fit, use cases, ROI, competitive advantage.
Use WebSearch for market data and business insights.
Save findings to /docs/business_analysis.md""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            ),
            "user-analyst": AgentDefinition(
                description="UX expert analyzing user experience, adoption, and user feedback.",
                prompt="""You are a UX analyst specializing in user experience and adoption.
Focus on user aspects: UX, ease of use, learning curve, user feedback, adoption barriers.
Use WebSearch for user reviews and UX insights.
Save findings to /docs/user_analysis.md""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            )
        }
    )

    console.print("[bold green]Hybrid Workflow (Sequential + Parallel)[/bold green]")
    console.print("Pattern: Prep → Parallel Analysis → Synthesis → Save\n")

    # ==================================================================
    # Get User Input
    # ==================================================================

    topic = get_user_input(console, "What technology/product would you like analyzed? ")

    if not topic or topic.lower() in ['exit', 'quit']:
        console.print("[yellow]Exiting...[/yellow]")
        return

    # ==================================================================
    # Execute Hybrid Workflow
    # ==================================================================

    async with ClaudeSDKClient(options=options) as client:

        # ================================================================
        # Phase 1: Preparation (Sequential)
        # ================================================================
        console.print("\n[bold cyan]Phase 1: Preparation[/bold cyan]")
        prep_prompt = f"""Before we dive into detailed analysis, first:
1. Provide a brief overview of {topic}
2. Identify the key aspects that should be analyzed
3. Outline 3 specific analysis angles:
   - Technical (architecture, implementation)
   - Business (market fit, value proposition)
   - User (UX, adoption, feedback)

This will guide our parallel analysis."""

        prep_result = await run_agent_task(client, prep_prompt, console=console)
        print_message("assistant", prep_result, console)

        # ================================================================
        # Phase 2: Parallel Analysis
        # ================================================================
        console.print("\n[bold cyan]Phase 2: Parallel Analysis[/bold cyan]")
        console.print("Delegating to 3 specialized analysts working in parallel...\n")

        parallel_prompt = f"""Based on the overview, coordinate comprehensive analysis of {topic}:

Delegate these analyses to specialized subagents (they will work in parallel):
1. Technical analysis → technical-analyst subagent
2. Business analysis → business-analyst subagent
3. User experience analysis → user-analyst subagent

Each analyst should:
- Conduct thorough research in their specialty
- Use web search for current information
- Save findings to their specific report file

Coordinate the parallel analysis and report when all three are complete."""

        parallel_result = await run_agent_task(client, parallel_prompt, show_tools=True, console=console)
        print_message("assistant", parallel_result, console)

        # ================================================================
        # Phase 3: Synthesis (Sequential)
        # ================================================================
        console.print("\n[bold cyan]Phase 3: Synthesis[/bold cyan]")
        synthesis_prompt = """Now synthesize all findings into a comprehensive report:

Read all three analysis reports:
- /docs/technical_analysis.md
- /docs/business_analysis.md
- /docs/user_analysis.md

Create a unified analysis that:
1. Executive Summary (key findings from all angles)
2. Technical Assessment
3. Business Evaluation
4. User Experience Review
5. Cross-cutting Insights (patterns across analyses)
6. Overall Recommendation
7. Next Steps

Synthesize findings to show the complete picture."""

        synthesis_result = await run_agent_task(client, synthesis_prompt, console=console)
        print_message("assistant", synthesis_result, console)

        # ================================================================
        # Phase 4: Save Final Report (Sequential)
        # ================================================================
        console.print("\n[bold cyan]Phase 4: Save Report[/bold cyan]")
        save_prompt = """Save the synthesized analysis to /docs/comprehensive_analysis.md

Use proper markdown formatting with:
- Clear section headings
- Bullet points for key findings
- Tables where appropriate
- Citations from the three source reports

Confirm when the report is saved."""

        save_result = await run_agent_task(client, save_prompt, console=console)
        print_message("system", save_result, console)

    console.print("\n[bold green]✓ Hybrid Workflow Complete![/bold green]")
    console.print("[dim]Check /docs/comprehensive_analysis.md for the final report[/dim]")


if __name__ == "__main__":
    asyncio.run(main())
