#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno>=2.2.10",
#   "ollama",
#   "click",
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///

"""
Simple Click-Based Agent CLI

Professional command-line interface for Agno agents using Click.
Provides multiple operation modes with clean CLI UX.

Usage:
  Query mode:       ./agent_simple_cli.py query "What is Python?"
  Interactive chat: ./agent_simple_cli.py chat
  Batch processing: ./agent_simple_cli.py batch --file queries.txt

With custom model:
  ./agent_simple_cli.py --model gpt-oss:120b-cloud query "Hello"
"""

# Disable Agno telemetry before importing agno modules
import os
os.environ["AGNO_TELEMETRY"] = "false"

import click
from agno.agent import Agent
from agno.models.ollama import Ollama


@click.group()
@click.option('--model', default='glm-4.6:cloud',
              help='Ollama model to use (e.g., gpt-oss:120b-cloud, glm-4.6:cloud, deepseek-v3.1:671b-cloud)')
@click.option('--debug/--no-debug', default=False,
              help='Enable verbose debug output with full execution trace')
@click.pass_context
def cli(ctx, model, debug):
    """AI Assistant with query, chat, and batch processing modes

    Professional CLI interface for Agno agent with three operation modes:
    - query: Single question/answer (scriptable)
    - chat: Interactive conversation (REPL)
    - batch: Process multiple queries from file

    Global Options:
        --model: Switch between Ollama cloud models for speed/quality tradeoff
        --debug: Enable detailed logging for troubleshooting

    Examples:
        ./agent_simple_cli.py query "What is Python?"
        ./agent_simple_cli.py --model gpt-oss:120b-cloud query "Fast query"
        ./agent_simple_cli.py chat
        ./agent_simple_cli.py batch --file queries.txt --output results.txt
    """
    ctx.obj = Agent(
        model=Ollama(
            id=model,
            options={"num_ctx": 198000}  # 198K context window - full capacity
        ),
        instructions="""
            You are a helpful AI assistant.
            Provide clear, concise, and accurate responses.
            Be friendly and professional.
        """,
        markdown=True,
        debug_mode=debug,
        # debug_level=1,            # 1=basic, 2=detailed (only if debug_mode=True)
        # Automatic retry with exponential backoff (recommended)
        exponential_backoff=True,
        retries=3,
        delay_between_retries=15,  # With exponential backoff: 15s, 30s, 60s
    )


@cli.command()
@click.argument('prompt')
@click.option('--stream/--no-stream', default=True,
              help='Stream response in real-time (default: True)')
@click.pass_obj
def query(agent, prompt, stream):
    """Execute a single query and return results

    Processes one prompt and exits. Perfect for:
    - Quick questions and one-off queries
    - Shell scripting and automation
    - Testing agent responses
    - Command-line workflows and pipelines

    Arguments:
        PROMPT: The question or instruction for the agent

    Options:
        --stream/--no-stream: Toggle real-time streaming output

    Examples:
        ./agent_simple_cli.py query "What is Python?"
        ./agent_simple_cli.py query "Explain AI" --no-stream
        ./agent_simple_cli.py --model gpt-oss:120b-cloud query "Fast query"
    """
    agent.print_response(prompt, stream=stream)


@cli.command()
@click.pass_obj
def chat(agent):
    """Start interactive chat session (REPL mode)

    Launches an interactive conversation interface with the agent.
    Maintains context throughout the session for natural dialogue.

    Features:
    - Real-time streaming responses
    - Conversation history preserved during session
    - Type 'exit' or 'quit' to end
    - Markdown formatting support

    Use Cases:
    - Exploratory conversations
    - Multi-turn problem solving
    - Brainstorming sessions
    - Interactive assistance

    Examples:
        ./agent_simple_cli.py chat
        ./agent_simple_cli.py --debug chat  # With verbose output
    """
    agent.cli_app(stream=True)


@cli.command()
@click.option('--file', type=click.File('r'), required=True,
              help='Text file with queries, one per line')
@click.option('--output', type=click.File('w'),
              help='Output file for results (default: stdout)')
@click.pass_obj
def batch(agent, file, output):
    """Process multiple queries from file in batch mode

    Reads queries from a text file (one per line) and processes them
    sequentially. Results are written to stdout or a specified output file.

    Input Format:
    - Plain text file
    - One query per line
    - Empty lines are skipped
    - No special formatting needed

    Output Format:
    - Separator lines between queries
    - Query echoed before response
    - Full agent response for each query

    Use Cases:
    - Bulk processing of questions
    - Automated testing
    - Generating reports from multiple prompts
    - Data extraction workflows

    Examples:
        # Create queries file
        echo -e "What is Python?\\nExplain AI\\nDefine recursion" > queries.txt

        # Process to stdout
        ./agent_simple_cli.py batch --file queries.txt

        # Save to file
        ./agent_simple_cli.py batch --file queries.txt --output results.txt

        # Use different model
        ./agent_simple_cli.py --model gpt-oss:120b-cloud batch --file queries.txt
    """
    for line in file:
        query = line.strip()
        if query:
            click.echo(f"\n{'='*60}", file=output)
            click.echo(f"Query: {query}", file=output)
            click.echo(f"{'='*60}", file=output)
            result = agent.run(query)
            click.echo(result.content, file=output)


if __name__ == "__main__":
    cli()
