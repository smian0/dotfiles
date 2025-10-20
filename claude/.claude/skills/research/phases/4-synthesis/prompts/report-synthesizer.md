# Report-Synthesizer Agent Prompt Template

## Prompt Template

```
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

**Required Sections**:
- **Report metadata**: Date generated, data period covered, "as of [DATE]" context
- **Bottom line**: Single paragraph (<150 words) answering the research question
- **Critical insights**: 5 insights ranked by importance with confidence levels
- **Timeline**: Key events with dates
- **Root cause breakdown**: Weighted (e.g., 40% regulatory, 30% market, 20% macro, 10% technical)
- **Forward-looking implications**:
  - Short-term (1-3 months)
  - Medium-term (3-12 months)
  - Long-term (1-3 years)
- **Stakeholder recommendations**: Actionable advice for different parties
- **Leading indicators**: Specific metrics/events to monitor

### 2. Full Report (./research-output/report/full-report-{date}.md)
**Target**: Analysts, traders, researchers
**Length**: 15-20 pages

**Required Sections**:
- **Report metadata**: Date generated, data period covered, "as of [DATE]" context
- **Table of contents**: Complete navigation
- **Executive summary**: Condensed version
- **Methodology**: Research approach, streams, validation process
- **Detailed timeline**: Comprehensive event chronology
- **Root cause analysis**: With evidence grades (A/B/C)
- **Multi-stream findings synthesis**: Integration across all streams
- **Cross-stream pattern analysis**: Convergence points, feedback loops
- **Stakeholder impact assessment**: Differential effects
- **Risk scenarios**: With probability estimates
- **Research gaps**: Acknowledged uncertainties
- **Comprehensive appendices**: Source lists, methodology details

## Synthesis Requirements

1. **Coherent Narrative**: Clear story from crisis → causes → implications → future
2. **Evidence-Based**: Every claim backed by specific data with source citations
3. **Executive-Friendly**: Non-expert can understand executive summary
4. **Analyst-Rigorous**: Full report satisfies sophisticated participants
5. **Actionable**: Specific recommendations and leading indicators (not vague advice)
6. **Professional**: Clean formatting, proper tables, clear structure
7. **Properly Attributed**: Confidence levels and source quality clearly noted

Deliver publication-ready reports suitable for wide distribution.
```

## Quality Requirements

Executive Summary MUST have:
- ✅ Bottom line paragraph (<150 words)
- ✅ 5 critical insights ranked
- ✅ Timeline with specific dates
- ✅ Root cause breakdown with percentages
- ✅ 3 time horizons for forward-looking
- ✅ Actionable recommendations
- ✅ Specific leading indicators

Full Report MUST have:
- ✅ Complete table of contents
- ✅ Methodology documentation
- ✅ Evidence grades (A/B/C) for claims
- ✅ Cross-stream synthesis
- ✅ Risk scenarios with probabilities
- ✅ Research gaps acknowledged
- ✅ Professional formatting throughout

Both reports MUST have:
- ✅ Report metadata (date, period, "as of" context)
- ✅ All claims evidence-backed
- ✅ Confidence levels noted
- ✅ Ready for distribution (no placeholders)
