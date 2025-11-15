#!/usr/bin/env python3
"""Quick test for Newsletters page helper functions."""

import sys
from pathlib import Path

# Add .audit to path
audit_dir = Path(__file__).parent / ".audit"
if str(audit_dir) not in sys.path:
    sys.path.insert(0, str(audit_dir))

from inspector import WorkflowAuditInspector

# Import helper function from audit_dashboard
sys.path.insert(0, str(Path(__file__).parent))

# Test get_runs_with_newsletters
print("Testing get_runs_with_newsletters()...")
print("-" * 60)

# We need to replicate the function here since we can't import from Streamlit app
import re
from datetime import datetime

newsletters_dir = Path(__file__).parent / "newsletters"
pattern = re.compile(r'newsletter_(technical|consumer)_(\d{8}_\d{6})\.md')

# Group newsletters by timestamp
newsletter_groups = {}

for file in newsletters_dir.glob("newsletter_*.md"):
    match = pattern.match(file.name)
    if match:
        newsletter_type, timestamp = match.groups()

        if timestamp not in newsletter_groups:
            newsletter_groups[timestamp] = {
                'timestamp': timestamp,
                'technical': None,
                'consumer': None,
                'audit_run_id': None,
                'workflow_id': None,
                'article_count': None
            }

        newsletter_groups[timestamp][newsletter_type] = str(file)

# Attempt to correlate with audit runs
inspector = WorkflowAuditInspector("rss_intelligence.db")
runs = inspector.list_runs(limit=100)

for timestamp, group in newsletter_groups.items():
    # Parse newsletter timestamp
    try:
        newsletter_dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
    except ValueError:
        continue

    # Find matching run within 1 minute
    for run in runs:
        try:
            run_dt = datetime.fromisoformat(run['created_at'])
            if abs((run_dt - newsletter_dt).total_seconds()) < 60:
                group['audit_run_id'] = run['audit_run_id']
                group['workflow_id'] = run['workflow_id']

                # Try to extract article count
                try:
                    session_id = run['session_id']
                    steps = inspector.get_step_history(session_id)
                    for step in steps:
                        if step['step_name'] == 'log_rss_articles':
                            metrics = step.get('metrics', {})
                            group['article_count'] = metrics.get('article_count')
                            break
                except:
                    pass
                break
        except:
            continue

# Convert to sorted list
results = sorted(
    newsletter_groups.values(),
    key=lambda x: x['timestamp'],
    reverse=True
)

print(f"\n✅ Found {len(results)} newsletter runs")
print("\nMost recent 5 runs:")
print("-" * 60)

for i, run in enumerate(results[:5], 1):
    print(f"\n{i}. Timestamp: {run['timestamp']}")
    print(f"   Technical: {'✓' if run['technical'] else '✗'}")
    print(f"   Consumer: {'✓' if run['consumer'] else '✗'}")
    print(f"   Audit Run ID: {run['audit_run_id'] or 'N/A'}")
    print(f"   Workflow ID: {run['workflow_id'] or 'N/A'}")
    print(f"   Article Count: {run['article_count'] or 'N/A'}")

# Check today's run specifically
target_timestamp = "20251115_094854"
target_run = next((r for r in results if r['timestamp'] == target_timestamp), None)

if target_run:
    print(f"\n{'=' * 60}")
    print("TARGET RUN: 20251115_094854")
    print(f"{'=' * 60}")
    print(f"Technical: {target_run['technical']}")
    print(f"Consumer: {target_run['consumer']}")
    print(f"Audit Run ID: {target_run['audit_run_id']}")
    print(f"Workflow ID: {target_run['workflow_id']}")
    print(f"Article Count: {target_run['article_count']}")

    # Check file sizes
    if target_run['technical']:
        tech_path = Path(target_run['technical'])
        tech_size = tech_path.stat().st_size
        tech_words = len(tech_path.read_text().split())
        print(f"\nTechnical Newsletter:")
        print(f"  Size: {tech_size:,} bytes")
        print(f"  Words: {tech_words:,}")

    if target_run['consumer']:
        cons_path = Path(target_run['consumer'])
        cons_size = cons_path.stat().st_size
        cons_words = len(cons_path.read_text().split())
        print(f"\nConsumer Newsletter:")
        print(f"  Size: {cons_size:,} bytes")
        print(f"  Words: {cons_words:,}")

print("\n" + "=" * 60)
print("✅ Test completed successfully!")
print("=" * 60)
