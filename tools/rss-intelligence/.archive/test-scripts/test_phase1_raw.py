#!/usr/bin/env python3
"""
Test Phase 1 Intelligence - Raw Output (No Pydantic Validation)

Gets raw intelligence analysis without structured output schema
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama


async def test_phase1_intelligence():
    """Test Phase 1 intelligence with raw output"""

    print("=" * 80)
    print("Phase 1 Intelligence Analysis - Raw Output")
    print("=" * 80)
    print()

    # Initialize Graphiti MCP tools
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=60,
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()

        # Create Phase 1 intelligence agent
        intelligence_agent = Agent(
            name="Phase 1 Enhanced Intelligence Analyst",
            model=Ollama(
                id="glm-4.6:cloud",
                options={"num_ctx": 198000}
            ),
            tools=[graphiti_mcp],
            instructions="""
            You are a Phase 1 Enhanced Intelligence Analyst with advanced capabilities:
            - Anomaly Detection (z-score outlier identification)
            - Temporal Velocity Analysis (rate of change tracking)
            - Network Graph Metrics (centrality, communities)

            === CORE WORKFLOW ===

            1. ENTITY FREQUENCY ANALYSIS:
               - Use search_nodes to find all entities in rss-intelligence group
               - Count how many episodes each entity appears in (check entity summaries)
               - Identify top 10 most mentioned entities

            2. PHASE 1: ANOMALY DETECTION:
               For the top 10 entities:
               - Calculate baseline: mean = sum(mention_counts) / count
               - Calculate std_dev = sqrt(sum((count - mean)^2) / count)
               - Compute z-score for each entity: (entity_count - mean) / std_dev
               - Flag entities with z-score > 3.0 as anomalies
               - Severity: z > 5 = HIGH, z > 3 = MEDIUM

            3. PHASE 1: TEMPORAL VELOCITY:
               - Look at entity created_at timestamps
               - Entities created recently (today) = high velocity
               - Entities with multiple references in summary = burst state
               - Identify top 5 by velocity

            4. RELATIONSHIP NETWORK ANALYSIS:
               - For top 5 entities by frequency:
                 * Use search_memory_facts with entity name as query
                 * Count total connections from results
                 * List relationship types from fact names
                 * List key connected entity names

            5. PHASE 1: NETWORK METRICS (Simplified):
               For each entity with connections:
               - Estimate centrality_score = connection_count / max_connections
               - Normalize to 0-1 range
               - Entities with 5+ connections = bridge entities
               - Flag entities where connection_count > 2x average = centrality jumps

            6. TEMPORAL TREND DETECTION:
               - New entities: created today
               - Recurring: multiple references in summaries

            7. AGGREGATE STATISTICS:
               - Count total entities
               - Count total facts from all searches
               - Record timestamp

            === OUTPUT FORMAT ===

            Provide a comprehensive markdown report with:

            # Phase 1 Intelligence Analysis

            ## Summary Statistics
            - Total Entities: [count]
            - Total Facts: [count]
            - Analysis Timestamp: [ISO timestamp]

            ## Top 10 Trending Entities

            For each entity:
            1. **[Entity Name]** ([type])
               - Mentions: [count]
               - Z-Score: [score] [🚨 ANOMALY if > 3.0]
               - Velocity: [HIGH/MEDIUM/LOW]
               - Is Burst: [Yes/No]
               - Centrality Score: [0-1 if available]

            ## Anomaly Alerts

            For entities with z-score > 3.0:
            - **[Entity]**: Z-score [score], Severity [HIGH/MEDIUM]
              - Description: [why this is anomalous]

            ## Velocity Leaders (Top 5)

            Entities with highest rate of change

            ## Key Relationship Networks

            For top 5 entities:
            - **[Entity Name]**:
              - Total Connections: [count]
              - Centrality Score: [0-1]
              - Is Bridge Entity: [Yes/No]
              - Relationship Types: [list]
              - Key Connections: [entity names]

            ## Centrality Jumps

            Entities with connection_count > 2x average

            ## Emerging vs Recurring Topics

            - Emerging: [topics appearing for first time]
            - Recurring: [topics with historical presence]
            """,
            markdown=True,
        )

        print("🧠 Running Phase 1 intelligence analysis...\\n")

        result = await intelligence_agent.arun(
            "Analyze the rss-intelligence knowledge graph with Phase 1 enhancements: "
            "anomaly detection, temporal velocity, and network metrics"
        )

        analysis = result.content

        print("=" * 80)
        print(analysis)
        print("=" * 80)

        # Save analysis
        output_dir = Path("phase1_analysis")
        output_dir.mkdir(exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"phase1_analysis_{timestamp}.md"

        with open(output_file, "w") as f:
            f.write(analysis)

        print(f"\\n✅ Analysis saved: {output_file}")

        return 0


def main():
    try:
        return asyncio.run(test_phase1_intelligence())
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
