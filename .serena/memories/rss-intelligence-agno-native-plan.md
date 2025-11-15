# RSS Intelligence System - Agno-Native Implementation Plan

## Critical Correction: Anti-Patterns Identified

### ❌ Original Plan Problems

**Problem 1: Subprocess Anti-Pattern**
```python
# WRONG - Not Agno-native
subprocess.run(["python3", "graphiti_intelligence.py"])
```
- Breaks workflow paradigm
- Loses Agno debug mode, state management
- Can't use workflow features (show_step_details, show_time)
- Brittle error handling

**Problem 2: Missing Structured Output**
```python
# WRONG - Free text parsing
agent = Agent(instructions="Output JSON...")
result = json.loads(result.content)  # Brittle, no validation
```
- No type safety
- No Pydantic validation
- Manual JSON parsing errors

### ✅ Agno-Native Solution

**Correct Pattern: Intelligence as Workflow Step**
```python
# RIGHT - Agno-native workflow step
Step(
    name="analyze_knowledge_graph",
    executor=intelligence_executor_with_async_mcp,
    description="Query knowledge graph for intelligence insights",
)
```

**Correct Pattern: Structured Output with Pydantic**
```python
# RIGHT - Type-safe, validated output
agent = Agent(
    model=Ollama(id="glm-4.6:cloud"),           # Tool calling
    parser_model=Ollama(id="gpt-oss:120b-cloud"), # JSON parsing
    output_schema=IntelligenceInsights,  # Pydantic validation
)
```

---

## Architecture: Intelligence as Workflow Step

### Workflow Structure

```
rss_intelligence_workflow.py (11 steps):
  1. Fetch RSS feeds
  2. Prepare URLs
  3. Extract content
  4. Merge content
  5. Format for analysis
  6. Parallel analysis (entities, sentiment, topics)
  7. Prepare Graphiti episodes
  8. [Ingest to Graphiti - external async script]
  9. Analyze knowledge graph ← NEW STEP (Agno-native)
  10. Generate newsletter (now uses intelligence insights)
  11. Save to file
```

### Why Step 8 is External but Step 9 is Internal?

**Step 8 (Graphiti Ingestion):**
- ✅ External async script is CORRECT
- Reason: Background batch processing, no workflow output needed
- Pattern: Fire-and-forget, archives episodes file

**Step 9 (Intelligence Analysis):**
- ✅ Internal workflow step is CORRECT
- Reason: Produces structured output for newsletter generation
- Pattern: Query → structured insights → pass to next step

---

## Implementation: Agno-Native Intelligence Step

### 1. Define Pydantic Models

```python
# In rss_intelligence_workflow.py

from pydantic import BaseModel, Field
from typing import List

class EntityTrend(BaseModel):
    """Entity with frequency and trend data"""
    name: str = Field(..., description="Entity name")
    mention_count: int = Field(..., description="Number of episodes mentioning this entity")
    change_percent: float | None = Field(None, description="Percent change vs previous period (null if first appearance)")
    entity_type: str = Field(..., description="Type of entity (person, organization, location, etc.)")

class RelationshipNetwork(BaseModel):
    """Relationship network around a central entity"""
    entity_name: str = Field(..., description="Central entity name")
    connection_count: int = Field(..., description="Number of connected entities")
    relationship_types: List[str] = Field(..., description="Types of relationships (e.g., DENIES_MEETING, PHOTOGRAPHED_WITH)")
    key_connections: List[str] = Field(..., description="Names of key connected entities")

class IntelligenceInsights(BaseModel):
    """Structured intelligence analysis from knowledge graph"""
    trending_entities: List[EntityTrend] = Field(
        ..., 
        description="Top 10 entities by mention frequency with trend data"
    )
    key_networks: List[RelationshipNetwork] = Field(
        ..., 
        description="Relationship networks for top 5 entities"
    )
    emerging_topics: List[str] = Field(
        ..., 
        description="Topics/entities that appeared for the first time this cycle"
    )
    recurring_topics: List[str] = Field(
        ..., 
        description="Topics/entities that appear consistently over multiple cycles"
    )
    analysis_timestamp: str = Field(
        ..., 
        description="ISO timestamp of when this analysis was performed"
    )
    total_entities: int = Field(..., description="Total number of entities in knowledge graph")
    total_facts: int = Field(..., description="Total number of facts (relationships) in knowledge graph")
```

