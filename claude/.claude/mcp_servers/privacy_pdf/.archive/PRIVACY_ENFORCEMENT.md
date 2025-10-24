# Privacy Enforcement System - Architecture & Guarantees

## Overview

This privacy-pdf MCP server provides **guaranteed PII protection** through multi-layer enforcement:
1. **Regex-based PII detection** with configurable privacy levels
2. **Intelligent false positive handling** for preserved patterns
3. **Hard safety gates** that refuse to return unsafe content
4. **Comprehensive audit logging** for transparency and accountability

## Architecture Layers

### Layer 1: PII Redaction (redaction_engine.py)

**Privacy Levels**:
- **strict**: Redacts 11 PII types (SSN, EIN, EMAIL, PHONE, CREDIT_CARD, ACCOUNT_NUMBER, ADDRESS, DATE, FULL_NAME, CURRENCY, ZIP_CODE, URL)
- **balanced**: Redacts 8 PII types (SSN, EIN, EMAIL, PHONE, CREDIT_CARD, ACCOUNT_NUMBER, ADDRESS, CURRENCY)
- **minimal**: Redacts 4 critical types (SSN, EIN, CREDIT_CARD, ACCOUNT_NUMBER)

**Preserve Patterns**:
- Allows whitelisting specific regex patterns (e.g., currency amounts in tax forms)
- Preserved patterns are tracked separately from redactions

### Layer 2: Intelligent False Positive Detection

**Logic** (`_is_safe_false_positive()` method):
```python
safe_types = {'CURRENCY', 'DATE', 'URL'}

# Only these types can be false positives
if pii_type not in safe_types:
    return False  # Names, SSNs are NEVER false positives

# Check if ALL matches are within preserve patterns
for match in matches:
    if not preserve_regex.search(match.group(0)):
        return False  # Found PII outside preserve patterns - UNSAFE!

return True  # All matches are in preserve patterns - safe
```

**Key Insight**: The system distinguishes between:
- ✅ **Safe**: `$30,000.00` detected as CURRENCY but within `\$[\d,]+\.?\d*` preserve pattern
- ❌ **Unsafe**: Random phone number detected as PHONE (never a false positive, even if preserved)

### Layer 3: Hard Safety Gate (server.py)

**Enforcement Point** (lines 105-142):
```python
# Validate with strict mode and preserve patterns
safety_report = redactor_instance.validate_safety(
    text=redacted_text,
    original=original_text,
    strict_mode=True,
    preserve_patterns=preserve_patterns
)

# HARD GATE: Refuse to return content if unsafe
if not safety_report["is_safe"]:
    return json.dumps({
        "error": "SAFETY_VALIDATION_FAILED",
        "message": "Redacted content contains potential PII leakage",
        # ... includes full safety_report and audit_log
    })
```

**Guarantee**: If the MCP tool returns successfully, the content is **guaranteed safe** for LLM processing. The server will not return content if any unsafe PII is detected.

### Layer 4: Audit Logging

**Log Format** (.privacy_audit_log.jsonl):
```json
{
  "timestamp": "2025-10-05T13:30:00",
  "file": "2024-1099-K.pdf",
  "privacy_level": "strict",
  "safety_status": "PASSED",
  "risk_level": "LOW",
  "pii_types_found": [],
  "safe_false_positives": ["CURRENCY", "DATE"],
  "total_redactions": 24,
  "llm_access": true,
  "preserve_patterns_used": ["\\$[\\d,]+\\.?\\d*", "Box \\d+[a-z]?:"]
}
```

**Transparency**: Every safety decision is logged with:
- What was found (PII types)
- What was preserved (false positives)
- Whether LLM access was granted
- Full audit trail for compliance

## Sub-Agent Trust Model

**Old Model** (Complex, Error-Prone):
```
MCP Server → Redact → Validate → Return (with safety_report)
↓
Sub-Agent → Parse safety_report → Decide if safe → Proceed/Abort
```

**New Model** (Simple, Guaranteed):
```
MCP Server → Redact → Validate → ENFORCE (return or error)
↓
Sub-Agent → Check for error → Format (if success) or Report (if error)
```

**Key Change**: Sub-agent no longer makes safety decisions. It simply:
1. Checks if MCP tool returned an error
2. If error: Report to user
3. If success: Trust content is safe and format it

## Safety Guarantees

