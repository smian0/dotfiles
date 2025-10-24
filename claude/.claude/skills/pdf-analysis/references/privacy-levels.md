# Privacy Level Selection Guide

This reference explains how the pdf-analysis skill automatically selects privacy levels based on document type detection.

## Privacy Levels Overview

The MCP server supports three privacy levels with different redaction strategies:

### Strict
**When Used:**
- Tax documents (W-2, 1099, Schedule K-1, tax returns) - **Use with `preserve_patterns` for dates**
- Medical records (lab results, prescriptions, health insurance) - **Do NOT preserve dates**
- Documents with highly sensitive PII

**What Gets Redacted:**
- Social Security Numbers (SSN)
- Employer Identification Numbers (EIN)
- Full names
- Complete addresses
- Phone numbers
- Account numbers
- Medical record numbers
- **Dates (unless `preserve_patterns` is used)**
- URLs

**What Gets Preserved:**
- Dollar amounts and percentages
- Form box labels (e.g., "Box 1: Wages")
- Document structure
- Non-PII descriptive text

**Tax Document Date Preservation:**
For tax forms, dates are structural information (tax year, reporting periods, deadlines). Use `preserve_patterns`:
```python
preserve_patterns=[
    r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # MM/DD/YYYY
    r'\b(?:January|...|December)\s+\d{1,2},?\s+\d{4}\b'  # Month DD, YYYY
]
```

**Example Output (Tax Document with Date Preservation):**
```
Box 1 (Wages): $85,000.00
Tax Year: 2024
Employer: [REDACTED_FULL_NAME_0]
EIN: [REDACTED_EIN_1]
Employee SSN: [REDACTED_SSN_2]
```

**Example Output (Medical Record without Date Preservation):**
```
Patient: [REDACTED_FULL_NAME_0]
DOB: [REDACTED_DATE_1]
Procedure Date: [REDACTED_DATE_2]
Diagnosis: [Medical information]
```

---

### Balanced
**When Used:**
- Legal contracts and NDAs
- Business agreements
- Financial statements (not tax forms)
- General business correspondence

**What Gets Redacted:**
- SSNs and EINs
- Account numbers
- Credit card numbers
- Email addresses
- Phone numbers
- Street addresses (full address patterns)

**What Gets Preserved:**
- **Full names** (for structural context in contracts)
- **Dates** (all date patterns)
- **URLs** (reference links)
- Company names
- City/state locations
- Dollar amounts

**Note:** If you need to redact names but preserve dates, use `strict` with `preserve_patterns` instead of `balanced`.

**Example Output:**
```
Agreement between John Smith and Jane Doe
Date: December 15, 2024
Payment: $50,000
Account: [REDACTED_ACCOUNT_NUMBER_0]
SSN: [REDACTED_SSN_1]
```
*Note: Names and dates preserved for contract context*

---

### Minimal
**When Used:**
- **Resumes/CVs** - Preserves complete resume content (names, contact info, work history)
- General documents (invoices, receipts)
- Public information
- Documents with low sensitivity
- Default fallback

**What Gets Redacted:**
- SSNs (rarely appear on resumes)
- EINs (rarely appear on resumes)
- Credit card numbers (rarely appear on resumes)
- Full account numbers (rarely appear on resumes)

**What Gets Preserved:**
- ✅ Full names (candidate/person, company names)
- ✅ Addresses (home address, work location)
- ✅ Phone numbers
- ✅ Email addresses
- ✅ URLs and portfolio links
- ✅ Company information
- ✅ Job titles and dates
- ✅ Skills and accomplishments
- ✅ Educational information

**Perfect for Resume Parsing:**
Minimal privacy level provides **zero meaningful redactions** for resume analysis:
```
Resume for Jane Doe
Address: 123 Main St, Anytown, CA 90210
Phone: (555) 123-4567
Email: jane.doe@example.com
LinkedIn: linkedin.com/in/janedoe
Company: Acme Corporation
Position: Senior Software Engineer
Period: 2020-2024
```
*Complete resume content visible - suitable for resume parsing, ATS analysis, and career coaching*

**Example Output (General Document):**
```
Invoice for Jane Doe
Address: 123 Main St, Anytown, CA 90210
Amount: $1,500.00
Card ending in: [REDACTED_CREDIT_CARD_0]
```

