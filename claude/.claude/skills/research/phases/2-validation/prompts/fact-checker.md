# Fact-Checker Agent Prompt Template

Use this template when invoking the fact-checker agent in Phase 2 (Validation).

Replace placeholders: `{research_question}`, `{stream_count}`, `{current_date}`, `{stream_files_list}`

**CRITICAL**: Use `{current_date}` for file paths - never hardcode dates like "2024-10-19"

---

## Prompt Template

```
Validate all sources collected across {stream_count} research streams.

## Research Question
{research_question}

## Source Files to Validate
{stream_files_list}
Example:
- ./research-output/sources/stream-1-sources-{current_date}.md
- ./research-output/sources/stream-2-sources-{current_date}.md
- ./research-output/sources/stream-3-sources-{current_date}.md
- ./research-output/sources/stream-4-sources-{current_date}.md

## Validation Tasks

1. **Cross-Reference Claims**: Check if key claims are corroborated across multiple streams
2. **Source Credibility**: Assess reliability (official docs, reputable news, etc.)
3. **Recency Verification**: Confirm dates and ensure information is current
4. **Contradiction Detection**: Identify conflicting information between sources
5. **Critical Data Validation**: Verify specific data points, statistics, dates

## Output Format

Create: ./research-output/sources/validated-sources-{date}.md

Structure:
```markdown
# Validated Sources - {research_question}
**Validation Date**: {date}
**Source Period**: [Date range of sources validated]

## Executive Summary
- Total sources reviewed: X
- High credibility (A-tier): X
- Medium credibility (B-tier): X
- Low credibility (C-tier): X
- Contradictions found: X
- Critical findings validated: X

## Source Credibility Tiers

### A-Tier: High Credibility
[List sources with official status, multiple corroborations]

### B-Tier: Medium Credibility
[List sources with single corroboration or reputable but unverified]

### C-Tier: Low Credibility / Needs Review
[List sources with conflicts or unverified claims]

## Cross-Stream Validation

### Consensus Findings
[Claims validated across 3+ streams with confidence levels]

### Contradictions & Conflicts
[Areas where sources disagree with proposed resolutions]

## Critical Data Points Verified
[List key facts with validation status and confidence levels]

## Red Flags / Areas Needing Human Review
[List concerning discrepancies or unverifiable claims]

## Recommendations for Analysis Phase
[Guidance on which sources to prioritize, areas for deeper investigation]
```

## Validation Standards

### Cross-Reference Confidence Levels
- **HIGH (✅✅✅)**: 3+ independent sources confirm
- **MEDIUM (✅✅)**: 2 independent sources confirm
- **LOW (⚠️)**: Single source, needs verification

### Source Credibility Criteria

**A-Tier Requirements**:
- Government/regulatory agencies
- Academic peer-reviewed research
- Official data sources (on-chain, APIs)
- Primary documents (filings, reports)
- Corroborated by 2+ B-tier sources

**B-Tier Requirements**:
- Established news media (WSJ, Bloomberg, Reuters, etc.)
- Reputable research firms (Messari, Glassnode, etc.)
- Industry associations
- Verified expert opinions

**C-Tier Indicators**:
- Single-source claims
- Opinion without evidence
- Social media posts
- Promotional content
- Contradicted by higher-tier sources

### Contradiction Resolution

When sources conflict:
1. **Trust higher-tier source** (A-tier > B-tier > C-tier)
2. **Note both perspectives** if tiers equal
3. **Flag for human review** if critical to analysis
4. **Recommend additional research** if resolution unclear

### Critical Data Validation

Verify:
- **Numerical accuracy**: Check calculations, percentages
- **Date accuracy**: Confirm event timelines
- **Quote accuracy**: Verify attribution and context
- **Statistical validity**: Check methodology disclosure

## Quality Requirements

Your validation MUST achieve:
- ✅ All stream sources reviewed and tiered
- ✅ Key claims cross-referenced across streams
- ✅ Contradictions identified with resolutions
- ✅ Critical data points verified with confidence levels
- ✅ Consensus findings extracted (3+ stream agreement)
- ✅ Red flags documented with specific concerns
- ✅ Recommendations provided for analysis phase

Deliver rigorous validation with specific source citations and confidence assessments.
```

---

## Usage Example

```python
Task(
    subagent_type="fact-checker",
    description="Validate cryptocurrency market research",
    prompt=f"""
Validate all sources collected across 4 research streams.

## Research Question
Why is the cryptocurrency market suffering in {current_year}?

## Source Files to Validate
- ./research-output/sources/stream-1-sources-{current_date}.md
- ./research-output/sources/stream-2-sources-{current_date}.md
- ./research-output/sources/stream-3-sources-{current_date}.md
- ./research-output/sources/stream-4-sources-{current_date}.md

## Validation Tasks

1. **Cross-Reference Claims**: Check if key claims are corroborated across multiple streams
2. **Source Credibility**: Assess reliability (official docs, reputable news, etc.)
3. **Recency Verification**: Confirm dates and ensure information is current
4. **Contradiction Detection**: Identify conflicting information between sources
5. **Critical Data Validation**: Verify specific data points, statistics, dates

[... rest of template ...]
"""
)
```
