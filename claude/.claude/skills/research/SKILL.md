---
name: research
description: Comprehensive multi-source research with strict grounding (100% citation requirement). NO DATA > BAD DATA.
---

# Research Skill

## Purpose
Conduct thorough research with mandatory citation grounding. Every claim must be sourced. If sources cannot be validated, research is rejected.

## Core Principles
1. **100% Grounding Required** - Every claim must have a citation
2. **Fail Hard** - Better no data than bad data
3. **Level 3 Validation** - Thorough source checking (URL + quote + metadata)
4. **Quality Threshold** - Minimum 8/10 score (5/5 grounding mandatory)
5. **Full Transparency** - User sees all stages, retries, iterations

## Usage
```
User: "Research: [topic]"
```

The skill automatically executes the 7-stage workflow below.

---

## Workflow Overview

**Stage 1**: Parallel Search (4 angles) → 12+ results
**Stage 2**: Citation Extraction → 8+ valid citations
**Stage 3**: Source Validation (Level 3) → 5+ validated
**Stage 4**: Claim Grounding → 100% coverage, 5+ claims
**Stage 5**: Report Writing → inline citations
**Stage 6**: Quality Scoring → 1-10 scale
**Stage 7**: Iteration (if needed) → improve quality

---

## Detailed Workflow

### Stage 1: Parallel Search (4 Angles)

**Orchestration**: PARALLEL - Launch 4 research-web-researcher instances simultaneously

**Process**:
1. Generate 4 research angles from query
2. Launch 4 agents in parallel using Task tool (ALL IN SINGLE MESSAGE):
   ```
   Task(subagent_type="research-web-researcher", description="Search for angle 1", prompt="{query: ..., angle: 'hardware', attempt: 1}")
   Task(subagent_type="research-web-researcher", description="Search for angle 2", prompt="{query: ..., angle: 'software', attempt: 1}")
   Task(subagent_type="research-web-researcher", description="Search for angle 3", prompt="{query: ..., angle: 'performance', attempt: 1}")
   Task(subagent_type="research-web-researcher", description="Search for angle 4", prompt="{query: ..., angle: 'adoption', attempt: 1}")
   ```
3. Wait for all agents to complete
4. Collect results from each agent

**Retry Logic** (per agent, 3 attempts):
- **Attempt 1 - Standard**: Direct keywords from angle
  - Example: "quantum error correction"

- **Attempt 2 - Adversarial**: Challenge assumption, flip perspective
  - Use OR operators to expand, synonyms to diversify
  - Example: "quantum computing challenges" OR "quantum fault tolerance limits"

- **Attempt 3 - Citation Mining**: Find seminal sources, check what cites them
  - Add qualifiers: "review paper", "survey", "comprehensive analysis"
  - Target: arxiv.org, scholar.google.com, official documentation

**Failure Handling**:
- **Soft fail**: If 1-2 agents fail, continue with successful ones
- **Hard fail**: If <2 agents succeed, ABORT workflow
  - Show user: "Stage 1 failed: Only X/4 search agents succeeded (minimum 2 required)"

**Output**: Save all search results to `.research/[YYYY-MM-DD-topic]/agent-outputs/research-web-researcher-*.yaml`

**User Sees**:
```
✓ Stage 1: Search completed
- Agent 1 (hardware): ✓ Success (3 results)
- Agent 2 (software): ✓ Success after 2 attempts (4 results)
- Agent 3 (performance): ✓ Success (3 results)
- Agent 4 (adoption): ✗ Failed after 3 attempts
Total: 10 results from 3 successful agents
```

---

### Stage 2: Citation Extraction

**Orchestration**: SEQUENTIAL - Process all search results

**Process**:
1. Read search results from `.research/[topic]/agent-outputs/research-web-researcher-*.yaml`
2. Combine all results into single list
3. Launch citation-extractor agent:
   ```
   Task(subagent_type="citation-extractor", prompt="{results: [...], attempt: 1}")
   ```
4. Agent extracts verbatim quotes from sources

