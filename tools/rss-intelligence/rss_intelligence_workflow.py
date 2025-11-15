#!/usr/bin/env python3
"""
RSS Intelligence Workflow - Simplified MVP

Architecture:
- Agno-native scheduling (while True + time.sleep)
- Single-model pattern (no parser complexity)
- Newspaper4kTools for content extraction
- Free Ollama Cloud models only
- Persistent URL deduplication via JSON file (processed_urls.json)
- Parallel analysis for entity/sentiment/topic extraction
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "agno",
#     "feedparser",
#     "fastapi",
#     "newspaper4k",
#     "lxml_html_clean",
#     "ollama",
#     "mcp",
#     "sqlalchemy",
# ]
# ///

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import feedparser
from pydantic import BaseModel, Field, ConfigDict

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.mcp import MCPTools
from agno.workflow import Workflow
from agno.workflow.parallel import Parallel
from agno.workflow.step import Step, StepInput, StepOutput

# Local agent imports
from agents.intelligence_analyst import create_intelligence_analyst
from agents.newsletter_generator import create_newsletter_generator
from agents.consumer_newsletter_generator import create_consumer_newsletter_generator
from agents.content_extractor import create_content_extractor
from agents.entity_extractor import create_entity_extractor
from agents.sentiment_analyzer import create_sentiment_analyzer
from agents.topic_extractor import create_topic_extractor

# ============================================================================
# Data Models
# ============================================================================

class Article(BaseModel):
    """RSS article with metadata"""
    title: str
    url: str
    summary: str
    published: str
    content: Optional[str] = None  # Full content extracted via Newspaper4k


class ExtractedEntity(BaseModel):
    """Entity with type and context"""
    model_config = ConfigDict(populate_by_name=True)  # Allow both 'type' and 'entity_type'

    name: str
    entity_type: str = Field(alias="type")  # person, organization, location, event, concept
    context: str
    confidence: float = Field(ge=0.0, le=1.0)


class SentimentAnalysis(BaseModel):
    """Sentiment with scores"""
    overall_sentiment: str  # positive, negative, neutral
    confidence: float = Field(ge=0.0, le=1.0)
    key_emotions: List[str] = Field(default_factory=list)


class TopicClassification(BaseModel):
    """Topic with relevance"""
    topic: str
    relevance: float = Field(ge=0.0, le=1.0)


class ExtractedData(BaseModel):
    """Combined analysis results"""
    entities: List[ExtractedEntity] = Field(default_factory=list)
    sentiment: Optional[SentimentAnalysis] = None
    topics: List[TopicClassification] = Field(default_factory=list)


class Newsletter(BaseModel):
    """Generated newsletter output"""
    title: str
    summary: str
    top_stories: List[Dict[str, str]]
    key_entities: List[str]
    generated_at: str


# ============================================================================
# Intelligence Analysis Models (Knowledge Graph)
# ============================================================================

class EntityTrend(BaseModel):
    """Entity with frequency and trend data - Phase 1 Enhanced"""
    name: str = Field(..., description="Entity name")
    mention_count: int = Field(..., description="Number of episodes mentioning this entity")
    change_percent: float | None = Field(None, description="Percent change vs previous period (null if first appearance)")
    entity_type: str = Field(..., description="Type of entity (person, organization, location, etc.)")

    # Phase 1: Anomaly Detection
    anomaly_score: float | None = Field(None, description="Z-score for anomaly detection (>3.0 = anomaly)")
    is_anomaly: bool = Field(False, description="True if entity shows anomalous surge")

    # Phase 1: Temporal Velocity
    velocity: float | None = Field(None, description="Rate of change in mentions (first derivative)")
    acceleration: float | None = Field(None, description="Rate of change in velocity (second derivative)")
    is_burst: bool = Field(False, description="True if entity is in Kleinberg burst state")

    # Phase 1: Network Metrics
    centrality_score: float | None = Field(None, description="PageRank centrality (0-1)")
    betweenness_score: float | None = Field(None, description="Betweenness centrality (0-1)")


class RelationshipNetwork(BaseModel):
    """Relationship network around a central entity - Phase 1 Enhanced"""
    entity_name: str = Field(..., description="Central entity name")
    connection_count: int = Field(..., description="Number of connected entities")
    relationship_types: List[str] = Field(..., description="Types of relationships (e.g., DENIES_MEETING, PHOTOGRAPHED_WITH)")
    key_connections: List[str] = Field(..., description="Names of key connected entities")

    # Phase 1: Network Metrics
    community_id: int | None = Field(None, description="Community cluster ID from Leiden algorithm")
    centrality_rank: int | None = Field(None, description="Rank by centrality (1=highest)")


class AnomalyAlert(BaseModel):
    """Phase 1: Anomaly detection alert"""
    entity_name: str = Field(..., description="Entity showing anomalous behavior")
    anomaly_type: str = Field(..., description="Type: 'frequency_surge', 'unexpected_connection', 'centrality_jump'")
    severity: str = Field(..., description="Severity: 'low', 'medium', 'high', 'critical'")
    z_score: float = Field(..., description="Statistical z-score (standard deviations from mean)")
    description: str = Field(..., description="Human-readable explanation of anomaly")


class IntelligenceInsights(BaseModel):
    """Structured intelligence analysis from knowledge graph - Phase 1 Enhanced"""
    trending_entities: List[EntityTrend] = Field(
        default_factory=list,
        description="Top 10 entities by mention frequency with trend data"
    )
    key_networks: List[RelationshipNetwork] = Field(
        default_factory=list,
        description="Relationship networks for top 5 entities"
    )
    emerging_topics: List[str] = Field(
        default_factory=list,
        description="Topics/entities that appeared for the first time this cycle"
    )
    recurring_topics: List[str] = Field(
        default_factory=list,
        description="Topics/entities that appear consistently over multiple cycles"
    )

    # Phase 1: Anomaly Detection
    anomaly_alerts: List[AnomalyAlert] = Field(
        default_factory=list,
        description="Detected anomalies requiring attention"
    )

    # Phase 1: Temporal Intelligence
    burst_entities: List[str] = Field(
        default_factory=list,
        description="Entities in Kleinberg burst state (sustained surges)"
    )
    velocity_leaders: List[str] = Field(
        default_factory=list,
        description="Entities with highest velocity (fastest growing)"
    )

    # Phase 1: Network Intelligence
    centrality_jumps: List[str] = Field(
        default_factory=list,
        description="Entities with significant centrality increases"
    )
    bridge_entities: List[str] = Field(
        default_factory=list,
        description="Entities connecting different communities (high betweenness)"
    )

    analysis_timestamp: str = Field(
        ...,
        description="ISO timestamp of when this analysis was performed"
    )
    total_entities: int = Field(..., description="Total number of entities in knowledge graph")
    total_facts: int = Field(..., description="Total number of facts (relationships) in knowledge graph")


# ============================================================================
# Executor Functions (Custom Transformations)
# ============================================================================

def fetch_rss_feeds(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Fetch articles from multiple RSS feeds with URL deduplication.
    Stores processed URLs in persistent JSON file to avoid re-processing across runs.
    """
    feeds = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
        "https://www.theguardian.com/world/rss",
        "https://www.aljazeera.com/xml/rss/all.xml",  # Al Jazeera English
    ]

    # Load persistent URL tracking from JSON file
    persistent_file = Path("processed_urls.json")
    if persistent_file.exists():
        with open(persistent_file, 'r') as f:
            seen_urls = set(json.load(f))
    else:
        seen_urls = set()

    initial_count = len(seen_urls)
    new_articles = []

    print(f"\n📡 Fetching from {len(feeds)} RSS feeds...")
    print(f"📊 Already tracked: {initial_count} articles")

    for feed_url in feeds:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                url = entry.get("link", "")
                if url and url not in seen_urls:
                    new_articles.append(Article(
                        title=entry.get("title", "Untitled"),
                        url=url,
                        summary=entry.get("summary", ""),
                        published=entry.get("published", datetime.now().isoformat())
                    ))
                    seen_urls.add(url)
        except Exception as e:
            print(f"⚠️  Error fetching {feed_url}: {e}")

    # Limit to 10 articles per cycle to control costs
    new_articles = new_articles[:10]

    # Save persistent URL tracking to JSON file
    with open(persistent_file, 'w') as f:
        json.dump(list(seen_urls), f, indent=2)

    # Update session state for this workflow run
    session_state["new_articles"] = [a.model_dump() for a in new_articles]

    print(f"✅ Found {len(new_articles)} NEW articles (total tracked: {len(seen_urls)}, +{len(seen_urls) - initial_count} this run)")

    return StepOutput(
        content=f"Fetched {len(new_articles)} new articles from {len(feeds)} feeds"
    )


