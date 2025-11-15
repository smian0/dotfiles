"""Lightweight audit artifact saver for Agno workflows."""
from pathlib import Path
import json
from typing import Any, Optional
from datetime import datetime


class AuditArtifacts:
    """Save step outputs to .audit/runs/ for inspection."""

    def __init__(self, session_state: dict, base_dir: str = ".audit/runs"):
        """
        Initialize artifact saver.

        Args:
            session_state: Workflow session state (must contain _audit_run_id)
            base_dir: Base directory for audit runs (relative to project root)
        """
        self.run_id = session_state.get("_audit_run_id")
        if not self.run_id:
            raise ValueError("session_state must contain '_audit_run_id'")

        # Get project root (where rss_intelligence_workflow.py is located)
        project_root = Path(__file__).parent.parent
        self.run_dir = project_root / base_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def save(self, step_name: str, filename: str, content: Any,
             metadata: Optional[dict] = None):
        """
        Save artifact to step directory.

        Args:
            step_name: Name of the workflow step
            filename: Artifact filename (e.g., "output.json", "analysis.md")
            content: Content to save (dict/list → JSON, str → text)
            metadata: Optional metadata (timestamps, versions, etc.)
        """
        step_dir = self.run_dir / step_name
        step_dir.mkdir(parents=True, exist_ok=True)

        filepath = step_dir / filename

        # Save content based on type
        if isinstance(content, (dict, list)):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, default=str)
        else:
            filepath.write_text(str(content), encoding='utf-8')

        # Save metadata if provided
        if metadata:
            meta_path = step_dir / f"{filename}.meta.json"
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "step_name": step_name,
                    "filename": filename,
                    **metadata
                }, f, indent=2)

    def get_run_dir(self) -> Path:
        """Get the run directory path."""
        return self.run_dir
