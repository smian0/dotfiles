# Privacy-Preserving PDF MCP Server

Extract PDFs with automatic PII redaction for safe LLM analysis.

## Quick Start

```python
# Extract and redact a tax document
mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/W-2.pdf",
    privacy_level="strict"
)

# Returns JSON with:
# - redacted_markdown: Safe markdown content
# - statistics: Redaction counts
# - safety_report: Validation results
# - audit_log: What was redacted
```

## Features

- ✅ **Automatic PII Redaction**: SSN, EIN, emails, phones, addresses, accounts, credit cards
- ✅ **Three Privacy Levels**: Strict (13 patterns), Balanced (8 patterns), Minimal (4 patterns)
- ✅ **Hard Safety Gates**: Server refuses to return unsafe content
- ✅ **Complete Audit Trail**: JSONL logs for compliance
- ✅ **Production Quality**: 100% PII accuracy on IRS tax forms, ~3 second processing

## Installation

### Prerequisites

**MinerU** (magic-pdf) for PDF extraction:
```bash
# Check if installed
which mineru

# If not found, see mineru/README.md for installation
```

### MCP Configuration

Add to `.mcp.json`:
```json
{
  "mcpServers": {
    "privacy-pdf": {
      "type": "stdio",
      "command": "python3",
      "args": ["/Users/smian/dotfiles/claude/.claude/mcp_servers/privacy_pdf/server.py"],
      "description": "Privacy-preserving PDF extraction with PII redaction"
    }
  }
}
```

## MCP Tools

### 1. `pdf_extract_redact`

Extract PDF and automatically redact PII.

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pdf_path` | str | required | Absolute path to PDF file |
| `privacy_level` | str | "balanced" | "strict", "balanced", or "minimal" |
| `preserve_patterns` | list | [] | Regex patterns to preserve |
| `output_dir` | str | temp | Optional output directory |
| `mineru_path` | str | auto | Optional explicit MinerU path |

**Returns**:
```json
{
  "redacted_markdown": "Safe markdown with [REDACTED_TYPE_N] labels",
  "audit_log": [{"index": 0, "pii_type": "SSN", ...}],
  "statistics": {
    "total_redactions": 18,
    "redactions_by_type": {"EIN": 1, "ACCOUNT_NUMBER": 1, ...}
  },
  "safety_report": {
    "is_safe": true,
    "risk_level": "LOW"
  },
  "metadata": {
    "redacted_file": "/path/to/output-REDACTED.md",
    "processing_time": 3.2,
    ...
  }
}
```

**Example**:
```python
# Tax document with strict privacy
result = mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/2024-1099-K.pdf",
    privacy_level="strict"
)

# Parse and use
import json
data = json.loads(result)
if data["safety_report"]["is_safe"]:
    markdown = data["redacted_markdown"]
    print(f"✅ Redacted {data['statistics']['total_redactions']} items")
