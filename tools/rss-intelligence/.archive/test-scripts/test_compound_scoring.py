#!/usr/bin/env python3
"""
Test Phase 1 compound scoring with existing Graphiti data.
This script runs ONLY the intelligence analysis step to test compound scoring
without needing to rerun the full workflow.
"""

import asyncio
from rss_intelligence_workflow import analyze_knowledge_graph
from agno.workflow.step import StepInput

async def test_phase1():
    """Test Phase 1 intelligence analysis with existing Graphiti data."""

    print("=" * 80)
    print("Testing Phase 1 Compound Scoring")
    print("=" * 80)
    print()

    # Create mock step input (intelligence analysis doesn't use it)
    step_input = StepInput(
        step_name="analyze_knowledge_graph",
        content="Test run for Phase 1 compound scoring",
    )

    # Create empty session state
    session_state = {}

    try:
        # Run intelligence analysis step
        print("Running intelligence analysis step...")
        result = await analyze_knowledge_graph(step_input, session_state)

        print()
        print("=" * 80)
        print("Intelligence Analysis Output")
        print("=" * 80)
        print()
        print(result.content)
        print()

        # Check for COMPOUND_SCORE section
        if 'COMPOUND_SCORE:' in result.content:
            print("✅ SUCCESS: COMPOUND_SCORE section found!")
            print()
            # Extract and display just the compound score section
            parts = result.content.split('COMPOUND_SCORE:')
            if len(parts) > 1:
                compound_section = parts[1].split('\n\n')[0]
                print("=" * 80)
                print("Compound Score Section")
                print("=" * 80)
                print("COMPOUND_SCORE:" + compound_section)
        else:
            print("⚠️  No COMPOUND_SCORE section found")
            print()
            print("Possible reasons:")
            print("- Fewer than 10 entities with both velocity AND cascade metrics")
            print("- LLM didn't follow Phase 1 instructions")
            print("- No data in knowledge graph")

        print()
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_phase1())
