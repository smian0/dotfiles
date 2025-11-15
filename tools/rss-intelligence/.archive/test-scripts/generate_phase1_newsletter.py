#!/usr/bin/env python3
"""
Generate Phase 1 Enhanced Newsletter

Uses Phase 1 intelligence analysis to generate comprehensive newsletter
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama


async def generate_phase1_newsletter():
    """Generate newsletter from Phase 1 intelligence analysis"""

    print("=" * 80)
    print("Phase 1 Enhanced Newsletter Generation")
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

        # Step 1: Run Phase 1 intelligence analysis
        print("🧠 Step 1: Running Phase 1 intelligence analysis...\n")

        intelligence_agent = Agent(
            name="Phase 1 Enhanced Intelligence Analyst",
            model=Ollama(
                id="glm-4.6:cloud",
                options={"num_ctx": 198000}
            ),
            tools=[graphiti_mcp],
            add_datetime_to_context=True,  # Inject today's date
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

            Provide a structured data summary (NOT markdown):

            SUMMARY:
            Total Entities: [count]
            Total Facts: [count]
            Timestamp: [ISO]

            TOP 10 ENTITIES:
            1. [Name] ([type]): [mentions] mentions, z-score [X.XX], velocity [HIGH/MED/LOW], burst [Yes/No], centrality [0.XX]
            2. ...

            ANOMALIES:
            - [Entity]: z=[X.XX], severity [HIGH/MED], reason: [description]

            VELOCITY LEADERS:
            1. [Entity] - [reason]
            2. ...

            KEY NETWORKS:
            [Entity]: [connections] connections, centrality [0.XX], bridge [Yes/No]
            Types: [list]
            Connected to: [entities]

            CENTRALITY JUMPS:
            - [Entity]: [connections] connections (>[2x] average)

            EMERGING/RECURRING:
            Emerging: [list]
            Recurring: [list]
            """,
            markdown=False,
        )

        result = await intelligence_agent.arun(
            "Analyze the rss-intelligence knowledge graph with Phase 1 enhancements"
        )

        intelligence_summary = result.content

        print("✅ Intelligence analysis complete\n")
        print("=" * 80)
        print("Intelligence Summary:")
        print("=" * 80)
        print(intelligence_summary[:1000] + "...\n")

        # Step 2: Generate newsletter from intelligence
        print("=" * 80)
        print("🖊️  Step 2: Generating Phase 1 Enhanced Newsletter...")
        print("=" * 80)
        print()

        newsletter_context = f"""Phase 1 Enhanced Intelligence Analysis for {datetime.now().strftime('%Y-%m-%d')}

{intelligence_summary}

Create a daily intelligence brief that showcases Phase 1 intelligence capabilities:

1. Executive Summary highlighting:
   - Anomaly alerts (entities with z-score > 3.0)
   - Velocity leaders and burst patterns
   - Centrality jumps indicating structural shifts
   - Strategic significance

2. Phase 1 Intelligence Insights:

   ### Anomaly Detection 🚨
   - List all detected anomalies with z-scores and severity
   - Explain WHY each is anomalous (not just that it is)
   - Strategic implications of anomalous patterns

   ### Temporal Velocity Analysis 🚀
   - Velocity leaders with HIGH/MEDIUM/LOW classification
   - Burst entities (Kleinberg burst detection)
   - Rate of change insights
   - What velocity patterns reveal about trends

   ### Network Graph Metrics 🌐
   - Top entities by centrality score
   - Bridge entities connecting different domains
   - Centrality jumps (entities gaining structural importance)
   - Community patterns and clusters

   ### Key Relationship Networks 🔗
   - Densest networks with connection counts
   - Relationship types revealing narrative structure
   - Cross-domain connections
   - Network evolution patterns

3. Strategic Assessment:
   - What do Phase 1 metrics reveal that raw counts don't?
   - Anomaly + velocity + centrality convergence
   - Early warning signals from combined metrics
   - Structural vs temporal patterns

4. Intelligence Value Demonstration:
   - Show how anomaly detection caught what would be missed
   - Explain velocity insights vs static frequency
   - Demonstrate centrality revealing hidden importance
   - Cross-reference all three metric types for validation

CRITICAL: This is a Phase 1 enhanced intelligence brief, not a news summary.
Focus on what the METRICS reveal, not just what happened.
"""

        newsletter_agent = Agent(
            name="Phase 1 Newsletter Generator",
            model=Ollama(id="deepseek-v3.1:671b-cloud"),
            add_datetime_to_context=True,  # Inject today's date
            instructions="""
            You are an intelligence analyst creating Phase 1 enhanced daily intelligence briefs.

            Structure:
            1. **Title**: "Phase 1 Enhanced Intelligence Brief - [DATE]"

            2. **Executive Summary** (4-5 paragraphs):
               - Lead with anomaly alerts (z-score > 3.0)
               - Highlight velocity leaders and burst patterns
               - Note centrality jumps indicating structural shifts
               - Synthesize what Phase 1 metrics reveal together
               - Strategic significance and implications

            3. **Phase 1 Intelligence Metrics**:

               ### 🚨 Anomaly Detection
               For each anomaly (z-score > 3.0):
               - Entity name and z-score
               - Severity level
               - WHY it's anomalous (statistical context)
               - Strategic implications
               - What raw frequency counts would miss

               ### 🚀 Temporal Velocity Analysis
               - Velocity leaders with classifications
               - Burst entities (Kleinberg detection)
               - Rate of change insights
               - Velocity vs frequency comparison
               - What velocity patterns reveal about momentum

               ### 🌐 Network Graph Metrics
               - Top entities by centrality score (0-1)
               - Bridge entities connecting domains
               - Centrality jumps (>2x average connections)
               - Why centrality ≠ frequency
               - Structural importance insights

               ### 🔗 Key Relationship Networks
               - Densest networks with metrics
               - Connection counts and types
               - Cross-domain links
               - Network topology insights
               - Relationship type analysis

            4. **Phase 1 Metric Convergence**:
               - Entities strong in ALL metrics (anomaly + velocity + centrality)
               - Entities strong in ONE metric (what that reveals)
               - Divergence patterns (high frequency, low centrality = isolated events)
               - Convergence patterns (anomaly + velocity + centrality = critical focus)

            5. **Strategic Assessment**:
               - What Phase 1 metrics reveal that raw counts don't
               - Early warning signals from combined metrics
               - Anomalous patterns requiring attention
               - Velocity trends indicating momentum
               - Structural shifts from centrality changes

            6. **Intelligence Value**:
               - Demonstrate anomaly detection catching outliers
               - Show velocity revealing momentum raw counts miss
               - Explain centrality identifying hidden importance
               - Prove Phase 1 > simple frequency analysis

            CRITICAL: Focus on what METRICS reveal, not just events.
            This is intelligence analysis using Phase 1 enhancements.
            """,
            markdown=True,
        )

        result = newsletter_agent.run(newsletter_context)
        newsletter_content = result.content

        # Save newsletter
        newsletters_dir = Path("newsletters")
        newsletters_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        newsletter_file = newsletters_dir / f"newsletter_phase1_{timestamp}.md"

        with open(newsletter_file, "w") as f:
            f.write(newsletter_content)

        print(f"\n✅ Newsletter saved: {newsletter_file}\n")
        print("=" * 80)
        print(newsletter_content)
        print("=" * 80)

        return 0


def main():
    try:
        return asyncio.run(generate_phase1_newsletter())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
