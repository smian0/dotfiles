# Phase 2: Validation

**Execution**: Sequential
**Duration**: 3-7 minutes
**Dependencies**: Phase 1 complete (all discovery streams)

## Overview

Validate all sources collected across discovery streams using the fact-checker agent. This phase ensures research quality through:

1. Cross-referencing claims across multiple streams
2. Assessing source credibility
3. Verifying recency and temporal accuracy
4. Detecting contradictions
5. Validating critical data points

## Execution Pattern

**Sequential Execution - Single fact-checker Agent**

```python
Task(
    subagent_type="fact-checker",
    description="Validate [topic] research sources",
    prompt="""
    [Comprehensive validation prompt]
    """
)
```

## Inputs

All discovery stream outputs from Phase 1:
- `./research-output/sources/stream-1-sources-YYYY-MM-DD.md`
- `./research-output/sources/stream-2-sources-YYYY-MM-DD.md`
- `./research-output/sources/stream-3-sources-YYYY-MM-DD.md`
- `./research-output/sources/stream-4-sources-YYYY-MM-DD.md`

## Outputs

Single validated sources file:
- `./research-output/sources/validated-sources-YYYY-MM-DD.md`

Contains:
- Executive summary (total sources, credibility distribution, contradictions)
- Source credibility tiers (A/B/C)
- Cross-stream validation (consensus findings, contradictions)
- Critical data points verified
- Red flags / areas needing human review
- Recommendations for analysis phase

## Validation Tasks

### 1. Cross-Reference Claims
Check if key claims are corroborated across multiple streams.

**Example**:
- Stream 1 claims: "Bitcoin down 30% in Q3 2024"
- Stream 2 mentions: "Major crypto losses in summer 2024"
- Stream 3 provides: "BTC price: $68k (June) → $47k (Sept)"
- **Validation**: ✅ Consensus across 3 streams, specific data matches

### 2. Source Credibility Assessment
Evaluate reliability using credibility tiers (A/B/C).

**Criteria**:
- A-Tier: Official, multiple corroborations, primary sources
- B-Tier: Reputable, single corroboration or unverified
- C-Tier: Conflicts, unverified, questionable sources

### 3. Recency Verification
Confirm dates and ensure information is current for the research question.

### 4. Contradiction Detection
Identify conflicting information between sources and propose resolutions.

### 5. Critical Data Validation
Verify specific data points, statistics, dates through cross-referencing.

## Quality Gates

Before proceeding to Phase 3:

- [ ] All stream files validated
- [ ] Source credibility tiers assigned
- [ ] Contradictions identified and documented
- [ ] Critical data points verified
- [ ] Consensus findings extracted
- [ ] Red flags documented (if any)

## Common Pitfalls

1. **Uncritical acceptance** - Failing to question sources
2. **Confirmation bias** - Ignoring contradictory evidence
3. **Missing contradictions** - Not identifying conflicts between sources
4. **Weak cross-referencing** - Not checking claims across streams
5. **Ignoring temporal context** - Missing that sources are outdated

## Transition to Phase 3

Once validation complete:
→ Proceed to Phase 3: Analysis (Sequential)

## Related Files

- `protocol.md` - Detailed validation protocol
- `prompts/fact-checker.md` - Template for fact-checker agent prompts
