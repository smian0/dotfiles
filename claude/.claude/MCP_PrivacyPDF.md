# Privacy PDF MCP Server

**Purpose**: Privacy-preserving PDF extraction with automatic PII redaction

## Triggers
- PDF file paths (`.pdf` extension)
- Sensitive documents: tax, K-1, W-2, 1099, medical, legal, financial
- User mentions: "analyze PDF", "extract from PDF", "read document"
- Large PDFs (>30 pages) causing token limits

## Choose When
- **Over Read tool**: NEVER use Read for PDFs - always use privacy_pdf
- **For K-1 tax forms**: Use `pdf_extract_k1_hybrid` (fast, 2-3 min, 6K tokens)
- **For large K-1s**: Use `pdf_extract_k1_summary` if still too big (500-1K tokens)
- **For general PDFs**: Use `pdf_extract_redact`
- **Privacy levels**: `strict` (medical/legal), `balanced` (default), `minimal`

## Examples
```
"analyze this K-1 at ~/tax/k1-2023.pdf"
→ pdf_extract_k1_hybrid (best for K-1s)

"extract text from ~/medical/lab-results.pdf"
→ pdf_extract_redact(privacy_level="strict")

"what's in this contract at ~/legal/nda.pdf"
→ pdf_extract_redact(privacy_level="balanced")

"read ~/invoice.pdf"
→ pdf_extract_redact (never use Read tool for PDFs!)
```
