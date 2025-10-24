#!/usr/bin/env python3
"""
Demo: Workflow Tree Visualizer

Shows how to use the tree visualizer with debug mode.
"""

import asyncio
import sys
from pathlib import Path

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent / "helpers"))

from claude_agent_sdk import ClaudeSDKClient
from workflow_helpers import (
    create_base_options,
    run_agent_task,
)
from workflow_tree_visualizer import visualize_workflow
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()


async def main():
    """Run a simple workflow with debug mode, then visualize it."""
    console = Console()

    console.print("[bold green]Workflow Tree Visualizer Demo[/bold green]")
    console.print("This demo will run a simple workflow with debug mode enabled,")
    console.print("then visualize the execution as an ASCII tree.\n")

    # Step 1: Run workflow with debug mode
    console.print("[bold cyan]Step 1: Running workflow with debug mode...[/bold cyan]")

    options = await create_base_options(
        model="claude-sonnet-4-20250514",
        allowed_tools=['Read', 'Write', 'TodoWrite'],
        debug=True,
        verbose=True,
        workflow_name="tree_demo"
    )

    async with ClaudeSDKClient(options=options) as client:
        # Simple task that uses TodoWrite
        prompt = """Create a todo list for researching Python web frameworks:
1. Research Flask
2. Research FastAPI
3. Research Django
4. Compare features
5. Write recommendation"""

        result = await run_agent_task(client, prompt, console=console)
        console.print(f"\n[green]Task completed![/green]\n")

    # Step 2: Find the log file
    logs_dir = Path(__file__).parent / "logs"
    log_files = sorted(logs_dir.glob("*_tree_demo.log"))

    if not log_files:
        console.print("[red]No log file found![/red]")
        return

    latest_log = log_files[-1]
    console.print(f"[bold cyan]Step 2: Visualizing workflow from log file...[/bold cyan]")
    console.print(f"[dim]Log file: {latest_log}[/dim]\n")

    # Step 3: Visualize with tree
    visualize_workflow(
        log_file=str(latest_log),
        verbose=True,
        show_metrics=True,
        show_timeline=True
    )

    console.print("[bold green]✓ Demo Complete![/bold green]")
    console.print(f"\nLog file saved to: {latest_log}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Demo interrupted[/yellow]")
    except Exception as e:
        console = Console()
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
