---
name: pdf-analysis
description: Analyze PDFs with automatic PII redaction. Use when user provides PDF path(s) and analysis question. Supports single PDF or batch processing with parallel execution.
---

# PDF Analysis with Privacy Protection

Analyze PDF documents safely by automatically detecting document type, applying appropriate privacy level, and delegating to the privacy-pdf-agent for extraction and redaction.

## When to Use

Invoke this skill when:
- User provides PDF file path(s) and an analysis question
- User requests document information from sensitive PDFs (tax, medical, legal, financial)
- User needs batch processing of multiple PDFs
- Privacy protection is required for PII (SSN, EIN, addresses, names)

## Input Format

The skill receives input through:
- **User's natural language request** (e.g., "Analyze this PDF...")
- **Slash command arguments** via `$ARGUMENTS` variable
- **Direct file paths** in conversation

**Parse from user message:**
- **PDF path(s)**: Look for strings ending in `.pdf` or glob patterns like `*.pdf`
- **Question**: Text after the file path(s), or implied (default to "Summarize this document")
- **Multiple files**: Space-separated paths or glob patterns

**Common input patterns:**
```
'/path/to/file.pdf' "What is my income?"           → Single PDF + question
'/path/*.pdf' "Summarize"                          → Batch + question
file1.pdf file2.pdf "Compare these"                → Multiple explicit + question
/tax/2024-W2.pdf                                   → Single PDF (implied summary)
```

## Workflow

### Step 1: Parse Input

Extract from user request:
- **PDF path(s)**: Single file or multiple files (glob patterns supported)
- **Analysis question**: What information to extract (or default to summary)

**Handle glob patterns:**
If user provides `*.pdf` pattern, expand it to list of matching files before processing.

If ambiguous, prompt user:
```
Please provide:
1. PDF file path (or glob pattern for batch)
2. Your analysis question (optional - defaults to "Summarize this document")

Example: "/tax-docs/2024-W2.pdf" "What's my total income?"
Example: "/medical/*.pdf" "Summarize test results"
Example: "/contracts/agreement.pdf" (implied: summarize)
```

### Step 2: Auto-Detect Document Type

Classify each PDF by examining file path and name:

**Tax Documents** → `privacy_level="strict"`:
- Path contains: `/tax/`, `/1099/`, `/W-2/`, `/tax-return/`, `/irs/`
- Filename contains: `W-2`, `W2`, `1099`, `1098`, `Schedule`, `K-1`, `tax`

**Medical Documents** → `privacy_level="strict"`:
- Path contains: `/medical/`, `/health/`, `/insurance/`, `/lab-results/`
- Filename contains: `medical`, `health`, `prescription`, `lab`, `diagnosis`

**Legal Documents** → `privacy_level="balanced"`:
- Path contains: `/legal/`, `/contract/`, `/agreement/`, `/nda/`
- Filename contains: `contract`, `NDA`, `agreement`, `terms`, `license`

**Financial Documents** → `privacy_level="balanced"`:
- Path contains: `/financial/`, `/bank/`, `/brokerage/`, `/investment/`
- Filename contains: `statement`, `account`, `brokerage`, `portfolio`

**Resume/CV Documents** → `privacy_level="minimal"` (no meaningful redactions):
- Path contains: `/resume/`, `/cv/`, `/curriculum/`, `/hiring/`, `/candidates/`
- Filename contains: `resume`, `cv`, `CV`, `curriculum`, `cover-letter`
- **Result**: Complete resume content preserved (names, contact, work history, dates, URLs)

**General Documents** → `privacy_level="minimal"`:
- Any document not matching above patterns

For detailed privacy level behavior, see [references/privacy-levels.md](references/privacy-levels.md).

### Step 3: Process PDF(s)

#### Single PDF:

Delegate to privacy-pdf-agent using the Task tool.

**Delegation template** (customize with actual values):

```
Use the Task tool with:
- subagent_type: "privacy-pdf-agent"
- description: "Extract and redact PDF with privacy protection"
- prompt: """
  Process this PDF with privacy protection:
  - PDF Path: {actual_pdf_path}
  - Privacy Level: {detected_privacy_level}
  - Analysis Question: "{user's_question}"

  Return formatted redacted content and answer the question.
  """
```

**Example invocation:**