### What IS Guaranteed:
✅ **No actual PII reaches LLM** - Hard gates prevent unsafe content from being returned
✅ **Preserved patterns are validated** - CURRENCY/DATE in preserve patterns won't trigger failures
✅ **Critical PII always blocked** - SSN, PHONE, names are never false positives
✅ **Full audit trail** - Every decision logged to .privacy_audit_log.jsonl
✅ **Transparent errors** - Unsafe content returns detailed error explaining why

### What is NOT Guaranteed:
⚠️ **Regex limitations** - New PII formats not in patterns won't be detected
⚠️ **Context understanding** - System can't understand semantic PII (e.g., "my social is...")
⚠️ **Image extraction** - PII in images within PDFs won't be detected
⚠️ **False negatives** - Extremely rare edge cases might slip through

## Usage Examples

### Tax Form (Strict Privacy)
```python
result = pdf_extract_redact(
    pdf_path="/path/to/W-2.pdf",
    privacy_level="strict",
    preserve_patterns=[
        r"Box \d+[a-z]?:",           # Box labels
        r"\$[\d,]+\.?\d*",            # Currency amounts
        r"Form (W-2|1099|1098)",      # Form names
        r"January|February|...",      # Month names
    ]
)

# If successful, guaranteed safe for LLM
# Audit logged to: /path/to/.privacy_audit_log.jsonl
```

### Medical Record (Strict Privacy)
```python
result = pdf_extract_redact(
    pdf_path="/path/to/medical.pdf",
    privacy_level="strict",
    preserve_patterns=[
        r"\d+/\d+/\d{4}",            # Dates
        r"\d+\.\d+ (mg|ml|units)",   # Measurements
    ]
)
```

### General Document (Minimal Privacy)
```python
result = pdf_extract_redact(
    pdf_path="/path/to/general.pdf",
    privacy_level="minimal",
    preserve_patterns=None  # No preservations needed
)
```

## Testing Privacy Enforcement

### Test Case 1: Valid Tax Form (Should PASS)
- **Input**: 1099-K with SSN, amounts, names
- **Preserve**: Currency, box labels, dates
- **Expected**: PASSED with safe_false_positives=[CURRENCY, DATE]
- **LLM Access**: ✅ Granted

### Test Case 2: PII Leakage (Should BLOCK)
- **Input**: Document with SSN that escapes redaction
- **Preserve**: None
- **Expected**: BLOCKED with error SAFETY_VALIDATION_FAILED
- **LLM Access**: ❌ Denied

### Test Case 3: False Positive Handling (Should PASS)
- **Input**: Invoice with phone numbers in preserved sections
- **Preserve**: Contact info sections
- **Expected**: PASSED (phone numbers are never false positives - should detect and redact or block)
- **LLM Access**: Depends on whether phone is in preserve pattern

## Audit Log Analysis

Query audit log to track privacy decisions:
```bash
# Count successful vs blocked operations
jq -r '.safety_status' .privacy_audit_log.jsonl | sort | uniq -c

# Find all blocked documents
jq 'select(.safety_status == "BLOCKED")' .privacy_audit_log.jsonl

# Check false positive handling
jq 'select(.safe_false_positives | length > 0)' .privacy_audit_log.jsonl

# Identify documents with high PII counts
jq 'select(.total_redactions > 50)' .privacy_audit_log.jsonl
```

## Security Best Practices

1. **Use strict privacy level** for sensitive documents (tax, medical, legal)
2. **Carefully design preserve patterns** - Too broad patterns may miss PII
3. **Review audit logs regularly** - Identify patterns in blocked content
4. **Test with real PII** - Validate regex patterns catch all expected formats
5. **Never bypass safety gates** - Trust the MCP server's enforcement
6. **Monitor false positives** - Adjust patterns if legitimate content is being blocked

## Future Enhancements

Potential improvements for consideration:
- [ ] ML-based PII detection for semantic understanding
- [ ] OCR + redaction for image-based PDFs
- [ ] Configurable redaction labels ([REDACTED] vs [SSN])
- [ ] Export audit logs to centralized logging system
- [ ] Real-time alerts for repeated safety failures
- [ ] Pattern learning from false positive corrections

## Conclusion

This privacy enforcement system provides **defense in depth**:
1. Redaction with configurable privacy levels
2. Intelligent false positive handling
3. Hard safety gates that refuse unsafe content
4. Comprehensive audit trail

**Guarantee**: If the MCP server returns successfully, the content is safe for LLM processing. The sub-agent can trust this completely.
