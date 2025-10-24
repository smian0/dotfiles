"""
Enhanced Workflow Tree Visualizer for Claude Agent SDK

Displays workflow execution with MAXIMUM detail extraction from logs,
similar to Agno's workflow debugger. Shows all available input data,
context, timing, and output information.

NOW INCLUDES TRANSCRIPT PARSING to show agent responses!

Usage:
    from workflow_tree_visualizer_enhanced import visualize_workflow_enhanced

    # Maximum verbosity - shows everything including agent responses
    visualize_workflow_enhanced(
        log_file="logs/my_workflow.log",
        transcript_file="path/to/session.jsonl",  # NEW!
        show_all_inputs=True,
        show_context=True,
        show_timing=True,
        show_agent_responses=True  # NEW!
    )
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text

# Import transcript parser
try:
    from transcript_parser import TranscriptParser, AgentMessage, ToolExecution
except ImportError:
    # Fallback if running from different directory
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from transcript_parser import TranscriptParser, AgentMessage, ToolExecution


class EnhancedWorkflowTreeVisualizer:
    """
    Enhanced visualizer that extracts and displays ALL available data
    from Claude Agent SDK workflow logs.
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console(width=140)
        self.workflow_name = "Workflow"
        self.start_time = None
        self.tool_calls = []
        self.agent_messages = []  # NEW: Store agent responses from transcript
        self.transcript_parser = None  # NEW: Store transcript parser instance
        self.log_file_path = None  # Store log file path for markdown export

    def load_from_log(self, log_file: str, transcript_file: Optional[str] = None):
        """
        Parse log file and extract MAXIMUM detail.

        Args:
            log_file: Path to workflow log file
            transcript_file: Optional path to .jsonl transcript file for agent responses
        """
        log_path = Path(log_file)
        if not log_path.exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")

        # Store log file path for markdown export
        self.log_file_path = log_path

        # Load transcript if provided
        if transcript_file:
            self._load_transcript(transcript_file)

        with open(log_path, 'r') as f:
            content = f.read()

        # Extract workflow metadata
        workflow_match = re.search(r'Workflow Log: (\w+)', content)
        if workflow_match:
            self.workflow_name = workflow_match.group(1)

        start_match = re.search(r'Started: (.+)', content)
        if start_match:
            self.start_time = datetime.fromisoformat(start_match.group(1))

        # Parse with state machine for robust JSON extraction
        lines = content.split('\n')
        current_tool = None
        state = 'IDLE'  # States: IDLE, IN_INPUT, IN_OUTPUT, IN_CONTEXT
        json_buffer = []

        for i, line in enumerate(lines):
            # Detect tool start
            tool_start = re.search(r'\[(\d+:\d+:\d+\.\d+)\] \[TOOL\] 🔧 Using tool: (.+)', line)
            if tool_start:
                timestamp_str = tool_start.group(1)
                tool_name = tool_start.group(2)
                current_tool = {
                    'timestamp': timestamp_str,
                    'name': tool_name,
                    'tool_id': None,
                    'duration': None,
                    'input_data': None,
                    'output_data': None,
                    'context_data': None,
                    'context_keys': [],
                    'output_keys': [],
                }
                state = 'IDLE'
                continue

            if not current_tool:
                continue

            # Extract tool ID
            if 'Tool ID:' in line:
                tool_id_match = re.search(r'Tool ID: (.+)', line)
                if tool_id_match:
                    current_tool['tool_id'] = tool_id_match.group(1).strip()

            # Extract context keys
            if 'Context keys:' in line:
                keys_match = re.search(r'Context keys: \[(.*)\]', line)
                if keys_match:
                    current_tool['context_keys'] = [
                        k.strip().strip("'\"") for k in keys_match.group(1).split(',') if k.strip()
                    ]

            # Extract output keys
            if 'Output keys:' in line:
                keys_match = re.search(r'Output keys: \[(.*)\]', line)
                if keys_match:
                    current_tool['output_keys'] = [
                        k.strip().strip("'\"") for k in keys_match.group(1).split(',') if k.strip()
                    ]

            # State transitions
            if 'Complete input_data structure:' in line:
                state = 'IN_INPUT'
                json_buffer = []
                continue
            elif 'Complete output_data structure:' in line:
                state = 'IN_OUTPUT'
                json_buffer = []
                continue
            elif 'Complete context:' in line:
                state = 'IN_CONTEXT'
                json_buffer = []
                continue

            # Capture JSON content in current state
            if state != 'IDLE':
                # Remove log prefix
                json_line = re.sub(r'^\[\d+:\d+:\d+\.\d+\] \[DEBUG\] ', '', line)
                if json_line.strip():
                    json_buffer.append(json_line)

                # Try to parse when we have balanced braces
                if json_buffer:
                    full_text = '\n'.join(json_buffer)
                    open_count = full_text.count('{')
                    close_count = full_text.count('}')

                    if open_count > 0 and open_count == close_count:
                        # Attempt parse
                        try:
                            parsed_data = json.loads(full_text)
                            if state == 'IN_INPUT':
                                current_tool['input_data'] = parsed_data
                            elif state == 'IN_OUTPUT':
                                current_tool['output_data'] = parsed_data
                            elif state == 'IN_CONTEXT':
                                current_tool['context_data'] = parsed_data
                            state = 'IDLE'
                            json_buffer = []
                        except json.JSONDecodeError:
                            # Try extracting JSON object
                            json_match = re.search(r'(\{.*\})', full_text, re.DOTALL)
                            if json_match:
                                try:
                                    parsed_data = json.loads(json_match.group(1))
                                    if state == 'IN_INPUT':
                                        current_tool['input_data'] = parsed_data
                                    elif state == 'IN_OUTPUT':
                                        current_tool['output_data'] = parsed_data
                                    elif state == 'IN_CONTEXT':
                                        current_tool['context_data'] = parsed_data
                                    state = 'IDLE'
                                    json_buffer = []
                                except:
                                    pass

            # Detect tool completion
            if '✅ Completed:' in line:
                # Extract duration
                duration_match = re.search(r'\((\d+\.\d+)s\)', line)
                if duration_match:
                    current_tool['duration'] = float(duration_match.group(1))

                self.tool_calls.append(current_tool)
                current_tool = None
                state = 'IDLE'

    def _load_transcript(self, transcript_file: str):
        """Load and parse transcript file to extract agent responses."""
        try:
            self.transcript_parser = TranscriptParser(transcript_file)
            self.transcript_parser.parse()
            self.agent_messages = self.transcript_parser.get_agent_responses()

            self.console.print(f"[green]✓[/green] Loaded {len(self.agent_messages)} agent responses from transcript")

        except Exception as e:
            self.console.print(f"[yellow]⚠[/yellow] Could not load transcript: {e}")
            self.agent_messages = []

    def show_enhanced_tree(
        self,
        show_all_inputs: bool = True,
        show_context: bool = True,
        show_timing: bool = True,
        show_output: bool = False,
        show_agent_responses: bool = True  # NEW!
    ):
        """
        Display workflow with MAXIMUM detail.

        Args:
            show_all_inputs: Show complete input_data structure
            show_context: Show context data
            show_timing: Show execution timing
            show_output: Show output data (can be very large)
            show_agent_responses: Show agent text responses from transcript (NEW!)
        """
        self.console.print("\n" + "=" * 140)
        self.console.print(f"[bold cyan]📊 ENHANCED Workflow Execution Tree - {self.workflow_name}[/bold cyan]")
        if self.start_time:
            self.console.print(f"[dim]Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        self.console.print(f"[dim]Total tool calls: {len(self.tool_calls)}[/dim]")
        self.console.print("=" * 140 + "\n")

        # Build rich tree
        tree = Tree(
            f"[bold green]🌳 {self.workflow_name}[/bold green]",
            guide_style="cyan"
        )

        if not self.tool_calls:
            tree.add("[yellow]No tool calls recorded[/yellow]")
            self.console.print(tree)
            return

        for idx, tool in enumerate(self.tool_calls, 1):
            # Tool header
            tool_name = tool.get('name', 'Unknown')
            timestamp = tool.get('timestamp', '')
            duration = tool.get('duration')

            # Check if this is a sub-agent spawner (Task tool)
            is_subagent_spawn = 'Task' in str(tool.get('input_data', {}).get('tool_name', ''))

            # Use different icon for sub-agent spawners
            icon = "🚀" if is_subagent_spawn else "🔧"
            label = "SUB-AGENT" if is_subagent_spawn else tool_name

            header_parts = [f"[bold magenta]{idx}. {icon} {label}[/bold magenta]"]
            if timestamp:
                header_parts.append(f"[dim]@ {timestamp}[/dim]")
            if show_timing and duration is not None:
                header_parts.append(f"[yellow]⏱️  {duration:.3f}s[/yellow]")

            tool_node = tree.add(" ".join(header_parts))

            # Add sub-agent indicator
            if is_subagent_spawn and tool.get('input_data'):
                subagent_type = tool['input_data'].get('tool_input', {}).get('subagent_type', 'unknown')
                description = tool['input_data'].get('tool_input', {}).get('description', 'No description')
                tool_node.add(f"[cyan]👥 Sub-Agent Type: {subagent_type}[/cyan]")
                tool_node.add(f"[cyan]📋 Task: {description}[/cyan]")

            # Tool ID
            if tool.get('tool_id'):
                tool_node.add(f"[dim]🆔 Tool ID: {tool['tool_id']}[/dim]")

            # Context keys
            if show_context and tool.get('context_keys'):
                keys_str = ", ".join(tool['context_keys'])
                tool_node.add(f"[cyan]📋 Context Keys: {keys_str}[/cyan]")

            # COMPLETE Input Data
            if show_all_inputs and tool.get('input_data'):
                input_node = tool_node.add("[bold yellow]📥 COMPLETE INPUT DATA:[/bold yellow]")

                input_json = json.dumps(tool['input_data'], indent=2)

                # Show as formatted JSON with syntax highlighting
                syntax = Syntax(input_json, "json", theme="monokai", line_numbers=False)
                input_node.add(syntax)

                # Also show key summary
                if isinstance(tool['input_data'], dict):
                    input_keys = list(tool['input_data'].keys())
                    input_node.add(f"[dim]Keys: {', '.join(input_keys)}[/dim]")

            # Context data
            if show_context and tool.get('context_data'):
                context_node = tool_node.add("[bold cyan]🔧 CONTEXT DATA:[/bold cyan]")
                context_json = json.dumps(tool['context_data'], indent=2)
                syntax = Syntax(context_json, "json", theme="monokai", line_numbers=False)
                context_node.add(syntax)

            # Output data from transcript (tool results) with success/failure indicators
            if show_output:
                # Try to find matching tool result from transcript
                tool_result = None
                tool_error = None
                if self.transcript_parser:
                    tool_id = tool.get('tool_id')
                    if tool_id:
                        for tool_exec in self.transcript_parser.get_tool_executions():
                            if tool_exec.tool_id == tool_id:
                                tool_result = tool_exec.tool_result
                                tool_error = tool_exec.error
                                break

                # Show tool result if found with success/error indicator
                if tool_result:
                    # Add success/error indicator
                    status_icon = "❌" if tool_error else "✅"
                    status_label = "ERROR" if tool_error else "SUCCESS"
                    status_color = "red" if tool_error else "green"
                    output_node = tool_node.add(f"[bold {status_color}]{status_icon} TOOL OUTPUT ({status_label}):[/bold {status_color}]")

                    # Show preview (first 500 chars)
                    result_str = str(tool_result)
                    if len(result_str) > 500:
                        preview = result_str[:500] + "..."
                        output_node.add(Text(preview, style="green"))
                        output_node.add(f"[dim]({len(result_str)} total chars)[/dim]")
                    else:
                        output_node.add(Text(result_str, style="green"))

                # Fallback to output_data from hooks if no transcript result
                elif tool.get('output_data'):
                    output_node = tool_node.add("[bold green]📤 OUTPUT DATA:[/bold green]")

                    # Show first N keys only
                    if isinstance(tool['output_data'], dict):
                        # Show output keys
                        output_keys = list(tool['output_data'].keys())
                        output_node.add(f"[dim]Keys: {', '.join(output_keys)}[/dim]")

                        # Show output preview (first 500 chars)
                        output_json = json.dumps(tool['output_data'], indent=2)
                        if len(output_json) > 500:
                            preview = output_json[:500] + "..."
                            output_node.add(f"[dim]{preview}[/dim]")
                            output_node.add(f"[yellow]⚠️  Output truncated ({len(output_json)} total chars)[/yellow]")
                        else:
                            syntax = Syntax(output_json, "json", theme="monokai", line_numbers=False)
                            output_node.add(syntax)

        # NEW: Show agent responses from transcript
        if show_agent_responses and self.agent_messages:
            self.console.print("\n" + "=" * 140)
            self.console.print("[bold magenta]💬 Agent Responses (from transcript)[/bold magenta]")
            self.console.print("=" * 140 + "\n")

            for idx, msg in enumerate(self.agent_messages, 1):
                response_node = tree.add(f"[bold cyan]{idx}. 💬 Agent Response[/bold cyan]")

                if msg.timestamp:
                    response_node.add(f"[dim]⏰ {msg.timestamp}[/dim]")

                # Show response text with word wrap
                text_lines = msg.text.strip().split('\n')
                response_text_node = response_node.add("[bold yellow]📝 Response Text:[/bold yellow]")

                # Show first 500 chars with option to expand
                full_text = msg.text.strip()
                if len(full_text) > 500:
                    preview_text = full_text[:500] + "..."
                    response_text_node.add(Text(preview_text, style="white"))
                    response_text_node.add(f"[dim]({len(full_text)} total chars)[/dim]")
                else:
                    response_text_node.add(Text(full_text, style="white"))

                # Show associated tool calls
                if msg.tool_calls:
                    tools_node = response_node.add(f"[cyan]🔧 Tool Calls in Response: {len(msg.tool_calls)}[/cyan]")
                    for tc in msg.tool_calls:
                        tools_node.add(f"[dim]• {tc.get('name', 'unknown')} (id: {tc.get('id', 'N/A')})[/dim]")

        self.console.print(tree)
        self.console.print()

    def show_detailed_metrics(self):
        """Show detailed metrics with timing analysis."""
        if not self.tool_calls:
            return

        self.console.print("[bold cyan]📈 Detailed Metrics Analysis[/bold cyan]\n")

        # Overall stats
        table = Table(title="Tool Call Statistics", show_header=True, border_style="cyan")
        table.add_column("Tool", style="magenta", width=30)
        table.add_column("Calls", justify="right", style="cyan")
        table.add_column("Avg Time (s)", justify="right", style="yellow")
        table.add_column("Total Time (s)", justify="right", style="green")

        tool_stats = {}
        for tool in self.tool_calls:
            name = tool.get('name', 'Unknown')
            duration = tool.get('duration', 0)

            if name not in tool_stats:
                tool_stats[name] = {'count': 0, 'total_time': 0, 'times': []}

            tool_stats[name]['count'] += 1
            if duration:
                tool_stats[name]['total_time'] += duration
                tool_stats[name]['times'].append(duration)

        for tool_name, stats in sorted(tool_stats.items(), key=lambda x: x[1]['total_time'], reverse=True):
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            table.add_row(
                tool_name,
                str(stats['count']),
                f"{avg_time:.3f}" if avg_time > 0 else "N/A",
                f"{stats['total_time']:.3f}" if stats['total_time'] > 0 else "N/A"
            )

        self.console.print(table)
        self.console.print()

    def export_to_markdown(
        self,
        output_path: Optional[Path] = None,
        show_all_inputs: bool = True,
        show_context: bool = True,
        show_timing: bool = True,
        show_output: bool = False,
        show_agent_responses: bool = True
    ) -> Path:
        """
        Export workflow visualization to markdown file with ASCII tree in code block.

        Args:
            output_path: Optional output path. If None, uses log file path with .debug.md suffix
            Other args: Same as show_enhanced_tree()

        Returns:
            Path to created markdown file
        """
        # Capture console output to string
        from io import StringIO
        from rich.console import Console as RichConsole

        string_buffer = StringIO()
        export_console = RichConsole(file=string_buffer, width=140, legacy_windows=False, force_terminal=False)

        # Temporarily replace console
        original_console = self.console
        self.console = export_console

        try:
            # Generate the tree output
            self.show_enhanced_tree(
                show_all_inputs=show_all_inputs,
                show_context=show_context,
                show_timing=show_timing,
                show_output=show_output,
                show_agent_responses=show_agent_responses
            )

            # Capture the output
            tree_output = string_buffer.getvalue()

        finally:
            # Restore original console
            self.console = original_console

        # Determine output path
        if output_path is None:
            # Use log file path with .debug.md suffix
            if self.log_file_path:
                output_path = self.log_file_path.with_suffix('.debug.md')
            else:
                output_path = Path(f"{self.workflow_name}_workflow.debug.md")

        # Create markdown content
        md_content = f"""# Workflow Debug Report: {self.workflow_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Started:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else 'N/A'}
**Total Tool Calls:** {len(self.tool_calls)}
**Agent Responses:** {len(self.agent_messages)}

---

## Workflow Execution Tree

```
{tree_output}
```

---

## Summary Statistics

- **Workflow Name:** {self.workflow_name}
- **Tool Calls:** {len(self.tool_calls)}
- **Agent Messages:** {len(self.agent_messages)}
- **Duration:** {sum(t.get('duration', 0) for t in self.tool_calls):.2f}s total
"""

        # Add tool breakdown
        if self.tool_calls:
            tool_names = {}
            for tool in self.tool_calls:
                name = tool.get('input_data', {}).get('tool_name', tool.get('name', 'Unknown'))
                tool_names[name] = tool_names.get(name, 0) + 1

            md_content += "\n### Tool Usage Breakdown\n\n"
            for tool_name, count in sorted(tool_names.items(), key=lambda x: x[1], reverse=True):
                md_content += f"- **{tool_name}:** {count} calls\n"

        # Write to file
        with open(output_path, 'w') as f:
            f.write(md_content)

        return Path(output_path)


def visualize_workflow_enhanced(
    log_file: str,
    transcript_file: Optional[str] = None,  # NEW!
    show_all_inputs: bool = True,
    show_context: bool = True,
    show_timing: bool = True,
    show_output: bool = True,  # Changed to True by default for full debug output
    show_agent_responses: bool = True,  # NEW!
    show_metrics: bool = True,
    export_markdown: bool = True,  # Auto-export to .debug.md by default
    markdown_output_path: Optional[str] = None
):
    """
    Visualize workflow with MAXIMUM detail extraction including agent responses.

    Args:
        log_file: Path to workflow log file
        transcript_file: Path to .jsonl transcript file (NEW! - provides agent responses)
        show_all_inputs: Show complete input_data (recommended: True)
        show_context: Show context data (recommended: True)
        show_timing: Show execution timing (recommended: True)
        show_output: Show tool output/results (default: True for full debug visibility)
        show_agent_responses: Show agent text responses from transcript (default: True)
        show_metrics: Show detailed metrics table (default: True)
        export_markdown: Automatically export to .debug.md file (default: True)
        markdown_output_path: Optional custom path for markdown export

    Example:
        # Full debug mode (all features enabled by default)
        visualize_workflow_enhanced(
            log_file="logs/my_workflow.log",
            transcript_file="/path/to/session-id.jsonl"
        )

        # Minimal view (disable features as needed)
        visualize_workflow_enhanced(
            log_file="logs/my_workflow.log",
            show_output=False,  # Disable if outputs are too large
            export_markdown=False  # Skip markdown export
        )
    """
    console = Console()
    visualizer = EnhancedWorkflowTreeVisualizer(console=console)
    visualizer.load_from_log(log_file, transcript_file=transcript_file)
    visualizer.show_enhanced_tree(
        show_all_inputs=show_all_inputs,
        show_context=show_context,
        show_timing=show_timing,
        show_output=show_output,
        show_agent_responses=show_agent_responses
    )
    if show_metrics:
        visualizer.show_detailed_metrics()

    # Auto-export markdown
    if export_markdown:
        md_path = visualizer.export_to_markdown(
            output_path=Path(markdown_output_path) if markdown_output_path else None,
            show_all_inputs=show_all_inputs,
            show_context=show_context,
            show_timing=show_timing,
            show_output=show_output,
            show_agent_responses=show_agent_responses
        )
        console.print(f"\n[green]✓[/green] Exported markdown to: [cyan]{md_path}[/cyan]")


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Workflow Visualizer with Agent Response Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visualize with agent responses from transcript
  python workflow_tree_visualizer_enhanced.py logs/workflow.log --transcript session.jsonl

  # Show everything including outputs
  python workflow_tree_visualizer_enhanced.py logs/workflow.log --show-output

  # Minimal view
  python workflow_tree_visualizer_enhanced.py logs/workflow.log --no-inputs --no-context
        """
    )
    parser.add_argument("log_file", help="Path to workflow log file")
    parser.add_argument("--transcript", "-t", help="Path to .jsonl transcript file for agent responses")
    parser.add_argument("--no-inputs", action="store_true", help="Hide input data")
    parser.add_argument("--no-context", action="store_true", help="Hide context data")
    parser.add_argument("--no-timing", action="store_true", help="Hide timing info")
    parser.add_argument("--show-output", action="store_true", help="Show output data (large!)")
    parser.add_argument("--no-agent-responses", action="store_true", help="Hide agent responses")
    parser.add_argument("--no-metrics", action="store_true", help="Hide metrics table")
    parser.add_argument("--no-markdown", action="store_true", help="Skip markdown export (default: auto-export to .debug.md)")
    parser.add_argument("--markdown-output", "-o", help="Custom path for markdown output")

    args = parser.parse_args()

    visualize_workflow_enhanced(
        log_file=args.log_file,
        transcript_file=args.transcript,
        show_all_inputs=not args.no_inputs,
        show_context=not args.no_context,
        show_timing=not args.no_timing,
        show_output=args.show_output,
        show_agent_responses=not args.no_agent_responses,
        show_metrics=not args.no_metrics,
        export_markdown=not args.no_markdown,
        markdown_output_path=args.markdown_output
    )
