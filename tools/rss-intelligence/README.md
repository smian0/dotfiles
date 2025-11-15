# RSS Intelligence Workflow

Automated RSS feed processing with AI-powered entity extraction, sentiment analysis, and knowledge graph integration.

## Architecture

**Simplified MVP Design**:
- ✅ Agno-native scheduling (Python loop, no external schedulers)
- ✅ Single-model pattern (structured output, no parser complexity)
- ✅ Free Ollama Cloud models only (`glm-4.6:cloud`, `deepseek-v3.1:671b-cloud`)
- ✅ Agno's built-in `Newspaper4kTools` for content extraction
- ✅ Basic URL deduplication via session state
- ✅ Parallel analysis (entities, sentiment, topics)
- ✅ Graphiti knowledge graph integration

## Quick Start

### Prerequisites

1. **Ollama Cloud Models** (free tier):
   ```bash
   # Models used:
   # - glm-4.6:cloud (fast, general)
   # - deepseek-v3.1:671b-cloud (reasoning)
   ```

2. **Graphiti MCP Server** (optional, for knowledge graph):
   ```bash
   # Start Graphiti if using knowledge graph features
   cd ~/Services/graphiti-mcp
   docker-compose up -d
   ```

### Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run with uv (handles dependencies automatically)
cd ~/dotfiles/tools/rss-intelligence
uv run test_single_run.py
```

### Testing

**Single Run Test** (recommended first):
```bash
uv run test_single_run.py
```

**Continuous Operation** (2-hour cycles):
```bash
uv run rss_intelligence_workflow.py
```

Stop with `Ctrl+C`.

## Features

### 1. RSS Feed Processing
- Fetches from BBC World News and NYT World News
- URL deduplication to avoid re-processing
- Limits to 10 articles per cycle (cost control)

### 2. Content Extraction
- Uses Agno's `Newspaper4kTools` for full article extraction
- Extracts title, summary, published date, and full content

### 3. Parallel Analysis
- **Entity Extraction**: People, organizations, locations, events, concepts
- **Sentiment Analysis**: Positive/negative/neutral with confidence scores
- **Topic Classification**: Categorizes into Politics, Business, Tech, Health, etc.

### 4. Knowledge Graph Integration
- Updates Graphiti with extracted entities and relationships
- Stores articles as episodes with temporal metadata
- Enables graph queries for entity relationships and trends

### 5. Newsletter Generation
- Generates Markdown newsletter with top stories
- Highlights key entities and recurring themes
- Saves to `newsletters/` with timestamp

## Workflow Steps

```
1. fetch_feeds              → Fetch RSS feeds with deduplication
2. prepare_urls             → Prepare URLs for content extraction
3. extract_content          → Extract full article content (Newspaper4k)
4. merge_content            → Merge extracted content back into articles
5. format_articles          → Format for parallel analysis
6. parallel_analysis        → Run entity/sentiment/topic extraction in parallel
   ├─ extract_entities
   ├─ analyze_sentiment
   └─ extract_topics
7. prepare_graphiti_episodes → Prepare articles for knowledge graph
8. ingest_to_graphiti       → Ingest into Graphiti using MCP tools
9. prepare_newsletter_context → Prepare newsletter context with metadata
10. generate_newsletter     → Generate newsletter from analysis
11. save_newsletter         → Save to newsletters/ directory
```

## Configuration

### RSS Feeds

Edit `rss_intelligence_workflow.py` → `fetch_rss_feeds()`:
```python
feeds = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    # Add more feeds here
]
```

### Cycle Interval

Default: 2 hours (7200 seconds)

Change in `main()`:
```python
time.sleep(7200)  # Change to desired seconds
```

### Article Limit

Default: 10 articles per cycle

Change in `fetch_rss_feeds()`:
```python
new_articles = new_articles[:10]  # Change limit
```

## File Structure

```
rss-intelligence/
├── rss_intelligence_workflow.py  # Main workflow
├── test_single_run.py             # Single-run test
├── rss_intelligence.db            # SQLite workflow storage
├── newsletters/                   # Generated newsletters
│   └── newsletter_20251113_143022.md
└── README.md
```

## Models Used

### Free Tier (Ollama Cloud)
- **glm-4.6:cloud**: Fast general-purpose (192 tok/s)
- **deepseek-v3.1:671b-cloud**: Reasoning and analysis (76 tok/s)

### Cost
- $0 per cycle (all models are free via Ollama Cloud)
- No API keys required for Ollama Cloud

## Extending the Workflow

### Add Graphiti Queries

Create a new agent to query the knowledge graph:
```python
query_agent = Agent(
    name="Graph Query Agent",
    model=Ollama(id="deepseek-v3.1:671b-cloud"),
    tools=[graphiti_mcp],
    instructions="Query Graphiti for entity relationships and trends",
)
```

### Add Email Delivery

Add a new step to send newsletters via email:
```python
Step(
    name="send_email",
    executor=send_newsletter_email,
    description="Send newsletter via email",
)
```

### Add More Analysis

Add new parallel steps for:
- Fact-checking
- Source credibility scoring
- Duplicate detection
- Geographic clustering

## Troubleshooting

**No articles fetched**:
- Check RSS feed URLs are accessible
- Verify internet connection
- Check `processed_urls` set isn't too large

**Content extraction fails**:
- Newspaper4k may struggle with paywalled sites
- Some sites block automated access
- Try alternative content extraction tools

**Knowledge graph not updating**:
- Verify Graphiti MCP server is running
- Check Docker logs: `docker logs graphiti-mcp-server`
- Ensure models have sufficient context window

**Models not responding**:
- Check Ollama is running: `ollama ps`
- Verify models are pulled: `ollama list`
- Try switching to different model

## Next Steps

1. ✅ **Test single run** - Verify workflow completes
2. ✅ **Check newsletter output** - Review generated content
3. ⏭️ **Query knowledge graph** - Explore entity relationships
4. ⏭️ **Enable continuous operation** - Start 2-hour cycles
5. ⏭️ **Add monitoring** - Track cycle duration and article counts

## Related Projects

- [Agno Framework](https://docs.agno.com)
- [Graphiti Knowledge Graphs](https://github.com/getzep/graphiti)
- [Newspaper4k](https://github.com/AndyTheFactory/newspaper4k)

**Last Updated**: 2025-11-13
