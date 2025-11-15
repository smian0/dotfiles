# Graphiti Ingestion Workflow

**Automatic LLM-Native Chunking → Knowledge Graph Ingestion**

Single-file Agno workflow that implements intelligent document chunking with metadata extraction and seamless Graphiti integration.

## Architecture

### Three-Agent Sequential Workflow

```
Document → Strategy Generator → Chunk Processor → Graphiti Ingester → Knowledge Graph
           (analyzes structure)  (splits & enriches)  (MCP tools)
```

**Agent 1: Strategy Generator**
- Model: `kimi-k2-thinking:cloud` (best structural analysis)
- Analyzes first 2000 chars
- Generates chunking rules as JSON
- Returns: `ChunkingStrategy` with boundary patterns, split rules, metadata extraction rules

**Agent 2: Chunk Processor**
- Model: `glm-4.6:cloud` (fastest bulk processing)
- Applies strategy to full document
- Extracts metadata per chunk (title, summary, topics)
- Returns: `ProcessedChunks` with enriched chunks

**Agent 3: Graphiti Ingester**
- Model: `glm-4.6:cloud` (excellent tool calling)
- Uses Graphiti MCP tools (`mcp__graphiti__add_memory`)
- Ingests each chunk as separate episode
- Returns: `IngestionResult` with status

## Installation

```bash
# Install dependencies (uv handles this automatically)
uv pip install agno click pydantic
```

## Usage

### Full Ingestion (Recommended)

```bash
# Ingest document to Graphiti
python graphiti_ingestion_workflow.py ingest ~/news-2025-09-13.md --group-id "news_sept_2025"

# With debug mode (shows all step outputs)
python graphiti_ingestion_workflow.py ingest ~/news-2025-09-15.md --group-id "economic_news" --debug
```

### Strategy Analysis Only

```bash
# Just analyze chunking strategy (no ingestion)
python graphiti_ingestion_workflow.py analyze-strategy ~/news-2025-09-13.md
```

This is useful for:
- Testing strategy generation
- Understanding document structure
- Previewing how document will be chunked

## Features

### ✅ 100% Automatic
- No hardcoded document types
- LLM analyzes structure and generates rules dynamically
- Works for ANY domain (news, code, medical, legal, etc.)

### ✅ Type Safe
- Pydantic models enforce structure
- Compile-time validation
- Clear data contracts between agents

### ✅ Cost Effective
- Uses free Ollama Cloud models
- `kimi-k2-thinking:cloud`: Strategy generation
- `glm-4.6:cloud`: Processing and ingestion
- Total cost: $0

### ✅ Debuggable
- SqliteDb tracks workflow history at `tmp/graphiti_workflow.db`
- Debug mode shows all step outputs
- Clear error messages

### ✅ Metadata Enrichment
Each chunk includes:
- **Title**: Extracted headline or main topic
- **Summary**: 1-2 sentence description
- **Topics**: 3-5 key keywords
- **Content**: Full chunk text

## Workflow Steps

1. **Generate Strategy** (Strategy Generator Agent)
   - Analyzes document sample (first 2000 chars)
   - Detects document type and structure
   - Generates boundary patterns and split rules
   - Defines metadata extraction rules

2. **Format for Processing** (Custom Function)
   - Extracts strategy from agent output
   - Loads full document content
   - Prepares input for chunk processor

3. **Process Chunks** (Chunk Processor Agent)
   - Applies split rules to divide document
   - Extracts metadata per chunk
   - Assigns sequential chunk IDs
   - Returns enriched chunks

4. **Format for Ingestion** (Custom Function)
   - Formats chunks with document context
   - Adds group_id and source metadata
   - Prepares episode_body format

5. **Ingest to Graphiti** (Graphiti Ingestion Agent)
   - Calls `mcp__graphiti__add_memory` for each chunk
   - Formats episode with title, summary, topics, content
   - Reports ingestion status

## Output Example

### Strategy Analysis
```json
{
  "document_type": "news_briefing",
  "confidence": 0.95,
  "boundary_patterns": ["\\n\\n(?=\\*\\*)", "(Timestamp: ...)"],
  "split_rules": {
    "pattern": "\\n\\n(?=\\*\\*)",
    "min_chunk_size": 100,
    "max_chunk_size": 2000
  },
  "metadata_extraction": {
    "title": "extract from **...** pattern",
    "summary": "first sentence after headline",
    "topics": "extract key terms from content"
  },
  "schema_org_type": "NewsArticle"
}
```