**Retry Logic** (3 attempts total):
- Attempt 1: Standard extraction (check snippets)
- Attempt 2: Deep extraction (WebFetch full pages)
- Attempt 3: Alternative extraction (related claims, FAQ sections)

**Failure Handling**:
- **Hard fail**: If <2 valid citations extracted, ABORT
  - Show user: "Stage 2 failed: Only X citations found (minimum 2 required). Details: [retry attempts]"

**Output**: Save to `.research/[topic]/agent-outputs/citation-extractor.yaml`

**User Sees**:
```
✓ Stage 2: Citation extraction completed
- Attempt 1: Found 7 citations
- 3 results rejected (no valid quotes)
Total: 7 valid citations extracted
```

---

### Stage 3: Source Validation (Level 3)

**Orchestration**: SEQUENTIAL - Validate each citation

**Process**:
1. Read citations from `.research/[topic]/agent-outputs/citation-extractor.yaml`
2. Launch source-validator agent:
   ```
   Task(subagent_type="source-validator", prompt="{citations: [...], attempt: 1}")
   ```
3. Agent performs Level 3 checks:
   - Level 1: URL reachable, HTTPS
   - Level 2: Quote found verbatim, recent date
   - Level 3: Author identified, credentials verified, has references

**Retry Logic** (3 attempts):
- Attempt 1: Standard validation (strict requirements)
- Attempt 2: Retry failed URLs (network retry)
- Attempt 3: Relaxed date requirement (accept 2-5 years if credibility ≥9)

**Failure Handling**:
- **Hard fail**: If <2 citations validated, ABORT
  - Show user: "Stage 3 failed: Only X citations validated (minimum 2 required). Validation failures: [reasons]"

**Output**: Save to `.research/[topic]/agent-outputs/source-validator.yaml`

**User Sees**:
```
✓ Stage 3: Source validation completed (Level 3)
- 7 citations checked
- 5 validated (avg credibility: 8.6/10)
- 2 rejected (1 quote not found, 1 low credibility)

Bias Check:
- ✓ Multiple perspectives (3 pro, 1 cautionary, 1 neutral)
- ✓ No funding conflicts detected

Total: 5 validated citations
```

**Source Evaluation Framework**:

Validators use **CRAAP Test Enhanced** for credibility scoring:
- **Currency**: Published ≤2 years (or seminal if >2 years with high impact)
- **Relevance**: Directly addresses research angle (not tangential)
- **Authority**: Verifiable author expertise (credentials, position, publications)
- **Accuracy**: Claims cited, methodology described, limitations acknowledged
- **Purpose**: Educational/research intent (not marketing/opinion)
- **+ Bias Check**: Flag emotional language, missing counterarguments, funding conflicts

**Credibility Tiers**:
- **9-10**: Peer-reviewed, primary research, government data
- **7-8**: Expert analysis, industry reports, established news
- **5-6**: Technical blogs with citations, documentation
- **<5**: Reject (opinion, marketing, uncited claims)

---

### Stage 4: Claim Grounding Mapping

**Orchestration**: SEQUENTIAL - Map claims to citations

**Process**:
1. Read validated citations from `.research/[topic]/agent-outputs/source-validator.yaml`
2. Launch claim-grounding-mapper agent:
   ```
   Task(subagent_type="claim-grounding-mapper", prompt="{validated_citations: [...], research_query: '...', attempt: 1}")
   ```
3. Agent extracts factual claims and maps to citations

**Retry Logic** (3 attempts):
- Attempt 1: Standard extraction (high confidence only)
- Attempt 2: Aggressive extraction (medium confidence accepted)
- Attempt 3: Relaxed confidence threshold (more medium confidence)

**Failure Handling**:
- **Hard fail**: If <5 grounded claims OR grounding coverage <100%, ABORT
  - Show user: "Stage 4 failed: Only X grounded claims (minimum 5 required). Grounding coverage: Y%"

**Output**: Save to `.research/[topic]/agent-outputs/claim-grounding-mapper.yaml`

**User Sees**:
```
✓ Stage 4: Claim grounding completed
- 8 claims extracted
- 100% grounding coverage (8/8 claims sourced)
- Confidence: 6 high, 2 medium
Total: 8 grounded claims ready for report
```

