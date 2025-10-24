"""
Transcript Parser for Claude Agent SDK

Parses .jsonl transcript files to extract:
- Agent response text (what agents actually said/generated)
- Tool calls and results
- Sub-agent execution details
- Complete conversation flow

This is necessary because SDK hooks don't capture agent outputs directly.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentMessage:
    """Represents an agent's text response."""
    text: str
    timestamp: Optional[str] = None
    role: str = "assistant"
    tool_calls: List[Dict] = None

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []


@dataclass
class ToolExecution:
    """Represents a complete tool execution."""
    tool_name: str
    tool_id: str
    tool_input: Dict[str, Any]
    tool_result: Optional[Any] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


class TranscriptParser:
    """
    Parse Claude Agent SDK transcript files to extract complete execution data.

    Complements hook-based logging by providing:
    - Agent response text (not available in hooks)
    - Sub-agent outputs (delegated via Task tool)
    - Complete conversation history
    """

    def __init__(self, transcript_path: str):
        self.transcript_path = Path(transcript_path)
        self.events = []
        self.messages = []
        self.tool_executions = []

    def parse(self) -> None:
        """Parse the transcript file and extract all events."""
        if not self.transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {self.transcript_path}")

        with open(self.transcript_path) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    event = json.loads(line)
                    self.events.append(event)

                    # Extract different event types
                    # Claude SDK format uses type='assistant' or type='user'
                    if event.get('type') in ('message', 'assistant', 'user'):
                        self._process_message(event)
                    elif event.get('type') == 'tool_use':
                        self._process_tool_use(event)
                    elif event.get('type') == 'tool_result':
                        self._process_tool_result(event)

                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue

    def _process_message(self, event: Dict) -> None:
        """Extract assistant messages (agent responses) AND tool results from user events."""
        # Handle Claude SDK transcript format where type='assistant' and message contains the actual message
        if event.get('type') == 'assistant':
            message_obj = event.get('message', {})

            # Extract role from the nested message object
            if message_obj.get('role') != 'assistant':
                return

            content_blocks = message_obj.get('content', [])
            tool_calls_in_message = []
            text_content = []

            for block in content_blocks:
                if block.get('type') == 'text':
                    text_content.append(block['text'])
                elif block.get('type') == 'tool_use':
                    tool_calls_in_message.append({
                        'id': block.get('id'),
                        'name': block.get('name'),
                        'input': block.get('input')
                    })
                    # Also create ToolExecution entry
                    tool_exec = ToolExecution(
                        tool_name=block.get('name', 'unknown'),
                        tool_id=block.get('id', ''),
                        tool_input=block.get('input', {}),
                        timestamp=event.get('timestamp')
                    )
                    self.tool_executions.append(tool_exec)

            if text_content:
                self.messages.append(AgentMessage(
                    text='\n'.join(text_content),
                    timestamp=event.get('timestamp'),
                    tool_calls=tool_calls_in_message
                ))

        # Handle user events that contain tool_result content blocks
        elif event.get('type') == 'user':
            message_obj = event.get('message', {})
            content_blocks = message_obj.get('content', [])

            if isinstance(content_blocks, list):
                for block in content_blocks:
                    if isinstance(block, dict) and block.get('type') == 'tool_result':
                        # Process tool result
                        tool_id = block.get('tool_use_id', '')
                        result_content = block.get('content', '')
                        is_error = block.get('is_error', False)

                        # Find matching tool execution and add result
                        for tool_exec in self.tool_executions:
                            if tool_exec.tool_id == tool_id:
                                tool_exec.tool_result = result_content
                                if is_error:
                                    tool_exec.error = str(result_content)
                                break

        # Also handle legacy format where event.get('role') == 'assistant'
        elif event.get('role') == 'assistant':
            content_blocks = event.get('content', [])
            tool_calls_in_message = []
            text_content = []

            for block in content_blocks:
                if block.get('type') == 'text':
                    text_content.append(block['text'])
                elif block.get('type') == 'tool_use':
                    tool_calls_in_message.append({
                        'id': block.get('id'),
                        'name': block.get('name'),
                        'input': block.get('input')
                    })
                    # Also create ToolExecution entry
                    tool_exec = ToolExecution(
                        tool_name=block.get('name', 'unknown'),
                        tool_id=block.get('id', ''),
                        tool_input=block.get('input', {}),
                        timestamp=event.get('timestamp')
                    )
                    self.tool_executions.append(tool_exec)

            if text_content:
                self.messages.append(AgentMessage(
                    text='\n'.join(text_content),
                    timestamp=event.get('timestamp'),
                    tool_calls=tool_calls_in_message
                ))

    def _process_tool_use(self, event: Dict) -> None:
        """Extract tool execution details."""
        tool_exec = ToolExecution(
            tool_name=event.get('name', 'unknown'),
            tool_id=event.get('id', ''),
            tool_input=event.get('input', {}),
            timestamp=event.get('timestamp')
        )
        self.tool_executions.append(tool_exec)

    def _process_tool_result(self, event: Dict) -> None:
        """Link tool results back to their executions."""
        tool_id = event.get('tool_use_id', '')
        result_content = event.get('content', '')

        # Find matching tool execution and add result
        for tool_exec in self.tool_executions:
            if tool_exec.tool_id == tool_id:
                tool_exec.tool_result = result_content
                if event.get('is_error'):
                    tool_exec.error = str(result_content)
                break

    def get_agent_responses(self) -> List[AgentMessage]:
        """Get all agent text responses."""
        return self.messages

    def get_tool_executions(self) -> List[ToolExecution]:
        """Get all tool executions with results."""
        return self.tool_executions

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Generate summary of workflow execution."""
        return {
            'total_messages': len(self.messages),
            'total_tool_calls': len(self.tool_executions),
            'tools_used': list(set(t.tool_name for t in self.tool_executions)),
            'has_errors': any(t.error for t in self.tool_executions),
            'agent_response_count': len([m for m in self.messages if m.text.strip()]),
            'transcript_path': str(self.transcript_path)
        }

    def export_to_enhanced_log(self, output_path: Optional[Path] = None) -> None:
        """
        Export parsed data to enhanced log format.

        Combines hook-based tool logging with transcript-based agent responses
        to provide complete visibility.
        """
        if output_path is None:
            output_path = self.transcript_path.with_suffix('.enhanced.log')

        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("Enhanced Workflow Log with Agent Responses\n")
            f.write(f"Transcript: {self.transcript_path}\n")
            f.write("=" * 80 + "\n\n")

            # Write summary
            summary = self.get_workflow_summary()
            f.write("SUMMARY:\n")
            for key, value in summary.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n" + "=" * 80 + "\n\n")

            # Interleave messages and tool executions by timestamp
            all_items = []

            for msg in self.messages:
                all_items.append(('message', msg.timestamp, msg))

            for tool in self.tool_executions:
                all_items.append(('tool', tool.timestamp, tool))

            # Sort by timestamp
            all_items.sort(key=lambda x: x[1] or '')

            # Write chronologically
            for item_type, timestamp, item in all_items:
                if item_type == 'message':
                    f.write(f"\n[{timestamp or 'N/A'}] [AGENT RESPONSE]\n")
                    f.write("-" * 80 + "\n")
                    f.write(item.text + "\n")
                    f.write("-" * 80 + "\n")

                    if item.tool_calls:
                        f.write(f"Tool calls in this message: {len(item.tool_calls)}\n")
                        for tc in item.tool_calls:
                            f.write(f"  - {tc['name']} (id: {tc['id']})\n")

                elif item_type == 'tool':
                    f.write(f"\n[{timestamp or 'N/A'}] [TOOL: {item.tool_name}]\n")
                    f.write(f"  Tool ID: {item.tool_id}\n")
                    f.write(f"  Input: {json.dumps(item.tool_input, indent=4)}\n")
                    if item.tool_result:
                        result_str = str(item.tool_result)[:500]  # Truncate long results
                        f.write(f"  Result: {result_str}...\n")
                    if item.error:
                        f.write(f"  ERROR: {item.error}\n")

        print(f"Enhanced log written to: {output_path}")


def parse_and_enhance(transcript_path: str, output_path: Optional[str] = None) -> TranscriptParser:
    """
    Convenience function to parse transcript and export enhanced log.

    Args:
        transcript_path: Path to .jsonl transcript file
        output_path: Optional output path for enhanced log

    Returns:
        TranscriptParser instance with parsed data
    """
    parser = TranscriptParser(transcript_path)
    parser.parse()
    parser.export_to_enhanced_log(Path(output_path) if output_path else None)
    return parser


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python transcript_parser.py <transcript.jsonl> [output.log]")
        sys.exit(1)

    transcript_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        parser = parse_and_enhance(transcript_file, output_file)
        summary = parser.get_workflow_summary()

        print("\nWorkflow Summary:")
        print(f"  Messages: {summary['total_messages']}")
        print(f"  Tool Calls: {summary['total_tool_calls']}")
        print(f"  Tools Used: {', '.join(summary['tools_used'])}")
        print(f"  Agent Responses: {summary['agent_response_count']}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