### 2. Create Intelligence Step with Async MCP

```python
# In rss_intelligence_workflow.py

from agno.workflow.step import Step
from agno.workflow.types import StepInput, StepOutput
from agno.tools.mcp import MCPTools
from datetime import datetime

def create_intelligence_step() -> Step:
    """
    Create knowledge graph intelligence analysis step.
    
    Uses async MCP tools within a synchronous workflow step.
    Follows pattern from agno-workflow-builder/examples/agno_mcp_structured.py
    """
    
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
                parser_model=Ollama(id="gpt-oss:120b-cloud"),  # Dedicated parser
                tools=[graphiti_mcp],
                output_schema=IntelligenceInsights,
                instructions="""
                You are an intelligence analyst querying a knowledge graph.
                
                WORKFLOW:
                1. ENTITY FREQUENCY ANALYSIS:
                   - Use search_nodes to find all entities in rss-intelligence group
                   - Count how many episodes each entity appears in
                   - Identify top 10 most mentioned entities
                   - Calculate trends (if historical data exists)
                
                2. RELATIONSHIP NETWORK ANALYSIS:
                   - For the top 5 entities by frequency:
                     * Use search_memory_facts with center_node_uuid
                     * Count total connections
                     * Identify relationship types
                     * List key connected entities
                
                3. TEMPORAL TREND DETECTION:
                   - Compare current entities vs historical patterns
                   - Identify: New (first appearance), Recurring (3+ appearances)
                   - Note: May be limited on first run (no historical baseline)
                
                4. AGGREGATE STATISTICS:
                   - Total entities in graph
                   - Total facts (relationships)
                   - Analysis timestamp
                
                Output structured IntelligenceInsights JSON.
                Be specific with numbers and entity names.
                ALWAYS use the MCP tools - never answer from memory.
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
                    content=insights,  # Pydantic model, type-safe
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
        """Synchronous wrapper that runs async executor"""
        import asyncio
        return asyncio.run(async_intelligence_executor(step_input))
    
    return Step(
        name="analyze_knowledge_graph",
        executor=sync_wrapper,
        description="Query Graphiti knowledge graph for intelligence insights using MCP tools",
    )
```

### 3. Integrate Intelligence Step into Workflow

```python
# In create_rss_workflow():

def create_rss_workflow() -> Workflow:
    """Create RSS intelligence workflow with knowledge graph analysis"""
    
    # ... existing agents and steps 1-7 ...
    
    # Step 8: Intelligence Analysis (NEW)
    intelligence_step = create_intelligence_step()
    
    # Step 9: Prepare newsletter context (was Step 8)
    # ... existing code ...
    
    # Step 10: Generate newsletter (was Step 9)
    # Update newsletter agent to use intelligence insights
    newsletter_agent = Agent(
        name="Newsletter Writer",
        model=Ollama(id="qwen3-coder:480b-cloud"),
        instructions="""
        You are an intelligence analyst creating a daily brief.
        
        INPUT DATA:
        - Intelligence insights from knowledge graph (structured analysis)
        - Article metadata with dates and sources
        
        OUTPUT FORMAT:
        
        # Daily Intelligence Brief - {date}
        
        ## Intelligence Insights
        [Use the structured intelligence data to show:]
        - **Trending Entities**: Show top entities with mention counts and trends
        - **Key Networks**: Describe relationship clusters with specific connections
        - **Emerging Topics**: Highlight new entities/topics this cycle
        - **Recurring Patterns**: Show topics appearing consistently
        
        ## Summary
        [High-level overview incorporating intelligence context]
        
        ## Top Stories
        [Existing format, but now contextualized with intelligence insights]
        
        ## Key Entities
        [Existing format]
        
        ## Themes
        [Existing format]
        
        IMPORTANT: Use the intelligence insights to provide context that 
        wouldn't be obvious from reading individual articles. Show temporal 
        trends, network connections, and emerging patterns.
        """,
        markdown=True,
    )
    
    newsletter_step = Step(
        name="generate_newsletter",
        agent=newsletter_agent,
        description="Generate newsletter incorporating intelligence insights",
    )
    
    # Step 11: Save to file (was Step 10)
    # ... existing code ...
    
    # Create workflow with intelligence step
    workflow = Workflow(
        name="RSS Intelligence with Knowledge Graph",
        steps=[
            # ... steps 1-7 (existing) ...
            intelligence_step,  # NEW - Step 8
            prepare_newsletter_context_step,  # Step 9
            newsletter_step,  # Step 10
            save_newsletter_step,  # Step 11
        ],
        debug_mode=False,  # Set to True for verbose output
    )
    
    return workflow
```