---

## Document Type Detection Patterns

The skill uses path and filename analysis to auto-detect document types:

### Tax Documents → Strict
**Path patterns:**
- `/tax/`, `/taxes/`, `/tax-docs/`
- `/1099/`, `/w2/`, `/w-2/`
- `/tax-return/`, `/irs/`

**Filename patterns:**
- `W-2`, `W2`, `1099`, `1098`
- `Schedule`, `Form 1040`
- `tax-return`, `tax_form`
- `K-1`, `K1`

### Medical Documents → Strict
**Path patterns:**
- `/medical/`, `/health/`, `/healthcare/`
- `/insurance/`, `/lab-results/`
- `/prescription/`

**Filename patterns:**
- `medical`, `health-record`
- `prescription`, `lab-result`
- `diagnosis`, `treatment`
- `insurance-card`, `EOB`

### Legal Documents → Balanced
**Path patterns:**
- `/legal/`, `/contracts/`
- `/agreement/`, `/nda/`

**Filename patterns:**
- `contract`, `agreement`
- `NDA`, `non-disclosure`
- `terms-of-service`, `TOS`
- `license-agreement`

### Financial Documents → Balanced
**Path patterns:**
- `/financial/`, `/bank/`
- `/brokerage/`, `/statements/`
- `/investment/`

**Filename patterns:**
- `bank-statement`, `account-statement`
- `brokerage`, `investment`
- `portfolio`, `financial-report`

### Resume/CV Documents → Minimal
**Path patterns:**
- `/resume/`, `/resumes/`
- `/cv/`, `/curriculum/`
- `/hiring/`, `/recruitment/`
- `/candidates/`

**Filename patterns:**
- `resume`, `Resume`, `RESUME`
- `cv`, `CV`, `Curriculum`
- `curriculum-vitae`, `cover-letter`
- Anything with name + resume/cv pattern (e.g., `John_Doe_Resume.pdf`)

**Note:** Minimal level ensures complete resume content is visible (names, contact info, work history, dates, URLs) for resume parsing, ATS analysis, and career coaching.

### General Documents → Minimal
**Default for:**
- Any document not matching above patterns
- Personal correspondence
- General business documents
- Invoices, receipts, general forms

---

## Troubleshooting Auto-Detection

### Document Classified Incorrectly?

If a document is getting the wrong privacy level:

1. **Check the path and filename** - Does it match the patterns above?
2. **Rename strategically** - Add keywords like "tax" or "medical" to the filename
3. **Move to appropriate folder** - Organize into `/tax/`, `/medical/`, etc.

### Need Custom Privacy Level?

The skill currently only supports auto-detection. For custom privacy levels:
- Use the MCP tools directly: `mcp__privacy_pdf__pdf_extract_redact(privacy_level="custom")`
- Or organize files to match auto-detection patterns

---

## Common Use Cases

### Tax Season Batch Processing
```bash
# Organize files:
~/tax-docs/2024/
  ├── W2-employer1.pdf
  ├── W2-employer2.pdf
  ├── 1099-INT-bank.pdf
  └── Schedule-K1.pdf

# All auto-detected as "strict"
```

### Medical Records Review
```bash
# Organize files:
~/medical/lab-results/
  ├── bloodwork-2024-01.pdf
  ├── radiology-report.pdf
  └── prescription-history.pdf

# All auto-detected as "strict"
```

### Contract Review
```bash
# Organize files:
~/legal/contracts/
  ├── service-agreement.pdf
  ├── NDA-vendor.pdf
  └── employment-contract.pdf

# All auto-detected as "balanced"
```

---

## False Positives and Preservation

The redaction engine handles common false positives:

**Preserved (not redacted):**
- ✅ Dates: `12/31/2024` (not SSN)
- ✅ Currency: `$1,234.56` (not account number)
- ✅ Form labels: `Box 1`, `Line 12a` (not PII)
- ✅ Percentages: `7.5%` (not part of SSN)

**Smart detection:**
- Tax ID format in context of "EIN:" → Redacted
- Same format in date context → Preserved
- Pattern matching considers surrounding text

---

*For implementation details, see the privacy_pdf MCP server documentation.*
