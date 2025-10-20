# Phase 1 Discovery Protocol (PARALLEL)

## Parallel Execution Critical Requirements

**⚡ MUST execute all Task calls in a SINGLE message ⚡**

**Correct (Parallel)**:
```python
# Single message with 4 Task calls
Task(subagent_type="web-researcher", description="Stream 1", ...)
Task(subagent_type="web-researcher", description="Stream 2", ...)
Task(subagent_type="web-researcher", description="Stream 3", ...)
Task(subagent_type="web-researcher", description="Stream 4", ...)
# All execute simultaneously
```

**Incorrect (Sequential - SLOW!)**:
```python
# Message 1
Task(subagent_type="web-researcher", description="Stream 1", ...)
# Wait for completion...
# Message 2
Task(subagent_type="web-researcher", description="Stream 2", ...)
# This takes 4x longer!
```

## Stream Allocation Strategy

### For Research Question: "[TOPIC]"

1. **Identify Key Dimensions**
   - What are the major perspectives on this topic?
   - Which factors/stakeholders are most important?
   - Are there temporal, geographic, or sectoral angles?

2. **Allocate Streams**
   - Stream 1: Most critical dimension (highest priority)
   - Stream 2: Secondary dimension (supporting evidence)
   - Stream 3: Contextual dimension (broader context)
   - Stream 4: Contrarian/niche dimension (alternative views)

### Stream Count Guidelines

- **3 streams**: Simple topics with clear dimensions
- **4 streams**: Default for most complex topics
- **5 streams**: Highly multifaceted topics requiring maximum coverage

## Web-Researcher Agent Prompt Structure

For each stream, use template from `prompts/web-researcher.md`:

```python
Task(
    subagent_type="web-researcher",
    description="Stream [N]: [Brief angle description]",
    prompt=f"""
Research [specific angle] for the question: {research_question}

## Your Research Focus
[Detailed description of what this stream should investigate]

## Key Areas to Cover
- [Specific area 1]
- [Specific area 2]
- [Specific area 3]

## Deliverables Required
1. **10-20 quality sources** with:
   - Source name and URL
   - Credibility assessment (A/B/C tier)
   - Key findings summary
   - Specific data points with dates

2. **Source diversity**:
   - Primary sources (government, official data)
   - Secondary sources (established media, research firms)
   - Geographic diversity where applicable

3. **Structured output** at ./research-output/sources/stream-{N}-sources-{date}.md

## Research Rigor Standards
- Multiple search queries with different angles
- Adversarial search (test contrary perspectives)
- Source diversity (not just top results)
- Primary source prioritization
- Date verification for current events
"""
)
```

## Source Credibility Tiers

**A-Tier: High Credibility**
- Government agencies (Fed, SEC, Treasury)
- Official data sources (on-chain data, public APIs)
- Academic peer-reviewed papers
- Primary source documents
- Regulatory filings

**B-Tier: Medium Credibility**
- Established news media (WSJ, Bloomberg, Reuters)
- Reputable research firms (Messari, Glassnode)
- Industry associations
- Expert opinions from credible sources

**C-Tier: Low Credibility / Needs Verification**
- Social media posts
- Opinion blogs
- Unverified claims
- Single-source reporting
- Promotional content

## Research Rigor Requirements

Each stream MUST employ:

### 1. Multiple Search Queries
Don't rely on single query. Try:
- Direct question format
- Different terminology
- Related concepts
- Temporal variations (recent vs historical)

### 2. Adversarial Search
Test contrary perspectives:
- "Why X is NOT true"
- "Criticisms of X"
- "Alternative explanations for X"

### 3. Source Diversity
Avoid echo chambers:
- Different publishers
- Different geographic regions
- Different ideological perspectives
- Mix of primary and secondary sources

### 4. Primary Source Prioritization
Prefer original data:
- Government reports over news articles about reports
- Research papers over summaries
- On-chain data over aggregator sites
- Company filings over analyst commentary

### 5. Date Verification
Always note temporal context:
- Publication date
- Data collection period
- Last updated timestamp
- Relevance to current situation

## Output Format

Each stream outputs to: `./research-output/sources/stream-[N]-sources-YYYY-MM-DD.md`

Use template from `assets/stream-sources.template.md`

**Required sections**:
1. Stream metadata (number, angle, date)
2. Executive summary (3-5 bullet points)
3. Key sources (10-20 entries with credibility tiers)
4. Additional context

## Quality Validation

Before proceeding, verify each stream has:

- [ ] 10-20 quality sources documented
- [ ] Credibility tiers assigned (A/B/C)
- [ ] Specific data points with dates
- [ ] Source URLs included
- [ ] Key findings summarized
- [ ] Executive summary present
- [ ] Geographic/institutional diversity
- [ ] Primary sources prioritized (when available)

## Failure Handling

If a stream fails:

1. **Log failure** in coordinator-status.md
2. **Continue with remaining streams**
3. **Minimum 2 successful streams** required to proceed
4. **Notify user** of partial failure

## Success Criteria

Discovery phase successful when:

- ✅ 2+ streams completed successfully
- ✅ 30+ total sources collected (across all streams)
- ✅ 80%+ A/B tier source credibility
- ✅ Source diversity across geography/institutions
- ✅ Temporal accuracy (dates verified)
- ✅ All outputs properly formatted

## Transition to Phase 2

Once all streams complete:

1. **Update coordinator-status.md** - Mark discovery phase complete
2. **Verify quality gates** - Check minimum requirements met
3. **Prepare file list** - Note all stream output files for validation
4. **Proceed to Phase 2** - Validation (Sequential)

## Related Files

- `prompts/web-researcher.md` - Prompt template for web-researcher agents
- `assets/stream-sources.template.md` - Output template for streams
- `../0-initialization/protocol.md` - Initialization protocol
- `../2-validation/protocol.md` - Next phase protocol
