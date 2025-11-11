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
Simple Click-Based Agent CLI

Professional command-line interface for Agno agents using Click.
Provides multiple operation modes with clean CLI UX.

Usage:
  Query mode:       ./click_agent_simple.py query "What is Python?"
  Interactive chat: ./click_agent_simple.py chat
  Batch processing: ./click_agent_simple.py batch --file queries.txt

With custom model:
  ./click_agent_simple.py --model gpt-oss:120b-cloud query "Hello"
"""

import click
from agno.agent import Agent
from agno.models.ollama import Ollama


@click.group()
@click.option('--model', default='glm-4.6:cloud', help='Ollama model to use')
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.pass_context
def cli(ctx, model, debug):
    """AI Assistant with multiple operation modes"""
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
        # Automatic retry with exponential backoff (recommended)
        exponential_backoff=True,
        retries=3,
        delay_between_retries=15,  # With exponential backoff: 15s, 30s, 60s
    )


@cli.command()
@click.argument('prompt')
@click.option('--stream/--no-stream', default=True, help='Stream response')
@click.pass_obj
def query(agent, prompt, stream):
    """Execute a single query and exit"""
    agent.print_response(prompt, stream=stream)


@cli.command()
@click.pass_obj
def chat(agent):
    """Start interactive chat session"""
    agent.cli_app(stream=True)


@cli.command()
@click.option('--file', type=click.File('r'), required=True, help='File with queries (one per line)')
@click.option('--output', type=click.File('w'), help='Output file (default: stdout)')
@click.pass_obj
def batch(agent, file, output):
    """Process queries from file in batch mode"""
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
