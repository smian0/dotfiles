# Quality Framework Reference

## Overview

The research skill uses a **1-10 point quality scale** with 50% weight on grounding (citations). Reports must achieve ≥8/10 with perfect grounding (5/5) to pass.

**Core Principle**: Quality is #1 priority. 100% grounding is non-negotiable.

---

## Scoring Breakdown (10 Points Total)

```
Grounding & Citations:    5 points (50%) ← MANDATORY 5/5 TO PASS
Source Quality:           2 points (20%)
Source Diversity:         1 point  (10%)
Completeness:             1 point  (10%)
Clarity:                  1 point  (10%)
────────────────────────────────────────
TOTAL:                   10 points (100%)
```

---

## 1. Grounding & Citations (5 Points) ⚠️ HARD REQUIREMENT

### Calculation
```
citation_coverage = (cited_claims / total_claims) × 100%
grounding_score = (citation_coverage / 100) × 5
```

### Point Assignment
| Coverage | Score | Status |
|----------|-------|--------|
| 100% | 5.0 | ✅ Required for pass |
| 95-99% | 4.0-4.9 | ❌ Insufficient |
| 85-94% | 3.0-3.9 | ❌ Fail |
| 70-84% | 2.0-2.9 | ❌ Fail |
| 50-69% | 1.0-1.9 | ❌ Fail |
| <50% | 0.0 | ❌ Automatic fail |

### Measurement Method
1. Parse report markdown
2. Count factual sentences (statements that can be verified)
3. Count inline citations (format: `[text](url "quote")`)
4. Calculate: `cited_claims / total_claims × 100%`

### Critical Rule
**If grounding_score < 5.0, status = FAIL regardless of other scores.**

No data is better than unsourced data. Cannot proceed with incomplete citation coverage.

---

## 2. Source Quality (2 Points)

### Calculation
```
avg_credibility = sum(credibility_scores) / num_sources
```

### Point Assignment
| Avg Credibility | Score | Description |
|-----------------|-------|-------------|
| 9-10 | 2.0 | Primary sources (gov, edu, org, official docs) |
| 7-8 | 1.5 | Secondary sources (news, journals, analysis) |
| 5-6 | 1.0 | Tertiary sources (Wikipedia, general blogs) |
| <5 | 0.0 | Low-quality sources (forums, anonymous) |

### Credibility Scoring Algorithm

**Primary Sources (9-10 points)**:
- `.gov` government sites: 10
- `.edu` educational institutions: 10
- `.org` official organizations (W3C, IEEE, IETF, ISO): 9
- Official documentation sites (python.org, reactjs.org): 9

**Secondary Sources (7-8 points)**:
- Tier 1 news outlets (NYT, WSJ, Reuters, AP, BBC): 8
- Academic journals (Nature, Science, ACM, IEEE publications): 8
- Industry analysis (Gartner, Forrester, IDC): 7
- Technical blogs by recognized experts: 7

**Tertiary Sources (4-6 points)**:
- Tier 2 news outlets: 6
- Wikipedia: 5
- General tech blogs (with author): 5
- General tech blogs (anonymous): 4

**Low-Quality Sources (1-3 points)**:
- Forums (Stack Overflow, Reddit): 3
- Anonymous blogs: 2
- User-generated content sites: 1

### Adjustments
- **+1**: Recent (< 6 months old)
- **+1**: Has multiple citations/references
- **+1**: Author has verified credentials
- **-1**: Old (> 2 years)
- **-1**: No author listed
- **-2**: No references/citations in source

**Final credibility score**: Base + adjustments (capped at 1-10)

---

## 3. Source Diversity (1 Point)

### Calculation
```
unique_sources = count(distinct source URLs in report)
```

### Point Assignment
| Unique Sources | Score |
|----------------|-------|
| ≥5 | 1.0 |
| <5 | 0.0 |

### Measurement Method
1. Extract all URLs from inline citations in report
2. Count unique URLs (deduplicate)
3. Assign points based on count

**Rationale**: Multiple sources reduce bias and improve reliability.

---

## 4. Completeness (1 Point)

### Assessment
Check if all key aspects of research query are addressed.

### Point Assignment
| Coverage | Score |
|----------|-------|
| All key aspects covered | 1.0 |
| Major gaps in coverage | 0.0 |

### Measurement Method
1. Parse research query to identify key aspects
2. Check report sections cover all aspects
3. List `gaps_identified` if any

### Examples

**Query**: "What are the key features of WebAssembly?"
- Must cover: language support, performance, browser compatibility, architecture
- Missing any major feature category → 0 points

**Query**: "Compare React vs Vue"
- Must cover: both frameworks, comparison points
- Only covers React → 0 points (missing Vue)

---

## 5. Clarity (1 Point)

### Assessment
Check report structure and readability.

### Point Assignment
| Quality | Score |
|---------|-------|
| Well-structured, clear, logical flow | 1.0 |
| Confusing structure or unclear writing | 0.0 |

### Measurement Method

**Structure Check**:
- ✅ Has Executive Summary?
- ✅ Has Main Findings sections?
- ✅ Has Conclusion?
- ✅ Has Sources section?

