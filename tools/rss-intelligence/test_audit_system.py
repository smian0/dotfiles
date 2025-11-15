#!/usr/bin/env python3
"""Test the audit system with just the first few steps."""

import asyncio
from datetime import datetime
import time

from agno.db.sqlite import SqliteDb
from agno.workflow import Workflow
from agno.workflow.step import Step

from rss_intelligence_workflow import (
    fetch_rss_feeds,
    log_rss_articles,
)


async def test_audit_system():
    """Test audit system with just fetch and log steps."""

    # Initialize audit system session state
    audit_session_state = {
        # Audit metadata (auto-initialized)
        "_audit_run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "_audit_start_time": time.time(),
        "_audit_workflow_version": "1.0.0-test",

        # Workflow state
        "processed_urls": [],
    }

    # Create minimal workflow with just first 2 steps
    test_workflow = Workflow(
        name="RSS Intelligence Test",

        # ✅ Agno Native Event Storage
        store_events=True,
        add_workflow_history_to_steps=True,

        steps=[
            Step(
                name="fetch_feeds",
                executor=fetch_rss_feeds,
                description="Fetch articles from RSS feeds with deduplication",
            ),
            Step(
                name="log_rss_articles",
                executor=log_rss_articles,
                description="Create timestamped audit log of new articles",
            ),
        ],

        db=SqliteDb(
            session_table="rss_intelligence_sessions",
            db_file="rss_intelligence.db",
        ),

        session_state=audit_session_state,
    )

    print("🧪 Testing Audit System")
    print("=" * 60)
    print(f"Run ID: {audit_session_state['_audit_run_id']}")
    print("=" * 60)

    # Run the test workflow
    result = await test_workflow.arun(input="Test audit system")

    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)

    # Get session info
    session_state = test_workflow.get_session_state()
    print(f"\nAudit Run ID: {session_state.get('_audit_run_id')}")
    print(f"Articles Found: {len(session_state.get('new_articles', []))}")

    return session_state


if __name__ == "__main__":
    session_state = asyncio.run(test_audit_system())

    # Check audit artifacts
    print("\n" + "=" * 60)
    print("Checking Audit Artifacts...")
    print("=" * 60)

    from pathlib import Path
    run_id = session_state.get('_audit_run_id')
    audit_dir = Path(f".audit/runs/{run_id}")

    if audit_dir.exists():
        print(f"\n✅ Audit directory created: {audit_dir}")
        for step_dir in audit_dir.iterdir():
            if step_dir.is_dir():
                print(f"\n  📁 {step_dir.name}/")
                for file in step_dir.iterdir():
                    print(f"    - {file.name} ({file.stat().st_size} bytes)")
    else:
        print(f"\n⚠️ Audit directory not found: {audit_dir}")

    print("\n" + "=" * 60)
    print("Test Inspector CLI")
    print("=" * 60)
    print("\nRun: python -m .audit.inspector list")
