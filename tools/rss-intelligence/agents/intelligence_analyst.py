"""
Phase 1 Enhanced Intelligence Analyst Agent

This agent performs multi-horizon intelligence analysis on the RSS knowledge graph,
including breaking news detection (6h), rising patterns (24-72h), structural importance,
and enhanced metrics (velocity, cascade potential, compound crisis alerts).

Recent Changes:
- 2025-11-14: Added BREAKING NEWS DETECTION (Last 6 Hours) to fix missing breaking news section
"""

from agno.agent import Agent
from agno.models.ollama import Ollama

# Intelligence analyst instructions with Phase 1 enhancements
INSTRUCTIONS = """
=== ANALYSIS SCOPE ===

You will analyze approximately 10 HIGH-FREQUENCY entities only.
This focused approach ensures analysis stays within token limits
while capturing the most significant patterns in recent news.

=== CORE WORKFLOW ===

1. EPISODE AND ENTITY ANALYSIS:
   - First use get_episodes(group_ids=['rss-intelligence'], max_episodes=15) to see ALL recent stories
   - Then use search_nodes(group_ids=['rss-intelligence'], max_nodes=20) to get entities
   - Focus on extracting topics FROM THE EPISODES, not just generic entity names
   - Analyze BOTH the episode titles/content AND the extracted entities

2. ANOMALY DETECTION:
   For the top 10 entities:
   - Calculate baseline: mean = sum(mention_counts) / 10
   - Calculate std_dev = sqrt(sum((count - mean)^2) / 10)
   - Compute z-score for each entity: (entity_count - mean) / std_dev
   - Flag entities with z-score > 3.0 as anomalies
   - Severity: z > 5 = HIGH, z > 3 = MEDIUM

3. BREAKING NEWS DETECTION (Last 6 Hours):
   For each top entity:
   a) Get facts: search_memory_facts(entity_name, max_facts=15)
   b) Extract created_at timestamps from facts
   c) Filter facts created in last 6 hours
   d) Count facts in last 6h window
   e) If entity has facts in last 6h:
      - Entity is "breaking"
      - List most recent fact and its significance
      - Note velocity spike (if 6h count is unusually high)

4. TEMPORAL VELOCITY (Simplified):
   For each top entity:
   a) Get facts: search_memory_facts(entity_name, max_facts=15)
   b) Extract created_at timestamps from facts
   c) Calculate simple 24h comparison:
      - Last 24 hours: count facts created in last 24h
      - Previous 24 hours: count facts from 24-48h ago
   d) Calculate velocity:
      - velocity = (last_24h / previous_24h) if previous_24h > 0 else "NEW"
   e) Simple classification:
      - "increasing" if velocity > 1.2
      - "stable" if velocity 0.8-1.2
      - "decreasing" if velocity < 0.8
      - "new" if no historical data

5. RELATIONSHIP NETWORK ANALYSIS:
   For top 5 entities by frequency:
   - Use search_memory_facts(entity_name, max_facts=15)
   - Count total unique entities mentioned in facts
   - List relationship types from fact names
   - List key connected entity names

6. NETWORK METRICS (Simplified):
   For each entity with connections:
   - centrality_score = connection_count / max_connections_in_top10
   - Entities with 5+ connections = bridge entities

7. CASCADE POTENTIAL (Simplified):
   For top entities by centrality:
   - Count primary connections only (no secondary)
   - cascade_score = primary_connections / max_connections
   - Risk: score > 0.7 = HIGH, 0.4-0.7 = MODERATE, < 0.4 = LOW

8. TEMPORAL TRENDS:
   - New entities: first appearance in knowledge graph
   - Recurring: 3+ mentions across different time periods

9. STATISTICS:
   - Total entities analyzed: 10
   - Total facts reviewed: sum across all entities
   - Timestamp: current ISO time

=== OUTPUT FORMAT ===

Provide concise markdown intelligence report:

# Intelligence Brief - [Date]

## Summary
- Stories in Knowledge Graph: [total episodes]
- Entities Analyzed: 10 (top frequency)
- Facts Reviewed: [total]
- Timestamp: [ISO]

## ALL STORIES (Recent Episodes)

List all episodes from get_episodes, organized by topic category:

**International Conflicts:**
- [Episode title with key details]

**Politics & Governance:**
- [Episode title with key details]

**Economy & Business:**
- [Episode title with key details]

**Technology:**
- [Episode title with key details]

**Other:**
- [Episode title with key details]

## BREAKING (Last 6 Hours)

Entities with facts created in the last 6 hours:

1. **[Entity]** ([type]): [N] facts in last 6h
   - Most recent: [fact description from last 6h]
   - Significance: [why this matters right now]
   - Velocity: [If unusually high activity, note it]

2. [Continue for all entities with 6h activity]

**If no entities have facts in last 6h:** "No breaking developments in last 6 hours. See Rising Patterns for emerging trends."

## RISING PATTERNS (24-72H)

Entities showing momentum over last 24-72 hours:

1. **[Entity]** ([type]): [mentions] mentions, velocity=[increasing/stable/decreasing/new]
   - Pattern: [brief description of what's happening]
   - 24h activity: [last_24h] facts (vs [prev_24h] previously)
   - Key connections: [list top 3 connected entities]

2. [Continue for top 5 by momentum]

## STRUCTURAL IMPORTANCE

Highest centrality entities (network hubs):

1. **[Entity]**: centrality=[0.XX], connections=[N], role=[hub/bridge]
   - Strategic position: [why this entity matters]
   - Key connections: [list]

2. [Continue for entities with centrality > 0.5]

## HIDDEN SIGNALS

Statistical anomalies and unusual patterns:

1. **[Entity]**: z-score=[X.XX], anomaly_type=[HIGH/MEDIUM]
   - What's unusual: [description]
   - Why it matters: [implications]

2. [Continue for entities with z-score > 3.0]

## ENHANCED INTELLIGENCE

### Velocity Analysis
Top entities by 24h momentum:
1. [Entity]: [last_24h] facts vs [prev_24h] = [X.XX]x velocity, status=[increasing/stable/decreasing]

### Cascade Potential
Entities with highest ripple risk:
1. [Entity]: cascade_score=[0.XX], risk=[HIGH/MODERATE/LOW]
   - Primary connections: [N] entities
   - Impact: Could directly affect [N] entities

### Network Positions
Key network roles:
1. [Entity]: [connections] connections, centrality=[0.XX], bridge=[Yes/No]

## COMPOUND CRISIS ALERTS

For entities with both high velocity AND high cascade:

**[ALERT_LEVEL]**: [Entity]
- Velocity: [description] - [N] facts in 24h
- Cascade: [N] direct connections, risk=[HIGH/MOD/LOW]
- Rationale: [Fast-moving + well-connected = compound risk]
- Top cascade paths:
  * [Entity A] → [Entity B] ([relationship])
  * [Entity C] → [Entity D] ([relationship])
  * [Entity E] → [Entity F] ([relationship])

Alert levels: EXTREME (both velocity > 1.5x AND cascade > 0.7), HIGH (one metric extreme), MONITOR (elevated but not extreme)

## Emerging/Recurring Topics
- Emerging (new this cycle): [list]
- Recurring (3+ periods): [list]

---

IMPORTANT NOTES:
- Use ACTUAL data from MCP tools, not estimates
- All timestamps from created_at fields
- Focus on top 10 entities only - this is deliberate scoping
- Keep analysis concise and actionable
"""


def create_intelligence_analyst(graphiti_mcp):
    """
    Create Phase 1 Enhanced Intelligence Analyst agent.

    This agent analyzes the RSS knowledge graph with focus on:
    - Breaking news detection (last 6 hours)
    - Rising patterns (24-72 hours)
    - Structural importance (network hubs)
    - Enhanced intelligence (velocity, cascade, crisis alerts)

    Args:
        graphiti_mcp: Graphiti MCP tool instance for knowledge graph access

    Returns:
        Agent: Configured intelligence analyst agent

    Model Configuration:
        - Model: GLM-4.6 cloud (198K context, 16K max output)
        - Context: 196K tokens (99% utilization with 2K safety buffer)
        - Output: 15K tokens (safe limit under 16K max)
        - Retries: 3 with exponential backoff
        - Delay: 90s between retries (handles 60s Ollama timeout)
    """
    return Agent(
        name="Phase 1 Enhanced Intelligence Analyst",
        model=Ollama(id="glm-4.6:cloud"),  # Use default options
        tools=[graphiti_mcp],
        instructions=INSTRUCTIONS,
        exponential_backoff=True,
        retries=3,
        delay_between_retries=90,  # 90s to overcome 60s Ollama timeout
        markdown=False,
    )
