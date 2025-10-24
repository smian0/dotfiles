#!/usr/bin/env python3
"""
Privacy-Preserving PDF MCP Server
Extract PDFs with automatic PII redaction for safe LLM analysis using MinerU OCR
"""
import sys
import json
from pathlib import Path
from typing import Optional, List
from fastmcp import FastMCP

# Import engines (try relative import first, then absolute)
try:
    from .extraction_engine import ExtractionEngine
    from .redaction_engine import RedactionEngine
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from extraction_engine import ExtractionEngine
    from redaction_engine import RedactionEngine

# Initialize FastMCP server
mcp = FastMCP(
    "privacy_pdf",
    instructions="Privacy-preserving PDF processing with automatic PII redaction"
)

# Initialize engines
extractor = ExtractionEngine()
redactor = RedactionEngine()


@mcp.tool()
def pdf_extract_redact(
    pdf_path: str,
    privacy_level: str = "balanced",
    preserve_patterns: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    mineru_path: Optional[str] = None
) -> str:
    """
    Extract PDF using MinerU and automatically redact PII.

    This tool:
    1. Runs MinerU to extract PDF content to markdown
    2. Detects PII using regex patterns based on privacy level
    3. Redacts detected PII with labeled replacements
    4. Validates safety of redacted output
    5. Returns redacted markdown with audit log

    Args:
        pdf_path: Absolute path to PDF file
        privacy_level: 'strict', 'balanced', 'minimal', or 'business' (default: balanced)
        preserve_patterns: Optional list of regex patterns to preserve
        output_dir: Optional output directory for MinerU
        mineru_path: Optional path to mineru executable

    Returns:
        JSON string containing redacted_markdown, audit_log, safety_report, and metadata
    """
    # Step 1: Extract PDF using MinerU
    extraction_result = extractor.extract_pdf(
        pdf_path=pdf_path,
        output_dir=output_dir,
        mineru_path=mineru_path
    )

    if "error" in extraction_result:
        return json.dumps({
            "error": "PDF extraction failed",
            "details": extraction_result
        }, indent=2)

    # Step 2: Redact PII from extracted markdown
    markdown_content = extraction_result["markdown"]

    # Initialize redactor with specified privacy level
    try:
        redactor_instance = RedactionEngine(privacy_level=privacy_level)
    except ValueError as e:
        return json.dumps({
            "error": "Invalid privacy_level",
            "details": str(e),
            "valid_levels": ["strict", "balanced", "minimal"]
        }, indent=2)

    redaction_result = redactor_instance.redact(
        text=markdown_content,
        preserve_patterns=preserve_patterns
    )

    if "error" in redaction_result:
        return json.dumps({
            "error": "Redaction failed",
            "details": redaction_result
        }, indent=2)

    # Step 3: Validate safety with hard enforcement
    safety_report = redactor_instance.validate_safety(
        text=redaction_result["redacted_text"],
        original=markdown_content,
        strict_mode=True,
        preserve_patterns=preserve_patterns
    )

    # Step 3a: Create audit log entry for this safety decision
    from datetime import datetime
    pdf_file = Path(pdf_path)

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "file": pdf_file.name,
        "file_path": str(pdf_file),
        "privacy_level": privacy_level,
        "safety_status": "BLOCKED" if not safety_report["is_safe"] else "PASSED",
        "risk_level": safety_report["risk_level"],
        "pii_types_found": [i.get('pii_type', i.get('issue', 'unknown')) for i in safety_report.get('issues', [])],
        "safe_false_positives": [fp['pii_type'] for fp in safety_report.get('safe_false_positives', [])],
        "total_redactions": redaction_result['statistics']['total_redactions'],
        "llm_access": safety_report["is_safe"],
        "preserve_patterns_used": preserve_patterns or []
    }

    # Save audit entry to log file
    audit_log_path = pdf_file.parent / ".privacy_audit_log.jsonl"
    try:
        with open(audit_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry) + '\n')
    except Exception as e:
        # Don't fail the operation if audit logging fails
        pass

    # HARD SAFETY GATE: Refuse to return content if unsafe
    if not safety_report["is_safe"]:
        error_response = {
            "error": "SAFETY_VALIDATION_FAILED",
            "message": "Redacted content contains potential PII leakage",
            "safety_report": safety_report,
            "recommendation": "Manual review required - do not send to LLM",
            "audit_log": redaction_result["audit_log"],
            "statistics": redaction_result["statistics"],
            "audit_entry": audit_entry
        }

        # CRITICAL: Sanitize error response to prevent PII leakage in error messages
        try:
            error_response = redactor_instance.sanitize_response(error_response)
        except Exception as e:
            # If sanitization detects PII in response, return minimal safe error
            return json.dumps({
                "error": "CRITICAL_SECURITY_VIOLATION",
                "message": "Response blocked - PII detected in error metadata",
                "details": str(e),
                "recommendation": "Contact system administrator - redaction logic has a bug"
            }, indent=2)

        return json.dumps(error_response, indent=2)

    # Step 4: Save redacted markdown with minimal frontmatter
    import shutil
    redacted_md_path = pdf_file.parent / f"{pdf_file.stem}-REDACTED.md"

    try:
        with open(redacted_md_path, 'w', encoding='utf-8') as f:
            # Write minimal frontmatter - only critical debug info
            f.write(f"---\n")
            f.write(f"source: {pdf_file.name}\n")
            f.write(f"privacy_level: {privacy_level}\n")
            if redaction_result['statistics']['redactions_by_type']:
                f.write(f"redacted: {', '.join(redaction_result['statistics']['redactions_by_type'].keys())}\n")
            f.write(f"---\n\n")
            f.write(redaction_result["redacted_text"])

        redacted_file_saved = str(redacted_md_path)
    except Exception as e:
        redacted_file_saved = None

    # Step 5: Clean up MinerU intermediate files
    output_dir_path = extraction_result["metadata"].get("output_dir")
    cleanup_successful = extraction_result["metadata"].get("intermediate_files_cleaned", False)

    if output_dir_path and Path(output_dir_path).exists() and not cleanup_successful:
        try:
            shutil.rmtree(output_dir_path)
            cleanup_successful = True
        except Exception as e:
            # Don't fail the whole operation if cleanup fails
            cleanup_successful = False

    # Step 6: Return comprehensive result
    return json.dumps({
        "redacted_markdown": redaction_result["redacted_text"],
        "audit_log": redaction_result["audit_log"],
        "statistics": redaction_result["statistics"],
        "safety_report": safety_report,
        "audit_entry": audit_entry,
        "metadata": {
            **extraction_result["metadata"],
            "privacy_level": privacy_level,
            "preserve_patterns": preserve_patterns or [],
            "timestamp": redaction_result["timestamp"],
            "redacted_file": redacted_file_saved,
            "intermediate_files_cleaned": cleanup_successful,
            "audit_log_file": str(audit_log_path)
        }
    }, indent=2)