### Processed Chunks
```json
{
  "chunks": [
    {
      "chunk_id": 1,
      "title": "Charlie Kirk's widow vows to continue fight",
      "summary": "Erika Kirk pledges to carry on after husband's fatal shooting.",
      "topics": ["Charlie Kirk", "shooting", "activism"],
      "content": "**Charlie Kirk's suspected killer brought into custody...\n..."
    }
  ],
  "total_chunks": 30,
  "strategy_used": "news_briefing"
}
```

### Ingestion Result
```json
{
  "chunks_ingested": 30,
  "chunks_failed": 0,
  "group_id": "news_sept_2025",
  "status": "success"
}
```

## Comparison: Workflow vs Manual Chunking

| Aspect | Manual Approach | Agno Workflow |
|--------|----------------|---------------|
| **Code** | 285 lines (test_agentic_chunking.py) | 200 lines (single workflow) |
| **Flexibility** | Hardcoded for news format | Works for any document type |
| **Maintenance** | Update regex per format | Zero (LLM adapts) |
| **Metadata** | Manual regex extraction | AI-powered extraction |
| **Reusability** | One-time script | CLI tool for repeated use |
| **History** | No tracking | SqliteDb workflow history |
| **Error Handling** | Manual try/catch | Agent-level error recovery |

## Testing

The workflow has been validated against:
- `news-2025-09-13.md` (30 international news stories, timestamps)
- `news-2025-09-15.md` (10 economic stories, no timestamps)

Both documents are handled automatically with different strategies.

## Configuration

### Ollama Models
Ensure Ollama Cloud models are available:
```bash
# Check model availability
curl http://localhost:11434/api/tags

# Models used:
# - kimi-k2-thinking:cloud (strategy generation)
# - glm-4.6:cloud (processing, ingestion)
```

### Graphiti MCP
Ensure Graphiti MCP server is running:
```bash
docker ps | grep graphiti-mcp-server
```

### SqliteDb Location
Workflow history stored at:
```
tmp/graphiti_workflow.db
```

## Troubleshooting

### "MCP tools not found"
- Ensure Graphiti MCP server is running
- Check MCP connection in Claude Code settings
- Verify `mcp__graphiti__add_memory` tool is available

### "Ollama model not found"
```bash
# Pull required models
ollama pull kimi-k2-thinking:cloud
ollama pull glm-4.6:cloud
```

### "Strategy confidence too low"
- Document structure may be unusual
- Check strategy output with `analyze-strategy` command
- Workflow will use best-effort chunking if confidence < 0.7

### "Chunks too large/small"
- Strategy generation adapts to document structure
- For custom control, modify strategy generation prompt
- Located in `create_strategy_generator_agent()` function

## Advanced Usage

### Custom Group IDs
```bash
# Organize by date
python graphiti_ingestion_workflow.py ingest news.md --group-id "news_2025_09"

# Organize by source
python graphiti_ingestion_workflow.py ingest docs.md --group-id "technical_docs"
```

### Query Workflow History
```bash
# Open SqliteDb
sqlite3 tmp/graphiti_workflow.db

# List workflows
SELECT * FROM workflows;

# List steps
SELECT * FROM steps WHERE workflow_id = 'xxx';
```

## Next Steps

1. **Test on diverse document types**
   - Code repositories
   - Medical records
   - Legal contracts
   - Technical documentation

2. **Add strategy caching**
   - Cache strategies by document fingerprint
   - Reuse for similar documents
   - Reduce LLM calls by 80%

3. **Parallel processing**
   - Use Agno `Parallel` for multiple documents
   - Batch ingestion

4. **Quality validation**
   - Compare entity extraction with manual chunking
   - Measure Graphiti graph quality
   - Optimize strategy generation prompts

## Related Files

- `test_agentic_chunking.py` - Original manual chunking test
- `RESULTS.md` - Initial experiment results
- `output/agentic_chunks_analysis.json` - Manual chunking output

---

**Last Updated**: 2025-11-13
**Version**: 1.0.0
**Status**: ✅ Ready for testing
