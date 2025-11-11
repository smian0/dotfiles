#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
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
  Single query: ./simple_cli_agent.py query "What is Python?"
  Chat mode:    ./simple_cli_agent.py chat
"""

import click
from agno.agent import Agent
from agno.models.ollama import Ollama


@click.group()
@click.pass_context
def cli(ctx):
    """Simple AI Assistant"""
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
    )


@cli.command()
@click.argument('prompt')
@click.pass_obj
def query(agent, prompt):
    """Execute single query"""
    agent.print_response(prompt, stream=True)


@cli.command()
@click.pass_obj
def chat(agent):
    """Start interactive chat"""
    agent.cli_app(stream=True)


if __name__ == "__main__":
    cli()