def log_rss_articles(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Create audit log of new RSS articles discovered in this run.

    Saves a timestamped markdown document with all new articles for:
    - Data integrity verification
    - Historical audit trail
    - Debugging and comparison
    - Compliance documentation
    """
    # Import audit system (only if audit_run_id is set)
    # Using late import to avoid circular dependencies
    import sys
    from pathlib import Path
    audit_dir = Path(__file__).parent / ".audit"
    if str(audit_dir) not in sys.path:
        sys.path.insert(0, str(audit_dir))

    articles = session_state.get("new_articles", [])

    if not articles:
        print("📋 No new articles to log")
        return StepOutput(content="No new articles to log")

    # Create rss_logs directory if it doesn't exist
    log_dir = Path("rss_logs")
    log_dir.mkdir(exist_ok=True)

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"rss_articles_{timestamp}.md"

    # Build markdown content
    md_content = f"""# RSS Articles Audit Log
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- **Total New Articles**: {len(articles)}
- **Workflow Run**: {timestamp}

## Articles

"""

    for i, article in enumerate(articles, 1):
        md_content += f"""### {i}. {article.get('title', 'Untitled')}

- **URL**: {article.get('url', 'N/A')}
- **Published**: {article.get('published', 'N/A')}
- **Summary**: {article.get('summary', 'No summary available')}

---

"""

    # Write to file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"📋 Audit log saved: {log_file}")

    # Optional: Save to audit system for easy inspection
    if session_state.get("_audit_run_id"):
        try:
            from audit_helpers import AuditArtifacts
            audit = AuditArtifacts(session_state)
            audit.save(
                step_name="log_rss_articles",
                filename="articles.json",
                content=[{
                    "title": art.get('title'),
                    "url": art.get('url'),
                    "published": art.get('published'),
                    "summary": art.get('summary', '')[:200],  # Truncate for readability
                } for art in articles],
                metadata={"article_count": len(articles), "timestamp": timestamp}
            )
        except Exception as e:
            # Don't fail workflow if audit save fails
            print(f"⚠️ Warning: Failed to save audit artifact: {e}")

    return StepOutput(
        content=f"Logged {len(articles)} articles to {log_file}"
    )


def prepare_urls_for_extraction(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Format article URLs as a numbered list for content extraction.
    """
    articles = session_state.get("new_articles", [])

    if not articles:
        return StepOutput(content="No articles to extract content from")

    # Format as numbered list of URLs
    url_list = "\n".join([
        f"{i+1}. {art['url']}"
        for i, art in enumerate(articles)
    ])

    print(f"📝 Prepared {len(articles)} URLs for content extraction")

    return StepOutput(content=url_list)


def merge_extracted_content(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Merge extracted content back into articles.
    Parses the agent's JSON response and updates session state.
    """
    articles = session_state.get("new_articles", [])
    extracted_content = step_input.previous_step_content

    if not articles:
        return StepOutput(content="No articles to merge content into")

    # Try to parse JSON response from content extractor
    import json
    import re

    # Look for JSON in the response
    json_match = re.search(r'\{[^}]*\}', extracted_content, re.DOTALL)
    if json_match:
        try:
            content_map = json.loads(json_match.group())

            # Merge content into articles
            for i, article in enumerate(articles):
                article_num = str(i + 1)
                if article_num in content_map and content_map[article_num]:
                    article['content'] = content_map[article_num]
                else:
                    article['content'] = article.get('summary', '')  # Fallback to summary

            print(f"✅ Merged extracted content for {len(articles)} articles")
        except json.JSONDecodeError:
            print("⚠️  Failed to parse extracted content JSON, using summaries as fallback")
            for article in articles:
                article['content'] = article.get('summary', '')
    else:
        print("⚠️  No JSON found in extraction response, using summaries as fallback")
        for article in articles:
            article['content'] = article.get('summary', '')

    session_state["new_articles"] = articles

    return StepOutput(content=f"Merged content for {len(articles)} articles")


def format_for_analysis(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Format articles with full content for parallel analysis.
    Content should already be extracted and merged at this point.
    """
    articles = session_state.get("new_articles", [])

    if not articles:
        return StepOutput(content="No articles to analyze")

    # Format for agents: include title, summary, and full content
    formatted = "\n\n---\n\n".join([
        f"**{art['title']}**\n"
        f"URL: {art['url']}\n"
        f"Published: {art['published']}\n\n"
        f"Summary: {art['summary']}\n\n"
        f"Content: {art.get('content', 'Content extraction pending')}"
        for art in articles
    ])

    session_state["formatted_articles"] = formatted

    return StepOutput(
        content=formatted
    )


def prepare_newsletter_context(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Prepare article metadata, analysis results, and Phase 1 intelligence insights for newsletter generation.
    Includes BOTH new articles from this cycle AND recent episodes from Graphiti knowledge graph.
    This ensures newsletters aggregate intelligence from ALL feeds, not just current cycle.
    """
    new_articles = session_state.get("new_articles", [])

    # Get Phase 1 intelligence summary from analyze_knowledge_graph step (raw text)
    intelligence_summary: str = step_input.get_step_content("analyze_knowledge_graph")

    # Get parallel analysis results
    analysis_results = step_input.get_step_content("parallel_analysis")

    # Build Phase 1 intelligence insights section
    intelligence_text = ""
    # Check if intelligence analysis has actual content (not error message)
    has_intelligence = intelligence_summary and (
        "Stories in Knowledge Graph:" in intelligence_summary or
        "ALL STORIES" in intelligence_summary or
        "RISING PATTERNS" in intelligence_summary
    )

    if has_intelligence:
        intelligence_text = f"""# Phase 1 Enhanced Intelligence Insights from Knowledge Graph

IMPORTANT: This intelligence analysis aggregates data from ALL {session_state.get('processed_urls', []).__len__()} articles
tracked across all RSS feeds, not just today's new articles. The metrics reflect accumulated intelligence.

{intelligence_summary}

---

"""
    else:
        intelligence_text = """# Phase 1 Enhanced Intelligence Insights from Knowledge Graph

*Knowledge graph analysis not available yet. Run graphiti_ingest_async.py to populate the graph.*

---

"""

    # Build article metadata section for NEW articles from this cycle
    article_list = ""
    if new_articles:
        article_list = "\n\n".join([
            f"**New Article {i+1} (This Cycle):**\n"
            f"- Title: {art['title']}\n"
            f"- URL: {art['url']}\n"
            f"- Published: {art.get('published', 'Today')}"
            for i, art in enumerate(new_articles)
        ])

    # Combine everything
    newsletter_input = f"""{intelligence_text}# Analysis Results
{analysis_results}

---

# Article Metadata (for citations)
{article_list}

---

**Today's Date:** {datetime.now().strftime('%B %d, %Y')}

**Instructions:**
Generate newsletter using TODAY'S date, cite each story with its actual title and URL, and incorporate the intelligence insights to provide context on trends, networks, and patterns.
"""

    return StepOutput(content=newsletter_input)


def save_newsletter(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Save generated technical newsletter to file with timestamp.
    """
    # Import audit system (only if audit_run_id is set)
    import sys
    from pathlib import Path
    audit_dir = Path(__file__).parent / ".audit"
    if str(audit_dir) not in sys.path:
        sys.path.insert(0, str(audit_dir))

    newsletter_content = step_input.previous_step_content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Ensure newsletters directory exists
    output_dir = Path(__file__).parent / "newsletters"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"newsletter_technical_{timestamp}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(newsletter_content)

    print(f"\n📰 Technical newsletter saved to: {output_path}")

    # Optional: Save to audit system for easy inspection
    if session_state.get("_audit_run_id"):
        try:
            from audit_helpers import AuditArtifacts
            audit = AuditArtifacts(session_state)
            audit.save(
                step_name="generate_newsletter",
                filename="technical_newsletter.md",
                content=newsletter_content,
                metadata={"timestamp": timestamp, "type": "technical"}
            )
        except Exception as e:
            print(f"⚠️ Warning: Failed to save audit artifact: {e}")

    # Store in session for consumer newsletter generation
    session_state["technical_newsletter"] = newsletter_content
    session_state["newsletter_timestamp"] = timestamp

    return StepOutput(
        content=newsletter_content  # Pass to next step for consumer translation
    )


def prepare_consumer_newsletter_context(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Prepare context for consumer newsletter generation from technical newsletter.
    """
    technical_newsletter = step_input.previous_step_content

    consumer_context = f"""Technical Intelligence Analysis for {datetime.now().strftime('%Y-%m-%d')}

{technical_newsletter}

Translate this technical analysis into a consumer-friendly intelligence digest.

REMEMBER:
- No technical jargon (z-scores, centrality, velocity)
- Plain language ("2x normal attention" not "z-score 2.0")
- Answer "So what?" for every insight
- Make it scannable and engaging
"""

    return StepOutput(content=consumer_context)


def save_consumer_newsletter(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Save generated consumer newsletter to file with same timestamp as technical version.
    """
    consumer_newsletter = step_input.previous_step_content
    timestamp = session_state.get("newsletter_timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))

    # Ensure newsletters directory exists
    output_dir = Path(__file__).parent / "newsletters"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"newsletter_consumer_{timestamp}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(consumer_newsletter)

    print(f"📰 Consumer newsletter saved to: {output_path}")

    return StepOutput(
        content=f"Consumer newsletter saved to {output_path}"
    )


# ============================================================================
# Agent Definitions
# ============================================================================

# Content extractor using Agno's built-in Newspaper4kTools
# Content extractor using factory function from agents module
content_extractor = create_content_extractor()

# Entity extractor using factory function from agents module
entity_agent = create_entity_extractor(ExtractedData)

# Sentiment analyzer using factory function from agents module
sentiment_agent = create_sentiment_analyzer(ExtractedData)

# Topic classifier using factory function from agents module
topic_agent = create_topic_extractor(ExtractedData)

# Newsletter generator using factory function from agents module
newsletter_generator = create_newsletter_generator()

# Consumer-friendly newsletter generator using factory function from agents module
consumer_newsletter_generator = create_consumer_newsletter_generator()

# ============================================================================
# Graphiti Knowledge Graph Integration
# ============================================================================
#
# Note: Graphiti MCP Tools require async context manager initialization,
# which Agno workflows don't support at module level. Episodes are prepared
# by the workflow and ingested via separate async script: graphiti_ingest_async.py
#
# This is the proper Agno native pattern for MCP tools that require async setup.
# ============================================================================


def prepare_graphiti_episodes(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Prepare articles as Graphiti episodes for knowledge graph ingestion.

    This function creates structured episode data that will be added to
    Graphiti's knowledge graph, enabling cross-article entity tracking,
    temporal pattern recognition, and relationship network analysis.
    """
    from datetime import datetime
    import json
    from pathlib import Path

    articles = session_state.get("new_articles", [])

    if not articles:
        return StepOutput(content="No articles to add to knowledge graph")

    print(f"\n📊 Preparing {len(articles)} articles as Graphiti episodes...")

    # Create episodes for each article
    episodes = []
    for i, article in enumerate(articles):
        # Create episode name and body
        episode_name = f"News: {article['title'][:80]}"

        # Structure episode body with full article data
        episode_data = {
            "title": article['title'],
            "source": article.get('link', article.get('url', 'Unknown')),
            "published_date": article.get('published', str(datetime.now())),
            "summary": article.get('summary', ''),
            "content": article.get('content', article.get('summary', ''))[:3000],
        }

        # Convert to JSON for structured ingestion
        episode_body = json.dumps(episode_data, indent=2)

        episodes.append({
            "name": episode_name,
            "body": episode_body,
            "source_type": "json",
            "article_index": i
        })

        print(f"  📝 Episode {i+1}: {episode_name}")

    # Store episodes in session state for the Graphiti step
    session_state["graphiti_episodes"] = episodes

    # Also save to a JSON file for Claude Code to process
    episodes_file = Path("graphiti_episodes_pending.json")
    with open(episodes_file, "w") as f:
        json.dump(episodes, f, indent=2)

    print(f"💾 Saved episodes to {episodes_file} for Graphiti ingestion")

    # Create summary for next step
    summary = f"""Prepared {len(episodes)} episodes for Graphiti knowledge graph:

{chr(10).join([f"{i+1}. {ep['name']}" for i, ep in enumerate(episodes)])}

Episodes saved to: {episodes_file}

These episodes will be ingested into Graphiti to:
- Extract entities (people, organizations, locations, events)
- Build relationship graphs between entities across articles
- Enable temporal pattern tracking
- Support cross-article intelligence queries

⚠️  NOTE: Episodes are prepared but not yet ingested.
    Run 'python graphiti_ingestion.py' or have Claude Code ingest them using mcp__graphiti__add_memory.
"""

    print(f"✅ Prepared {len(episodes)} episodes for knowledge graph ingestion")

    return StepOutput(content=summary)


async def ingest_graphiti_episodes(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Ingest prepared episodes into Graphiti knowledge graph using optimized agent-based MCP tool calls.

    This function takes episodes from session_state and adds them to Graphiti,
    enabling immediate intelligence analysis on the new data.

    Performance: Uses fastest available model (glm-4.6:cloud) to minimize LLM overhead.
    """
    from agno.tools.mcp import MCPTools
    from agno.agent import Agent

    episodes = session_state.get("graphiti_episodes", [])

    if not episodes:
        return StepOutput(
            step_name="ingest_graphiti_episodes",
            content="No episodes to ingest",
            success=True,
        )

    print(f"\n📊 Ingesting {len(episodes)} episodes into Graphiti knowledge graph...")

    # Initialize Graphiti MCP tools
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=120,
    )

    ingested_count = 0
    failed_count = 0

    # CRITICAL: Use async context manager
    async with graphiti_mcp:
        await graphiti_mcp.initialize()
        print("✓ Graphiti MCP tools initialized\n")

        # Create minimal agent for tool calling (fastest model)
        agent = Agent(
            name="Graphiti Ingestor",
            model=Ollama(id="glm-4.6:cloud"),  # Fastest cloud model
            tools=[graphiti_mcp],
            instructions="Use add_memory tool with provided parameters. Return only 'OK' on success.",
            markdown=False,
        )

        # Ingest each episode via agent (required for MCP tool invocation)
        for i, episode in enumerate(episodes):
            episode_name = episode["name"]
            episode_body = episode["body"]

            try:
                print(f"  [{i+1}/{len(episodes)}] {episode_name[:55]}...", end=" ", flush=True)

                # Minimal prompt for fast processing
                result = await agent.arun(
                    f"add_memory(name={repr(episode_name)}, episode_body={repr(episode_body)}, "
                    f"source='json', source_description='RSS news article', group_id='rss-intelligence')"
                )

                ingested_count += 1
                print("✅")

            except Exception as e:
                failed_count += 1
                print(f"❌ {str(e)[:40]}")

        # Summary
        summary = f"""Graphiti Ingestion Complete:

✅ Successfully ingested: {ingested_count}/{len(episodes)} episodes
❌ Failed: {failed_count}/{len(episodes)} episodes

Episodes are queued for Graphiti processing (async extraction of entities and relationships).
"""

        print()
        print("=" * 80)
        print(summary)
        print("=" * 80)

        # Note: Graphiti processes episodes asynchronously in the background.
        # The intelligence analysis step will query the most up-to-date graph state,
        # so no explicit polling is needed here. Graphiti's async processing ensures
        # entities and facts are extracted from episodes continuously.

    return StepOutput(
        step_name="ingest_graphiti_episodes",
        content=summary,
        success=ingested_count > 0,
    )


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

            # Create Phase 1 Enhanced Intelligence agent with raw markdown output
            # Create intelligence analyst using factory function from agents module
            intelligence_agent = create_intelligence_analyst(graphiti_mcp)

            try:
                # Execute Phase 1 intelligence analysis
                result = await intelligence_agent.arun(
                    "Analyze the rss-intelligence knowledge graph with Phase 1 enhancements"
                )

                # result.content is raw text with Phase 1 metrics
                intelligence_summary = result.content

                print("✓ Phase 1 intelligence analysis complete")
                print(f"  Analysis length: {len(intelligence_summary)} characters")

                # DEBUG: Save full intelligence output for inspection
                with open('intelligence_output_debug.txt', 'w') as f:
                    f.write(intelligence_summary)
                print("  💾 Saved full output to intelligence_output_debug.txt")

                # DEBUG: Print first 500 chars to verify content
                if intelligence_summary:
                    print(f"  Preview: {intelligence_summary[:500]}...")
                else:
                    print("  ⚠️ WARNING: Intelligence summary is empty!")

                # Extract summary statistics from text for display
                import re
                entities_match = re.search(r'Total Entities:\s*(\d+)', intelligence_summary)
                facts_match = re.search(r'Total Facts:\s*(\d+)', intelligence_summary)

                if entities_match:
                    print(f"  Entities analyzed: {entities_match.group(1)}")
                if facts_match:
                    print(f"  Facts analyzed: {facts_match.group(1)}")

                # Check for anomalies
                if "ANOMALIES:" in intelligence_summary:
                    anomaly_section = intelligence_summary.split("ANOMALIES:")[1].split("\n\n")[0]
                    anomaly_count = len([line for line in anomaly_section.split("\n") if line.strip().startswith("-")])
                    if anomaly_count > 0:
                        print(f"  🚨 Anomalies detected: {anomaly_count}")

                # Check for velocity leaders
                if "VELOCITY LEADERS:" in intelligence_summary:
                    velocity_section = intelligence_summary.split("VELOCITY LEADERS:")[1].split("\n\n")[0]
                    velocity_count = len([line for line in velocity_section.split("\n") if line.strip() and line.strip()[0].isdigit()])
                    if velocity_count > 0:
                        print(f"  🚀 Velocity leaders: {velocity_count}")

                # Check for centrality jumps
                if "CENTRALITY JUMPS:" in intelligence_summary:
                    centrality_section = intelligence_summary.split("CENTRALITY JUMPS:")[1].split("\n\n")[0]
                    centrality_count = len([line for line in centrality_section.split("\n") if line.strip().startswith("-")])
                    if centrality_count > 0:
                        print(f"  🌐 Centrality jumps: {centrality_count}")

                return StepOutput(
                    step_name="analyze_knowledge_graph",
                    content=intelligence_summary,  # Raw Phase 1 analysis text
                    success=True,
                )

            except Exception as e:
                print(f"❌ Phase 1 intelligence analysis failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                import traceback
                print("   Full traceback:")
                traceback.print_exc()

                # Return empty analysis on failure
                return StepOutput(
                    step_name="analyze_knowledge_graph",
                    content=f"Phase 1 analysis failed: {str(e)}",
                    success=False,
                )

    # Return async step directly (Agno workflows support async executors)
    return Step(
        name="analyze_knowledge_graph",
        executor=async_intelligence_executor,
        description="Query Graphiti knowledge graph for intelligence insights using MCP tools",
    )


# ============================================================================
# Visualization Generation (Phase 2)
# ============================================================================

async def generate_visualizations(step_input: StepInput, session_state: dict) -> StepOutput:
    """
    Generate network visualizations for top compound crisis alerts.

    Parses COMPOUND_SCORE section from intelligence output and creates:
    - Cascade path diagrams showing ripple effect chains
    - Network graphs with entity connections
    - Color-coded edge types (economic, political, security, humanitarian)

    Saves PNG files to visualizations/ directory.
    """
    import re
    from pathlib import Path

    intelligence_summary = session_state.get('intelligence_summary', '')

    # Check if COMPOUND CRISIS ALERTS section exists (supports both formats)
    has_compound_section = (
        'COMPOUND_SCORE:' in intelligence_summary or
        'COMPOUND CRISIS ALERTS' in intelligence_summary or
        'COMPOUND CRISIS ALERT' in intelligence_summary
    )

    if not has_compound_section:
        print("⚠️ No COMPOUND CRISIS ALERTS section found - skipping visualizations")
        return StepOutput(
            step_name="generate_visualizations",
            content="No compound scores available for visualization",
            success=True,
        )

    # Create visualizations directory if it doesn't exist
    viz_dir = Path("visualizations")
    viz_dir.mkdir(exist_ok=True)

    try:
        # Import visualization libraries
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import networkx as nx
        from datetime import datetime

        # Parse COMPOUND CRISIS ALERTS section (try multiple formats)
        if 'COMPOUND_SCORE:' in intelligence_summary:
            compound_section = intelligence_summary.split('COMPOUND_SCORE:')[1].split('\n\n')[0]
            # Old format: "1. Entity: score=0.88, alert=EXTREME_ALERT"
            alert_pattern = r'(\d+)\.\s+([^:]+):\s+score=([0-9.]+),\s+alert=(EXTREME_ALERT|HIGH_ALERT)'
            alerts = re.findall(alert_pattern, compound_section)
        else:
            # New format: "## 🚨 COMPOUND CRISIS ALERTS\n\n**EXTREME ALERT (0.88): Russia-Kyiv Attack**"
            compound_section_match = re.search(
                r'##\s+🚨\s+COMPOUND CRISIS ALERTS(.*?)(?=##|$)',
                intelligence_summary,
                re.DOTALL
            )
            if compound_section_match:
                compound_section = compound_section_match.group(1)
                # Extract markdown alerts: **EXTREME ALERT (0.88): Entity Name**
                alert_pattern = r'\*\*(EXTREME ALERT|HIGH ALERT)\s+\(([0-9.]+)\):\s+([^*]+)\*\*'
                raw_alerts = re.findall(alert_pattern, compound_section)
                # Convert to old format for compatibility: (rank, entity_name, score, alert_level)
                alerts = [(str(i+1), entity.strip(), score, level.replace(' ', '_'))
                          for i, (level, score, entity) in enumerate(raw_alerts)]
            else:
                alerts = []

        if not alerts:
            print("⚠️ No EXTREME_ALERT or HIGH_ALERT entities found")
            return StepOutput(
                step_name="generate_visualizations",
                content="No high-priority alerts for visualization",
                success=True,
            )

        visualization_paths = []

        # Limit to top 3 alerts
        for idx, (rank, entity_name, score, alert_level) in enumerate(alerts[:3], 1):
            print(f"📊 Generating visualization {idx}/3: {entity_name} ({alert_level})")

            # Extract cascade paths for this entity
            # Try old format first, then new markdown format
            entity_section_pattern = rf'{rank}\.\s+{re.escape(entity_name)}:.*?(?=\n\d+\.|$)'
            entity_match = re.search(entity_section_pattern, compound_section, re.DOTALL)

            if not entity_match:
                # Try new markdown format: **ALERT (score): Entity Name**
                entity_pattern = rf'\*\*{re.escape(alert_level.replace("_", " "))}[^*]*{re.escape(entity_name)}\*\*.*?(?=\*\*|##|$)'
                entity_match = re.search(entity_pattern, compound_section, re.DOTALL | re.IGNORECASE)

            if not entity_match:
                print(f"  ⚠️ Could not find entity section for {entity_name}")
                continue

            entity_text = entity_match.group(0)

            # Parse cascade paths - try both formats
            # New format: "1. Source → Target (type)"
            # Old format: "* Source → Target (type)"
            path_pattern = r'(?:\d+\.\s+|\*\s+)([^→]+)\s+→\s+([^(]+)\s+\(([^)]+)\)'
            paths = re.findall(path_pattern, entity_text)

            if not paths:
                print(f"  ⚠️ No cascade paths found for {entity_name}")
                continue

            # Create network graph
            G = nx.DiGraph()

            # Add center node (the alert entity)
            G.add_node(entity_name, node_type='center')

            # Add cascade paths
            for source, target, edge_type in paths:
                source = source.strip()
                target = target.strip()
                edge_type = edge_type.strip().lower()

                # Add nodes if not exists
                if source not in G.nodes():
                    G.add_node(source, node_type='related')
                if target not in G.nodes():
                    G.add_node(target, node_type='related')

                # Add edge
                G.add_edge(source, target, edge_type=edge_type)

            # Create visualization
            plt.figure(figsize=(12, 9))

            # Layout: spring layout for nice distribution
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

            # Separate center node from others
            center_nodes = [n for n, attr in G.nodes(data=True) if attr.get('node_type') == 'center']
            other_nodes = [n for n in G.nodes() if n not in center_nodes]

            # Draw center node (red, large)
            if center_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=center_nodes,
                                      node_color='#FF4444', node_size=1500, alpha=0.9,
                                      node_shape='s')  # Square for center

            # Draw other nodes (blue, medium)
            nx.draw_networkx_nodes(G, pos, nodelist=other_nodes,
                                  node_color='#4A90E2', node_size=800, alpha=0.7)

            # Draw edges with different colors for types
            edge_colors = {
                'economic': '#2ECC71',      # Green
                'political': '#3498DB',     # Blue
                'security': '#E74C3C',      # Red
                'humanitarian': '#F39C12',  # Orange
                'dependency': '#9B59B6',    # Purple
                'response': '#1ABC9C',      # Teal
            }

            # Group edges by type and draw with appropriate colors
            for edge_type, color in edge_colors.items():
                edges = [(u, v) for u, v, attr in G.edges(data=True)
                        if attr.get('edge_type', '').lower() == edge_type]
                if edges:
                    nx.draw_networkx_edges(G, pos, edgelist=edges,
                                          edge_color=color, width=2.5, alpha=0.7,
                                          arrows=True, arrowsize=25, arrowstyle='->')

            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold',
                                   font_color='white',
                                   bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

            # Title
            plt.title(f"Cascade Analysis: {entity_name}\n{alert_level} (Score: {score})",
                     fontsize=16, fontweight='bold', pad=20)

            # Legend
            legend_elements = [
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#FF4444', markersize=12, label='Crisis Entity'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4A90E2', markersize=10, label='Connected Entity'),
            ]
            for edge_type, color in edge_colors.items():
                legend_elements.append(
                    plt.Line2D([0], [0], color=color, linewidth=3, label=edge_type.title())
                )
            plt.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.9)

            plt.axis('off')
            plt.tight_layout()

            # Save
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = re.sub(r'[^\w\s-]', '', entity_name).replace(' ', '_')
            filepath = viz_dir / f"cascade_{safe_name}_{timestamp}.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            visualization_paths.append(str(filepath))
            print(f"  ✅ Saved: {filepath}")

        print(f"\n📊 Generated {len(visualization_paths)} visualizations")

        # Store paths in session state for newsletter reference
        session_state['visualization_paths'] = visualization_paths

        return StepOutput(
            step_name="generate_visualizations",
            content=f"Generated {len(visualization_paths)} cascade visualizations",
            success=True,
        )

    except ImportError as e:
        print(f"⚠️ Visualization libraries not available: {e}")
        print("   Install with: pip install matplotlib networkx")
        return StepOutput(
            step_name="generate_visualizations",
            content="Visualization libraries not installed",
            success=False,
        )
    except Exception as e:
        print(f"❌ Visualization generation failed: {e}")
        import traceback
        traceback.print_exc()
        return StepOutput(
            step_name="generate_visualizations",
            content=f"Visualization failed: {str(e)}",
            success=False,
        )


# ============================================================================
# Workflow Definition
# ============================================================================

def create_rss_workflow() -> Workflow:
    """
    Create the RSS intelligence workflow with parallel analysis and knowledge graph.

    Flow:
    1. Fetch RSS feeds (deduplicated)
    2. Log new articles to audit trail (timestamped markdown in rss_logs/)
    3. Prepare URLs for extraction
    4. Extract full content (Newspaper4k)
    5. Merge extracted content back into articles
    6. Format for analysis
    7. Parallel analysis (entities, sentiment, topics)
    8. Prepare Graphiti episodes (saved to graphiti_episodes_pending.json)
    9. Ingest episodes into Graphiti knowledge graph (automatic using MCP tools)
    10. Analyze knowledge graph (intelligence insights with MCP tools)
    11. Generate network visualizations for compound crisis alerts
    12. Prepare newsletter context (metadata + intelligence insights + visualization paths)
    13. Generate technical newsletter with Phase 1 intelligence metrics
    14. Save technical newsletter to file
    15. Prepare consumer newsletter context (translate technical → consumer)
    16. Generate consumer-friendly intelligence digest
    17. Save consumer newsletter to file

    Note: Audit logging (Step 2) creates timestamped markdown files for data integrity verification.
    Graphiti ingestion (Step 9) happens automatically within the workflow.
    Episodes are ingested immediately before intelligence analysis for fresh temporal data.
    Intelligence analysis (Step 10) uses async MCP to query the knowledge graph.
    Visualizations (Step 11) generate cascade diagrams for EXTREME/HIGH alerts.
    Both technical and consumer newsletters generated with same timestamp for comparison.
    """
    # Initialize audit system session state
    from datetime import datetime
    import time

    audit_session_state = {
        # Audit metadata (auto-initialized)
        "_audit_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "_audit_start_time": time.time(),
        "_audit_workflow_version": "1.0.0",

        # Workflow state (existing)
        "processed_urls": [],
    }

    return Workflow(
        name="RSS Intelligence",

        # ✅ Agno Native Event Storage
        store_events=True,  # Capture all workflow execution events
        add_workflow_history_to_steps=True,  # Provide step-level history

        # Optional: Skip verbose events to reduce noise
        # events_to_skip=[
        #     WorkflowRunEvent.step_started,
        # ],

        steps=[
            # Step 1: Fetch new articles from RSS feeds
            Step(
                name="fetch_feeds",
                executor=fetch_rss_feeds,
                description="Fetch articles from RSS feeds with deduplication",
            ),

            # Step 2: Log new articles to audit trail
            Step(
                name="log_rss_articles",
                executor=log_rss_articles,
                description="Create timestamped audit log of new articles for data integrity verification",
            ),

            # Step 3: Prepare URLs for extraction
            Step(
                name="prepare_urls",
                executor=prepare_urls_for_extraction,
                description="Format article URLs as numbered list",
            ),

            # Step 4: Extract full article content
            Step(
                name="extract_content",
                agent=content_extractor,
                description="Extract full content from article URLs using Newspaper4k",
            ),

            # Step 5: Merge extracted content
            Step(
                name="merge_content",
                executor=merge_extracted_content,
                description="Merge extracted content back into articles",
            ),

            # Step 6: Format articles for analysis
            Step(
                name="format_articles",
                executor=format_for_analysis,
                description="Format articles with full content for analysis",
            ),

            # Step 7: Parallel analysis (entities, sentiment, topics)
            Parallel(
                Step(name="extract_entities", agent=entity_agent),
                Step(name="analyze_sentiment", agent=sentiment_agent),
                Step(name="extract_topics", agent=topic_agent),
                name="parallel_analysis",
            ),

            # Step 8: Prepare Graphiti episodes
            Step(
                name="prepare_graphiti_episodes",
                executor=prepare_graphiti_episodes,
                description="Prepare articles as Graphiti episodes (saved to JSON)",
            ),

            # Step 9: Ingest episodes into Graphiti knowledge graph
            Step(
                name="ingest_graphiti_episodes",
                executor=ingest_graphiti_episodes,
                description="Ingest prepared episodes into Graphiti using MCP tools for immediate analysis",
            ),

            # Step 10: Analyze knowledge graph (Intelligence layer)
            create_intelligence_step(),

            # Step 11: Generate network visualizations for compound crisis alerts
            Step(
                name="generate_visualizations",
                executor=generate_visualizations,
                description="Generate cascade path diagrams for top compound crisis alerts",
            ),

            # Step 12: Prepare newsletter context with metadata, intelligence, and visualizations
            Step(
                name="prepare_newsletter_context",
                executor=prepare_newsletter_context,
                description="Prepare article metadata, intelligence insights, and visualization paths for newsletter",
            ),

            # Step 13: Generate technical newsletter from analysis
            Step(
                name="generate_newsletter",
                agent=newsletter_generator,
                description="Generate newsletter with proper dates, citations, and intelligence insights",
            ),

            # Step 14: Save technical newsletter to file
            Step(
                name="save_newsletter",
                executor=save_newsletter,
                description="Save generated technical newsletter to file",
            ),

            # Step 15: Prepare consumer newsletter context
            Step(
                name="prepare_consumer_newsletter_context",
                executor=prepare_consumer_newsletter_context,
                description="Prepare technical newsletter for consumer translation",
            ),

            # Step 16: Generate consumer-friendly newsletter
            Step(
                name="generate_consumer_newsletter",
                agent=consumer_newsletter_generator,
                description="Generate consumer-friendly intelligence digest",
            ),

            # Step 17: Save consumer newsletter to file
            Step(
                name="save_consumer_newsletter",
                executor=save_consumer_newsletter,
                description="Save consumer newsletter to file",
            ),
        ],
        db=SqliteDb(
            session_table="rss_intelligence_sessions",
            db_file="rss_intelligence.db",
        ),

        # ✅ Initialize session state with audit metadata
        session_state=audit_session_state,
    )


# ============================================================================
# Main Loop (Agno-Native Scheduling)
# ============================================================================

async def main():
    """
    Main loop with Agno-native scheduling.

    Runs every 2 hours (7200 seconds).
    For testing: comment out while True loop and run once.
    """
    workflow = create_rss_workflow()

    print("🚀 RSS Intelligence Workflow Starting...")
    print("📊 Using free Ollama Cloud models: glm-4.6, deepseek-v3.1")
    print("⏰ Cycle interval: 2 hours\n")

    # For testing: comment out while True and run once
    # Uncomment for continuous operation
    # while True:
    try:
        print(f"\n{'='*60}")
        print(f"⏰ Cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # Run workflow (session_state initialized in create_rss_workflow)
        await workflow.arun(
            input="Process all RSS feeds",
        )

        print(f"\n{'='*60}")
        print(f"✅ Cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # print("💤 Sleeping for 2 hours...")
        # time.sleep(7200)  # 2 hours

    except KeyboardInterrupt:
        print("\n\n🛑 Workflow stopped by user")
        # break
    except Exception as e:
        print(f"\n⚠️  Error in workflow cycle: {e}")
        import traceback
        traceback.print_exc()
        # print("💤 Sleeping for 2 hours before retry...")
        # time.sleep(7200)


if __name__ == "__main__":
    asyncio.run(main())