@mcp.tool()
def validate_redaction(
    redacted_text: str,
    original_text: Optional[str] = None,
    strict_mode: bool = True
) -> str:
    """
    Validate that redacted text contains no PII leakage.

    Performs multi-layer safety checks:
    1. Pattern matching for known PII formats
    2. Similarity comparison with original (if provided)
    3. Risk assessment and recommendations

    Args:
        redacted_text: Text to validate for PII
        original_text: Optional original text for comparison
        strict_mode: If True, fail on any potential PII

    Returns:
        JSON string containing safety report with risk level and issues
    """
    # Use balanced redactor for validation
    redactor_instance = RedactionEngine(privacy_level="balanced")

    safety_report = redactor_instance.validate_safety(
        text=redacted_text,
        original=original_text,
        strict_mode=strict_mode
    )

    return json.dumps(safety_report, indent=2)


@mcp.tool()
def analyze_redacted_content(
    redacted_text: str,
    analysis_prompt: str,
    require_validation: bool = True
) -> str:
    """
    Prepare redacted content for safe LLM analysis with audit logging.

    This tool acts as a safety gate before sending content to LLMs:
    1. Optionally validates safety of redacted text
    2. Logs the analysis request for audit trail
    3. Returns confirmation that content is safe for analysis

    Args:
        redacted_text: Pre-redacted text to analyze
        analysis_prompt: What you want to analyze (e.g., "Calculate total income")
        require_validation: Require safety check first (default: True)

    Returns:
        JSON string with safety status and ready-for-analysis content
    """
    if require_validation:
        # Validate safety first
        redactor_instance = RedactionEngine(privacy_level="balanced")
        safety_report = redactor_instance.validate_safety(
            text=redacted_text,
            strict_mode=True
        )

        if not safety_report["is_safe"]:
            return json.dumps({
                "safe_for_analysis": False,
                "error": "Content failed safety validation",
                "safety_report": safety_report,
                "recommendation": "Do NOT send to LLM - contains PII leakage"
            }, indent=2)

    # Audit log entry
    from datetime import datetime
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "analyze_redacted_content",
        "analysis_prompt": analysis_prompt,
        "content_length": len(redacted_text),
        "validation_performed": require_validation
    }

    return json.dumps({
        "safe_for_analysis": True,
        "content": redacted_text,
        "analysis_prompt": analysis_prompt,
        "audit_log_entry": audit_entry,
        "recommendation": "Safe to proceed with LLM analysis"
    }, indent=2)


