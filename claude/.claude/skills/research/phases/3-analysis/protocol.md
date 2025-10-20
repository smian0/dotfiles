# Phase 3 Analysis Protocol

## Deep-Research-Agent Invocation

```python
Task(
    subagent_type="deep-research-agent",
    description="Analyze {topic} findings",
    prompt="""
Conduct deep analysis of comprehensive research on: {research_question}

## Input Materials
1. **Validated Sources**: ./research-output/sources/validated-sources-{date}.md
2. **Stream 1**: ./research-output/sources/stream-1-sources-{date}.md
3. **Stream 2**: ./research-output/sources/stream-2-sources-{date}.md
4. **Stream 3**: ./research-output/sources/stream-3-sources-{date}.md
5. **Stream 4**: ./research-output/sources/stream-4-sources-{date}.md

## Analysis Framework

### 1. Root Cause Analysis
Identify and rank primary, secondary, tertiary causes with confidence levels

### 2. Pattern Recognition
Identify recurring themes across all streams:
- Convergence points where multiple factors intersect
- Amplification mechanisms
- Feedback loops

### 3. Causal Chain Mapping
Trace cause-and-effect relationships with evidence grades

### 4. Comparative Analysis
Compare to historical events or analogous situations if applicable

### 5. Stakeholder Impact Analysis
Assess differential impacts across affected parties

### 6. Forward-Looking Implications
Short-term (1-3mo), medium-term (3-12mo), long-term (1-3yr) predictions

## Output Structure

Create: ./research-output/analysis/comprehensive-analysis-{date}.md

[Use template from assets/comprehensive-analysis.template.md]

Provide evidence-based analysis with confidence levels throughout.
"""
)
```

## Analysis Methodology

### Root Cause Analysis

**Ranking Criteria**:
- **Primary Cause**: Highest impact, necessary condition
- **Secondary Causes**: Major contributing factors (2-3)
- **Tertiary Causes**: Amplifying or contextual factors (3-5)

**Confidence Levels**:
- HIGH (80-95%): Strong evidence, multiple corroborations
- MEDIUM (60-79%): Moderate evidence, some corroboration
- LOW (40-59%): Weak evidence, limited corroboration

### Pattern Recognition

Look for:
- **Convergence points**: Where multiple factors intersect
- **Amplification mechanisms**: How causes reinforce each other
- **Feedback loops**: Self-reinforcing cycles
- **Common threads**: Themes appearing across streams

### Causal Chain Mapping

Format: `Cause A → Effect B → Effect C`

**Evidence Grades**:
- A: Strong causal link, well-documented
- B: Moderate causal link, some evidence
- C: Weak/theoretical link, limited evidence

### Strategic Insights

Extract 5-7 key insights with structure:
- **Evidence**: What the data shows
- **Implication**: What it means
- **Forward-looking**: What to watch

## Quality Standards

Analysis complete when:
- ✅ Root causes ranked with confidence levels
- ✅ Cross-stream patterns identified
- ✅ Causal chains mapped with evidence grades
- ✅ 5-7 strategic insights extracted
- ✅ Forward-looking implications provided (3 time horizons)
- ✅ Research gaps acknowledged

## Transition to Phase 4

1. **Update coordinator-status.md** - Mark analysis complete
2. **Review recommendations** - Note themes for synthesis
3. **Proceed to Phase 4** - Synthesis
