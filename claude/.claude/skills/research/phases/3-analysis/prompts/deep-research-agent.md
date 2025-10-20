# Deep-Research-Agent Prompt Template

## Prompt Template

```
Conduct deep analysis of comprehensive research on: {research_question}

## Input Materials
Read and analyze:
1. **Validated Sources**: ./research-output/sources/validated-sources-{date}.md
2. **Stream 1**: ./research-output/sources/stream-1-sources-{date}.md
3. **Stream 2**: ./research-output/sources/stream-2-sources-{date}.md
4. **Stream 3**: ./research-output/sources/stream-3-sources-{date}.md
4. **Stream N**: ./research-output/sources/stream-N-sources-{date}.md

## Analysis Framework

### 1. Root Cause Analysis
Identify and rank primary, secondary, tertiary causes with confidence levels:
- Primary (Highest Impact): [Necessary condition]
- Secondary (Major Factors): [2-3 key contributors]
- Tertiary (Amplifying): [3-5 contextual factors]

### 2. Pattern Recognition
Identify recurring themes across all streams:
- Convergence points where multiple factors intersect
- Amplification mechanisms (how causes reinforce)
- Feedback loops (self-reinforcing cycles)

### 3. Causal Chain Mapping
Trace cause-and-effect relationships with evidence grades (A/B/C)

### 4. Comparative Analysis
Compare to historical events or analogous situations if applicable

### 5. Stakeholder Impact Analysis
Assess differential impacts across affected parties

### 6. Forward-Looking Implications
- Short-term (1-3 months): [Immediate predictions with confidence]
- Medium-term (3-12 months): [Trajectory analysis]
- Long-term (1-3 years): [Structural change predictions]

## Output Structure

Create: ./research-output/analysis/comprehensive-analysis-{date}.md

```markdown
# Comprehensive Analysis: {research_question}
**Analysis Date**: {date}
**Data Period**: [Date range of analyzed sources]

## Executive Summary
[3-5 key findings ranked by importance]

## Root Cause Hierarchy
- **Primary Cause (Highest Impact)**: [with evidence and confidence %]
- **Secondary Causes**: [2-3 major factors]
- **Tertiary Causes**: [3-5 amplifying factors]

## Pattern Analysis
[Cross-stream convergence points, amplification mechanisms, feedback loops]

## Causal Chain Map
[Visual text representation of cause → effect pathways with evidence grades]

## Strategic Insights
[5-7 key insights with: Evidence → Implication → Forward-looking]

## Unanswered Questions & Research Gaps
[Areas requiring further investigation]

## Forward-Looking Implications
- Short-term (1-3 months): [predictions with confidence]
- Medium-term (3-12 months): [trajectories]
- Long-term (1-3 years): [structural changes]

## Recommendations for Synthesis Phase
- Priority themes to emphasize
- Narrative structure suggestions
- Key visualizations needed
```

Provide evidence-based analysis with confidence levels throughout.
```

## Quality Requirements

- ✅ Root causes ranked with HIGH/MEDIUM/LOW confidence
- ✅ Cross-stream patterns identified
- ✅ Causal chains mapped with evidence grades (A/B/C)
- ✅ 5-7 strategic insights (Evidence → Implication → Forward)
- ✅ 3 time horizons for forward-looking (short/med/long)
- ✅ Research gaps explicitly acknowledged
- ✅ Recommendations for synthesis provided
