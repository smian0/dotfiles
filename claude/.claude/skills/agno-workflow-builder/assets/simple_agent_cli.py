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
Simple CLI Agent with Click

Minimal Agno agent CLI using Click command groups.
Provides query and interactive chat modes.

Usage:
  Single query: ./simple_agent_cli.py query "What is Python?"
  Chat mode:    ./simple_agent_cli.py chat
"""

# Disable Agno telemetry before importing agno modules
import os
os.environ["AGNO_TELEMETRY"] = "false"

import click
from agno.agent import Agent
from agno.models.ollama import Ollama


@click.group()
@click.pass_context
def cli(ctx):
    """Simple AI Assistant with query and chat modes

    A minimal Agno agent CLI with two operation modes:
    - query: Single question/answer (great for scripting)
    - chat: Interactive conversation (REPL-style)

    Examples:
        ./simple_agent_cli.py query "What is Python?"
        ./simple_agent_cli.py chat
    """
    ctx.obj = Agent(
        model=Ollama(
            id="glm-4.6:cloud",
            options={"num_ctx": 198000}  # 198K context window - full capacity
        ),
        instructions="""
            You are a helpful AI assistant.
            Provide clear, concise, and accurate responses.
            Be friendly and professional.
        """,
        markdown=True,
        exponential_backoff=True,
        retries=3,
        delay_between_retries=15,
        # debug_mode=True,          # Uncomment for development/debugging
        # debug_level=1,            # 1=basic, 2=detailed
    )


@cli.command()
@click.argument('prompt')
@click.pass_obj
def query(agent, prompt):
    """Execute a single query and exit

    Processes one prompt and returns the response. Perfect for:
    - Quick questions
    - Shell scripting/automation
    - Testing agent responses
    - Command-line workflows

    Arguments:
        PROMPT: The question or instruction for the agent

    Examples:
        ./simple_agent_cli.py query "What is Python?"
        ./simple_agent_cli.py query "Explain recursion in simple terms"
        ./simple_agent_cli.py query "Write a haiku about coding"
    """
    agent.print_response(prompt, stream=True)


@cli.command()
@click.pass_obj
def chat(agent):
    """Start interactive chat session

    Launches an interactive REPL-style chat interface.
    Type your messages and get responses in real-time.

    Features:
    - Streaming responses
    - Conversation history maintained during session
    - Type 'exit' or 'quit' to end the session

    Examples:
        ./simple_agent_cli.py chat
    """
    agent.cli_app(stream=True)


if __name__ == "__main__":
    cli()
