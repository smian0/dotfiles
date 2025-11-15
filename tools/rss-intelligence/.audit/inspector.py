"""CLI tool for inspecting workflow audit data from Agno's SQLite database."""
import sqlite3
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse


class WorkflowAuditInspector:
    """Query Agno's SQLite database for workflow audit information."""

    def __init__(self, db_file: str = "rss_intelligence.db"):
        """Initialize inspector with database path."""
        # Resolve relative to project root (where this script's parent is located)
        project_root = Path(__file__).parent.parent
        db_path = project_root / db_file

        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.db_file = str(db_path)
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # Access columns by name

    def list_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent workflow runs."""
        cursor = self.conn.cursor()

        query = """
            SELECT
                session_id,
                workflow_id,
                created_at,
                updated_at,
                runs,
                session_data
            FROM rss_intelligence_sessions
            ORDER BY created_at DESC
            LIMIT ?
        """

        cursor.execute(query, (limit,))
        results = []

        for row in cursor.fetchall():
            # Parse runs JSON to get event count
            try:
                runs_data = json.loads(row['runs']) if row['runs'] else []
                # Agno double-encodes runs data too
                if isinstance(runs_data, str):
                    runs_data = json.loads(runs_data)
            except (json.JSONDecodeError, TypeError):
                runs_data = []

            try:
                session_data = json.loads(row['session_data']) if row['session_data'] else {}
                # Agno double-encodes session_data, parse again if still string
                if isinstance(session_data, str):
                    session_data = json.loads(session_data)
            except (json.JSONDecodeError, TypeError):
                session_data = {}

            # Get audit metadata from session_data
            # Agno stores session_state nested inside session_data
            session_state = session_data.get('session_state', {}) if isinstance(session_data, dict) else {}

            audit_run_id = session_state.get('_audit_run_id', 'N/A')
            audit_version = session_state.get('_audit_workflow_version', 'N/A')

            results.append({
                "session_id": row['session_id'],
                "workflow_id": row['workflow_id'],
                "created_at": datetime.fromtimestamp(row['created_at']).isoformat(),
                "updated_at": datetime.fromtimestamp(row['updated_at']).isoformat(),
                "audit_run_id": audit_run_id,
                "audit_version": audit_version,
                "run_count": len(runs_data) if isinstance(runs_data, list) else 0,
            })

        return results

    def inspect_run(self, session_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific run."""
        cursor = self.conn.cursor()

        # Get session data
        cursor.execute(
            """SELECT * FROM rss_intelligence_sessions WHERE session_id = ?""",
            (session_id,)
        )
        session = cursor.fetchone()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Parse JSON fields
        try:
            session_data = json.loads(session['session_data']) if session['session_data'] else {}
            # Agno double-encodes session_data, parse again if still string
            if isinstance(session_data, str):
                session_data = json.loads(session_data)
        except (json.JSONDecodeError, TypeError):
            session_data = {}

        try:
            runs_data = json.loads(session['runs']) if session['runs'] else []
            # Agno double-encodes runs data too
            if isinstance(runs_data, str):
                runs_data = json.loads(runs_data)
        except (json.JSONDecodeError, TypeError):
            runs_data = []

        workflow_data = json.loads(session['workflow_data']) if session['workflow_data'] else {}

        # Extract audit metadata from nested session_state
        session_state = session_data.get('session_state', {}) if isinstance(session_data, dict) else {}

        return {
            "session_id": session['session_id'],
            "workflow_id": session['workflow_id'],
            "created_at": datetime.fromtimestamp(session['created_at']).isoformat(),
            "updated_at": datetime.fromtimestamp(session['updated_at']).isoformat(),
            "audit_run_id": session_state.get('_audit_run_id'),
            "audit_start_time": session_state.get('_audit_start_time'),
            "audit_workflow_version": session_state.get('_audit_workflow_version'),
            "session_data": session_data,
            "workflow_data": workflow_data,
            "runs": runs_data,
            "run_count": len(runs_data) if isinstance(runs_data, list) else 0,
        }

    def get_session_state_diff(self, session_id: str) -> Dict[str, Any]:
        """Show session state changes during a run."""
        cursor = self.conn.cursor()

        cursor.execute(
            """SELECT session_data, runs FROM rss_intelligence_sessions WHERE session_id = ?""",
            (session_id,)
        )
        session = cursor.fetchone()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        try:
            session_data = json.loads(session['session_data']) if session['session_data'] else {}
            # Agno double-encodes session_data, parse again if still string
            if isinstance(session_data, str):
                session_data = json.loads(session_data)
        except (json.JSONDecodeError, TypeError):
            session_data = {}

        try:
            runs_data = json.loads(session['runs']) if session['runs'] else []
            # Agno double-encodes runs data too
            if isinstance(runs_data, str):
                runs_data = json.loads(runs_data)
        except (json.JSONDecodeError, TypeError):
            runs_data = []

        # Extract initial and final state
        initial_state = session_data.copy()
        final_state = session_data.copy()

        # If runs data contains state changes, extract them
        if runs_data:
            # Runs may contain state modifications - this depends on store_events=True
            pass

        return {
            "session_id": session_id,
            "initial_state": initial_state,
            "final_state": final_state,
            "changes": {
                k: {"before": initial_state.get(k), "after": final_state.get(k)}
                for k in set(initial_state.keys()) | set(final_state.keys())
                if initial_state.get(k) != final_state.get(k)
            }
        }

    def get_step_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get step-by-step execution history with detailed results."""
        cursor = self.conn.cursor()

        cursor.execute(
            """SELECT runs FROM rss_intelligence_sessions WHERE session_id = ?""",
            (session_id,)
        )
        session = cursor.fetchone()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        try:
            runs_data = json.loads(session['runs']) if session['runs'] else []
            # Agno double-encodes runs data too
            if isinstance(runs_data, str):
                runs_data = json.loads(runs_data)
        except (json.JSONDecodeError, TypeError):
            runs_data = []

        if not runs_data:
            return []

        # Extract detailed step information from runs data
        steps = []
        for run in runs_data:
            if isinstance(run, dict) and 'step_results' in run:
                for step_result in run.get('step_results', []):
                    steps.append({
                        "step_name": step_result.get('step_name'),
                        "executor_name": step_result.get('executor_name'),
                        "content": step_result.get('content', ''),
                        "success": step_result.get('success'),
                        "error": step_result.get('error'),
                        "metrics": step_result.get('metrics'),
                        "step_id": step_result.get('step_id'),
                    })

        return steps

    def get_step_detail(self, session_id: str, step_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific step."""
        steps = self.get_step_history(session_id)

        matching_steps = [s for s in steps if s['step_name'] == step_name]

        if not matching_steps:
            raise ValueError(f"Step '{step_name}' not found in session {session_id}")

        # Return the most recent execution of this step
        step = matching_steps[-1]

        # Try to find saved artifacts
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT session_data FROM rss_intelligence_sessions WHERE session_id = ?""",
            (session_id,)
        )
        session = cursor.fetchone()

        if session:
            try:
                session_data = json.loads(session['session_data'])
                if isinstance(session_data, str):
                    session_data = json.loads(session_data)
                session_state = session_data.get('session_state', {})
                run_id = session_state.get('_audit_run_id')

                if run_id:
                    from pathlib import Path
                    project_root = Path(__file__).parent.parent
                    artifact_dir = project_root / '.audit' / 'runs' / run_id / step_name

                    step['artifacts'] = []
                    if artifact_dir.exists():
                        for file in artifact_dir.iterdir():
                            if not file.name.endswith('.meta.json'):
                                step['artifacts'].append({
                                    "filename": file.name,
                                    "path": str(file),
                                    "size": file.stat().st_size,
                                })
            except Exception as e:
                step['artifact_error'] = str(e)

        return step

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Inspect Agno workflow audit data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List recent runs
  python .audit/inspector.py list

  # Inspect specific run
  python .audit/inspector.py inspect <session_id>

  # Show all steps in a run
  python .audit/inspector.py steps <session_id>

  # Inspect a specific step (shows output, errors, artifacts)
  python .audit/inspector.py step <session_id> fetch_feeds
  python .audit/inspector.py step <session_id> log_rss_articles

  # Show session state changes
  python .audit/inspector.py diff <session_id>
        """
    )
    parser.add_argument("--db", default="rss_intelligence.db", help="Database file path")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list command
    list_parser = subparsers.add_parser("list", help="List recent workflow runs")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of runs to show")

    # inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a specific run")
    inspect_parser.add_argument("session_id", help="Session ID to inspect")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Show session state changes")
    diff_parser.add_argument("session_id", help="Session ID to analyze")

    # steps command
    steps_parser = subparsers.add_parser("steps", help="Show step execution history")
    steps_parser.add_argument("session_id", help="Session ID to analyze")

    # step command (singular) - inspect individual step
    step_parser = subparsers.add_parser("step", help="Inspect a specific step in a run")
    step_parser.add_argument("session_id", help="Session ID to analyze")
    step_parser.add_argument("step_name", help="Step name to inspect (e.g., 'fetch_feeds', 'log_rss_articles')")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        inspector = WorkflowAuditInspector(args.db)

        if args.command == "list":
            runs = inspector.list_runs(args.limit)
            print(json.dumps(runs, indent=2, default=str))

        elif args.command == "inspect":
            run_data = inspector.inspect_run(args.session_id)
            print(json.dumps(run_data, indent=2, default=str))

        elif args.command == "diff":
            diff = inspector.get_session_state_diff(args.session_id)
            print(json.dumps(diff, indent=2, default=str))

        elif args.command == "steps":
            steps = inspector.get_step_history(args.session_id)
            print(json.dumps(steps, indent=2, default=str))

        elif args.command == "step":
            step_detail = inspector.get_step_detail(args.session_id, args.step_name)
            print(json.dumps(step_detail, indent=2, default=str))

        inspector.close()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
