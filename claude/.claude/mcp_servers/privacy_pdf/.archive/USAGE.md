# Privacy-PDF MCP Server - Quick Usage Guide

## Structure

```
privacy_pdf/
├── server.py              # FastMCP server (entry point)
├── extraction_engine.py   # MinerU PDF extraction
├── redaction_engine.py    # PII detection & redaction
├── mineru/               # Bundled MinerU installation
│   ├── venv/            # Python virtual environment
│   ├── Makefile         # Build commands
│   └── README.md        # MinerU documentation
├── __init__.py          # Package initialization
├── README.md            # Full documentation
└── USAGE.md             # This file
```

## Quick Start (After Claude Code Restart)

### Extract & Redact a Tax Form

```python
mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/2024_W2.pdf",
    privacy_level="strict"
)
```

### With Pattern Preservation

```python
mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/1099-K.pdf",
    privacy_level="strict",
    preserve_patterns=[
        "Box \\d+:",           # Preserve "Box 1:", "Box 2:", etc.
        "\\$[\\d,]+\\.\\d{2}", # Preserve currency amounts
        "Form 1099-K"          # Preserve form name
    ]
)
```

### Parse Result

```python
import json

result = mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/document.pdf",
    privacy_level="balanced"
)

data = json.loads(result)

# Access components
markdown = data["redacted_markdown"]
audit_log = data["audit_log"]
stats = data["statistics"]
safety = data["safety_report"]

# Check if safe
if safety["is_safe"]:
    print(f"✅ Safe for LLM analysis")
    print(f"   Redacted: {stats['total_redactions']} items")
else:
    print(f"⚠️ {safety['risk_level']} risk - review needed")
```

## Privacy Levels

| Level | Patterns | Use Case |
|-------|----------|----------|
| **strict** | 13 patterns | Tax forms, medical records, legal contracts |
| **balanced** | 8 patterns | General business documents (default) |
| **minimal** | 4 patterns | Low-sensitivity documents |

### Strict Redacts
SSN, EIN, Email, Phone, Credit Cards, Account Numbers, Addresses, Dates, Full Names, Currency, ZIP Codes, URLs

### Balanced Redacts
SSN, EIN, Email, Phone, Credit Cards, Account Numbers, Addresses, Currency

### Minimal Redacts
SSN, EIN, Credit Cards, Account Numbers

## Common Patterns to Preserve

```python
preserve_patterns = [
    # Tax form fields
    "Box \\d+:",
    "Wages, tips",
    "Federal income tax withheld",

    # Currency amounts
    "\\$[\\d,]+\\.\\d{2}",

    # Form names
    "Form 1099-K",
    "Form W-2",

    # Common labels (non-sensitive)
    "Total",
    "Amount",
    "Date:",
    "Employer"
]
```

## Example: Tax Document Analysis Workflow

```python
# 1. Extract and redact
result = mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/tax_doc.pdf",
    privacy_level="strict",
    preserve_patterns=["Box \\d+:", "\\$[\\d,]+\\.\\d{2}"]
)

data = json.loads(result)

# 2. Check safety
if not data["safety_report"]["is_safe"]:
    print("❌ Document contains PII leakage - do NOT send to LLM")
    exit(1)

# 3. Analyze with LLM (now safe)
markdown = data["redacted_markdown"]

# Ask LLM: "What is the total income reported in Box 1?"
# LLM will see: "Box 1: $85,000" (preserved) but not SSN/EIN (redacted)
```

## Validation Only (No Extraction)

```python
# If you already have redacted text
mcp__privacy_pdf__validate_redaction(
    redacted_text="Your redacted content here",
    strict_mode=True
)
```

## Audit-Logged Analysis Gate

```python
# Use this before sending to LLM for audit trail
mcp__privacy_pdf__analyze_redacted_content(
    redacted_text="Redacted markdown here",
    analysis_prompt="Calculate total taxable income",
    require_validation=True  # Safety check first
)
```

## Troubleshooting

### "MinerU not found"
The bundled MinerU should be auto-detected. If not:
```python
mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/pdf",
    mineru_path="/custom/path/to/mineru"
)
```

### "HIGH risk" safety warning
This means potential PII was detected in redacted output. Options:
1. Use stricter privacy level: `privacy_level="strict"`
2. Add more preserve patterns to allow specific content
3. Review audit_log to see what triggered the warning

### Slow extraction
MinerU can be slow on large PDFs. Default timeout is 300s. The system will show extraction progress.

## Output Structure

```json
{
  "redacted_markdown": "Markdown with [REDACTED_TYPE_N] labels",
  "audit_log": [
    {
      "index": 0,
      "pii_type": "SSN",
      "original_length": 11,
      "position": 1234,
      "redacted_as": "[REDACTED_SSN_0]"
    }
  ],
  "statistics": {
    "total_redactions": 15,
    "original_length": 5000,
    "redacted_length": 4800,
    "reduction_bytes": 200,
    "redactions_by_type": {
      "SSN": 1,
      "EIN": 1,
      "EMAIL": 2,
      "PHONE": 3
    }
  },
  "safety_report": {
    "is_safe": true,
    "risk_level": "LOW",
    "issues": [],
    "recommendation": "Safe for LLM analysis"
  },
  "metadata": {
    "source_pdf": "/path/to/file.pdf",
    "output_file": "/path/to/output.md",
    "privacy_level": "strict",
    "timestamp": "2025-10-05T11:00:00"
  }
}
```

## Best Practices

1. **Always start with "strict"** for tax/medical/legal documents
2. **Use preserve_patterns** to keep necessary context
3. **Check safety_report** before LLM analysis
4. **Review audit_log** to understand what was redacted
5. **Test with sample first** before processing batch

## Integration with Vault

The server is configured in:
`/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/.mcp.json`

Bundled MinerU located at:
`/Users/smian/.claude/mcp_servers/privacy_pdf/mineru/`

## Next Steps

After restarting Claude Code, test with:
```python
mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/Users/smian/Library/Mobile Documents/iCloud~md~obsidian/Documents/shoaib-life-hub/roles/life-architect/projects/tax-preparation-2025/tax-docs-dropbox/01-Income/1099-Forms/1099-K/2024 Form 1099-K.pdf",
    privacy_level="strict",
    preserve_patterns=["Box \\d+:", "\\$[\\d,]+\\.\\d{2}", "Form 1099-K"]
)
```

---

**Privacy-first PDF processing for the age of LLMs** 🔒