@mcp.tool()
def pdf_extract_k1_summary(
    pdf_path: str,
    privacy_level: str = "balanced"
) -> str:
    """
    Extract ONLY key tax fields from Schedule K-1 PDF forms.

    This tool is optimized for large K-1 PDFs that exceed token limits.
    Instead of returning full markdown, it extracts only critical tax data:
    - Partnership name & EIN
    - Partner name & SSN (redacted)
    - Key income/loss lines (1, 2, 9a, 10, 11)
    - Distributions (line 19)
    - Section 199A QBI info (box 20Z)

    Args:
        pdf_path: Absolute path to K-1 PDF file
        privacy_level: 'strict', 'balanced', 'minimal', or 'business' (default: balanced)

    Returns:
        JSON string with structured K-1 tax data (500-1000 tokens vs 25K-68K)
    """
    import re
    from datetime import datetime

    # Step 1: Extract PDF using PyMuPDF fast path
    extraction_result = extractor.extract_pdf(pdf_path=pdf_path)

    if "error" in extraction_result:
        return json.dumps({
            "error": "PDF extraction failed",
            "details": extraction_result
        }, indent=2)

    markdown = extraction_result["markdown"]

    # Step 2: Extract key K-1 fields using regex patterns
    k1_data = {
        "file": Path(pdf_path).name,
        "pages": extraction_result["metadata"].get("pages", 0),
        "extraction_method": extraction_result["metadata"].get("method", "unknown")
    }

    # Partnership info (Part I)
    partnership_ein = re.search(r"Partnership.{0,50}employer identification number[^\d]*(\d{2}-?\d{7})", markdown, re.IGNORECASE)
    partnership_name = re.search(r"Partnership.{0,30}name[^\n]*\n([^\n]+)", markdown, re.IGNORECASE)

    if partnership_ein:
        k1_data["partnership_ein"] = "[REDACTED_EIN]"
    if partnership_name:
        k1_data["partnership_name"] = partnership_name.group(1).strip()

    # Partner info (Part II) - redact SSN
    partner_ssn = re.search(r"Partner.{0,50}SSN[^\d]*(\d{3}-?\d{2}-?\d{4})", markdown, re.IGNORECASE)
    partner_name = re.search(r"Name, address.*\n([^\n]+)", markdown, re.IGNORECASE)

    if partner_ssn:
        k1_data["partner_ssn"] = "[REDACTED_SSN]"
    if partner_name:
        k1_data["partner_name"] = partner_name.group(1).strip()

    # Part III - Income/Loss/Deductions (key lines only)
    k1_data["tax_items"] = {}

    # Line 1: Ordinary business income (loss)
    line1 = re.search(r"^\s*1\s+Ordinary business income.*?[-\(\)]?\s*([\d,]+\.?)\s*$", markdown, re.MULTILINE | re.IGNORECASE)
    if line1:
        k1_data["tax_items"]["line_1_ordinary_income"] = line1.group(1)

    # Line 2: Net rental real estate income (loss)
    line2 = re.search(r"^\s*2\s+Net rental real estate.*?[-\(\)]?\s*([\d,]+\.?)\s*$", markdown, re.MULTILINE | re.IGNORECASE)
    if line2:
        k1_data["tax_items"]["line_2_rental_income"] = line2.group(1)

    # Line 9a: Net long-term capital gain (loss)
    line9a = re.search(r"^\s*9a\s+Net long-term capital.*?[-\(\)]?\s*([\d,]+\.?)\s*$", markdown, re.MULTILINE | re.IGNORECASE)
    if line9a:
        k1_data["tax_items"]["line_9a_ltcg"] = line9a.group(1)

    # Line 10: Net section 1231 gain (loss)
    line10 = re.search(r"^\s*10\s+Net section 1231.*?[-\(\)]?\s*([\d,]+\.?)\s*$", markdown, re.MULTILINE | re.IGNORECASE)
    if line10:
        k1_data["tax_items"]["line_10_section_1231"] = line10.group(1)

    # Line 11: Other income (loss)
    line11 = re.search(r"^\s*11\s+Other income.*?[-\(\)]?\s*([\d,]+\.?)\s*$", markdown, re.MULTILINE | re.IGNORECASE)
    if line11:
        k1_data["tax_items"]["line_11_other_income"] = line11.group(1)

    # Line 19: Distributions
    line19 = re.search(r"^\s*19\s+Distributions.*?[-\(\)]?\s*([\d,]+\.?)\s*$", markdown, re.MULTILINE | re.IGNORECASE)
    if line19:
        k1_data["tax_items"]["line_19_distributions"] = line19.group(1)

    # Box 20Z: Section 199A QBI
    qbi_match = re.search(r"20Z.*?QUALIFIED BUSINESS INCOME.*?[-\(\)$]?\s*([\d,]+\.?)", markdown, re.IGNORECASE | re.DOTALL)
    if qbi_match:
        k1_data["tax_items"]["box_20z_qbi"] = qbi_match.group(1)

    # State apportionment (if present)
    state_income = re.findall(r"(CALIFORNIA|GEORGIA|VIRGINIA|TEXAS|FLORIDA).*?[-\(\)$]?\s*([\d,]+\.?)", markdown, re.IGNORECASE)
    if state_income:
        k1_data["state_apportionment"] = {state: amount for state, amount in state_income}

    # Step 3: Audit logging
    pdf_file = Path(pdf_path)
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "file": pdf_file.name,
        "file_path": str(pdf_file),
        "privacy_level": privacy_level,
        "extraction_type": "k1_summary",
        "fields_extracted": len(k1_data.get("tax_items", {})),
        "llm_access": True
    }

    # Save audit
    audit_log_path = pdf_file.parent / ".privacy_audit_log.jsonl"
    try:
        with open(audit_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry) + '\n')
    except Exception:
        pass

    return json.dumps({
        "k1_summary": k1_data,
        "audit_entry": audit_entry,
        "note": f"Extracted {len(k1_data.get('tax_items', {}))} key tax fields from {k1_data.get('pages', 0)}-page K-1"
    }, indent=2)