### 4. Newsletter Context Preparation (Modified)

```python
# Modify prepare_newsletter_context executor to include intelligence

def prepare_newsletter_context(step_input: StepInput) -> StepOutput:
    """Prepare newsletter context with intelligence insights"""
    
    # Get intelligence insights from previous step
    intelligence: IntelligenceInsights = step_input.get_step_content("analyze_knowledge_graph")
    
    # Get article metadata
    articles_data = step_input.get_step_content("prepare_graphiti_episodes")
    
    # Format intelligence for newsletter prompt
    intelligence_text = f"""
## Intelligence Insights from Knowledge Graph

### Entity Frequency & Trends
{chr(10).join([
    f"- **{e.name}** ({e.entity_type}): {e.mention_count} mentions" + 
    (f" ({e.change_percent:+.0f}% vs previous period)" if e.change_percent else " (new this cycle)")
    for e in intelligence.trending_entities[:10]
])}

### Relationship Networks
{chr(10).join([
    f"- **{n.entity_name}**: {n.connection_count} connections via {', '.join(n.relationship_types[:3])}"
    for n in intelligence.key_networks[:5]
])}

### Emerging Topics
{', '.join(intelligence.emerging_topics) if intelligence.emerging_topics else 'None detected'}

### Recurring Topics
{', '.join(intelligence.recurring_topics) if intelligence.recurring_topics else 'None detected'}

### Graph Statistics
- Total entities tracked: {intelligence.total_entities}
- Total relationships: {intelligence.total_facts}
- Analysis timestamp: {intelligence.analysis_timestamp}
"""
    
    # Combine with article metadata
    newsletter_context = f"""
{intelligence_text}

## Article Metadata
{articles_data}
"""
    
    return StepOutput(
        step_name="prepare_newsletter_context",
        content=newsletter_context,
        success=True,
    )
```

---

## Key Differences from Original Plan

| Aspect | Original Plan (Wrong) | Agno-Native Plan (Correct) |
|--------|----------------------|---------------------------|
| **Architecture** | Separate subprocess script | Workflow Step with async executor |
| **Output** | Free text JSON parsing | Pydantic models with validation |
| **Model Pattern** | Single model | Two-model (tool + parser) |
| **Integration** | `subprocess.run()` | `Step(executor=...)` |
| **Debug Support** | None (subprocess) | Full Agno debug mode |
| **Type Safety** | Manual parsing | Pydantic type checking |
| **Error Handling** | Brittle subprocess | Workflow error propagation |
| **State Management** | External file | Workflow state passing |

---

## Implementation Timeline

### Phase 1: Core Intelligence Step (3 hours)
1. ✅ Define Pydantic models (30 min)
   - `IntelligenceInsights`, `EntityTrend`, `RelationshipNetwork`
2. ✅ Create intelligence step with async MCP (1.5 hours)
   - Async executor with MCP context manager
   - Agent with structured output
   - Sync wrapper for workflow
3. ✅ Integrate into workflow (30 min)
   - Add intelligence step after episode preparation
   - Update step numbering
4. ✅ Modify newsletter context (30 min)
   - Format intelligence insights for prompt
   - Pass to newsletter agent

