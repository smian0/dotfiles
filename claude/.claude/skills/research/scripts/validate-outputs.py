#!/usr/bin/env python3
"""
Validate research outputs for completeness and quality.
"""

import sys
from pathlib import Path
from datetime import datetime

def validate_outputs(date: str = None):
    """Validate research workspace outputs."""

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    workspace = Path("./research-output")

    if not workspace.exists():
        print("❌ Research workspace not found: ./research-output/")
        return False

    issues = []
    checks = []

    # Check coordinator status
    coordinator = workspace / "progress" / "coordinator-status.md"
    if coordinator.exists():
        checks.append("✅ Coordinator status exists")
    else:
        issues.append("❌ Coordinator status missing")

    # Check discovery streams
    sources_dir = workspace / "sources"
    stream_files = list(sources_dir.glob(f"stream-*-sources-{date}.md"))
    if len(stream_files) >= 2:
        checks.append(f"✅ Discovery streams: {len(stream_files)} found")
    elif len(stream_files) > 0:
        issues.append(f"⚠️  Discovery streams: Only {len(stream_files)} found (minimum 2 required)")
    else:
        issues.append("❌ Discovery streams: None found")

    # Check validated sources
    validated = sources_dir / f"validated-sources-{date}.md"
    if validated.exists():
        checks.append("✅ Validated sources exists")
    else:
        issues.append("ℹ️  Validated sources not yet created (Phase 2)")

    # Check analysis
    analysis_dir = workspace / "analysis"
    analysis = analysis_dir / f"comprehensive-analysis-{date}.md"
    if analysis.exists():
        checks.append("✅ Comprehensive analysis exists")
    else:
        issues.append("ℹ️  Comprehensive analysis not yet created (Phase 3)")

    # Check reports
    report_dir = workspace / "report"
    exec_summary = report_dir / f"executive-summary-{date}.md"
    full_report = report_dir / f"full-report-{date}.md"

    if exec_summary.exists():
        checks.append("✅ Executive summary exists")
    else:
        issues.append("ℹ️  Executive summary not yet created (Phase 4)")

    if full_report.exists():
        checks.append("✅ Full report exists")
    else:
        issues.append("ℹ️  Full report not yet created (Phase 4)")

    # Print results
    print(f"\nResearch Output Validation (Date: {date})")
    print("=" * 60)
    print("\n" + "\n".join(checks))
    if issues:
        print("\n" + "\n".join(issues))

    all_complete = (
        coordinator.exists() and
        len(stream_files) >= 2 and
        validated.exists() and
        analysis.exists() and
        exec_summary.exists() and
        full_report.exists()
    )

    print("\n" + "=" * 60)
    if all_complete:
        print("✅ All phases complete!")
        return True
    else:
        print("ℹ️  Research in progress")
        return False

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    success = validate_outputs(date_arg)
    sys.exit(0 if success else 1)