> I'm delegating to @privacy-pdf-agent:
>
> Task(
>     subagent_type="privacy-pdf-agent",
>     description="Extract and redact 2024-W2.pdf",
>     prompt="""
> Process this PDF with privacy protection:
> - PDF Path: /tax-docs/2024-W2.pdf
> - Privacy Level: strict
> - Analysis Question: "What is my total income?"
>
> Return formatted redacted content and answer the question.
> """
> )

#### Batch Processing (Multiple PDFs):

**CRITICAL: Use sequential processing to avoid MCP tool availability race conditions.**

The privacy_pdf MCP server is resource-intensive (500MB+ models, GPU, OCR engine) and does not support concurrent requests. Parallel execution causes tool availability errors where the second agent cannot access `mcp__privacy_pdf__pdf_extract_redact`.

**Sequential delegation pattern:**

1. For each PDF in the batch (one at a time):
   - Detect document type → privacy level
   - Create Task() with unique description
   - **WAIT for agent to complete** before processing next PDF

2. Process PDFs sequentially (not in parallel)

3. Collect results as each agent completes

**Example sequential invocation:**

> Processing 2 K-1 forms sequentially:
>
> First, processing file1.pdf...
> [Task 1 for file1.pdf]
> [Wait for completion]
>
> Now processing file2.pdf...
> [Task 2 for file2.pdf]
> [Wait for completion]

**Performance**: Sequential processing takes N × 3 seconds, but ensures reliability. MinerU's PyMuPDF fast path (for born-digital PDFs) reduces time to ~0.5s per PDF.

### Step 4: Present Results

#### Single PDF Result:

```markdown
## Analysis: {filename}

{answer to user's question}

---

**Privacy Protection:**
- Level: {privacy_level}
- Redactions: {count} items ({types})
- Redacted File: {path}
```

#### Batch Results:

```markdown
## Batch Analysis Results ({N} files)

### {filename1}
{answer}
- Privacy: {level}, {redactions} items
- File: {path}

### {filename2}
{answer}
- Privacy: {level}, {redactions} items
- File: {path}

---

**Summary:**
- Files Processed: {N}
- Total Redactions: {total}
- Processing Time: ~3 seconds (parallel execution)
```

## Error Handling

### Single PDF Errors

If agent reports processing failure:
- Present the error message from agent
- Suggest manual review or alternative approach
- Do not attempt to process PDF directly (always use agent)

**Example error report:**

```markdown
❌ **PDF Processing Failed**

**File**: problematic-document.pdf
**Error**: {agent_error_message}

**Recommendation**:
- Manual review required
- PDF may be corrupted, password-protected, or contain unredactable PII
- Try alternative: {suggestion}
```

### Batch Processing Errors

If one or more PDFs fail in batch processing:

**1. Continue processing remaining PDFs** - Don't abort the entire batch

**2. Collect successful and failed results separately**

**3. Present partial results:**

```markdown
## Batch Analysis Results (3 files, 1 failed)

### ✅ Successful: file1.pdf
{analysis and privacy report}

### ✅ Successful: file2.pdf
{analysis and privacy report}

### ❌ Failed: file3.pdf
**Error**: {error_message}
**Recommendation**: {suggestion}

---

**Batch Summary:**
- Successfully processed: 2/3 files
- Failed: 1/3 files
- Total redactions (successful): {total}
- Partial results available above
```

**Common batch failure scenarios:**
- Corrupted PDF → Skip and continue
- Missing file → Report and continue
- MCP server timeout → Report and continue
- Safety validation failure → Expected behavior, report details

**Never:** Abort entire batch due to single failure

## Key Rules

1. **Always auto-detect** - Use path/filename analysis, never ask user for privacy level
2. **Always delegate** - Never call MCP tools directly, always use privacy-pdf-agent
3. **Parallel for batch** - Use parallel Task delegation for multiple PDFs
4. **Trust agent safety** - Agent validates safety, don't duplicate checks
5. **Concise results** - Answer the question, don't dump entire redacted content

## Quick Reference

```
Single PDF:  detect_type() → delegate_to_agent() → present_result()
Batch PDFs:  detect_types() → parallel_delegate() → collect_results() → present_summary()
```

---

*For privacy level details and troubleshooting, see [references/privacy-levels.md](references/privacy-levels.md).*