### Phase 2: Testing & Refinement (1 hour)
1. ✅ Test end-to-end with debug mode
2. ✅ Verify structured output validation
3. ✅ Check newsletter quality improvement

---

## Technical Notes

### Async MCP in Synchronous Workflow

**Challenge:** Graphiti MCP requires async context manager, but workflow steps are synchronous.

**Solution:** Async executor + sync wrapper
```python
async def async_executor(step_input):
    async with mcp_tools:
        # ... async MCP operations ...

def sync_wrapper(step_input):
    import asyncio
    return asyncio.run(async_executor(step_input))

Step(executor=sync_wrapper)
```

### Two-Model Pattern

**Why two models?**
- `glm-4.6:cloud` (192 tok/s): Excellent tool calling, fast
- `gpt-oss:120b-cloud` (parsing): Reliable JSON schema parsing

**Pattern:**
```python
Agent(
    model=Ollama(id="glm-4.6:cloud"),           # Tool invocation
    parser_model=Ollama(id="gpt-oss:120b-cloud"), # JSON parsing
    output_schema=IntelligenceInsights,
)
```

### Pydantic Model Design

**Keep flat structure:**
```python
# GOOD - Flat lists
trending_entities: List[EntityTrend]
emerging_topics: List[str]

# AVOID - Nested complex objects
network: Dict[str, List[Dict[str, List[str]]]]
```

**Why:** Parser models handle flat structures more reliably.

---

## Expected Output

### Intelligence Insights Structure (JSON)

```json
{
  "trending_entities": [
    {
      "name": "Prince Andrew",
      "mention_count": 3,
      "change_percent": 200.0,
      "entity_type": "person"
    },
    {
      "name": "Germany",
      "mention_count": 3,
      "change_percent": null,
      "entity_type": "location"
    }
  ],
  "key_networks": [
    {
      "entity_name": "Jeffrey Epstein",
      "connection_count": 4,
      "relationship_types": ["EMAIL_REFERENCED_PHOTO", "HAD_ASSOCIATE"],
      "key_connections": ["Prince Andrew", "Ghislaine Maxwell", "Virginia Giuffre"]
    }
  ],
  "emerging_topics": [
    "Germany defense policy",
    "Valve console"
  ],
  "recurring_topics": [
    "Epstein case",
    "Sudan conflict"
  ],
  "analysis_timestamp": "2025-11-13T21:30:00Z",
  "total_entities": 47,
  "total_facts": 89
}
```

### Newsletter with Intelligence Section

```markdown
# Daily Intelligence Brief - November 13, 2025

## Intelligence Insights

### Entity Frequency & Trends
- **Prince Andrew** (person): 3 mentions (+200% vs previous period)
- **Jeffrey Epstein** (person): 4 mentions (sustained high frequency)
- **Germany** (location): 3 mentions (new this cycle)

### Relationship Networks
- **Jeffrey Epstein**: 4 connections via EMAIL_REFERENCED_PHOTO, HAD_ASSOCIATE
- **Prince Andrew**: 3 connections via DENIES_MEETING, PHOTOGRAPHED_WITH

### Emerging Topics
Germany defense policy, Valve console

### Recurring Topics
Epstein case, Sudan conflict

### Graph Statistics
- Total entities tracked: 47
- Total relationships: 89
- Analysis timestamp: 2025-11-13T21:30:00Z

## Summary
[Rest of newsletter...]
```

---

## References

### Agno Patterns
- `agno-workflow-builder/examples/agno_mcp_structured.py` - MCP + structured output
- `agno-workflow-builder/references/workflow_patterns.md` - Step patterns
- `agno-workflow-builder/references/structured_outputs_guide.md` - Pydantic patterns

### Existing Code
- `rss_intelligence_workflow.py` - Main workflow (10 steps currently)
- `graphiti_ingest_async.py` - Async MCP pattern reference

---

**Last Updated:** 2025-11-13
**Status:** Agno-native plan complete, ready for implementation
**Estimated Effort:** 4 hours MVP
**Key Improvement:** Proper workflow integration vs subprocess anti-pattern
