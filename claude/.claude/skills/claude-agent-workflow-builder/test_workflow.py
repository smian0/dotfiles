#!/usr/bin/env python3
"""
Test Workflow: Technology Comparison

A simple workflow to test the claude-agent-workflow-builder skill.
Compares two technologies through sequential analysis.

Usage:
    python test_workflow.py
"""

import asyncio
import sys
from pathlib import Path

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent / "helpers"))

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from workflow_helpers import (
    create_base_options,
    run_agent_task,
    print_message,
    auto_visualize_workflow
)
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()


async def main():
    """Test workflow: Compare two technologies."""
    console = Console()

    console.print("[bold green]Technology Comparison Workflow[/bold green]")
    console.print("This workflow will compare Python and JavaScript.\n")

    # Configure options with debug mode enabled
    options = await create_base_options(
        model="claude-sonnet-4-20250514",
        allowed_tools=[
            'Read', 'Write', 'Edit',
            'TodoWrite', 'WebSearch', 'WebFetch'
        ],
        debug=True,
        verbose=True,
        workflow_name="tech_comparison"
    )

    async with ClaudeSDKClient(options=options) as client:

        # Step 1: Research Python
        console.print("\n[bold cyan]Step 1: Research Python[/bold cyan]")
        step1_prompt = """Research Python programming language:
- Key features and strengths
- Primary use cases
- Ecosystem and libraries
- Community size

Provide a concise summary (3-4 paragraphs)."""

        step1_result = await run_agent_task(client, step1_prompt, console=console)
        print_message("assistant", step1_result, console)

        # Step 2: Research JavaScript
        console.print("\n[bold cyan]Step 2: Research JavaScript[/bold cyan]")
        step2_prompt = """Research JavaScript programming language:
- Key features and strengths
- Primary use cases
- Ecosystem and libraries
- Community size

Provide a concise summary (3-4 paragraphs)."""

        step2_result = await run_agent_task(client, step2_prompt, console=console)
        print_message("assistant", step2_result, console)

        # Step 3: Compare both
        console.print("\n[bold cyan]Step 3: Comparison Analysis[/bold cyan]")
        step3_prompt = """Based on the previous research on Python and JavaScript, create a comparison:

1. Key Differences
2. Similarities
3. When to use Python
4. When to use JavaScript
5. Quick recommendation

Keep it practical and concise."""

        step3_result = await run_agent_task(client, step3_prompt, console=console)
        print_message("assistant", step3_result, console)

    console.print("\n[bold green]✓ Workflow Complete![/bold green]")

    # Auto-visualize with full debug output (enabled by default)
    console.print("\n" + "="*80)
    auto_visualize_workflow("tech_comparison", console=console)
    console.print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Workflow interrupted[/yellow]")
    except Exception as e:
        console = Console()
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
