#!/usr/bin/env python3
"""
Minimal Intelligence Step Test

Tests ONLY the intelligence analysis step without importing the full workflow.
This avoids unnecessary dependencies like newspaper4k.
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
from typing import List
from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools


# Pydantic models (copied from workflow)
class EntityTrend(BaseModel):
    """Entity with frequency and trend data"""
    name: str = Field(..., description="Entity name")
    entity_type: str = Field(..., description="Type of entity")
    mention_count: int = Field(..., description="Number of episodes mentioning this entity")
    change_percent: float | None = Field(None, description="Percent change vs previous period")


class RelationshipNetwork(BaseModel):
    """Relationship network around a central entity"""
    entity_name: str = Field(..., description="Central entity name")
    connection_count: int = Field(..., description="Number of connected entities")
    relationship_types: List[str] = Field(..., description="Types of relationships")
    key_connections: List[str] = Field(..., description="Names of key connected entities")


class IntelligenceInsights(BaseModel):
    """Structured intelligence analysis from knowledge graph"""
    trending_entities: List[EntityTrend] = Field(default_factory=list)
    key_networks: List[RelationshipNetwork] = Field(default_factory=list)
    emerging_topics: List[str] = Field(default_factory=list)
    recurring_topics: List[str] = Field(default_factory=list)
    analysis_timestamp: str = Field(...)
    total_entities: int = Field(...)
    total_facts: int = Field(...)


async def test_intelligence_analysis():
    """Test intelligence analysis directly"""

    print("=" * 80)
    print("Testing Intelligence Analysis Step")
    print("=" * 80)
    print()

    # Initialize Graphiti MCP tools
    print("🔧 Initializing Graphiti MCP tools...")
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=60,
    )

    # CRITICAL: Use async context manager
    async with graphiti_mcp:
        await graphiti_mcp.initialize()

        print(f"✓ MCP tools initialized")
        print(f"  Available: {list(graphiti_mcp.functions.keys())}\n")

        # Create intelligence agent with structured output
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

        print("🧠 Analyzing knowledge graph...")
        print()

        prompt = """Analyze the rss-intelligence knowledge graph to extract intelligence insights.

Query for:
1. All entities (use search_nodes with group_ids=["rss-intelligence"])
2. Entity frequency analysis (from entity summaries/descriptions)
3. Relationship networks (use search_memory_facts for top entities)
4. Temporal patterns (new vs recurring entities)
5. Aggregate statistics (total counts)

Return structured IntelligenceInsights with all required fields populated."""

        result = await intelligence_agent.arun(prompt)

        insights: IntelligenceInsights = result.content

        print("\n" + "=" * 80)
        print("Results")
        print("=" * 80)
        print()

        # Display results
        print(f"✅ Analysis Complete")
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
        print("✅ Intelligence analysis test completed successfully!")
        print("=" * 80)

        return 0


def main():
    """Run async test"""
    return asyncio.run(test_intelligence_analysis())


if __name__ == "__main__":
    exit(main())
