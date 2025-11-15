#!/usr/bin/env python3
"""
Test Phase 1 Workflow Integration

Verifies that Phase 1 enhancements are integrated into the main workflow
by running just the intelligence step with existing Graphiti data.
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Import from main workflow
from rss_intelligence_workflow import create_intelligence_step
from agno.workflow import StepInput


async def test_phase1_integration():
    """Test Phase 1 intelligence step integration"""

    print("=" * 80)
    print("Phase 1 Workflow Integration Test")
    print("=" * 80)
    print()

    # Create the intelligence step from main workflow
    intelligence_step = create_intelligence_step()

    print("✓ Intelligence step created from main workflow")
    print(f"  Step name: {intelligence_step.name}")
    print(f"  Description: {intelligence_step.description}\n")

    # Create dummy step input (intelligence step doesn't use it)
    step_input = StepInput(step_name="analyze_knowledge_graph", content="")

    print("🧠 Running Phase 1 intelligence step...\n")

    try:
        # Execute the step
        result = intelligence_step.executor(step_input)

        print("=" * 80)
        print("Phase 1 Intelligence Result")
        print("=" * 80)
        print()

        if result.success:
            print("✅ Phase 1 intelligence step executed successfully!\n")
            print("Intelligence Summary:")
            print("-" * 80)
            print(result.content[:2000])  # Show first 2000 chars
            if len(result.content) > 2000:
                print(f"\n... ({len(result.content) - 2000} more characters)")
            print("-" * 80)
            return 0
        else:
            print("⚠️  Intelligence step completed but marked as failed")
            print(f"Content: {result.content}")
            return 1

    except Exception as e:
        print(f"❌ Error executing intelligence step: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    try:
        return asyncio.run(test_phase1_integration())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
