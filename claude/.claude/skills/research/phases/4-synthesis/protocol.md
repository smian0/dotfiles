# Phase 4 Synthesis Protocol

## Report-Synthesizer Invocation

```python
Task(
    subagent_type="report-synthesizer",
    description="Synthesize {topic} research report",
    prompt="""
Synthesize all research findings into comprehensive, publication-ready reports.

## Research Question
{research_question}

## Input Materials
1. **Comprehensive Analysis**: ./research-output/analysis/comprehensive-analysis-{date}.md
2. **Validated Sources**: ./research-output/sources/validated-sources-{date}.md
3. **All Stream Files**: ./research-output/sources/stream-*-{date}.md

## Deliverables

### 1. Executive Summary (./research-output/report/executive-summary-{date}.md)
**Target**: C-suite, policymakers, board members
**Length**: 2-3 pages
**Content**:
- Report metadata (date generated, data period, "as of [DATE]" context)
- Single-paragraph bottom line
- 5 critical insights with confidence levels
- Timeline of key events
- Root cause breakdown (weighted)
- Forward-looking implications (3 time horizons)
- Stakeholder recommendations
- Leading indicators to watch

### 2. Full Report (./research-output/report/full-report-{date}.md)
**Target**: Analysts, traders, researchers
**Length**: 15-20 pages
**Content**:
- Report metadata (date generated, data period, "as of [DATE]" context)
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

Deliver publication-ready reports suitable for wide distribution.
"""
)
```

## Synthesis Methodology

### Executive Summary Structure

1. **Report Metadata** (header)
2. **Bottom Line** (single paragraph, <150 words)
3. **Critical Insights** (5 insights, ranked by importance)
4. **Timeline** (key events with dates)
5. **Root Cause Breakdown** (weighted percentages)
6. **Forward-Looking** (short/medium/long-term)
7. **Recommendations** (actionable, specific)
8. **Leading Indicators** (what to watch)

### Full Report Structure

1. **Table of Contents**
2. **Executive Summary** (shortened version)
3. **Methodology** (research approach, streams, validation)
4. **Detailed Timeline** (comprehensive event chronology)
5. **Root Cause Analysis** (with evidence grades)
6. **Findings Synthesis** (multi-stream integration)
7. **Pattern Analysis** (convergence, amplification, feedback)
8. **Stakeholder Impact** (differential effects)
9. **Risk Scenarios** (with probabilities)
10. **Research Gaps** (acknowledged uncertainties)
11. **Appendices** (source lists, methodology details)

## Quality Standards

Reports complete when:
- ✅ Executive summary 2-3 pages
- ✅ Full report 15-20 pages
- ✅ Bottom line clear and actionable
- ✅ All claims evidence-backed
- ✅ Professional formatting (tables, headings)
- ✅ Confidence levels noted
- ✅ Leading indicators specified
- ✅ Ready for distribution

## Finalization

1. **Update coordinator-status.md** - Mark synthesis complete
2. **Present to user**:
   - Research question answered
   - Key findings (3-5 bullets)
   - Overall confidence level
   - Location of deliverables
3. **Provide next steps** or follow-up areas
