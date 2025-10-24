#!/usr/bin/env python3
"""
Demo Agent: Analyze Claude Agent SDK Examples

This agent analyzes all the example Python files we created and provides:
- Count of examples
- Summary of what each demonstrates
- Learning path recommendations
"""

import asyncio
import os
import sys
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    """Analyze the Agent SDK example files."""

    # No API key needed! SDK uses Claude Code's existing authentication
    # via OAuth (your Pro/Max subscription) - no extra charges!

    # Configure the agent
    examples_dir = "/Users/smian/dotfiles/claude/.claude/ai_docs/examples"

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        cwd=examples_dir,
        permission_mode='acceptEdits'  # Auto-approve read operations
    )

    # Define the analysis task
    task = """
    Analyze all the Python example files in this directory and provide:

    1. **Count**: How many example files exist?

    2. **Categorization**: Group them by difficulty level (beginner, intermediate, advanced)

    3. **Summary Table**: For each file, briefly describe what it demonstrates

    4. **Learning Path**: Recommend which order to study them

    5. **Key Concepts**: List the main Agent SDK concepts covered across all examples

    Format the output as a clear, well-organized report with sections and bullet points.
    """

    print("=" * 70)
    print("AGENT SDK EXAMPLES ANALYSIS")
    print("=" * 70)
    print(f"Analyzing examples in: {examples_dir}")
    print("=" * 70)
    print()

    # Execute the agent
    try:
        async for message in query(prompt=task, options=options):
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
        print(f"\nERROR: {e}")
        print("\nIf you see 'ModuleNotFoundError', install the SDK:")
        print("  pip install claude-agent-sdk")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
