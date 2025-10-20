# Phase 2 Validation Protocol

## Fact-Checker Agent Invocation

**Sequential execution** - Single fact-checker agent validates all streams.

```python
Task(
    subagent_type="fact-checker",
    description="Validate {topic} research sources",
    prompt="""
Validate all sources collected across {N} research streams.

## Source Files to Validate
- ./research-output/sources/stream-1-sources-{date}.md
- ./research-output/sources/stream-2-sources-{date}.md
- ./research-output/sources/stream-3-sources-{date}.md
- ./research-output/sources/stream-4-sources-{date}.md

## Validation Tasks

1. **Cross-Reference Claims**: Check if key claims are corroborated across multiple streams
2. **Source Credibility**: Assess reliability (official docs, reputable news, etc.)
3. **Recency Verification**: Confirm dates and ensure information is current
4. **Contradiction Detection**: Identify conflicting information between sources
5. **Critical Data Validation**: Verify specific data points, statistics, dates

## Output Format

Create: ./research-output/sources/validated-sources-{date}.md

[Use template from assets/validated-sources.template.md]

Provide thorough validation with confidence levels and specific source citations.
"""
)
```

## Validation Methodology

### 1. Cross-Reference Claims

**Process**:
1. Extract key claims from each stream
2. Check if claim appears in 2+ streams
3. Assign confidence based on corroboration count
   - 3+ streams: High confidence (✅✅✅)
   - 2 streams: Medium confidence (✅✅)
   - 1 stream: Low confidence (⚠️)

**Example**:
```
Claim: "Bitcoin fell 30% in Q3 2024"
- Stream 1: "BTC down 30% Q3" (Bloomberg) ✅
- Stream 2: "Major crypto losses summer 2024" (WSJ) ✅
- Stream 3: "BTC: $68k → $47k June-Sept" (CoinGecko) ✅
Confidence: HIGH (3 independent sources)
```

### 2. Source Credibility Assessment

**A-Tier Criteria**:
- Government/regulatory agencies
- Academic peer-reviewed papers
- Official data (on-chain, public APIs)
- Primary source documents
- Corroborated by 2+ B-tier sources

**B-Tier Criteria**:
- Established news media (WSJ, Bloomberg, Reuters)
- Reputable research firms
- Industry associations
- Expert opinions (verified credentials)

**C-Tier Criteria**:
- Single-source, unverified claims
- Opinion blogs without evidence
- Social media posts
- Promotional content
- Contradicted by higher-tier sources

### 3. Recency Verification

**Check**:
1. Publication date vs data currency
2. "Last updated" timestamps
3. Relevance to research question timeframe
4. Historical vs current context

**Flag if**:
- Data from >6 months ago presented as current
- Outdated regulatory information
- Historical prices used for current analysis
- Missing temporal context

### 4. Contradiction Detection

**Process**:
1. Identify same topic covered by multiple sources
2. Compare claims, data points, conclusions
3. Document conflicts
4. Propose resolutions:
   - Trust higher-tier source
   - Note both perspectives
   - Flag for human review
   - Additional research needed

**Example**:
```
Contradiction: ETH regulatory status
- Stream 1 (SEC filing): "ETH classified as commodity"
- Stream 2 (News article): "ETH security status unclear"
Resolution: Trust primary source (SEC filing) over news interpretation
```

### 5. Critical Data Validation

**Verify**:
- Numerical data (prices, percentages, volumes)
- Dates (event timelines, announcements)
- Quotes (attribution, context)
- Statistics (source, methodology)

**Methods**:
- Cross-reference with official sources
- Check calculations (e.g., percentage changes)
- Verify quote context
- Confirm methodology disclosed

## Output Structure

Use template: `assets/validated-sources.template.md`

**Required Sections**:
1. Executive Summary
   - Total sources reviewed
   - Credibility tier distribution (A/B/C counts)
   - Contradictions found
   - Critical findings validated

2. Source Credibility Tiers
   - A-Tier: High Credibility (list sources)
   - B-Tier: Medium Credibility (list sources)
   - C-Tier: Low Credibility (list sources with concerns)

3. Cross-Stream Validation
   - Consensus Findings (3+ streams agree)
   - Contradictions & Conflicts (with resolutions)

4. Critical Data Points Verified
   - List key facts with confidence levels
   - Show corroboration across sources

5. Red Flags / Human Review
   - Unverifiable claims
   - Significant contradictions
   - Data gaps

6. Recommendations for Analysis
   - Which sources to prioritize
   - Areas needing deeper investigation
   - Confidence levels for key findings

## Quality Standards

Validation considered complete when:

- ✅ All stream files reviewed
- ✅ Every source assigned credibility tier
- ✅ Key claims cross-referenced
- ✅ Contradictions identified and documented
- ✅ Critical data points verified
- ✅ Consensus findings extracted
- ✅ Recommendations provided

## Transition to Phase 3

Once validation complete:

1. **Update coordinator-status.md** - Mark validation phase complete
2. **Review red flags** - Ensure critical issues documented
3. **Prepare validated sources** - Confirm file ready for analysis
4. **Proceed to Phase 3** - Analysis (Sequential)

## Related Files

- `prompts/fact-checker.md` - Prompt template
- `assets/validated-sources.template.md` - Output template
- `../3-analysis/protocol.md` - Next phase protocol
