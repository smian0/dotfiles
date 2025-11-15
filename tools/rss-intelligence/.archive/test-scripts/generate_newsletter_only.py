#!/usr/bin/env python3
"""
Generate Intelligence-Enhanced Newsletter

Runs ONLY the intelligence analysis and newsletter generation steps,
using existing Graphiti data. Skips RSS fetching entirely.
"""

import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools
from agno.workflow import Workflow
from agno.workflow.step import Step, StepInput, StepOutput


# ============================================================================
# Pydantic Models (from workflow)
# ============================================================================

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


# ============================================================================
# Intelligence Analysis Step
# ============================================================================

def create_intelligence_step() -> Step:
    """Create knowledge graph intelligence analysis step."""

    async def async_intelligence_executor(step_input: StepInput) -> StepOutput:
        """Async executor that handles MCP context manager"""

        print("\n" + "=" * 80)
        print("Knowledge Graph Intelligence Analysis")
        print("=" * 80 + "\n")

        # Initialize Graphiti MCP tools
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
                   - Count total facts returned by search_memory_facts
                   - Include current ISO timestamp

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

                ALWAYS use the MCP tools - never answer from memory.
                If no data exists yet, return empty lists but valid structure.
                """,
                markdown=False,
                exponential_backoff=True,
                retries=3,
                delay_between_retries=15,
            )

            try:
                # Execute intelligence analysis
                result = await intelligence_agent.arun(
                    "Analyze the rss-intelligence knowledge graph and provide comprehensive intelligence insights"
                )

                # result.content is IntelligenceInsights (Pydantic model)
                insights = result.content

                print("✓ Intelligence analysis complete")
                print(f"  Entities analyzed: {insights.total_entities}")
                print(f"  Facts analyzed: {insights.total_facts}")
                print(f"  Trending entities: {len(insights.trending_entities)}")
                print(f"  Key networks: {len(insights.key_networks)}")

                return StepOutput(
                    step_name="analyze_knowledge_graph",
                    content=insights,
                    success=True,
                )

            except Exception as e:
                print(f"❌ Intelligence analysis failed: {e}")
                import traceback
                traceback.print_exc()

                # Return empty insights on failure
                return StepOutput(
                    step_name="analyze_knowledge_graph",
                    content=IntelligenceInsights(
                        trending_entities=[],
                        key_networks=[],
                        emerging_topics=[],
                        recurring_topics=[],
                        analysis_timestamp=datetime.now().isoformat(),
                        total_entities=0,
                        total_facts=0,
                    ),
                    success=False,
                )

    # Wrap async executor for synchronous workflow
    def sync_wrapper(step_input: StepInput) -> StepOutput:
        return asyncio.run(async_intelligence_executor(step_input))

    return Step(
        name="analyze_knowledge_graph",
        executor=sync_wrapper,
        description="Query Graphiti knowledge graph for intelligence insights",
    )


# ============================================================================
# Newsletter Context Preparation
# ============================================================================

def prepare_newsletter_context_step(step_input: StepInput, session_state: dict) -> StepOutput:
    """Prepare comprehensive context for newsletter generation"""

    print("\n" + "=" * 80)
    print("Preparing Newsletter Context")
    print("=" * 80 + "\n")

    # Get intelligence insights from analyze_knowledge_graph step
    intelligence: IntelligenceInsights | None = step_input.get_step_content("analyze_knowledge_graph")

    if not intelligence:
        return StepOutput(content="No intelligence data available")

    # Build intelligence insights section
    intelligence_text = f"""# Intelligence Insights from Knowledge Graph

## Entity Frequency & Trends
{chr(10).join([
    f"- **{e.name}** ({e.entity_type}): {e.mention_count} mentions" +
    (f" ({e.change_percent:+.0f}% vs previous period)" if e.change_percent else " (new)")
    for e in intelligence.trending_entities[:10]
])}

## Relationship Networks
{chr(10).join([
    f"### {n.entity_name} ({n.connection_count} connections)\n" +
    f"- Relationship types: {', '.join(n.relationship_types[:5])}\n" +
    f"- Key connections: {', '.join(n.key_connections[:5])}"
    for n in intelligence.key_networks[:5]
])}

## Emerging Topics
{', '.join(intelligence.emerging_topics) if intelligence.emerging_topics else 'None identified'}

## Recurring Topics
{', '.join(intelligence.recurring_topics) if intelligence.recurring_topics else 'None identified'}

