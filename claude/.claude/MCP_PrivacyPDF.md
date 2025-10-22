# Privacy PDF MCP Server

**Purpose**: Privacy-preserving PDF extraction with automatic PII redaction for safe LLM analysis

## 🚀 Proactive Usage for PDF Work

**ALWAYS use privacy_pdf tools when:**
- User provides a PDF file path
- Working with sensitive documents (tax, medical, legal, financial)
- Need to extract and analyze PDF content while protecting PII
- Processing Schedule K-1 tax forms (specialized tools available)
- Large PDFs that exceed token limits (use hybrid extraction)

**NEVER read PDFs directly** - Always use privacy_pdf for automatic redaction.

## Triggers
- PDF file paths: `.pdf` extension
- Sensitive document keywords: tax, W-2, 1099, K-1, medical, patient, legal, contract
- User mentions: "analyze this PDF", "extract from PDF", "read this document"
- Privacy concerns: "don't share my SSN", "redact sensitive info", "protect my data"
- Token limit issues: Large PDFs (>30 pages) need hybrid extraction

## Choose When
- **Over Read tool**: Never use Read for PDFs - always use privacy_pdf
- **For any PDF**: Even if content seems non-sensitive, use privacy_pdf as safeguard
- **For tax forms**: Use specialized `pdf_extract_k1_summary` or `pdf_extract_k1_hybrid` for K-1s
- **For large PDFs**: Use `pdf_extract_k1_hybrid` (2-3 min) instead of full extraction (20+ min)
- **For validation**: Use `validate_redaction` to check PII leakage before analysis

## Privacy Levels

**Available levels** (default: `balanced`):
- **strict**: Maximum redaction - names, addresses, SSNs, EINs, phone, email, all numbers
- **balanced**: Redacts PII but preserves financial data structure (recommended)
- **minimal**: Only critical PII (SSN, bank accounts, credit cards)

## Tool Selection Guide

### When to Use Each Tool

**`pdf_extract_redact`** - General PDF extraction with redaction
- Any PDF that needs content extraction
- Unknown document type
- Standard-sized PDFs (<30 pages)
- Full markdown output needed

**`pdf_extract_k1_summary`** - Extract ONLY key K-1 tax fields
- Large K-1 PDFs (49+ pages) that exceed token limits
- Only need specific tax line items (1, 2, 9a, 10, 11, 19, 20Z)
- 500-1000 tokens output vs 25K-68K for full extraction
- Partnership/EIN info and critical income/loss data

**`pdf_extract_k1_hybrid`** - Smart K-1 extraction (RECOMMENDED for K-1s)
- Best balance of detail and speed for K-1 forms
- PyMuPDF detects data pages → MinerU OCR only those pages
- 8x faster than full extraction (2-3 min vs 20 min)
- Stays within token limits (6K vs 63K tokens)
- Better structure preservation than summary mode

**`validate_redaction`** - Safety check for redacted text
- Before sending redacted content to other tools
- Verify no PII leakage occurred
- Get risk assessment and recommendations
- Required for strict mode compliance

**`analyze_redacted_content`** - Prepare for LLM analysis
- Safety gate before LLM processing
- Logs analysis request for audit trail
- Returns confirmation that content is safe
- Use when passing redacted content to other agents

## Workflow Patterns

### Standard PDF Analysis
```
1. pdf_extract_redact(path, privacy_level="balanced")
2. validate_redaction(redacted_text, strict_mode=true)
3. analyze_redacted_content(redacted_text, "Calculate total income")
4. Perform analysis on safe content
```

### Large K-1 Tax Form (RECOMMENDED)
```
1. pdf_extract_k1_hybrid(path, privacy_level="balanced")
   → Returns structured K-1 data from data pages only
2. Analyze tax fields without PII concerns
```

### Quick K-1 Summary
```
1. pdf_extract_k1_summary(path, privacy_level="balanced")
   → Returns only essential tax line items
2. Immediate analysis of key financial data
```

### Strict Compliance Workflow
```
1. pdf_extract_redact(path, privacy_level="strict")
2. validate_redaction(redacted_text, strict_mode=true)
   → Fails if ANY potential PII detected
3. Only proceed if validation passes
```

## Document Type Detection

**Automatically applies appropriate privacy level:**
- **Tax documents**: K-1, W-2, 1099 → Balanced (preserves financial data)
- **Medical records**: Patient info, diagnoses → Strict (max redaction)
- **Legal contracts**: Parties, terms → Balanced (preserves structure)
- **Financial statements**: Bank, investment → Balanced (keeps amounts)

## Examples

```
"analyze this K-1 form at ~/tax/k1-2023.pdf"
→ pdf_extract_k1_hybrid (smart extraction, 2-3 min, 6K tokens)

"extract text from ~/medical/lab-results.pdf"
→ pdf_extract_redact(privacy_level="strict") (medical = max privacy)

"what's my total partnership income from k1.pdf?"
→ pdf_extract_k1_summary (only key tax fields needed)

"check if this redacted text is safe"
→ validate_redaction(text, strict_mode=true)

"read this PDF at ~/contract.pdf"
→ pdf_extract_redact(privacy_level="balanced") (never use Read tool!)
```

## Error Prevention

**DON'T:**
- ❌ Use Read tool for PDFs
- ❌ Skip redaction for "non-sensitive" PDFs
- ❌ Use full extraction for large K-1s (token limit issues)
- ❌ Send redacted content without validation in strict mode
- ❌ Guess at privacy level - use balanced as default

**DO:**
- ✅ Always use privacy_pdf for any PDF
- ✅ Use hybrid mode for K-1 forms (faster, better)
- ✅ Validate redaction before LLM analysis
- ✅ Check audit logs for compliance
- ✅ Default to balanced privacy level

## Token Optimization

**Large PDFs cause token issues:**
- Full K-1 extraction: 25K-68K tokens (exceeds limits)
- K-1 hybrid extraction: 6K tokens (within limits)
- K-1 summary: 500-1K tokens (minimal)

**Strategy:**
1. Try `pdf_extract_k1_hybrid` first for K-1s
2. Fall back to `pdf_extract_k1_summary` if still too large
3. Use `pdf_extract_redact` only for non-tax PDFs

## Works Best With

- **Research agents**: privacy_pdf extracts → research agent analyzes
- **Financial analyzer**: privacy_pdf provides K-1 data → analyzer calculates tax
- **Report writer**: privacy_pdf supplies redacted content → writer generates summary

## Security Features

- ✅ Automatic PII detection (regex patterns by privacy level)
- ✅ Labeled redactions: `[REDACTED_SSN]`, `[REDACTED_NAME]`
- ✅ Audit logging: Tracks all redactions and analysis requests
- ✅ Safety validation: Multi-layer checks for PII leakage
- ✅ MinerU OCR: Industry-standard PDF extraction (magic-pdf)
