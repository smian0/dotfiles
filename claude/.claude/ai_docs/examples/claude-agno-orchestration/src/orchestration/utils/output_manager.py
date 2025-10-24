"""
Output Manager for Research Runs
==================================

Manages timestamped output directories for research runs with full audit trails.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ResearchOutputManager:
    """
    Manages research output directories with timestamps and structured organization.

    Directory structure:
        outputs/
            2025-10-13_14-30-45_polymarket_research/
                - report.md              # Full research report
                - artifacts.json         # Detailed execution artifacts
                - metadata.json          # Run metadata
                - query.txt              # Original query
                - summary.txt            # Quick summary

    Usage:
        manager = ResearchOutputManager(base_dir="outputs")
        output_dir = manager.create_run_directory("polymarket_research")
        manager.save_report(output_dir, report_content)
        manager.save_artifacts(output_dir, artifacts)
    """

    def __init__(self, base_dir: str = "outputs"):
        """
        Initialize output manager.

        Args:
            base_dir: Base directory for all outputs (relative to project root)
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_run_directory(self, run_name: str) -> Path:
        """
        Create a timestamped directory for a research run.

        Args:
            run_name: Name/identifier for this research run

        Returns:
            Path to created directory

        Example:
            outputs/2025-10-13_14-30-45_polymarket_research/
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dir_name = f"{timestamp}_{run_name}"
        run_dir = self.base_dir / dir_name
        run_dir.mkdir(parents=True, exist_ok=True)

        return run_dir

    def save_report(
        self,
        run_dir: Path,
        report_content: str,
        filename: str = "report.md"
    ) -> Path:
        """
        Save the full research report as markdown.

        Args:
            run_dir: Directory for this run
            report_content: Full markdown report content
            filename: Output filename (default: report.md)

        Returns:
            Path to saved file
        """
        report_path = run_dir / filename
        report_path.write_text(report_content, encoding='utf-8')
        return report_path

    def save_artifacts(
        self,
        run_dir: Path,
        artifacts_data: Dict[str, Any],
        filename: str = "artifacts.json"
    ) -> Path:
        """
        Save detailed execution artifacts as JSON.

        Args:
            run_dir: Directory for this run
            artifacts_data: Artifacts dictionary
            filename: Output filename (default: artifacts.json)

        Returns:
            Path to saved file
        """
        artifacts_path = run_dir / filename
        with open(artifacts_path, 'w', encoding='utf-8') as f:
            json.dump(artifacts_data, f, indent=2, ensure_ascii=False)
        return artifacts_path

    def save_metadata(
        self,
        run_dir: Path,
        metadata: Dict[str, Any],
        filename: str = "metadata.json"
    ) -> Path:
        """
        Save run metadata (timing, success, configuration, etc.).

        Args:
            run_dir: Directory for this run
            metadata: Metadata dictionary
            filename: Output filename (default: metadata.json)

        Returns:
            Path to saved file
        """
        metadata_path = run_dir / filename
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        return metadata_path

    def save_query(
        self,
        run_dir: Path,
        query: str,
        filename: str = "query.txt"
    ) -> Path:
        """
        Save the original query/prompt.

        Args:
            run_dir: Directory for this run
            query: Original query text
            filename: Output filename (default: query.txt)

        Returns:
            Path to saved file
        """
        query_path = run_dir / filename
        query_path.write_text(query, encoding='utf-8')
        return query_path

    def save_summary(
        self,
        run_dir: Path,
        summary: str,
        filename: str = "summary.txt"
    ) -> Path:
        """
        Save a quick summary of the run.

        Args:
            run_dir: Directory for this run
            summary: Summary text
            filename: Output filename (default: summary.txt)

        Returns:
            Path to saved file
        """
        summary_path = run_dir / filename
        summary_path.write_text(summary, encoding='utf-8')
        return summary_path

    def save_full_run(
        self,
        run_name: str,
        query: str,
        report_content: str,
        artifacts_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        summary: Optional[str] = None
    ) -> Path:
        """
        Save complete research run with all outputs.

        Args:
            run_name: Name for this research run
            query: Original query
            report_content: Full research report
            artifacts_data: Optional execution artifacts
            metadata: Optional run metadata
            summary: Optional quick summary

        Returns:
            Path to run directory
        """
        # Create directory
        run_dir = self.create_run_directory(run_name)

        # Save all components
        self.save_query(run_dir, query)
        self.save_report(run_dir, report_content)

        if artifacts_data:
            self.save_artifacts(run_dir, artifacts_data)

        if metadata:
            self.save_metadata(run_dir, metadata)

        if summary:
            self.save_summary(run_dir, summary)

        # Create index file
        self._create_index(run_dir, run_name, query, metadata)

        return run_dir

    def _create_index(
        self,
        run_dir: Path,
        run_name: str,
        query: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Create an index/README file for the run directory.

        Args:
            run_dir: Directory for this run
            run_name: Name of the run
            query: Original query
            metadata: Optional metadata

        Returns:
            Path to index file
        """
        index_content = f"""# Research Run: {run_name}

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Query
```
{query[:500]}{'...' if len(query) > 500 else ''}
```

## Files in This Directory

- `report.md` - Full institutional-grade research report
- `artifacts.json` - Detailed execution artifacts (agents, models, timings)
- `metadata.json` - Run metadata and configuration
- `query.txt` - Complete original query
- `summary.txt` - Quick summary of findings

"""

        if metadata:
            index_content += f"""## Run Statistics

- Duration: {metadata.get('duration', 'N/A')}s
- Agents Used: {metadata.get('agents_used', 'N/A')}
- Success: {'✅' if metadata.get('success') else '❌'}
- Workflow: {metadata.get('workflow_type', 'N/A')}

"""

        index_content += """## Usage

### View Report
```bash
cat report.md
```

### View Artifacts
```bash
cat artifacts.json | jq .
```

### Compare with Other Runs
```bash
# Compare reports
diff report.md ../other_run_directory/report.md

# Compare metadata
diff metadata.json ../other_run_directory/metadata.json
```

---
Generated by Claude + Agno Orchestration System
"""

        index_path = run_dir / "README.md"
        index_path.write_text(index_content, encoding='utf-8')
        return index_path

    def list_runs(self, pattern: str = "*") -> list[Path]:
        """
        List all research run directories.

        Args:
            pattern: Glob pattern for filtering (default: all runs)

        Returns:
            List of run directory paths, sorted by date (newest first)
        """
        runs = sorted(
            self.base_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return [r for r in runs if r.is_dir()]

    def get_latest_run(self, pattern: str = "*") -> Optional[Path]:
        """
        Get the most recent research run directory.

        Args:
            pattern: Glob pattern for filtering

        Returns:
            Path to latest run directory, or None if no runs exist
        """
        runs = self.list_runs(pattern)
        return runs[0] if runs else None

    def load_report(self, run_dir: Path) -> str:
        """Load report from run directory."""
        return (run_dir / "report.md").read_text(encoding='utf-8')

    def load_artifacts(self, run_dir: Path) -> Dict[str, Any]:
        """Load artifacts from run directory."""
        with open(run_dir / "artifacts.json", 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_metadata(self, run_dir: Path) -> Dict[str, Any]:
        """Load metadata from run directory."""
        with open(run_dir / "metadata.json", 'r', encoding='utf-8') as f:
            return json.load(f)


def generate_summary(result, duration: float) -> str:
    """
    Generate a quick summary from orchestration result.

    Args:
        result: OrchestrationResult
        duration: Total duration in seconds

    Returns:
        Summary text
    """
    summary_lines = [
        f"Research Run Summary",
        f"=" * 80,
        f"",
        f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}",
        f"Duration: {duration:.2f}s",
        f"",
    ]

    if result.artifacts:
        summary_lines.extend([
            f"Agents Used: {result.artifacts.total_agents_used}",
            f"Workflow: {result.artifacts.workflow_type}",
            f"",
            f"Agent Sequence:",
        ])

        for i, artifact in enumerate(result.artifacts.agent_artifacts, 1):
            summary_lines.append(
                f"  {i}. {artifact.agent_name} "
                f"({artifact.model_id}, {artifact.execution_time:.2f}s)"
            )

    summary_lines.extend([
        f"",
        f"Report Preview:",
        f"-" * 80,
        result.final_answer[:300] + "..." if len(result.final_answer) > 300 else result.final_answer,
    ])

    return "\n".join(summary_lines)
