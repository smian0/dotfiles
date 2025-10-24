#!/usr/bin/env python3
"""
Complex Parallel Workflow Demo

Demonstrates a workflow with two sub-agents working in parallel:
- Technical Analyst: Researches technical aspects
- Business Analyst: Researches business/market aspects

Then synthesizes findings into a comprehensive report.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "helpers"))

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from workflow_helpers import (
    create_base_options,
    run_agent_task,
    extract_text_from_message,
)
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()


async def main():
    """Run parallel research workflow with two sub-agents."""
    console = Console()

    console.print(Panel(
        "[bold cyan]Parallel Research Workflow Demo[/bold cyan]\n\n"
        "This workflow uses two sub-agents:\n"
        "• [magenta]Technical Analyst[/magenta] - Researches technical implementation\n"
        "• [green]Business Analyst[/green] - Researches market and business aspects\n\n"
        "Then synthesizes their findings into a comprehensive report.",
        title="🌳 Workflow Overview",
        border_style="cyan"
    ))

    # Define two specialized sub-agents
    technical_analyst = AgentDefinition(
        description=(
            "Technical specialist who researches implementation details, "
            "architecture, technical requirements, and engineering considerations. "
            "Focus on how things work technically."
        ),
        tools=["Read", "WebSearch", "WebFetch", "TodoWrite"],
        model="claude-sonnet-4-20250514",
    )

    business_analyst = AgentDefinition(
        description=(
            "Business and market specialist who researches market position, "
            "business model, competitive landscape, and strategic considerations. "
            "Focus on business value and market dynamics."
        ),
        tools=["Read", "WebSearch", "WebFetch", "TodoWrite"],
        model="claude-sonnet-4-20250514",
    )

    # Create options with debug mode and sub-agents
    console.print("\n[bold]Setting up workflow with debug mode...[/bold]")

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        allowed_tools=["Task", "TodoWrite", "Read", "Write"],
        permission_mode="acceptEdits",
        setting_sources=["project"],
        agents={
            "technical-analyst": technical_analyst,
            "business-analyst": business_analyst,
        }
    )

    # Manually add debug hooks
    from workflow_helpers import WorkflowLogger, create_debug_hooks
    logger = WorkflowLogger("parallel_research")
    hooks = await create_debug_hooks(logger, verbose=True)
    options.hooks = hooks

    console.print(f"[green]✓[/green] Debug logging to: {logger.log_file}\n")

    # Research topic
    topic = "FastAPI vs Flask for production APIs"

    async with ClaudeSDKClient(options=options) as client:
        # Step 1: Initial planning
        console.print(Panel(
            f"[bold yellow]Step 1:[/bold yellow] Planning research for: [cyan]{topic}[/cyan]",
            border_style="yellow"
        ))

        plan_prompt = f"""Create a research plan for: {topic}

Use TodoWrite to create 3 tasks:
1. Delegate technical research to @technical-analyst
2. Delegate business research to @business-analyst
3. Synthesize findings into comprehensive report"""

        result1 = await run_agent_task(client, plan_prompt, console=console)
        console.print("[green]✓[/green] Planning complete\n")

        # Step 2: Parallel research delegation
        console.print(Panel(
            "[bold yellow]Step 2:[/bold yellow] Delegating to sub-agents in parallel",
            border_style="yellow"
        ))

        delegate_prompt = f"""Now execute the research plan for: {topic}

Use the Task tool to delegate BOTH research tasks in parallel:

1. Delegate to @technical-analyst: Research technical aspects of {topic}:
   - Performance characteristics
   - Architecture and design patterns
   - Developer experience
   - Ecosystem and tooling

2. Delegate to @business-analyst: Research business aspects of {topic}:
   - Market adoption and trends
   - Use cases and industries
   - Company backing and community
   - Long-term viability

IMPORTANT: Use the Task tool twice in a single response to run both in parallel."""

        result2 = await run_agent_task(client, delegate_prompt, console=console)
        technical_findings = extract_text_from_message(result2)
        console.print("[green]✓[/green] Parallel research complete\n")

        # Step 3: Synthesis
        console.print(Panel(
            "[bold yellow]Step 3:[/bold yellow] Synthesizing findings",
            border_style="yellow"
        ))

        synthesis_prompt = f"""Based on the research findings from both analysts, create a comprehensive report on {topic}.

Structure:
1. Executive Summary
2. Technical Analysis (from technical-analyst)
3. Business Analysis (from business-analyst)
4. Comparative Insights
5. Recommendation

Use Write tool to save the report to 'research_report.md'"""

        result3 = await run_agent_task(client, synthesis_prompt, console=console)
        console.print("[green]✓[/green] Report generated\n")

    console.print(Panel(
        "[bold green]✓ Workflow Complete![/bold green]\n\n"
        f"Log file: [cyan]{logger.log_file}[/cyan]",
        title="Success",
        border_style="green"
    ))

    return logger.log_file


if __name__ == "__main__":
    try:
        log_file = asyncio.run(main())

        console = Console()
        console.print("\n" + "="*80 + "\n")
        console.print("[bold cyan]Now visualizing workflow execution...[/bold cyan]\n")

        # Import and run visualizer
        from workflow_tree_visualizer import visualize_workflow

        visualize_workflow(
            log_file=str(log_file),
            verbose=True,
            show_metrics=True,
            show_timeline=True
        )

    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Workflow interrupted[/yellow]")
    except Exception as e:
        console = Console()
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
