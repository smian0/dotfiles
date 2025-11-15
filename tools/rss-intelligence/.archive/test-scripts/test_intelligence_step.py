#!/usr/bin/env python3
"""
Test Intelligence Step Standalone

Tests the intelligence analysis step in isolation to verify:
1. Async MCP tools work properly
2. Pydantic output schema validation
3. Graphiti queries return structured data
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from rss_intelligence_workflow import (
    create_intelligence_step,
    IntelligenceInsights,
)
from agno.workflow.types import StepInput, StepOutput

async def test_intelligence_step():
    """Test the intelligence step directly"""

    print("=" * 80)
    print("Testing Intelligence Analysis Step")
    print("=" * 80)
    print()

    # Create the intelligence step
    intelligence_step = create_intelligence_step()

    # Create mock step input (intelligence step doesn't use it)
    mock_input = StepInput(
        step_name="test",
        messages=[],
        model=None,
    )

    # Execute the intelligence step
    print("Executing intelligence step...")
    result: StepOutput = intelligence_step.executor(mock_input)

    print("\n" + "=" * 80)
    print("Results")
    print("=" * 80)
    print()

    # Check if successful
    if not result.success:
        print("❌ Intelligence step failed!")
        return 1

    # Get insights
    insights: IntelligenceInsights = result.content

    # Display results
    print(f"✅ Success: {result.success}")
    print(f"📊 Total Entities: {insights.total_entities}")
    print(f"🔗 Total Facts: {insights.total_facts}")
    print(f"📈 Trending Entities: {len(insights.trending_entities)}")
    print(f"🕸️  Key Networks: {len(insights.key_networks)}")
    print(f"🆕 Emerging Topics: {len(insights.emerging_topics)}")
    print(f"🔄 Recurring Topics: {len(insights.recurring_topics)}")
    print(f"⏰ Timestamp: {insights.analysis_timestamp}")
    print()

    # Display trending entities
    if insights.trending_entities:
        print("Trending Entities:")
        for entity in insights.trending_entities[:5]:
            trend = f" ({entity.change_percent:+.0f}%)" if entity.change_percent else " (new)"
            print(f"  - {entity.name} ({entity.entity_type}): {entity.mention_count} mentions{trend}")
        print()

    # Display key networks
    if insights.key_networks:
        print("Key Relationship Networks:")
        for network in insights.key_networks[:3]:
            print(f"  - {network.entity_name}: {network.connection_count} connections")
            print(f"    Types: {', '.join(network.relationship_types[:3])}")
            print(f"    Connected to: {', '.join(network.key_connections[:3])}")
        print()

    # Display emerging topics
    if insights.emerging_topics:
        print(f"Emerging Topics: {', '.join(insights.emerging_topics)}")
        print()

    # Display recurring topics
    if insights.recurring_topics:
        print(f"Recurring Topics: {', '.join(insights.recurring_topics)}")
        print()

    print("=" * 80)
    print("✅ Intelligence step test completed successfully!")
    print("=" * 80)

    return 0


def main():
    """Run async test"""
    return asyncio.run(test_intelligence_step())


if __name__ == "__main__":
    exit(main())
