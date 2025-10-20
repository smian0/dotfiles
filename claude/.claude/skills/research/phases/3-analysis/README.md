# Phase 3: Analysis

**Execution**: Sequential
**Duration**: 5-10 minutes
**Dependencies**: Phase 2 complete (validation)

## Overview

Conduct deep analysis using the deep-research-agent. This phase synthesizes findings from all streams to identify:

1. Root causes (primary, secondary, tertiary)
2. Patterns and convergence points
3. Causal chains and relationships
4. Strategic insights
5. Forward-looking implications

## Execution Pattern

```python
Task(
    subagent_type="deep-research-agent",
    description="Analyze [topic] findings",
    prompt="""[Comprehensive analysis prompt]"""
)
```

## Inputs

- Validated sources: `./research-output/sources/validated-sources-YYYY-MM-DD.md`
- All stream files: `./research-output/sources/stream-*-YYYY-MM-DD.md`

## Outputs

- `./research-output/analysis/comprehensive-analysis-YYYY-MM-DD.md`

Contains:
- Executive summary (3-5 key findings)
- Root cause hierarchy
- Pattern analysis
- Causal chain map
- Strategic insights
- Forward-looking implications (short/medium/long-term)

## Analysis Framework

1. **Root Cause Analysis** - Identify and rank causes with confidence levels
2. **Pattern Recognition** - Find convergence points, amplification mechanisms, feedback loops
3. **Causal Chain Mapping** - Trace cause-effect relationships
4. **Comparative Analysis** - Compare to historical events or analogous situations
5. **Stakeholder Impact** - Assess differential impacts
6. **Forward-Looking** - Short (1-3mo), medium (3-12mo), long-term (1-3yr) predictions

## Quality Gates

- [ ] Root causes identified and ranked
- [ ] Patterns across streams documented
- [ ] Causal chains mapped with evidence
- [ ] Strategic insights extracted (5-7 minimum)
- [ ] Forward-looking implications provided
- [ ] Research gaps acknowledged

## Transition to Phase 4

→ Proceed to Phase 4: Synthesis (Sequential)

## Related Files

- `protocol.md` - Detailed analysis protocol
- `prompts/deep-research-agent.md` - Template for deep-research-agent prompts