---

### Stage 5: Report Writing (Strict Mode)

**Orchestration**: SEQUENTIAL - Write once

**Process**:
1. Read grounded claims from `.research/[topic]/agent-outputs/claim-grounding-mapper.yaml`
2. Launch report-writer agent:
   ```
   Task(subagent_type="report-writer", prompt="{grounded_claims: [...], research_query: '...'}")
   ```
3. Agent writes report with inline citations
4. Format: `[claim](url "verbatim quote")` for every factual statement

**No Retry**: Report writing is deterministic (no retries needed)

**Failure Handling**:
- **Hard fail**: If any unsourced claim detected during self-validation, ABORT
  - Show user: "Stage 5 failed: Unsourced claims detected in report. Agent self-validation failed."

**Output**: Save to `.research/[topic]/agent-outputs/report-writer.md`

**User Sees**:
```
✓ Stage 5: Report writing completed
- Executive summary: 4 key findings
- Main sections: 3 sections
- Inline citations: 8 citations
- Self-validation: Passed
```

---

### Stage 6: Quality Scoring

**Orchestration**: SEQUENTIAL - Score once

**Process**:
1. Read report, grounded claims, and validated citations
2. Launch quality-scorer agent:
   ```
   Task(subagent_type="quality-scorer", prompt="{report: '...', grounded_claims: [...], validated_citations: [...]}")
   ```
3. Agent calculates objective scores (1-10 scale)

**Scoring Breakdown** (Objective Criteria):

1. **Grounding (5 pts)**: Citation coverage percentage
   - 5/5: 100% cited
   - 0/5: <80% cited

2. **Source Quality (2 pts)**: Average credibility score
   - 2/2: Avg ≥8/10
   - 1/2: Avg 6-7.9/10
   - 0/2: Avg <6/10

3. **Diversity (1 pt)**: Unique sources AND perspectives
   - 1/1: ≥5 sources from 3+ types (academic, industry, news)
   - 0/1: <5 sources OR echo chamber (all same type)

4. **Completeness (1 pt)**: All query aspects covered
   - 1/1: Each research angle has ≥1 validated claim
   - 0/1: Missing coverage for any angle

5. **Clarity (1 pt)**: Structure and readability
   - 1/1: Has exec summary, sections, inline citations, no jargon
   - 0/1: Missing structure or unclear

**No Retry**: Scoring is objective calculation (no retries needed)

**Status Determination**:
- **PASS**: Total ≥8/10 AND grounding =5/5
- **ITERATE**: Total <8/10 AND grounding =5/5
- **FAIL**: Grounding <5/5 (reject immediately)

**Output**: Save to `.research/[topic]/agent-outputs/quality-scorer.yaml`

**User Sees**:
```
✓ Stage 6: Quality scoring completed

Quality Score: 9/10 ✓ PASS

Breakdown:
- Grounding: 5/5 (100% cited) ✓
- Source Quality: 2/2 (avg credibility 8.6) ✓
- Diversity: 1/1 (5 unique sources) ✓
- Completeness: 0/1 (missing performance benchmarks)
- Clarity: 1/1 (well-structured) ✓

Status: PASS - Quality threshold met
```

---

### Stage 7: Iteration (Conditional)

**Trigger**: Only if Stage 6 status = "iterate"

**Max Iterations**: 2

**Process**:
1. Read quality score from Stage 6
2. Identify deficiencies (which dimensions <threshold)
3. Apply fixes in priority order:
   - Priority 1: Grounding <5/5 → Search for missing citations
   - Priority 2: Source Quality <2/2 → Replace low-credibility sources
   - Priority 3: Diversity <1/1 → Search for additional sources
   - Priority 4: Completeness <1/1 → Address gaps
   - Priority 5: Clarity <1/1 → Restructure report

4. Re-run affected stages:
   - Need more sources? → Re-run Stages 1-6
   - Just restructure? → Re-run Stage 5-6

5. Re-score with quality-scorer
6. Check status again:
   - PASS → Done
   - ITERATE (iteration 2) → Try again
   - Still ITERATE after iteration 2 → REJECT

