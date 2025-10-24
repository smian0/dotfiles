#!/usr/bin/env python3
"""
Codebase Analyzer Agent

This agent analyzes a codebase and generates a summary report.
Designed to be run from within Claude Code via the Bash tool.

Usage from Claude Code:
    python3 codebase_analyzer_agent.py /path/to/project

Usage standalone:
    export ANTHROPIC_API_KEY='your-key'
    python3 codebase_analyzer_agent.py /path/to/project
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

try:
    from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock
except ImportError:
    print("Error: claude-agent-sdk not installed")
    print("Install with: pip install claude-agent-sdk")
    sys.exit(1)


async def analyze_codebase(project_path: str, task: Optional[str] = None) -> None:
    """
    Analyze a codebase using the Claude Agent SDK.

    Args:
        project_path: Path to the project directory
        task: Optional specific task to perform
    """
    # Validate path
    if not Path(project_path).exists():
        print(f"Error: Path does not exist: {project_path}")
        sys.exit(1)

    # Default task if none provided
    if not task:
        task = """
        Analyze this codebase and provide:
        1. Project structure overview
        2. Main technologies and frameworks used
        3. Key files and their purposes
        4. Code quality observations
        5. Suggestions for improvement
        """

    # Configure the agent
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        cwd=project_path,
        permission_mode='auto'  # Auto-approve read operations
    )

    print("=" * 70)
    print("CODEBASE ANALYSIS AGENT")
    print("=" * 70)
    print(f"Project: {project_path}")
    print(f"Task: {task.strip()[:100]}...")
    print("=" * 70)
    print()

    # Run the analysis
    try:
        async for message in query(task, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                        print()

        print()
        print("=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"\nError during analysis: {e}")
        sys.exit(1)


async def main():
    """Main entry point."""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print()
        print("Set it with:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python3 codebase_analyzer_agent.py <project_path> [task]")
        print()
        print("Examples:")
        print("  python3 codebase_analyzer_agent.py /path/to/project")
        print("  python3 codebase_analyzer_agent.py . 'Find all TODO comments'")
        sys.exit(1)

    project_path = sys.argv[1]
    task = sys.argv[2] if len(sys.argv) > 2 else None

    # Run the analysis
    await analyze_codebase(project_path, task)


if __name__ == "__main__":
    asyncio.run(main())
