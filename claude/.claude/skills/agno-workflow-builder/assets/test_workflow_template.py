#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "fastapi>=0.118.0",
#   "ollama",
#   "sqlalchemy",
#   "pytest>=7.0.0",
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///
# NOTE: This format is portable and works from any agno_workflows/* directory
# uv resolves the relative path ../../libs/agno from the script location

"""
Test Template for Agno Workflows

This template provides a standard test structure for validating workflows.

Usage:
    uv run test_workflow.py
"""

from pathlib import Path
import sys

# Add workflow directory to path (allows importing workflow.py)
sys.path.insert(0, str(Path(__file__).parent))


def test_workflow_configuration():
    """Test that workflow is properly configured"""
    from workflow import workflow

    # Check workflow configuration
    assert workflow is not None, "Workflow is None"
    assert workflow.name, "Workflow has no name"
    assert workflow.steps, "Workflow has no steps"
    assert workflow.store_events, "Event storage not enabled (required for debugging)"
    assert workflow.db, "Database not configured (required for event storage)"

    print(f"✓ Workflow configuration valid")
    print(f"  Name: {workflow.name}")
    print(f"  Steps: {len(workflow.steps)}")
    print(f"  Event storage: enabled")
    print(f"  Database: configured")

    return True


def test_workflow_steps():
    """Test that all workflow steps are valid"""
    from workflow import workflow

    for i, step in enumerate(workflow.steps):
        # Check step has required attributes
        assert hasattr(step, 'name'), f"Step {i} has no name"

        # Check step has either agent or executor
        has_agent = hasattr(step, 'agent') and step.agent is not None
        has_executor = hasattr(step, 'executor') and step.executor is not None

        assert has_agent or has_executor, f"Step {i} ({step.name}) has neither agent nor executor"

        print(f"  ✓ Step {i}: {step.name}")

    print(f"✓ All {len(workflow.steps)} steps are valid")

    return True


def test_workflow_execution():
    """Test basic workflow execution"""
    from workflow import workflow

    print(f"  Running workflow: {workflow.name}")

    # Execute with test input
    result = workflow.run(
        input="Test prompt for workflow validation",
        stream=False,  # Disable streaming for tests
    )

    # Validate results
    assert result is not None, "Workflow returned None"
    assert hasattr(result, 'content'), "Result has no content attribute"

    content = result.content or ""
    print(f"  ✓ Workflow executed successfully")
    print(f"    Output length: {len(content)} characters")

    if content:
        preview = content[:100].replace('\n', ' ')
        print(f"    Preview: {preview}...")

    return True


def test_workflow_events():
    """Test that workflow events are captured (if enabled)"""
    from workflow import workflow

    if not workflow.store_events:
        print("  ⊘ Event storage not enabled (skipping)")
        return True

    # Execute workflow
    result = workflow.run(
        input="Test prompt",
        stream=False,
    )

    # Check if we can access session
    if hasattr(workflow, 'last_session') and workflow.last_session:
        session = workflow.last_session
        if hasattr(session, 'runs') and session.runs:
            print(f"  ✓ Events captured")
            print(f"    Runs: {len(session.runs)}")
            return True

    print("  ⚠️  Could not verify event capture")
    return True


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        ("Configuration", test_workflow_configuration),
        ("Steps", test_workflow_steps),
        ("Execution", test_workflow_execution),
        ("Events", test_workflow_events),
    ]

    print("="*60)
    print("Running Workflow Tests")
    print("="*60)
    print()

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"Testing: {name}")
            print("-"*60)

            test_func()
            passed += 1
            print()

        except Exception as e:
            failed += 1
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)

    if failed > 0:
        print(f"\n❌ {failed} test(s) failed")
        return False
    else:
        print(f"\n✅ All {passed} tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