**Output**: Save each iteration to `.research/[topic]/iterations/iteration-N.md`

**User Sees** (Example Iteration 1):
```
⚠ Initial Score: 6/10 - Below threshold (need 8/10)

Issue: Source diversity (0/1) - only 4 sources, need 5+

Iteration 1: Fixing diversity
- Searching for additional sources...
- Found 2 more sources (benchmark sites)
- Total unique sources: 6

Updated Score: 8/10 ✓ PASS
- Grounding: 5/5 ✓
- Source Quality: 2/2 ✓
- Diversity: 1/1 ✓ (improved)
- Completeness: 0/1
- Clarity: 1/1 ✓

Result: Threshold met after 1 iteration
```

---

## Directory Structure Created

For each research query, create:
```
.research/[YYYY-MM-DD-topic]/
├── agent-outputs/
│   ├── research-web-researcher-1.yaml
│   ├── research-web-researcher-2.yaml
│   ├── research-web-researcher-3.yaml
│   ├── research-web-researcher-4.yaml
│   ├── citation-extractor.yaml
│   ├── source-validator.yaml
│   ├── claim-grounding-mapper.yaml
│   ├── report-writer.md
│   └── quality-scorer.yaml
├── iterations/ (if applicable)
│   ├── iteration-1.md
│   └── iteration-2.md
├── final-report.md
└── metadata.yaml
```

**Directory Creation**:
- Orchestrator creates `.research/[YYYY-MM-DD-topic]/` at workflow start
- Creates subdirectories: `agent-outputs/`, `iterations/`
- Saves metadata: query, start time, end time, status, final score

---

## Task Tool Invocation Pattern

### Parallel Execution (Stage 1)
```
# All 4 Task calls in SINGLE message = parallel execution
Task(subagent_type="research-web-researcher", description="Search angle 1", prompt="...")
Task(subagent_type="research-web-researcher", description="Search angle 2", prompt="...")
Task(subagent_type="research-web-researcher", description="Search angle 3", prompt="...")
Task(subagent_type="research-web-researcher", description="Search angle 4", prompt="...")
```

### Sequential Execution (Stages 2-6)
```
# Each Task in separate message = sequential execution
Task(subagent_type="citation-extractor", description="Extract citations", prompt="...")
# Wait for result, then...
Task(subagent_type="source-validator", description="Validate sources", prompt="...")
# Wait for result, then...
...
```

---

## Data Passing Between Stages

**Hybrid Approach**: Files for debugging, in-memory for speed

**Example** (Stage 2 → Stage 3):
1. Stage 2 (citation-extractor) outputs to `.research/[topic]/agent-outputs/citation-extractor.yaml`
2. Orchestrator reads this file
3. Orchestrator parses YAML content into data structure
4. Orchestrator passes data to Stage 3 as input parameter:
   ```
   Task(subagent_type="source-validator", prompt="{citations: [parsed_data], attempt: 1}")
   ```

**Benefits**:
- Files saved for debugging
- Data passed directly (no redundant file I/O for agents)
- Full traceability

---

## Critical Rules

**100% GROUNDING NON-NEGOTIABLE**: Cannot proceed past Stage 4 without complete citation coverage.

**QUALITY THRESHOLD**: 8/10 minimum (with grounding 5/5). Lower scores rejected.

**FAIL FAST**: Abort immediately at stage failures. Don't continue with bad data.

**TRANSPARENCY**: Show user every stage, retry, iteration. No hidden failures.

**NO DATA > BAD DATA**: Better to reject research than publish unverified claims.

**MAX 2 ITERATIONS**: If quality insufficient after 2 tries, reject. Don't iterate forever.

---

**Last Updated**: 2025-10-21
**Version**: 2.1 (Enhanced Evaluation Criteria)
**Changes**: Added CRAAP framework, concrete scoring criteria, enhanced search tactics, bias transparency
**Dependencies**: 6 small agents (research-web-researcher, citation-extractor, source-validator, claim-grounding-mapper, report-writer, quality-scorer)
