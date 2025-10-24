#!/usr/bin/env python3
"""
Trace Viewer for Claude Agent SDK JSONL Transcripts

Reads and displays Claude Code JSONL transcript files in a human-readable format.
Shows conversation flow, tool usage, and timing information.

Usage:
    python trace_viewer.py <transcript_file.jsonl>
    python trace_viewer.py <transcript_file.jsonl> --tools-only
    python trace_viewer.py <transcript_file.jsonl> --verbose
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax


class TranscriptViewer:
    """
    Viewer for Claude Agent SDK JSONL transcript files.

    Parses and displays conversation flow, tool usage, and timing.
    """

    def __init__(self, transcript_path: str):
        """
        Initialize transcript viewer.

        Args:
            transcript_path: Path to JSONL transcript file
        """
        self.transcript_path = Path(transcript_path)
        self.console = Console()
        self.entries = []

        if not self.transcript_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")

        self._load_transcript()

    def _load_transcript(self):
        """Load and parse JSONL transcript file."""
        with open(self.transcript_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    self.entries.append(entry)
                except json.JSONDecodeError as e:
                    self.console.print(f"[yellow]Warning: Skipped malformed line: {e}[/yellow]")

    def get_tool_calls(self) -> List[Dict[str, Any]]:
        """
        Extract all tool calls from transcript.

        Returns:
            List of tool call info dicts
        """
        tool_calls = []

        for entry in self.entries:
            if entry.get('type') != 'assistant':
                continue

            message = entry.get('message', {})
            content = message.get('content', [])
            timestamp = entry.get('timestamp', '')

            for item in content:
                if isinstance(item, dict) and item.get('type') == 'tool_use':
                    tool_calls.append({
                        'timestamp': timestamp,
                        'tool_name': item.get('name'),
                        'tool_input': item.get('input'),
                        'tool_id': item.get('id')
                    })

        return tool_calls

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Extract all messages from transcript.

        Returns:
            List of message info dicts
        """
        messages = []

        for entry in self.entries:
            entry_type = entry.get('type')
            timestamp = entry.get('timestamp', '')
            message = entry.get('message', {})

            if entry_type in ['user', 'assistant']:
                content_blocks = message.get('content', [])
                text_parts = []

                for block in content_blocks:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text_parts.append(block.get('text', ''))

                if text_parts:
                    messages.append({
                        'timestamp': timestamp,
                        'role': entry_type,
                        'text': ''.join(text_parts)
                    })

        return messages

    def display_summary(self):
        """Display high-level summary of transcript."""
        tool_calls = self.get_tool_calls()
        messages = self.get_messages()

        # Count by role
        user_messages = sum(1 for m in messages if m['role'] == 'user')
        assistant_messages = sum(1 for m in messages if m['role'] == 'assistant')

        # Count tools by name
        tool_counts = {}
        for call in tool_calls:
            name = call['tool_name']
            tool_counts[name] = tool_counts.get(name, 0) + 1

        # Create summary panel
        summary = f"""[bold]Transcript Summary[/bold]

File: {self.transcript_path.name}
Total Entries: {len(self.entries)}

Messages:
  User: {user_messages}
  Assistant: {assistant_messages}

Tool Calls: {len(tool_calls)}"""

        if tool_counts:
            summary += "\n\nTool Usage:"
            for tool_name, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
                summary += f"\n  {tool_name}: {count}"

        self.console.print(Panel(summary, border_style="cyan"))

    def display_tools_only(self, verbose: bool = False):
        """
        Display only tool calls from transcript.

        Args:
            verbose: If True, show full tool input/output
        """
        tool_calls = self.get_tool_calls()

        self.console.print(f"\n[bold cyan]Tool Calls ({len(tool_calls)})[/bold cyan]\n")

        for i, call in enumerate(tool_calls, 1):
            timestamp = call['timestamp']
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M:%S')
                except:
                    time_str = timestamp[:8]
            else:
                time_str = "??:??:??"

            self.console.print(f"[bold]{i}. [{time_str}] {call['tool_name']}[/bold]")

            if verbose:
                input_str = json.dumps(call['tool_input'], indent=2)
                self.console.print(Panel(
                    Syntax(input_str, "json", theme="monokai"),
                    title=f"Input (ID: {call['tool_id']})",
                    border_style="magenta"
                ))
            else:
                self.console.print(f"  ID: {call['tool_id']}")
                self.console.print(f"  Input: {list(call['tool_input'].keys())}")

            self.console.print()

    def display_conversation(self, max_length: int = 200):
        """
        Display conversation flow with messages and tool calls.

        Args:
            max_length: Maximum characters to display per message
        """
        messages = self.get_messages()

        self.console.print(f"\n[bold cyan]Conversation Flow[/bold cyan]\n")

        for msg in messages:
            timestamp = msg['timestamp']
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M:%S')
                except:
                    time_str = timestamp[:8]
            else:
                time_str = "??:??:??"

            role = msg['role']
            text = msg['text']

            # Truncate long messages
            if len(text) > max_length:
                text = text[:max_length] + "..."

            # Color by role
            role_colors = {
                'user': 'cyan',
                'assistant': 'green'
            }
            color = role_colors.get(role, 'white')

            self.console.print(f"[bold {color}][{time_str}] {role.upper()}:[/bold {color}]")
            self.console.print(f"  {text}\n")

    def display_full_trace(self):
        """Display complete trace with all details."""
        self.display_summary()
        self.display_conversation()
        self.display_tools_only(verbose=False)

    def export_summary(self, output_path: str):
        """
        Export summary to markdown file.

        Args:
            output_path: Path to output markdown file
        """
        tool_calls = self.get_tool_calls()
        messages = self.get_messages()

        # Count by role
        user_messages = sum(1 for m in messages if m['role'] == 'user')
        assistant_messages = sum(1 for m in messages if m['role'] == 'assistant')

        # Count tools
        tool_counts = {}
        for call in tool_calls:
            name = call['tool_name']
            tool_counts[name] = tool_counts.get(name, 0) + 1

        # Generate markdown
        md = f"""# Transcript Analysis

**File:** `{self.transcript_path.name}`
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Entries:** {len(self.entries)}
- **User Messages:** {user_messages}
- **Assistant Messages:** {assistant_messages}
- **Tool Calls:** {len(tool_calls)}

## Tool Usage

"""

        if tool_counts:
            md += "| Tool | Count |\n"
            md += "|------|-------|\n"
            for tool_name, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
                md += f"| `{tool_name}` | {count} |\n"
        else:
            md += "No tools used.\n"

        md += "\n## Tool Call Details\n\n"

        for i, call in enumerate(tool_calls, 1):
            md += f"### {i}. {call['tool_name']}\n\n"
            md += f"- **Time:** {call['timestamp']}\n"
            md += f"- **ID:** `{call['tool_id']}`\n"
            md += f"- **Input:**\n\n```json\n{json.dumps(call['tool_input'], indent=2)}\n```\n\n"

        # Write to file
        with open(output_path, 'w') as f:
            f.write(md)

        self.console.print(f"[green]✓ Exported summary to: {output_path}[/green]")


def main():
    """CLI entry point for trace viewer."""
    import argparse

    parser = argparse.ArgumentParser(description="View Claude Agent SDK JSONL transcripts")
    parser.add_argument("transcript", help="Path to JSONL transcript file")
    parser.add_argument("--tools-only", action="store_true", help="Show only tool calls")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    parser.add_argument("--export", "-e", help="Export summary to markdown file")
    parser.add_argument("--conversation", "-c", action="store_true", help="Show conversation flow")

    args = parser.parse_args()

    try:
        viewer = TranscriptViewer(args.transcript)

        if args.export:
            viewer.export_summary(args.export)
        elif args.tools_only:
            viewer.display_summary()
            viewer.display_tools_only(verbose=args.verbose)
        elif args.conversation:
            viewer.display_summary()
            viewer.display_conversation()
        else:
            viewer.display_full_trace()

    except FileNotFoundError as e:
        Console().print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        Console().print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
