#!/usr/bin/env python3
"""
Comprehensive Research Workflow Example

A practical example showing how to build a complete research workflow
that mirrors Agno patterns using Claude Agent SDK.

This workflow demonstrates:
- Sequential preparation
- Parallel research execution
- Result synthesis
- Report generation

Usage:
    python research_workflow.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from workflow_helpers import (
    run_agent_task,
    print_message,
    get_user_input
)
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()


async def main():
    """
    Complete research workflow with multiple phases.

    Workflow Pattern:
    1. Topic Analysis (Sequential)
    2. Parallel Research (3 angles)
    3. Synthesis (Sequential)
    4. Report Generation (Sequential)
    """
    console = Console()

    # Display workflow overview
    console.print(Panel.fit(
        """[bold cyan]Comprehensive Research Workflow[/bold cyan]

This workflow will:
1. Analyze your research topic
2. Conduct parallel research from 3 angles
3. Synthesize all findings
4. Generate a comprehensive report

Pattern: Sequential → Parallel → Sequential → Save""",
        border_style="cyan"
    ))

    # ==================================================================
    # Configuration
    # ==================================================================

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        permission_mode="acceptEdits",
        setting_sources=["project"],
        allowed_tools=[
            'Read', 'Write', 'Edit', 'Grep', 'Glob',
            'Task',  # Essential for subagent delegation
            'TodoWrite', 'WebSearch', 'WebFetch'
        ],
        agents={
            # Historical perspective researcher
            "history-specialist": AgentDefinition(
                description="Research specialist focusing on historical context, evolution, and key milestones.",
                prompt="""You are a research specialist focused on historical context and evolution.

Your mission:
1. Research the historical development of the topic
2. Identify key milestones and turning points
3. Understand how it evolved over time
4. Note important historical figures or organizations

Research process:
- Use WebSearch for historical information
- Use WebFetch to read detailed articles
- Focus on chronological development
- Cite sources with dates

Save your findings to: /docs/research_history.md

