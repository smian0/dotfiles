"""
Workflow helper functions for Claude Agent SDK.

Reduces boilerplate and simplifies common workflow patterns.
"""

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
)
from claude_agent_sdk.types import HookMatcher
from typing import AsyncIterator, Optional, Dict, List, Any, Callable
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import logging
import json
from datetime import datetime
import os


# ============================================================================
# Debugging and Tracing Helpers
# ============================================================================

class WorkflowLogger:
    """
    Dual-output logger that writes to both console and file.

    Automatically creates a logs/ directory and timestamped log files
    for each workflow session.
    """

    def __init__(self, workflow_name: str = "workflow", log_dir: str = "logs"):
        """
        Initialize workflow logger.

        Args:
            workflow_name: Name of the workflow (used in log filename)
            log_dir: Directory to store log files (default: "logs")
        """
        self.workflow_name = workflow_name
        self.log_dir = log_dir
        self.console = Console()

        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"{timestamp}_{workflow_name}.log")

        # Write header to log file
        with open(self.log_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"Workflow Log: {workflow_name}\n")
            f.write(f"Started: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

    def log(self, message: str, level: str = "INFO", console_style: str = ""):
        """
        Log message to both console and file.

        Args:
            message: Message to log
            level: Log level (INFO, DEBUG, WARNING, ERROR)
            console_style: Rich console style for console output
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

        # Write to console with styling
        if console_style:
            self.console.print(f"[dim]{timestamp}[/dim] {message}", style=console_style)
        else:
            level_colors = {
                "INFO": "cyan",
                "DEBUG": "blue",
                "WARNING": "yellow",
                "ERROR": "red",
                "TOOL": "magenta"
            }
            color = level_colors.get(level, "white")
            self.console.print(f"[dim]{timestamp}[/dim] [{color}]{level}[/{color}] {message}")


async def create_debug_hooks(logger: Optional[WorkflowLogger] = None, verbose: bool = True):
    """
    Create pre/post tool use hooks for debugging.

    Args:
        logger: Optional WorkflowLogger instance (creates one if None)
        verbose: If True, shows detailed input/output data

    Returns:
        dict: Hooks dict for ClaudeAgentOptions

    Example:
        logger = WorkflowLogger("my_workflow")
        hooks = await create_debug_hooks(logger, verbose=True)
        options = ClaudeAgentOptions(hooks=hooks)
    """
    if logger is None:
        logger = WorkflowLogger()

    # Track tool calls with timing
    tool_timings = {}

    async def pre_tool_hook(input_data: dict, tool_use_id: str, context: dict) -> dict:
        """Called before each tool use - captures ALL available data."""
        tool_name = context.get('tool_name', 'unknown')

        # Record start time
        tool_timings[tool_use_id] = datetime.now()

        logger.log(f"🔧 Using tool: {tool_name}", level="TOOL")
        logger.log(f"   Tool ID: {tool_use_id}", level="DEBUG")

        # Log ALL context keys available
        logger.log(f"   Context keys: {list(context.keys())}", level="DEBUG")

        # Log complete input_data structure
        if verbose:
            # Pretty print full input_data
            logger.log(f"   Complete input_data structure:", level="DEBUG")
            input_str = json.dumps(input_data, indent=2)
            logger.log(f"{input_str}", level="DEBUG")

            # Also log context details
            logger.log(f"   Complete context:", level="DEBUG")
            context_str = json.dumps(context, indent=2, default=str)
            logger.log(f"{context_str}", level="DEBUG")

        return {}

    async def post_tool_hook(output_data: dict, tool_use_id: str, context: dict) -> dict:
        """Called after each tool use - captures timing and output."""
        tool_name = context.get('tool_name', 'unknown')

        # Calculate duration
        duration = None
        if tool_use_id in tool_timings:
            duration = (datetime.now() - tool_timings[tool_use_id]).total_seconds()
            logger.log(f"✅ Completed: {tool_name} ({duration:.3f}s)", level="TOOL")
            del tool_timings[tool_use_id]
        else:
            logger.log(f"✅ Completed: {tool_name}", level="TOOL")

        if verbose:
            # Log complete output_data structure
            logger.log(f"   Complete output_data structure:", level="DEBUG")
            output_str = json.dumps(output_data, indent=2, default=str)
            # Don't truncate in log file, but show first 1000 chars
            if len(output_str) > 1000:
                logger.log(f"{output_str[:1000]}... (truncated, full data in file)", level="DEBUG")
            else:
                logger.log(f"{output_str}", level="DEBUG")

            # Log output data keys
            logger.log(f"   Output keys: {list(output_data.keys())}", level="DEBUG")

        return {}

    return {
        'PreToolUse': [HookMatcher(hooks=[pre_tool_hook])],
        'PostToolUse': [HookMatcher(hooks=[post_tool_hook])]
    }


# ============================================================================
# Message Parsing Helpers
# ============================================================================

def extract_text_from_message(message) -> str:
    """
    Extract all text content from any message type.

    Args:
        message: Any message from Claude SDK (AssistantMessage, etc.)

    Returns:
        str: Concatenated text content, empty string if none found

    Example:
        text = extract_text_from_message(msg)
        print(text)
    """
    if not isinstance(message, AssistantMessage):
        return ""

    text_parts = []
    for block in message.content:
        if isinstance(block, TextBlock):
            text_parts.append(block.text)

    return "".join(text_parts)


def extract_tool_uses(message) -> List[Dict[str, Any]]:
    """
    Extract all tool use blocks from a message.

    Args:
        message: Any message from Claude SDK

    Returns:
        List of dicts with tool_name, tool_input, and tool_id

    Example:
        tools = extract_tool_uses(msg)
        for tool in tools:
            print(f"Tool: {tool['name']}, Input: {tool['input']}")
    """
    if not isinstance(message, AssistantMessage):
        return []

    tools = []
    for block in message.content:
        if isinstance(block, ToolUseBlock):
            tools.append({
                "id": block.id,
                "name": block.name,
                "input": block.input
            })

    return tools


async def collect_full_response(message_stream: AsyncIterator) -> str:
    """
    Collect all text from a message stream into a single string.

    Args:
        message_stream: Async iterator of messages from client.receive_response()

    Returns:
        str: Full concatenated response text

    Example:
        await client.query("What is Python?")
        response = await collect_full_response(client.receive_response())
        print(response)
    """
    response_parts = []

    async for message in message_stream:
        text = extract_text_from_message(message)
        if text:
            response_parts.append(text)

    return "".join(response_parts)


# ============================================================================
# Display Helpers
# ============================================================================

def print_message(role: str, content: str, console: Optional[Console] = None):
    """
    Pretty-print a message with role-based styling.

    Args:
        role: Message role (user, assistant, system)
        content: Message content
        console: Optional Rich console instance

    Example:
        print_message("user", "Hello!")
        print_message("assistant", "Hi there!")
    """
    if console is None:
        console = Console()

    colors = {
        "user": "cyan",
        "assistant": "green",
        "system": "yellow",
        "tool": "magenta",
        "error": "red"
    }

    color = colors.get(role, "white")

    console.print(Panel(
        content,
        title=f"[bold]{role.capitalize()}[/bold]",
        border_style=color,
        padding=(0, 1)
    ))


def print_tool_use(tool_name: str, tool_input: Dict[str, Any], console: Optional[Console] = None):
    """
    Pretty-print tool usage information.

    Args:
        tool_name: Name of the tool being used
        tool_input: Tool input parameters
        console: Optional Rich console instance
    """
    if console is None:
        console = Console()

    import json
    input_str = json.dumps(tool_input, indent=2)

    console.print(Panel(
        f"[bold]{tool_name}[/bold]\n\n{input_str}",
        title="[bold magenta]Tool Use[/bold magenta]",
        border_style="magenta",
        padding=(0, 1)
    ))


# ============================================================================
# Workflow Execution Helpers
# ============================================================================

async def run_agent_task(
    client: ClaudeSDKClient,
    prompt: str,
    show_tools: bool = False,
    console: Optional[Console] = None
) -> str:
    """
    Run a single agent task and return the response.

    Args:
        client: Claude SDK client instance
        prompt: Task prompt
        show_tools: If True, display tool usage
        console: Optional Rich console for output

    Returns:
        str: Agent response text

    Example:
        async with ClaudeSDKClient(options=options) as client:
            response = await run_agent_task(client, "Analyze this data...")
            print(response)
    """
    await client.query(prompt)

    response_parts = []

    async for message in client.receive_response():
        # Extract and display text
        text = extract_text_from_message(message)
        if text:
            response_parts.append(text)

        # Optionally display tool usage
        if show_tools:
            tools = extract_tool_uses(message)
            for tool in tools:
                if console:
                    print_tool_use(tool['name'], tool['input'], console)

    return "".join(response_parts)


async def run_sequential_tasks(
    client: ClaudeSDKClient,
    tasks: List[str],
    console: Optional[Console] = None
) -> List[str]:
    """
    Run multiple tasks sequentially, each building on previous results.

    Args:
        client: Claude SDK client instance
        tasks: List of task prompts
        console: Optional Rich console

    Returns:
        List of responses for each task

    Example:
        tasks = [
            "Research Python frameworks",
            "Compare the top 3 frameworks from your research",
            "Write a recommendation report"
        ]
        results = await run_sequential_tasks(client, tasks)
    """
    results = []

    for i, task in enumerate(tasks, 1):
        if console:
            console.print(f"\n[bold cyan]Task {i}/{len(tasks)}:[/bold cyan] {task}")

        response = await run_agent_task(client, task, show_tools=False, console=console)
        results.append(response)

        if console:
            print_message("assistant", response, console)

    return results


# ============================================================================
# Subagent Helpers
# ============================================================================

def create_researcher_agent(
    tools: Optional[List[str]] = None,
    model: str = "sonnet"
) -> AgentDefinition:
    """
    Create a standard research subagent definition.

    Args:
        tools: List of allowed tools (defaults to research tools)
        model: Model to use (haiku, sonnet, opus)

    Returns:
        AgentDefinition configured for research tasks

    Example:
        agents={
            "researcher": create_researcher_agent()
        }
    """
    if tools is None:
        tools = [
            'Read', 'Write', 'Edit', 'Grep', 'Glob',
            'TodoWrite', 'WebSearch', 'WebFetch'
        ]

    return AgentDefinition(
        description="An expert researcher and documentation writer that performs deep research and generates comprehensive reports.",
        prompt="""You are an expert researcher and report writer.

Research workflow:
1. Break down the topic into key questions
2. Use WebSearch to find authoritative sources
3. Use WebFetch to read full articles
4. Synthesize findings into coherent narrative
5. Include citations and sources
6. Write report to /docs directory

Report structure:
- Executive Summary
- Key Findings
- Detailed Analysis
- Sources and Citations
- Recommendations

Use clear markdown formatting.""",
        model=model,
        tools=tools
    )


def create_analyst_agent(
    tools: Optional[List[str]] = None,
    model: str = "sonnet"
) -> AgentDefinition:
    """
    Create a standard data analyst subagent definition.

    Args:
        tools: List of allowed tools
        model: Model to use

    Returns:
        AgentDefinition configured for data analysis
    """
    if tools is None:
        tools = [
            'Read', 'Write', 'Edit', 'Grep', 'Glob', 'TodoWrite'
        ]

    return AgentDefinition(
        description="A data analyst that analyzes data files and generates insights and visualizations.",
        prompt="""You are an expert data analyst.

Analysis workflow:
1. Read and understand the data
2. Identify patterns and insights
3. Calculate key metrics
4. Generate visualizations if helpful
5. Write analysis report to /docs

Always explain your findings in clear language.""",
        model=model,
        tools=tools
    )


def create_code_reviewer_agent(
    tools: Optional[List[str]] = None,
    model: str = "sonnet"
) -> AgentDefinition:
    """
    Create a code review subagent definition.

    Args:
        tools: List of allowed tools
        model: Model to use

    Returns:
        AgentDefinition configured for code review
    """
    if tools is None:
        tools = [
            'Read', 'Grep', 'Glob', 'Write', 'TodoWrite'
        ]

    return AgentDefinition(
        description="A senior code reviewer that analyzes code quality, security, and suggests improvements.",
        prompt="""You are a senior software engineer specialized in code review.

Review process:
1. Read specified files
2. Check for:
   - Code style and best practices
   - Potential bugs and logic errors
   - Security vulnerabilities
   - Performance issues
   - Missing error handling
3. Create detailed review report in /docs with:
   - Overall assessment
   - Specific issues (with line numbers)
   - Actionable recommendations
   - Code examples for fixes

Be constructive and specific.
Rate severity: Critical, High, Medium, Low.""",
        model=model,
        tools=tools
    )


# ============================================================================
# Configuration Helpers
# ============================================================================

async def create_base_options(
    model: str = "claude-sonnet-4-20250514",
    allowed_tools: Optional[List[str]] = None,
    permission_mode: str = "acceptEdits",
    debug: bool = False,
    verbose: bool = True,
    workflow_name: str = "workflow"
) -> ClaudeAgentOptions:
    """
    Create base agent options with common settings.

    Args:
        model: Model to use
        allowed_tools: List of allowed tools
        permission_mode: Permission mode (default, acceptEdits, prompt)
        debug: If True, enables debugging hooks (logs to console + file)
        verbose: If True (and debug=True), shows detailed tool input/output
        workflow_name: Name for log files (used when debug=True)

    Returns:
        ClaudeAgentOptions with base configuration

    Example:
        # Without debugging
        options = await create_base_options(
            model="claude-sonnet-4-20250514",
            allowed_tools=['Read', 'Write', 'Task']
        )

        # With debugging
        options = await create_base_options(
            debug=True,
            verbose=True,
            workflow_name="my_research"
        )
    """
    if allowed_tools is None:
        allowed_tools = [
            'Read', 'Write', 'Edit', 'MultiEdit',
            'Grep', 'Glob', 'Task', 'TodoWrite'
        ]

    # Create debug hooks if requested
    hooks = None
    if debug:
        logger = WorkflowLogger(workflow_name)
        hooks = await create_debug_hooks(logger, verbose=verbose)
        logger.log(f"Debug mode enabled for workflow: {workflow_name}", level="INFO")
        logger.log(f"Verbose: {verbose}", level="INFO")
        logger.log(f"Log file: {logger.log_file}", level="INFO")

    return ClaudeAgentOptions(
        model=model,
        allowed_tools=allowed_tools,
        permission_mode=permission_mode,
        setting_sources=["project"],
        hooks=hooks
    )


# ============================================================================
# Interactive Helpers
# ============================================================================

def get_user_input(console: Optional[Console] = None, prompt: str = "You: ") -> str:
    """
    Get user input with optional styling.

    Args:
        console: Optional Rich console
        prompt: Input prompt text

    Returns:
        User input string
    """
    if console:
        console.print(f"\n[bold cyan]{prompt}[/bold cyan]", end="")

    try:
        user_input = input().strip()
        return user_input
    except (KeyboardInterrupt, EOFError):
        return "exit"


async def run_conversation_loop(
    client: ClaudeSDKClient,
    console: Optional[Console] = None,
    show_tools: bool = False
):
    """
    Run an interactive conversation loop.

    Args:
        client: Claude SDK client instance
        console: Optional Rich console
        show_tools: If True, display tool usage

    Example:
        options = create_base_options()
        async with ClaudeSDKClient(options=options) as client:
            await run_conversation_loop(client)
    """
    if console is None:
        console = Console()

    console.print("[bold green]Interactive mode - type 'exit' to quit[/bold green]\n")

    while True:
        user_input = get_user_input(console)

        if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
            console.print("[yellow]Goodbye![/yellow]")
            break

        if not user_input:
            continue

        await client.query(user_input)

        async for message in client.receive_response():
            text = extract_text_from_message(message)
            if text:
                print_message("assistant", text, console)

            if show_tools:
                tools = extract_tool_uses(message)
                for tool in tools:
                    print_tool_use(tool['name'], tool['input'], console)


# ============================================================================
# Visualization Helpers
# ============================================================================

def auto_visualize_workflow(
    workflow_name: str,
    log_dir: str = "logs",
    console: Optional[Console] = None
) -> None:
    """
    Automatically visualize the latest workflow execution with full debug output.

    Finds the most recent log file for the given workflow name and generates
    a complete debug visualization with all features enabled by default:
    - Tool inputs and outputs
    - Success/failure indicators
    - Agent responses from transcript
    - Timing metrics
    - Auto-exported markdown report

    Args:
        workflow_name: Name of the workflow to visualize
        log_dir: Directory containing log files (default: "logs")
        console: Optional Rich console for output

    Example:
        # After workflow completes
        auto_visualize_workflow("tech_comparison")

        # This will:
        # 1. Find logs/YYYYMMDD_HHMMSS_tech_comparison.log
        # 2. Extract transcript path from log
        # 3. Generate full debug visualization
        # 4. Auto-export to .debug.md file
    """
    from pathlib import Path
    import re

    if console is None:
        console = Console()

    # Find latest log file
    logs_path = Path(log_dir)
    if not logs_path.exists():
        console.print(f"[red]Error: Log directory not found: {log_dir}[/red]")
        return

    log_files = sorted(logs_path.glob(f"*_{workflow_name}.log"))
    if not log_files:
        console.print(f"[yellow]No log files found for workflow: {workflow_name}[/yellow]")
        return

    latest_log = log_files[-1]
    console.print(f"\n[cyan]Found log file:[/cyan] {latest_log}")

    # Extract transcript path from log
    transcript_path = None
    try:
        with open(latest_log) as f:
            content = f.read()
            # Look for transcript path in the log content
            match = re.search(r'"transcript_path":\s*"([^"]+)"', content)
            if match:
                transcript_path = match.group(1)
                if Path(transcript_path).exists():
                    console.print(f"[cyan]Found transcript:[/cyan] {transcript_path}")
                else:
                    console.print(f"[yellow]Transcript file not found: {transcript_path}[/yellow]")
                    transcript_path = None
    except Exception as e:
        console.print(f"[yellow]Could not extract transcript path: {e}[/yellow]")

    # Import and call the enhanced visualizer
    try:
        # Import here to avoid circular dependency
        import sys
        from pathlib import Path
        helpers_path = Path(__file__).parent
        sys.path.insert(0, str(helpers_path))

        from workflow_tree_visualizer_enhanced import visualize_workflow_enhanced

        console.print(f"\n[bold green]📊 Generating Full Debug Visualization[/bold green]\n")

        # Call with all debug features enabled by default
        visualize_workflow_enhanced(
            log_file=str(latest_log),
            transcript_file=transcript_path,
            show_all_inputs=True,
            show_context=True,
            show_timing=True,
            show_output=True,  # Enabled by default now!
            show_agent_responses=True,
            show_metrics=True,
            export_markdown=True  # Auto-export .debug.md
        )

    except ImportError as e:
        console.print(f"[red]Error importing visualizer: {e}[/red]")
        console.print("[yellow]Make sure workflow_tree_visualizer_enhanced.py is in the helpers/ directory[/yellow]")
    except Exception as e:
        console.print(f"[red]Error visualizing workflow: {e}[/red]")
        import traceback
        traceback.print_exc()
