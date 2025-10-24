#!/usr/bin/env python3
"""
Standalone K-1 processor - bypasses MCP timeout for large documents
Processes K-1 forms directly and saves redacted markdown
"""

import sys
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extraction_engine import ExtractionEngine
from redaction_engine import RedactionEngine


def process_k1(pdf_path: str, privacy_level: str = "balanced"):
    """Process K-1 form with extraction and redaction"""

    print(f"Processing: {Path(pdf_path).name}")
    print("=" * 80)

    # Step 1: Extract PDF to markdown with batch processing
    print("\n[1/3] Extracting PDF with MinerU (batch processing enabled)...")
    extractor = ExtractionEngine()
    extraction_result = extractor.extract_pdf(
        pdf_path=pdf_path,
        use_smart_filtering=True  # Enable batch processing for large docs
    )

    if "error" in extraction_result:
        print(f"❌ Extraction failed: {extraction_result['error']}")
        return extraction_result

    markdown = extraction_result['markdown']
    print(f"✅ Extracted {len(markdown)} characters of markdown")

    # Step 2: Redact PII
    print("\n[2/3] Redacting PII...")
    redactor = RedactionEngine(privacy_level=privacy_level)
    redaction_result = redactor.redact(markdown)  # Fixed: use redact() not redact_content()

    if "error" in redaction_result:
        print(f"❌ Redaction failed: {redaction_result['error']}")
        return redaction_result

    redacted_markdown = redaction_result['redacted_text']  # Fixed: use redacted_text
    stats = redaction_result['statistics']
    print(f"✅ Redacted {stats['total_redactions']} PII instances")

    # Step 3: Validate safety
    print("\n[3/3] Validating redaction safety...")
    safety_report = redactor.validate_safety(
        text=redacted_markdown,  # Fixed: use text parameter
        original=markdown
    )

    if not safety_report['is_safe']:
        print(f"⚠️  SAFETY ALERT: {safety_report['risk_level']} risk")
        print(f"Issues: {len(safety_report['issues'])}")
        for issue in safety_report['issues'][:3]:
            print(f"  - {issue.get('pii_type', issue.get('issue', 'Unknown'))}: {issue.get('count', 'N/A')}")
        return {"error": "Redaction safety validation failed", "safety_report": safety_report}

    print(f"✅ Safety validated: {safety_report['risk_level']} risk")

    # Save redacted output
    output_path = Path(pdf_path).parent / f"{Path(pdf_path).stem}_redacted.md"
    output_path.write_text(redacted_markdown, encoding='utf-8')
    print(f"\n📄 Saved redacted markdown: {output_path}")

    # Save audit log
    audit_path = Path(pdf_path).parent / f"{Path(pdf_path).stem}_audit.json"
    audit_data = {
        "file": str(pdf_path),
        "privacy_level": privacy_level,
        "extraction": extraction_result.get('metadata', {}),
        "redaction_stats": stats,
        "safety_report": safety_report
    }
    audit_path.write_text(json.dumps(audit_data, indent=2), encoding='utf-8')
    print(f"📋 Saved audit log: {audit_path}")

    print("\n" + "=" * 80)
    print("✅ Processing complete!")

    return {
        "success": True,
        "output_file": str(output_path),
        "audit_file": str(audit_path),
        "statistics": stats,
        "safety_report": safety_report,
        "redacted_markdown": redacted_markdown  # Include for immediate use
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_k1_standalone.py <pdf_path> [privacy_level]")
        print("Example: python process_k1_standalone.py '/path/to/k1.pdf' balanced")
        sys.exit(1)

    pdf_path = sys.argv[1]
    privacy_level = sys.argv[2] if len(sys.argv) > 2 else "balanced"

    result = process_k1(pdf_path, privacy_level)

    if "error" in result:
        print(f"\n❌ FAILED: {result['error']}")
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS: {result['output_file']}")
        sys.exit(0)