@mcp.tool()
def pdf_extract_k1_hybrid(
    pdf_path: str,
    privacy_level: str = "balanced",
    output_dir: Optional[str] = None
) -> str:
    """
    Hybrid K-1 extraction: Smart page detection + selective MinerU OCR.

    This solves the token limit problem for large K-1 PDFs (49+ pages):
    1. PyMuPDF scans all pages (instant) to detect data pages
    2. MinerU OCR processes ONLY data pages (2-6 pages typical)
    3. Returns structured K-1 data with full PII redaction

    Benefits:
    - 8x faster than full MinerU (2-3 min vs 20 min)
    - Stays within token limits (6K vs 63K tokens)
    - Better structure preservation than PyMuPDF text extraction
    - Automatic PII redaction

    Args:
        pdf_path: Absolute path to K-1 PDF file
        privacy_level: 'strict', 'balanced', 'minimal', or 'business' (default: balanced)
        output_dir: Optional output directory for MinerU

    Returns:
        JSON string with redacted K-1 markdown from data pages only
    """
    import re
    import shutil
    import fitz
    from datetime import datetime

    # Import page filter for smart detection
    try:
        from .page_filter import PageFilter
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from page_filter import PageFilter

    pdf_file = Path(pdf_path)

    # Step 1: Smart page detection (instant with PyMuPDF)
    print(f"Step 1: Analyzing {pdf_file.name} for K-1 data pages...")
    page_filter = PageFilter()
    data_pages = page_filter.identify_k1_data_pages(pdf_path)

    if not data_pages:
        return json.dumps({
            "error": "No K-1 data pages detected",
            "suggestion": "Try pdf_extract_redact for full extraction",
            "file": pdf_file.name
        }, indent=2)

    total_pages = len(fitz.open(pdf_path))
    speedup = total_pages / len(data_pages)

    print(f"  ✓ Detected {len(data_pages)} data pages out of {total_pages} total pages")
    print(f"  ✓ {speedup:.1f}x reduction in processing time")
    print(f"  ✓ Data pages: {data_pages}")

    # Step 2: Extract ONLY data pages with MinerU OCR
    print(f"\nStep 2: Running MinerU OCR on {len(data_pages)} data pages...")
    print(f"  (Estimated time: {len(data_pages) * 25} seconds)")

    # Configure MinerU to process specific pages
    # Note: MinerU doesn't have native page selection, so we extract to temp PDF first
    doc = fitz.open(pdf_path)

    # Create temporary PDF with only data pages
    temp_pdf = Path(output_dir) / f"{pdf_file.stem}_data_pages_only.pdf" if output_dir else pdf_file.parent / f".temp_{pdf_file.stem}_data.pdf"
    temp_doc = fitz.open()

    for page_num in data_pages:
        temp_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

    temp_doc.save(str(temp_pdf))
    temp_doc.close()
    doc.close()

    print(f"  ✓ Created temporary PDF with {len(data_pages)} pages")

    # Now run MinerU on the filtered PDF
    extraction_result = extractor.extract_pdf(
        pdf_path=str(temp_pdf),
        output_dir=output_dir
    )

    # Clean up temp PDF
    try:
        temp_pdf.unlink()
    except:
        pass

    if "error" in extraction_result:
        return json.dumps({
            "error": "MinerU extraction failed",
            "details": extraction_result
        }, indent=2)

    print(f"  ✓ MinerU extraction complete")

    # Step 3: Redact PII from extracted markdown
    print(f"\nStep 3: Redacting PII...")
    markdown_content = extraction_result["markdown"]

    try:
        redactor_instance = RedactionEngine(privacy_level=privacy_level)
    except ValueError as e:
        return json.dumps({
            "error": "Invalid privacy_level",
            "details": str(e)
        }, indent=2)

    redaction_result = redactor_instance.redact(text=markdown_content)

    if "error" in redaction_result:
        return json.dumps({
            "error": "Redaction failed",
            "details": redaction_result
        }, indent=2)

    # Step 4: Validate safety
    safety_report = redactor_instance.validate_safety(
        text=redaction_result["redacted_text"],
        original=markdown_content,
        strict_mode=True
    )

    # Audit entry
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "file": pdf_file.name,
        "file_path": str(pdf_file),
        "extraction_method": "hybrid_pymupdf_mineru",
        "total_pages": total_pages,
        "data_pages_processed": len(data_pages),
        "pages_skipped": total_pages - len(data_pages),
        "speedup_factor": f"{speedup:.1f}x",
        "privacy_level": privacy_level,
        "safety_status": "BLOCKED" if not safety_report["is_safe"] else "PASSED",
        "risk_level": safety_report["risk_level"],
        "total_redactions": redaction_result['statistics']['total_redactions'],
        "llm_access": safety_report["is_safe"]
    }

    # Save audit
    audit_log_path = pdf_file.parent / ".privacy_audit_log.jsonl"
    try:
        with open(audit_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry) + '\n')
    except Exception:
        pass

    # Safety gate
    if not safety_report["is_safe"]:
        return json.dumps({
            "error": "SAFETY_VALIDATION_FAILED",
            "safety_report": safety_report,
            "audit_entry": audit_entry
        }, indent=2)

    # Step 5: Save redacted output
    redacted_md_path = pdf_file.parent / f"{pdf_file.stem}-HYBRID-REDACTED.md"
    try:
        with open(redacted_md_path, 'w', encoding='utf-8') as f:
            f.write(f"---\n")
            f.write(f"source: {pdf_file.name}\n")
            f.write(f"extraction_method: hybrid_pymupdf_mineru\n")
            f.write(f"data_pages: {len(data_pages)} of {total_pages}\n")
            f.write(f"speedup: {speedup:.1f}x\n")
            f.write(f"---\n\n")
            f.write(redaction_result["redacted_text"])
    except Exception as e:
        redacted_md_path = None

    print(f"  ✓ Redaction complete: {redaction_result['statistics']['total_redactions']} PII items removed")
    print(f"\n✅ Hybrid extraction complete!")
    print(f"   Output: {len(redaction_result['redacted_text'])} chars (~{len(redaction_result['redacted_text'])//4} tokens)")

    return json.dumps({
        "redacted_markdown": redaction_result["redacted_text"],
        "audit_log": redaction_result["audit_log"],
        "statistics": redaction_result["statistics"],
        "safety_report": safety_report,
        "audit_entry": audit_entry,
        "metadata": {
            "method": "hybrid_pymupdf_mineru",
            "total_pages": total_pages,
            "data_pages_processed": len(data_pages),
            "data_page_numbers": data_pages,
            "pages_skipped": total_pages - len(data_pages),
            "speedup_factor": f"{speedup:.1f}x",
            "estimated_time_saved": f"{(total_pages - len(data_pages)) * 25} seconds",
            "redacted_file": str(redacted_md_path) if redacted_md_path else None
        }
    }, indent=2)


# Run server when executed directly
if __name__ == "__main__":
    mcp.run()