## Graph Statistics
- Total Entities: {intelligence.total_entities}
- Total Facts/Relationships: {intelligence.total_facts}
- Analysis Timestamp: {intelligence.analysis_timestamp}
"""

    context = f"""You are preparing an intelligence brief for {datetime.now().strftime('%Y-%m-%d')}.

{intelligence_text}

TASK: Create a comprehensive intelligence newsletter that:
1. Highlights trending entities and their importance
2. Explains key relationship networks and their significance
3. Identifies emerging vs recurring topics
4. Provides context that wouldn't be obvious from individual articles
5. Synthesizes patterns across the knowledge graph
"""

    print(f"✓ Newsletter context prepared")
    print(f"  Intelligence sections: 4")
    print(f"  Total entities: {intelligence.total_entities}")
    print(f"  Total facts: {intelligence.total_facts}")

    return StepOutput(content=context)


# ============================================================================
# Newsletter Generator
# ============================================================================

def create_newsletter_generator_step() -> Step:
    """Create newsletter generator agent step"""

    def newsletter_executor(step_input: StepInput) -> StepOutput:
        """Generate newsletter from context"""

        print("\n" + "=" * 80)
        print("Generating Intelligence Newsletter")
        print("=" * 80 + "\n")

        context = step_input.get_step_content("prepare_newsletter_context")

        if not context:
            return StepOutput(content="No context available for newsletter generation")

        # Create newsletter generator agent
        newsletter_generator = Agent(
            name="Newsletter Generator",
            model=Ollama(id="deepseek-v3.1:671b-cloud"),
            instructions="""
            You are an intelligence analyst creating a daily brief with knowledge graph insights.

            Structure:
            1. **Title**: "Daily Intelligence Brief - [DATE]"

            2. **Executive Summary** (3-4 paragraphs):
               - Synthesize the most important intelligence from the knowledge graph
               - Highlight connections and patterns not obvious from individual articles
               - Provide strategic context and implications

            3. **Intelligence Insights**:

               ### Trending Entities
               - List top entities with mention counts and trends
               - Explain WHY they're trending (context from relationships)

               ### Key Relationship Networks
               - Describe major relationship clusters
               - Explain significance of connections
               - Highlight unexpected or important links

               ### Emerging vs Recurring Topics
               - New topics appearing for the first time
               - Persistent topics showing patterns over time
               - Analysis of what this means

            4. **Strategic Implications**:
               - What do these patterns tell us?
               - What should we be watching?
               - Any anomalies or surprises?

            CRITICAL: Use intelligence insights to provide context that wouldn't be
            obvious from reading individual articles. Focus on CONNECTIONS, PATTERNS,
            and TRENDS across the knowledge graph.

            Make it insightful and analytical, not just a summary.
            """,
            markdown=True,
        )

        try:
            # Generate newsletter
            result = newsletter_generator.run(context)
            newsletter_content = result.content

            # Save to file
            newsletters_dir = Path("newsletters")
            newsletters_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            newsletter_file = newsletters_dir / f"newsletter_{timestamp}.md"

            with open(newsletter_file, "w") as f:
                f.write(newsletter_content)

            print(f"✓ Newsletter generated: {newsletter_file}")

            return StepOutput(content=f"Newsletter saved to: {newsletter_file}\n\n{newsletter_content}")

        except Exception as e:
            print(f"❌ Newsletter generation failed: {e}")
            import traceback
            traceback.print_exc()
            return StepOutput(content=f"Newsletter generation failed: {e}", success=False)

    return Step(
        name="generate_newsletter",
        executor=newsletter_executor,
        description="Generate intelligence-enhanced newsletter",
    )


# ============================================================================
# Main Workflow
# ============================================================================

def main():
    """Run newsletter generation workflow"""

    print("=" * 80)
    print("Intelligence-Enhanced Newsletter Generator")
    print("=" * 80)
    print()

    # Create workflow
    workflow = Workflow(
        name="Newsletter Generation Only",
        steps=[
            # Step 1: Analyze knowledge graph
            create_intelligence_step(),

            # Step 2: Prepare newsletter context
            Step(
                name="prepare_newsletter_context",
                executor=prepare_newsletter_context_step,
                description="Prepare newsletter context from intelligence",
            ),

            # Step 3: Generate newsletter
            create_newsletter_generator_step(),
        ],
    )

    # Run workflow
    result = workflow.run()

    print("\n" + "=" * 80)
    if result and result.success:
        print("✅ Newsletter generation complete!")
        print("=" * 80)
        print()
        print(result.content)
    else:
        print("❌ Newsletter generation failed!")
        print("=" * 80)

    return 0 if result and result.success else 1


if __name__ == "__main__":
    exit(main())