Format with:
- Timeline of key events
- Important milestones
- Evolution narrative
- Sources and citations""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            ),

            # Current state researcher
            "current-specialist": AgentDefinition(
                description="Research specialist focusing on current state, trends, and key players in the field.",
                prompt="""You are a research specialist focused on current state and trends.

Your mission:
1. Research current state of the topic
2. Identify key players and organizations
3. Understand current trends and developments
4. Gather recent statistics and data

Research process:
- Use WebSearch for recent information (2023-2025)
- Use WebFetch to read current articles
- Focus on present-day landscape
- Include current statistics

Save your findings to: /docs/research_current.md

Format with:
- Current landscape overview
- Key players and organizations
- Recent trends (last 2 years)
- Statistics and metrics
- Sources and citations""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            ),

            # Future trends researcher
            "future-specialist": AgentDefinition(
                description="Research specialist focusing on future trends, predictions, and implications.",
                prompt="""You are a research specialist focused on future trends and implications.

Your mission:
1. Research predicted future trends
2. Identify emerging technologies or approaches
3. Understand potential impacts and implications
4. Note expert predictions and forecasts

Research process:
- Use WebSearch for future predictions and analysis
- Use WebFetch to read forward-looking articles
- Focus on 1-5 year outlook
- Include expert opinions

Save your findings to: /docs/research_future.md

Format with:
- Predicted trends
- Emerging developments
- Potential impacts
- Expert forecasts
- Sources and citations""",
                model="sonnet",
                tools=['Read', 'Write', 'WebSearch', 'WebFetch', 'TodoWrite']
            )
        }
    )

    # ==================================================================
    # Get Research Topic
    # ==================================================================

    topic = get_user_input(
        console,
        "\n[bold]Enter research topic:[/bold] "
    )

    if not topic or topic.lower() in ['exit', 'quit']:
        console.print("[yellow]Exiting...[/yellow]")
        return

    console.print(f"\n[green]✓[/green] Starting research on: [bold]{topic}[/bold]\n")

    # ==================================================================
    # Execute Workflow
    # ==================================================================

    async with ClaudeSDKClient(options=options) as client:

        # ================================================================
        # Phase 1: Topic Analysis (Sequential)
        # ================================================================
        console.print(Panel(
            "[bold]Phase 1: Topic Analysis[/bold]",
            border_style="cyan"
        ))

        analysis_prompt = f"""Analyze this research topic: {topic}

Provide:
1. Topic overview and definition
2. Why this topic is important/relevant
3. Key aspects that should be researched
4. Three specific research angles:
   - Historical evolution
   - Current state and trends
   - Future implications

This will guide our parallel research phase.
Keep analysis concise (2-3 paragraphs)."""

        analysis = await run_agent_task(client, analysis_prompt, console=console)
        print_message("assistant", analysis, console)

        # ================================================================
        # Phase 2: Parallel Research (3 Specialists)
        # ================================================================
        console.print(Panel(
            "[bold]Phase 2: Parallel Research[/bold]\n[dim]Delegating to 3 specialized researchers...[/dim]",
            border_style="cyan"
        ))

        research_prompt = f"""Now coordinate comprehensive research on: {topic}

Delegate to specialized subagents working in PARALLEL:
1. Historical perspective → history-specialist subagent
2. Current state → current-specialist subagent
3. Future trends → future-specialist subagent

Each specialist will:
- Conduct thorough research in their area
- Use web search for information
- Save findings to their specific markdown file

Coordinate the parallel research and confirm when all three specialists
have completed their work."""

        research_result = await run_agent_task(
            client,
            research_prompt,
            show_tools=True,
            console=console
        )
        print_message("assistant", research_result, console)

        # ================================================================
        # Phase 3: Synthesis (Sequential)
        # ================================================================
        console.print(Panel(
            "[bold]Phase 3: Synthesis[/bold]\n[dim]Combining research from all angles...[/dim]",
            border_style="cyan"
        ))

        synthesis_prompt = """Read and synthesize all three research reports:
- /docs/research_history.md (historical context)
- /docs/research_current.md (current state)
- /docs/research_future.md (future trends)

Create a comprehensive synthesis that:
1. Integrates findings across all three time perspectives
2. Identifies connections and patterns between past, present, and future
3. Provides a cohesive narrative showing progression
4. Highlights key insights that emerge from the combined research

Structure the synthesis:
## Executive Summary
- 3-5 key takeaways from all research

## Integrated Analysis
- How historical developments led to current state
- How current trends point to future directions
- Cross-cutting themes and patterns

## Critical Insights
- What becomes clear when viewing all three angles together
- Surprising connections or contradictions
- Important implications

Provide the synthesis now (don't save yet - next step will format final report)."""

        synthesis = await run_agent_task(client, synthesis_prompt, console=console)
        print_message("assistant", synthesis, console)

        # ================================================================
        # Phase 4: Final Report Generation (Sequential)
        # ================================================================
        console.print(Panel(
            "[bold]Phase 4: Report Generation[/bold]\n[dim]Creating final comprehensive report...[/dim]",
            border_style="cyan"
        ))

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_prompt = f"""Generate the final comprehensive research report.

Combine:
1. The initial topic analysis
2. All three research reports (history, current, future)
3. The synthesis

Create a well-structured report with:

# Research Report: {topic}
*Generated: {timestamp}*

## Executive Summary
[Key findings summary]

## Historical Context
[From history specialist + analysis]

## Current Landscape
[From current specialist + analysis]

## Future Outlook
[From future specialist + analysis]

## Synthesis & Insights
[The integrated analysis from synthesis phase]

## Conclusions & Recommendations
[Your conclusions based on all research]

## References
[All sources cited by the three specialists]

---

Save this report to: /docs/comprehensive_research_report.md

Confirm once saved."""

        report_result = await run_agent_task(client, report_prompt, console=console)
        print_message("system", report_result, console)

    # ==================================================================
    # Completion
    # ==================================================================
    console.print(Panel.fit(
        f"""[bold green]✓ Research Workflow Complete![/bold green]

[bold]Files generated:[/bold]
• /docs/research_history.md
• /docs/research_current.md
• /docs/research_future.md
• /docs/comprehensive_research_report.md

[bold]Topic researched:[/bold] {topic}
[bold]Timestamp:[/bold] {timestamp}

[dim]Check the final report for comprehensive findings.[/dim]""",
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Research workflow interrupted by user[/yellow]")
    except Exception as e:
        console = Console()
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