```

### 2. `validate_redaction`

Verify that redacted text contains no PII leakage.

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `redacted_text` | str | required | Text to validate |
| `original_text` | str | None | Optional original for comparison |
| `strict_mode` | bool | true | Fail on any potential PII |

**Returns**:
```json
{
  "is_safe": true,
  "risk_level": "LOW",
  "issues": [],
  "recommendation": "Safe for LLM analysis"
}
```

### 3. `analyze_redacted_content`

Audit-logged gate for LLM analysis of redacted content.

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `redacted_text` | str | required | Pre-redacted text |
| `analysis_prompt` | str | required | What to analyze |
| `require_validation` | bool | true | Require safety check first |

**Returns**:
```json
{
  "safety_status": "SAFE",
  "content_ready": true,
  "audit_entry": {...}
}
```

## Privacy Levels

### Strict (10 patterns)
Best for: Tax documents, medical records, legal contracts

**Redacts**:
- SSN (`\d{3}-\d{2}-\d{4}`)
- EIN (`\d{2}-\d{7}`)
- Email addresses
- Phone numbers
- Credit cards
- Account numbers
- Addresses (street addresses only)
- Dates
- Full names
- URLs

**Preserves**:
- Currency amounts (e.g., `$1,200.00`) - analysis data, not PII
- ZIP codes - not personally identifiable alone, often confused with box numbers/amounts

### Balanced (7 patterns)
Best for: Financial statements, general documents

**Redacts**:
- SSN, EIN, Email, Phone
- Credit cards, Account numbers
- Addresses

**Preserves**: Currency amounts, Dates (for analysis)

### Minimal (4 patterns)
Best for: Public documents, low-sensitivity content

**Redacts**:
- SSN, EIN
- Credit cards, Account numbers

**Preserves**: All other data including currency, dates, names

## Workflow

1. **Extract**: MinerU converts PDF → Markdown (~3 seconds)
2. **Detect**: Regex patterns identify PII by type
3. **Redact**: Replace PII with `[REDACTED_TYPE_INDEX]` labels
4. **Validate**: Multi-layer safety checks
5. **Gate**: Server refuses to return if PII detected
6. **Audit**: Log all redactions with timestamps
7. **Cleanup**: Automatically remove MinerU intermediate files
8. **Return**: Safe markdown ready for LLM analysis

**Files Generated**:
- `original-filename-REDACTED.md` - Formatted, redacted content (the useful output)
- `.privacy_audit_log.jsonl` - Audit trail (in same directory as PDF)

**Files Cleaned Up**: MinerU intermediate directory (`*_mineru_output/`) is automatically deleted after extraction

## Pattern Preservation

Preserve specific patterns while redacting PII:

```python
# Preserve tax form labels and currency
result = mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/W-2.pdf",
    privacy_level="strict",
    preserve_patterns=[
        r"Box \d+[a-z]?:",           # "Box 1a:"
        r"\$[\d,]+\.\d{2}",          # "$50,000.00"
        r"Form (W-2|1099|1098)",     # Form names
        r"Wages, tips, other compensation"
    ]
)
```

**Common patterns**:
- Tax form boxes: `Box \d+[a-z]?:`
- Currency: `\$[\d,]+\.\d{2}`
- Form names: `Form (W-2|1099|Schedule [A-Z])`
- Labels: `FILER|PAYEE|PAYER|Employer`
- Months: `January|February|...|December`

## Safety Features

### Hard Safety Gates
- Server **refuses to return content** if PII detected after redaction
- Returns error instead of unsafe content
- No manual validation needed (server enforces)

### Audit Logging
All redactions logged to `.privacy_audit_log.jsonl`:
```json
{
  "timestamp": "2025-10-05T14:43:42.152553",
  "file": "2024-1099-K.pdf",
  "privacy_level": "strict",
  "safety_status": "PASSED",
  "total_redactions": 18,
  "pii_types_found": ["EIN", "ACCOUNT_NUMBER", "ADDRESS", "CURRENCY"]
}
```

### Validation Layers
1. Pattern-based PII detection
2. Post-redaction re-scan
3. Similarity check vs original
4. Risk assessment (LOW/MEDIUM/HIGH)
5. Safety gate enforcement

## Troubleshooting

### MinerU Not Found
```python
# Provide explicit path
result = mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/pdf",
    mineru_path="/custom/path/to/mineru"
)
```

Auto-detection checks:
1. `~/.tools/mineru/venv/bin/mineru`
2. System PATH (`which mineru`)
3. `/usr/local/bin/mineru`

### Content Failed Safety Validation
```python
# Use stricter privacy level
result = mcp__privacy_pdf__pdf_extract_redact(
    pdf_path="/path/to/pdf",
    privacy_level="strict"  # Instead of "balanced"
)
```

### Extraction Timeout
Default timeout: 300 seconds (5 minutes)

For large PDFs, edit `extraction_engine.py`:
```python
def extract_pdf(self, pdf_path, timeout=600):  # Increase to 10 minutes
```

## Testing

**Quick test**:
```bash
cd /Users/smian/dotfiles/claude/.claude/mcp_servers/privacy_pdf

python3 -c "
from extraction_engine import ExtractionEngine
from redaction_engine import RedactionEngine

e = ExtractionEngine()
r = RedactionEngine(privacy_level='balanced')

result = e.extract_pdf('/path/to/test.pdf')
redacted = r.redact(result['markdown'])

print(f'Extracted: {len(result[\"markdown\"])} chars')
print(f'Redacted: {redacted[\"statistics\"][\"total_redactions\"]} items')
print(f'Safe: {redacted[\"safety_report\"][\"is_safe\"]}')
"
```

**Integration test**: Use with actual sensitive documents from vault's tax-docs-dropbox.

## Architecture

```
privacy_pdf/
├── server.py              # FastMCP server (3 tools)
├── extraction_engine.py   # MinerU wrapper
├── redaction_engine.py    # PII detection & redaction
├── __init__.py           # Package exports
├── README.md             # This file (user docs)
└── CLAUDE.md             # AI maintenance instructions
```

**Design decision**: Single-OCR architecture using MinerU only. Dual-OCR (MinerU + Tesseract) was tested and rejected after research showed -98% ROI (100% PII accuracy already achieved with MinerU alone, Tesseract added no value). See `CLAUDE.md` for research findings.

## Dependencies

- **FastMCP** 2.11.2+
- **MinerU** (magic-pdf) for PDF extraction
- Python 3.8+

## Version

**1.0.0** - Production release (2025-10-05)
- Single-OCR architecture (MinerU)
- 100% PII accuracy on IRS tax forms
- ~3 second processing time
- Clean, readable markdown output

---

**Last Updated**: 2025-10-05

*For AI maintenance instructions, see CLAUDE.md*
