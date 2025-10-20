# Phase 4: Synthesis

**Execution**: Sequential
**Duration**: 5-10 minutes
**Dependencies**: Phase 3 complete (analysis)

## Overview

Synthesize all research findings into publication-ready reports using the report-synthesizer agent.

Produces two deliverables:
1. **Executive Summary** (2-3 pages) - For C-suite, policymakers, board members
2. **Full Report** (15-20 pages) - For analysts, traders, researchers

## Execution Pattern

```python
Task(
    subagent_type="report-synthesizer",
    description="Synthesize [topic] research report",
    prompt="""[Comprehensive synthesis prompt]"""
)
```

## Inputs

- Comprehensive analysis: `./research-output/analysis/comprehensive-analysis-YYYY-MM-DD.md`
- Validated sources: `./research-output/sources/validated-sources-YYYY-MM-DD.md`
- All stream files: `./research-output/sources/stream-*-YYYY-MM-DD.md`

## Outputs

1. `./research-output/report/executive-summary-YYYY-MM-DD.md`
   - Single-paragraph bottom line
   - 5 critical insights with confidence levels
   - Timeline of key events
   - Root cause breakdown (weighted)
   - Forward-looking implications (3 time horizons)
   - Stakeholder recommendations
   - Leading indicators to watch

2. `./research-output/report/full-report-YYYY-MM-DD.md`
   - Complete table of contents
   - Methodology documentation
   - Detailed timeline
   - Root cause analysis with evidence grades
   - Multi-stream findings synthesis
   - Cross-stream pattern analysis
   - Stakeholder impact assessment
   - Risk scenarios with probabilities
   - Research gaps identified
   - Comprehensive appendices

## Synthesis Requirements

1. **Coherent Narrative**: Clear story from crisis → causes → implications → future
2. **Evidence-Based**: Every claim backed by specific data
3. **Executive-Friendly**: Non-expert readable summary
4. **Analyst-Rigorous**: Satisfies sophisticated participants
5. **Actionable**: Specific recommendations and leading indicators
6. **Professional**: Clean formatting, proper tables, clear structure
7. **Properly Attributed**: Confidence levels and source quality noted

## Quality Gates

- [ ] Executive summary complete (2-3 pages)
- [ ] Full report complete (15-20 pages)
- [ ] Bottom line paragraph clear
- [ ] All claims evidence-backed
- [ ] Recommendations actionable
- [ ] Leading indicators specified
- [ ] Professional formatting

## Finalization

After synthesis:
1. Update coordinator-status.md to mark all phases complete
2. Present results to user with summary
3. Provide deliverable locations

## Related Files

- `protocol.md` - Detailed synthesis protocol
- `prompts/report-synthesizer.md` - Template for report-synthesizer agent prompts
