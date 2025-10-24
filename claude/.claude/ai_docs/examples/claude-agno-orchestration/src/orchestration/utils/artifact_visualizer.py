"""
Artifact Visualizer - Generate visual diagrams from orchestration artifacts.

Creates ASCII tree diagrams showing agent execution flow, inputs/outputs,
and timing information for easy understanding and debugging.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class ArtifactVisualizer:
    """
    Generate visual representations of agent execution from artifacts.

    Supports multiple visualization modes:
    - Tree view (ASCII art)
    - Compact summary
    - Detailed execution timeline
    """

    # Unicode box-drawing characters
    BRANCH = "├── "
    LAST_BRANCH = "└── "
    VERTICAL = "│   "
    SPACE = "    "

    def __init__(self, artifacts_path: Optional[Path] = None):
        """
        Initialize visualizer.

        Args:
            artifacts_path: Path to artifacts.json file (optional)
        """
        self.artifacts_path = artifacts_path
        self.artifacts_data = None

        if artifacts_path:
            self.load_artifacts(artifacts_path)

    def load_artifacts(self, path: Path) -> Dict[str, Any]:
        """Load artifacts from JSON file."""
        with open(path, 'r') as f:
            self.artifacts_data = json.load(f)
        return self.artifacts_data

    def generate_tree(
        self,
        artifacts: Optional[Dict[str, Any]] = None,
        detail_level: str = "normal",
        show_timestamps: bool = False,
        show_token_usage: bool = False
    ) -> str:
        """
        Generate ASCII tree diagram of agent execution.

        Args:
            artifacts: Artifacts data (uses loaded data if None)
            detail_level: "minimal", "normal", or "verbose"
            show_timestamps: Include execution timestamps
            show_token_usage: Include token usage info (if available)

        Returns:
            ASCII tree diagram as string
        """
        if artifacts is None:
            artifacts = self.artifacts_data

        if artifacts is None:
            raise ValueError("No artifacts data available. Load or provide artifacts.")

        lines = []

        # Header
        orchestrator = artifacts.get('orchestrator', 'Unknown')
        workflow = artifacts.get('workflow', 'Unknown')
        total_duration = artifacts.get('total_duration', 0)
        total_agents = artifacts.get('total_agents', 0)

        lines.append("=" * 80)
        lines.append(f"🎭 Orchestration Execution Diagram")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Orchestrator: {orchestrator} ({workflow} workflow)")
        lines.append(f"Total Duration: {total_duration:.2f}s")
        lines.append(f"Total Agents: {total_agents}")
        lines.append("")

        # Metadata section
        if 'metadata' in artifacts:
            metadata = artifacts['metadata']
            start_time = metadata.get('start_time', '')
            end_time = metadata.get('end_time', '')

            if show_timestamps:
                lines.append(f"Start: {self._format_timestamp(start_time)}")
                lines.append(f"End:   {self._format_timestamp(end_time)}")
                lines.append("")

        lines.append("Execution Tree:")
        lines.append("")

        # Root orchestrator node
        lines.append(f"┌─ {orchestrator}")
        lines.append(f"│")

        # Agent nodes
        agents = artifacts.get('agents', [])

        for i, agent in enumerate(agents):
            is_last = (i == len(agents) - 1)
            prefix = self.LAST_BRANCH if is_last else self.BRANCH
            continuation = self.SPACE if is_last else self.VERTICAL

            agent_lines = self._format_agent_node(
                agent,
                prefix,
                continuation,
                detail_level,
                show_token_usage
            )
            lines.extend(agent_lines)

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _format_agent_node(
        self,
        agent: Dict[str, Any],
        prefix: str,
        continuation: str,
        detail_level: str,
        show_token_usage: bool
    ) -> List[str]:
        """Format a single agent node with its details."""
        lines = []

        name = agent.get('name', 'Unknown')
        agent_type = agent.get('type', 'Unknown')
        duration = agent.get('duration', 0)
        success = agent.get('success', False)

        # Status icon
        status_icon = "✅" if success else "❌"

        # Main agent line
        lines.append(f"{prefix}{name} ({agent_type}) {status_icon}")

        if detail_level == "minimal":
            lines.append(f"{continuation}└─ Duration: {duration:.2f}s")
            lines.append(f"{continuation}")
            return lines

        # Normal or verbose details
        details = []

        # Model info
        model = agent.get('model', 'unknown')
        temperature = agent.get('temperature', 0)
        max_tokens = agent.get('max_tokens', 0)
        details.append(f"Model: {model} (temp={temperature}, max_tokens={max_tokens})")

        # Timing
        details.append(f"Duration: {duration:.2f}s")

        # Input/Output sizes
        input_length = agent.get('input_length', 0)
        output_length = agent.get('output_length', 0)
        details.append(f"Input: {input_length:,} chars")
        details.append(f"Output: {output_length:,} chars")

        # Token usage (if available)
        if show_token_usage and 'token_usage' in agent:
            token_usage = agent['token_usage']
            if token_usage:
                details.append(f"Tokens: {token_usage}")

        # Timestamp (if verbose)
        if detail_level == "verbose" and 'timestamp' in agent:
            timestamp = agent['timestamp']
            details.append(f"Timestamp: {self._format_timestamp(timestamp)}")

        # Error info (if failed)
        if not success and 'error' in agent:
            error = agent.get('error', 'Unknown error')
            details.append(f"Error: {error}")

        # Add detail lines
        for j, detail in enumerate(details):
            is_last_detail = (j == len(details) - 1)
            detail_prefix = f"{continuation}└─ " if is_last_detail else f"{continuation}├─ "
            lines.append(f"{detail_prefix}{detail}")

        lines.append(f"{continuation}")

        return lines

    def generate_compact_summary(
        self,
        artifacts: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate compact one-line summary per agent.

        Args:
            artifacts: Artifacts data (uses loaded data if None)

        Returns:
            Compact summary as string
        """
        if artifacts is None:
            artifacts = self.artifacts_data

        if artifacts is None:
            raise ValueError("No artifacts data available.")

        lines = []

        orchestrator = artifacts.get('orchestrator', 'Unknown')
        total_duration = artifacts.get('total_duration', 0)

        lines.append(f"🎭 {orchestrator} ({total_duration:.2f}s total)")
        lines.append("")

        agents = artifacts.get('agents', [])

        for i, agent in enumerate(agents, 1):
            name = agent.get('name', 'Unknown')
            model = agent.get('model', 'unknown')
            duration = agent.get('duration', 0)
            success = agent.get('success', False)
            status = "✅" if success else "❌"

            input_len = agent.get('input_length', 0)
            output_len = agent.get('output_length', 0)

            lines.append(
                f"{i}. {name} [{model}] {duration:.2f}s "
                f"({input_len:,}→{output_len:,} chars) {status}"
            )

        return "\n".join(lines)

    def generate_timeline(
        self,
        artifacts: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate execution timeline showing when each agent ran.

        Args:
            artifacts: Artifacts data (uses loaded data if None)

        Returns:
            Timeline diagram as string
        """
        if artifacts is None:
            artifacts = self.artifacts_data

        if artifacts is None:
            raise ValueError("No artifacts data available.")

        lines = []

        orchestrator = artifacts.get('orchestrator', 'Unknown')
        total_duration = artifacts.get('total_duration', 0)

        lines.append("=" * 80)
        lines.append(f"⏱️  Execution Timeline: {orchestrator}")
        lines.append("=" * 80)
        lines.append("")

        # Get start time from metadata
        metadata = artifacts.get('metadata', {})
        start_time_str = metadata.get('start_time', '')

        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
                lines.append(f"Start: {self._format_timestamp(start_time_str)}")
                lines.append("")
            except:
                start_time = None
        else:
            start_time = None

        # Timeline bars
        agents = artifacts.get('agents', [])

        # Calculate scale
        max_duration = total_duration
        bar_width = 60

        cumulative_time = 0.0

        for agent in agents:
            name = agent.get('name', 'Unknown')
            duration = agent.get('duration', 0)
            success = agent.get('success', False)
            status = "✅" if success else "❌"

            # Calculate bar length
            bar_length = int((duration / max_duration) * bar_width)
            bar_char = "█"

            # Create bar
            bar = bar_char * bar_length

            # Time range
            start = cumulative_time
            end = cumulative_time + duration

            lines.append(f"{name} {status}")
            lines.append(f"  [{start:.1f}s → {end:.1f}s] ({duration:.2f}s)")
            lines.append(f"  {bar}")
            lines.append("")

            cumulative_time += duration

        lines.append(f"Total: {total_duration:.2f}s")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format ISO timestamp to readable format."""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp_str

    def save_visualization(
        self,
        output_path: Path,
        mode: str = "tree",
        **kwargs
    ):
        """
        Generate and save visualization to file.

        Args:
            output_path: Path to save visualization
            mode: "tree", "compact", or "timeline"
            **kwargs: Additional arguments for visualization method
        """
        if mode == "tree":
            content = self.generate_tree(**kwargs)
        elif mode == "compact":
            content = self.generate_compact_summary(**kwargs)
        elif mode == "timeline":
            content = self.generate_timeline(**kwargs)
        else:
            raise ValueError(f"Unknown mode: {mode}")

        with open(output_path, 'w') as f:
            f.write(content)

        return output_path


def visualize_artifacts(
    artifacts_path: Path,
    mode: str = "tree",
    output_path: Optional[Path] = None,
    **kwargs
) -> str:
    """
    Convenience function to visualize artifacts.

    Args:
        artifacts_path: Path to artifacts.json
        mode: "tree", "compact", or "timeline"
        output_path: Optional path to save output
        **kwargs: Additional visualization options

    Returns:
        Visualization string
    """
    visualizer = ArtifactVisualizer(artifacts_path)

    if mode == "tree":
        result = visualizer.generate_tree(**kwargs)
    elif mode == "compact":
        result = visualizer.generate_compact_summary(**kwargs)
    elif mode == "timeline":
        result = visualizer.generate_timeline(**kwargs)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    if output_path:
        with open(output_path, 'w') as f:
            f.write(result)

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python artifact_visualizer.py <artifacts.json> [mode]")
        print("Modes: tree (default), compact, timeline")
        sys.exit(1)

    artifacts_path = Path(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else "tree"

    # Only pass detail_level for tree mode
    kwargs = {}
    if mode == "tree":
        kwargs['detail_level'] = "normal"

    result = visualize_artifacts(artifacts_path, mode=mode, **kwargs)
    print(result)
