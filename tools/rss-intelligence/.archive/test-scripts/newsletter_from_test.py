#!/usr/bin/env python3
"""
Generate Newsletter from Test Results

Runs the working test and uses the results to generate newsletter
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from test_intelligence_minimal import test_intelligence_analysis, IntelligenceInsights
from agno.agent import Agent
from agno.models.ollama import Ollama


async def generate_newsletter():
    """Generate newsletter from intelligence analysis"""

    print("=" * 80)
    print("Intelligence-Enhanced Newsletter Generation")
    print("=" * 80)
    print()

    # First, analyze knowledge graph (reusing test code)
    from test_intelligence_minimal import IntelligenceInsights
    from agno.tools.mcp import MCPTools
    from agno.agent import Agent
    from agno.models.ollama import Ollama

    # Initialize Graphiti MCP tools
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=60,
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()

        # Create intelligence agent
        intelligence_agent = Agent(
            name="Knowledge Graph Intelligence Analyst",
            model=Ollama(
                id="glm-4.6:cloud",
                options={"num_ctx": 198000}
            ),
            parser_model=Ollama(id="gpt-oss:120b-cloud"),
            tools=[graphiti_mcp],
            output_schema=IntelligenceInsights,
            instructions="""
            You are an intelligence analyst querying a knowledge graph.

            WORKFLOW:
            1. ENTITY FREQUENCY ANALYSIS:
               - Use search_nodes to find all entities in rss-intelligence group
               - Count how many episodes each entity appears in (check entity summaries)
               - Identify top 10 most mentioned entities
               - Estimate trends based on entity creation timestamps

            2. RELATIONSHIP NETWORK ANALYSIS:
               - For the top 5 entities by frequency:
                 * Use search_memory_facts with center_node_uuid to get their UUID first
                 * Then use that UUID to find connected facts
                 * Count total connections
                 * Identify relationship types from fact names
                 * List key connected entity names

            3. TEMPORAL TREND DETECTION:
               - Compare entity created_at timestamps
               - Identify: New entities (created today), Recurring (multiple references in summary)
               - Note: Full historical comparison limited on early runs

            4. AGGREGATE STATISTICS:
               - Count total entities returned by search_nodes
               - Count total facts returned across all searches
               - Record current timestamp

            CRITICAL: You MUST return JSON with EXACT field names matching the schema:

            {
              "trending_entities": [
                {
                  "name": "Entity Name",
                  "entity_type": "person|organization|location|event",
                  "mention_count": 5,
                  "change_percent": null
                }
              ],
              "key_networks": [
                {
                  "entity_name": "Central Entity",
                  "connection_count": 10,
                  "relationship_types": ["type1", "type2"],
                  "key_connections": ["entity1", "entity2"]
                }
              ],
              "emerging_topics": ["topic1", "topic2"],
              "recurring_topics": ["topic3", "topic4"],
              "analysis_timestamp": "2025-11-13T16:00:00",
              "total_entities": 20,
              "total_facts": 50
            }

            FIELD NAMES ARE CRITICAL:
            - Use "name" NOT "entity"
            - Use "entity_type" NOT "type"
            - Use "mention_count" NOT "mentions"
            - Use "entity_name" NOT "entity"
            - Use "connection_count" NOT "connections"
            """,
            markdown=False,
        )

        print("🧠 Analyzing knowledge graph...\n")

        result = await intelligence_agent.arun(
            "Analyze the rss-intelligence knowledge graph and provide comprehensive intelligence insights"
        )

        insights: IntelligenceInsights = result.content

        print(f"\n✅ Intelligence analysis complete")
        print(f"📊 Total Entities: {insights.total_entities}")
        print(f"🔗 Total Facts: {insights.total_facts}")
        print(f"📈 Trending Entities: {len(insights.trending_entities)}")
        print()

        # Now generate newsletter from insights
        print("=" * 80)
        print("Generating Newsletter")
        print("=" * 80)
        print()

        # Build context
        context = f"""Intelligence Brief for {datetime.now().strftime('%Y-%m-%d')}

KNOWLEDGE GRAPH ANALYSIS:

Total Entities: {insights.total_entities}
Total Facts/Relationships: {insights.total_facts}
Analysis Timestamp: {insights.analysis_timestamp}

TRENDING ENTITIES (Top {len(insights.trending_entities)}):
{chr(10).join([
    f"{i+1}. {e.name} ({e.entity_type}): {e.mention_count} mentions" +
    (f" ({e.change_percent:+.0f}%)" if e.change_percent else " (new)")
    for i, e in enumerate(insights.trending_entities)
])}

KEY RELATIONSHIP NETWORKS (Top {len(insights.key_networks)}):
{chr(10).join([
    f"\n{n.entity_name}:\n" +
    f"  - {n.connection_count} total connections\n" +
    f"  - Relationship types: {', '.join(n.relationship_types)}\n" +
    f"  - Key connections: {', '.join(n.key_connections)}"
    for n in insights.key_networks
])}

EMERGING TOPICS:
{', '.join(insights.emerging_topics) if insights.emerging_topics else 'None'}

RECURRING TOPICS:
{', '.join(insights.recurring_topics) if insights.recurring_topics else 'None'}

Create an intelligence brief that:
1. Synthesizes patterns across entities and relationships
2. Highlights unexpected or significant connections
3. Explains why certain entities/topics are trending
4. Provides strategic context from the relationship networks
5. Identifies implications that wouldn't be obvious from individual articles
"""

        # Generate newsletter
        newsletter_agent = Agent(
            name="Newsletter Generator",
            model=Ollama(id="deepseek-v3.1:671b-cloud"),
            instructions="""
            You are an intelligence analyst creating a daily intelligence brief.

            Structure:
            1. **Title**: "Daily Intelligence Brief - [DATE]"

            2. **Executive Summary** (3-4 paragraphs):
               - Synthesize most important patterns from knowledge graph
               - Highlight connections between entities
               - Provide strategic context and implications

            3. **Intelligence Insights**:

               ### Trending Entities
               - List top entities with counts and analysis
               - Explain WHY they're trending based on relationship context

               ### Key Relationship Networks
               - Describe major relationship clusters
               - Explain significance of specific connections
               - Highlight unexpected links

               ### Topic Analysis
               - Emerging topics (new patterns)
               - Recurring topics (persistent themes)
               - What this tells us strategically

            4. **Strategic Assessment**:
               - What do these patterns reveal?
               - What should we watch?
               - Any surprises or anomalies?

            CRITICAL: Focus on CONNECTIONS and PATTERNS that wouldn't be obvious
            from individual articles. This is intelligence analysis, not news summary.
            """,
            markdown=True,
        )

        result = newsletter_agent.run(context)
        newsletter_content = result.content

        # Save newsletter
        newsletters_dir = Path("newsletters")
        newsletters_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        newsletter_file = newsletters_dir / f"newsletter_intelligence_{timestamp}.md"

        with open(newsletter_file, "w") as f:
            f.write(newsletter_content)

        print(f"✅ Newsletter saved: {newsletter_file}\n")
        print("=" * 80)
        print(newsletter_content)
        print("=" * 80)

        return 0


def main():
    return asyncio.run(generate_newsletter())


if __name__ == "__main__":
    exit(main())
