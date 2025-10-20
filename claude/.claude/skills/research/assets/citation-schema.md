# Citation Schema Reference

## Overview

This document defines the data structures used throughout the research workflow for citations, from initial search results to final grounded claims.

## Schema Evolution Through Workflow

Citations evolve through 4 stages:

```
Stage 1: Search Result
  ↓
Stage 2: Extracted Citation
  ↓
Stage 3: Validated Citation
  ↓
Stage 4: Grounded Claim
```

---

## Stage 1: Search Result

**Output by**: search-agent
**Used by**: citation-extractor

```yaml
results:
  - result_id: 1
    title: "Page title from search result"
    url: "https://example.com/article"
    snippet: "Brief text snippet from search result (150-300 chars)"
    source_type: "primary|secondary|tertiary"
    accessed_date: "YYYY-MM-DD"
```

**Required Fields**:
- `result_id` (integer): Sequential identifier
- `title` (string): Page title
- `url` (string): HTTPS URL only
- `snippet` (string): Preview text
- `source_type` (enum): Classification
- `accessed_date` (string): ISO date format

**Validation Rules**:
- URL MUST use HTTPS protocol
- `source_type` MUST be one of: primary, secondary, tertiary
- Date MUST be valid ISO 8601 format (YYYY-MM-DD)

---

## Stage 2: Extracted Citation

**Output by**: citation-extractor
**Used by**: source-validator

```yaml
extracted_citations:
  - claim: "Factual statement extracted from source"
    quote: "Verbatim quote from source (1-3 sentences, max 150 words)"
    source_url: "https://example.com/article"
    source_type: "primary|secondary|tertiary"
    page_title: "Full page title"
    accessed_date: "YYYY-MM-DD"
```

**Required Fields**:
- `claim` (string): Factual statement supported by quote
- `quote` (string): Exact text from source (verbatim)
- `source_url` (string): HTTPS URL
- `source_type` (enum): Same as Stage 1
- `page_title` (string): Full page title
- `accessed_date` (string): ISO date

**Validation Rules**:
- Quote MUST be verbatim (exact text, not paraphrased)
- Quote length: 1-3 sentences, max 150 words
- Claim MUST be supported by quote (not speculation)
- URL MUST match original search result

---

## Stage 3: Validated Citation

**Output by**: source-validator
**Used by**: claim-grounding-mapper

```yaml
validated_citations:
  - claim: "Factual statement"
    quote: "Verbatim quote"
    source_url: "https://example.com/article"
    source_type: "primary|secondary|tertiary"
    page_title: "Full page title"
    accessed_date: "YYYY-MM-DD"
    validated: true
    credibility_score: 9
    validation_details:
      url_reachable: true
      quote_found: true
      quote_verbatim: true
      publication_date: "YYYY-MM-DD"
      author: "Author name or organization"
      author_verified: true
      has_references: true
    rejection_reason: null
```

**Additional Fields**:
- `validated` (boolean): Pass/fail validation
- `credibility_score` (integer 1-10): Source quality score
- `validation_details` (object): Level 1-3 check results
  - `url_reachable` (boolean): HTTP 200 response
  - `quote_found` (boolean): Quote exists on page
  - `quote_verbatim` (boolean): Exact text match
  - `publication_date` (string): Article date
  - `author` (string): Author or organization
  - `author_verified` (boolean): Credentials checked
  - `has_references` (boolean): Source cites others
- `rejection_reason` (string|null): Why validation failed

**Validation Rules**:
- `validated=true` requires ALL validation_details checks to pass
- `credibility_score` calculated via domain-based algorithm (see quality-framework.md)
- `rejection_reason` MUST be null if validated=true
- Publication date < 2 years preferred (or high credibility ≥9)

---

## Stage 4: Grounded Claim

**Output by**: claim-grounding-mapper
**Used by**: report-writer

```yaml
grounded_claims:
  - claim_id: 1
    claim: "Factual statement to include in report"
    citation_id: 1
    citation_url: "https://example.com/article"
    citation_quote: "Supporting verbatim quote"
    confidence: "high|medium"
```

**Required Fields**:
- `claim_id` (integer): Sequential identifier for report
- `claim` (string): Factual statement (concise, verifiable)
- `citation_id` (integer): Links to validated citation
- `citation_url` (string): Source URL for inline citation
- `citation_quote` (string): Verbatim quote supporting claim
- `confidence` (enum): high or medium (low confidence claims rejected)

**Validation Rules**:
- Confidence MUST be "high" or "medium" (low rejected)
- Claim MUST be directly supported by citation_quote
- One citation can support multiple claims
- Minimum 5 grounded claims required for report

---

## Confidence Level Definitions

### High Confidence
- Claim is **directly stated** in quote
- No inference required
- Example: Claim "WebAssembly supports 4 languages" from quote "WebAssembly currently supports C, C++, Rust, and AssemblyScript"

### Medium Confidence
- Claim is **strongly implied** by quote
- Minimal inference required
- Example: Claim "WebAssembly is widely adopted" from quote "All major browsers shipped support by Q4 2017"

### Low Confidence (REJECTED)
- Claim requires **significant inference**
- Quote does not directly support claim
- Example: Claim "WebAssembly will replace JavaScript" from quote "WebAssembly provides near-native performance"

---

## Source Type Classifications

### Primary Sources
Official, authoritative, firsthand sources:
- `.gov` government sites
- `.edu` educational institutions
- `.org` official standards organizations (W3C, IEEE, IETF, ISO)
- Official documentation sites (reactjs.org, python.org, etc.)

### Secondary Sources
Analysis, reporting, or synthesis of primary sources:
- Tier 1 news outlets (NYT, WSJ, Reuters, AP, BBC)
- Academic journals (Nature, Science, ACM, IEEE publications)
- Industry analysis (Gartner, Forrester, IDC)
- Technical blogs by recognized experts

### Tertiary Sources
Compilations, summaries, or general references:
- Tier 2 news outlets
- Wikipedia
- General tech blogs
- Technical forums (with caution)

---

## Data Passing Between Stages

Each stage:
1. Reads input from previous stage's output file
2. Validates input schema
3. Processes and transforms data
4. Writes output to designated file
5. Returns structured data to orchestrator

**Example**: Stage 2 → Stage 3
```
1. citation-extractor writes to:
   .research/[topic]/agent-outputs/citation-extractor.yaml

2. Orchestrator reads this file, parses YAML

3. Orchestrator passes parsed data to source-validator:
   Task(subagent_type="source-validator",
        prompt="{citations: [parsed_data], attempt: 1}")

4. source-validator processes, writes to:
   .research/[topic]/agent-outputs/source-validator.yaml
```

---

## Critical Schema Rules

**VERBATIM QUOTES MANDATORY**: All quotes MUST be exact text from source, not paraphrased.

**100% GROUNDING REQUIRED**: Every claim in final report MUST trace back to a validated citation.

**NO LOW CONFIDENCE**: Only high or medium confidence claims accepted. Reject low-confidence mappings.

**FAIL HARD**: If minimum thresholds not met at any stage, ABORT workflow (see failure conditions in each agent).

**TYPE CONSISTENCY**: source_type MUST remain consistent from Stage 1 → Stage 4.

---

**Last Updated**: 2025-10-20
**Version**: 1.0
**Related**: quality-framework.md, SKILL.md
