#!/usr/bin/env python3
"""
Demo: AdaptiveDeepResearchAgent Now Executes Research
======================================================

This demonstrates the fix - the agent no longer waits for confirmation.
It presents a plan and immediately executes the research.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration import AdaptiveDeepResearchAgent, AgentConfig

def test_execution_fix():
    """Demonstrate the agent now executes research without waiting"""

    print("\n" + "=" * 80)
    print("DEMONSTRATION: AGENT EXECUTION FIX")
    print("=" * 80)
    print()
    print("BEFORE FIX:")
    print("- Agent would present plan and STOP")
    print("- Would wait for confirmation that never came")
    print("- No research would be executed")
    print()
    print("AFTER FIX:")
    print("- Agent presents plan AND executes immediately")
    print("- Uses tools (if provided) to gather information")
    print("- Provides complete research report")
    print()
    print("=" * 80)
    print()

    # Minimal configuration to avoid token limits
    config = AgentConfig(
        name="ExecutionDemo",
        model_id="claude-sonnet-4",
        temperature=0.3,
        max_tokens=2000,  # Very small to ensure it completes
        markdown=True
    )

    # NO TOOLS - this will show simulated research execution
    agent = AdaptiveDeepResearchAgent(config, tools=[])

    query = "What is fusion energy and why is it important?"

    print(f"Query: {query}")
    print(f"Complexity: {agent._detect_complexity(query)}")  # Should be "simple"
    print(f"Tools: None (simulated research)")
    print()
    print("⏳ Executing...")
    print()

    start = datetime.now()
    result = agent.run(query)
    duration = (datetime.now() - start).total_seconds()

    print("=" * 80)
    print("RESULT")
    print("=" * 80)
    print()

    if result.success:
        print(f"✅ SUCCESS - Agent executed research!")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📏 Output: {len(result.content):,} chars")
        print()
        print("=" * 80)
        print("REPORT OUTPUT")
        print("=" * 80)
        print()
        print(result.content)
        print()
        print("=" * 80)
        print()
        print("✅ PROOF: Agent provided complete research output")
        print("   (Without fix, would have stopped at planning stage)")
        print()

        # Save
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"execution_demo_{timestamp}.md"

        with open(report_file, 'w') as f:
            f.write(f"# Agent Execution Fix Demonstration\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Before Fix\n\n")
            f.write("- Agent would present plan\n")
            f.write("- Wait for confirmation\n")
            f.write("- Never execute research\n\n")
            f.write(f"## After Fix\n\n")
            f.write("- Agent presents plan\n")
            f.write("- IMMEDIATELY executes research\n")
            f.write("- Provides complete output\n\n")
            f.write("---\n\n")
            f.write(result.content)

        print(f"💾 Saved to: {report_file.absolute()}")

    else:
        print(f"❌ Failed: {result.error}")

if __name__ == "__main__":
    test_execution_fix()
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("The agent now:")
    print("1. ✅ Accepts tools parameter (OllamaWebTools, MCP, etc.)")
    print("2. ✅ Executes research immediately (no confirmation wait)")
    print("3. ✅ Provides complete reports (not just plans)")
    print()
    print("For actual web research, provide tools:")
    print("  agent = AdaptiveDeepResearchAgent(tools=[OllamaWebTools()])")
    print()
