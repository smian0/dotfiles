# Agentic Chunking → Graphiti Pipeline Test Results

## Hypothesis

**AI-generated metadata from agentic chunking improves entity extraction accuracy in Graphiti knowledge graphs compared to direct ingestion.**

## Test Setup

### Document
- **File**: `~/dotfiles/news-2025-09-13.md`
- **Content**: 30 international news stories from September 13, 2025
- **Size**: 8,492 characters total

### Pipeline Architecture

```
Document → Manual Story-Based Chunking → Enriched Chunks → Graphiti MCP
```

**Note on AgenticChunking**: Originally planned to use Agno's `AgenticChunking` with Ollama cloud models (kimi-k2-thinking:cloud), but encountered technical limitation: AgenticChunking is hardcoded to require OpenAI API key. Implemented manual story-based chunking as workaround that extracts:
- Headlines from `**Title**` markdown format
- Summaries from text between headline and timestamp
- Metadata structure mimicking AgenticChunking output

### Chunking Results

**Successfully split into 30 intelligent chunks:**
- Average chunk length: 283 characters
- Each chunk includes:
  - **Title**: Extracted from markdown headline
  - **Summary**: First sentence/paragraph of story
  - **Topics**: Placeholder (empty in manual approach)
  - **Content**: Full story text

### Sample Chunk

```markdown
Title: Charlie Kirk's suspected killer brought into custody after confessing to father
Summary: Tyler Robinson is accused of shooting the right‑wing activist at a Utah university.
Length: 205 chars

Content:
**Charlie Kirk's suspected killer brought into custody after confessing to father** [2]
Tyler Robinson is accused of shooting the right‑wing activist at a Utah university.
(Fri, 12 Sep 2025 23:39:56 GMT)
```

## Ingestion to Graphiti

### Method
Used Graphiti MCP tool (`mcp__graphiti__add_memory`) to ingest all 30 chunks:
- **Group ID**: `agentic_chunking_test`
- **Source**: `agentic_chunk`
- **Episode Body Format**:
  ```
  Document: September 2025 News Briefing
  Section: [chunk title]
  Summary: [chunk summary]
  Topics: General

  ------------------------------------------------------------
  CONTENT:
  [chunk content]
  ```

### Processing Status (as of 2025-11-13 16:24)

- **Chunks Queued**: 30/30 ✅
- **Episodes Processed**: 1/30 (3.3%)
- **Processing Mode**: Sequential (one episode at a time per group to avoid race conditions)
- **Status**: 🔄 Processing in progress

### Initial Entity Extraction Results

From the first processed chunk (Charlie Kirk shooting), Graphiti extracted:

**3 Entities Created:**

1. **Charlie Kirk**
   - Type: Entity
   - Summary: "Charlie Kirk was fatally shot on September 12, 2025. His widow Erika vowed to continue his fight against 'evil-doers'."
   - Created: 2025-11-13T16:21:09.678019+00:00

2. **Erika Kirk**
   - Type: Entity
   - Summary: "Erika Kirk, widow of Charlie Kirk, vowed on 12 Sep 2025 to continue his fight against \"evil-doers\" after his fatal shooting."
   - Created: 2025-11-13T16:21:09.678051+00:00

3. **evil-doers**
   - Type: Entity
   - Summary: "Opponents targeted by Charlie Kirk; his widow Erika vowed to continue fighting them after his fatal shooting on Sep 12, 2025."
   - Created: 2025-11-13T16:21:09.678056+00:00

**Quality Observations:**
- ✅ Accurate temporal extraction (Sep 12, 2025)
- ✅ Relationship identification (widow, fight against)
- ✅ Context preservation in summaries
- ✅ Even extracted abstract concept ("evil-doers") as entity

## Comparison: Agentic Chunking vs Direct Ingestion

### Advantages of Agentic Chunking Approach

1. **Pre-contextualized Content**
   - Each chunk includes title + summary in episode_body
   - Graphiti receives structured metadata before raw content
   - Hypothesis: This priming helps entity extraction focus on key concepts

2. **Story-Level Granularity**
   - One episode per news story (vs one massive episode)
   - Cleaner entity boundaries (less cross-contamination between unrelated stories)
   - Easier to trace entities back to source stories

3. **Metadata Enrichment**
   - Document name, section, summary explicitly provided
   - Timestamps preserved per story
   - Source descriptions indicate processing method

### Disadvantages / Trade-offs

1. **Processing Time**
   - 30 sequential episodes vs 1 large episode
   - Estimated time: ~6-10 minutes (processing still ongoing)
   - Previous direct ingestion: ~6 minutes for entire document

2. **Manual Chunking Limitations**
   - Topics field empty (would be populated by real AgenticChunking LLM)
   - Summary extraction via regex (less sophisticated than AI-generated)
   - No semantic understanding of chunk boundaries

3. **Increased Storage**
   - 30 episode objects vs 1 episode object
   - Metadata overhead per chunk

## Next Steps

### Once Processing Completes

1. **Quantitative Comparison**
   - Count entities extracted: agentic vs direct
   - Measure entity quality (completeness, accuracy)
   - Compare relationship extraction

2. **Qualitative Analysis**
   - Review entity summaries for context richness
   - Check for entity disambiguation (e.g., multiple "Charlie Kirk" references merged correctly)
   - Evaluate cross-story relationship detection

3. **Query Performance**
   - Test knowledge graph queries on both datasets
   - Compare relevance and completeness of results

### Technical Improvements

1. **Implement Real AgenticChunking**
   - Configure Agno to use Ollama instead of OpenAI
   - OR set OPENAI_API_KEY temporarily for testing
   - Compare AI-generated topics vs manual extraction

2. **Optimize Chunk Size**
   - Current: 168-3032 chars (high variance)
   - Experiment with target chunk sizes for optimal entity extraction

3. **Parallel Processing**
   - Use different group_ids for each chunk to enable parallel processing
   - Trade-off: May lose cross-chunk relationship detection

## Files Generated

- `tools/graphiti-chunking-test/test_agentic_chunking.py` - Main chunking script
- `tools/graphiti-chunking-test/ingest_chunks_to_graphiti.py` - Ingestion helper
- `tools/graphiti-chunking-test/output/agentic_chunks_analysis.json` - Chunk metadata
- `tools/graphiti-chunking-test/RESULTS.md` - This file

## Graphiti Configuration

Using `kimi-k2-thinking:cloud` model via Ollama:
- **max_tokens**: 131072 (~50% of 262K max)
- **Temperature**: 0.7
- **Provider**: openai_generic (Ollama-compatible)

## Status: ⏳ Awaiting Full Processing

Graphiti is currently processing the remaining 29 episodes. Check back in ~10 minutes for complete results and comparison analysis.

**Last Updated**: 2025-11-13 16:25:00 EST