**Readability Check**:
- Sentences are clear (not overly complex)
- Logical progression (general → specific, or chronological)
- No repetition

**Result**: Structure good + Readability good → 1.0 point

---

## Status Determination Logic

```python
if grounding_score < 5.0:
    status = "fail"
    reason = "Grounding insufficient (< 5/5). Report rejected."

elif total_score >= 8.0:
    status = "pass"
    reason = "Quality threshold met."

else:  # grounding = 5, but total < 8
    status = "iterate"
    reason = "Grounding OK, but other dimensions need improvement."
```

### Status Meanings

**PASS** (total ≥ 8, grounding = 5):
- Report meets quality threshold
- Ready for user delivery
- No further action needed

**ITERATE** (total < 8, grounding = 5):
- Grounding is acceptable
- Other dimensions need improvement
- Can attempt up to 2 iterations

**FAIL** (grounding < 5):
- Insufficient citation coverage
- Report rejected immediately
- Cannot proceed (no data > bad data)

---

## Iteration Priority Queue

When `status = "iterate"`, fix deficiencies in priority order:

### Priority 1: Fix Grounding (if < 5/5)
- Search for missing citations
- Add citations to unsourced claims
- Remove unsourced claims if citations unavailable
- **Re-run**: Stages 1-6

### Priority 2: Fix Source Quality (if < 2/2)
- Replace low-credibility sources (< 7/10) with primary sources
- Search for `.gov`/`.edu`/`.org` alternatives
- **Re-run**: Stages 1-6

### Priority 3: Fix Diversity (if < 1/1)
- Search for additional sources (need 5+ unique)
- Target different domains
- **Re-run**: Stages 1-6

### Priority 4: Fix Completeness (if < 1/1)
- Address identified gaps
- Search for missing aspects
- **Re-run**: Stages 1-6 (for new data) or Stage 5-6 (restructure only)

### Priority 5: Fix Clarity (if < 1/1)
- Restructure sections
- Improve logical flow
- Simplify complex sentences
- **Re-run**: Stage 5-6 only

---

## Iteration Limits

**Maximum Iterations**: 2

### Iteration 1
- Apply highest priority fix
- Re-run affected stages
- Re-score with quality-scorer
- Check status:
  - PASS → Done
  - ITERATE → Try iteration 2
  - FAIL → Reject (grounding broken)

### Iteration 2
- Apply next priority fix
- Re-run affected stages
- Re-score
- Check status:
  - PASS → Done
  - ITERATE → REJECT (max iterations exhausted)
  - FAIL → Reject

### After Iteration 2
If still `status = "iterate"`, report is **rejected**. Don't iterate forever.

**Reason**: Quality threshold not achievable with current research scope. Need broader search or different query.

---

## Example Scoring

### Pass Case
```yaml
quality_score:
  grounding: 5/5       ← 100% claims cited
  source_quality: 2/2  ← Avg credibility 9.5
  source_diversity: 1/1 ← 6 unique sources
  completeness: 0/1    ← Missing performance benchmarks
  clarity: 1/1         ← Well-structured
  total: 9/10          ← PASS (≥8 required)

status: "pass"
reason: "Quality threshold met (9/10). Grounding requirement satisfied (5/5)."
```

### Iterate Case
```yaml
quality_score:
  grounding: 5/5       ← 100% claims cited ✅
  source_quality: 1/2  ← Avg credibility 6.2
  source_diversity: 0/1 ← Only 4 sources
  completeness: 0/1    ← Missing comparison data
  clarity: 0/1         ← Poor organization
  total: 6/10          ← ITERATE (need 8)

status: "iterate"
improvements_needed:
  - Priority 2: Replace low-credibility sources
  - Priority 3: Find 1 more source (need 5+)
  - Priority 4: Address missing comparison
  - Priority 5: Restructure sections
```

### Fail Case
```yaml
quality_score:
  grounding: 3/5       ← Only 80% claims cited ❌
  source_quality: 1/2  ← Avg credibility 7.5
  source_diversity: 1/1 ← 5 unique sources
  completeness: 1/1    ← All aspects covered
  clarity: 1/1         ← Well-structured
  total: 7/10          ← Would pass if grounding OK

status: "fail"
reason: "Grounding insufficient (3/5 < 5/5 requirement). 3 unsourced claims detected. Report rejected - cannot proceed with incomplete citation coverage."
```

---

## Critical Framework Rules

**GROUNDING = 5/5 MANDATORY**: If grounding < 5, status = fail regardless of other scores.

**PASS THRESHOLD = 8/10**: Total must be ≥ 8 to pass (with grounding = 5).

**OBJECTIVE SCORING**: Count, don't estimate. Use precise calculations.

**NO SUBJECTIVITY**: All scores based on measurable metrics (counts, averages, percentages).

**DETERMINISTIC**: Same report should always get same score.

**TRANSPARENT**: Show all calculations in details section.

**MAX 2 ITERATIONS**: If quality insufficient after 2 tries, reject.

---

**Last Updated**: 2025-10-20
**Version**: 1.0
**Related**: citation-schema.md, quality-scorer.md, SKILL.md
