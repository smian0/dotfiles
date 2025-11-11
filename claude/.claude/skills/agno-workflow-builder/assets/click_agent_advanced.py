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
Advanced Multi-Agent CLI with Click Command Groups

Demonstrates complex CLI organization with:
- Multiple specialized agents
- Command groups and subgroups
- Configuration management
- Context passing between commands

Usage:
  Research commands:
    ./click_agent_advanced.py research query "AI trends"
    ./click_agent_advanced.py research deep "Python best practices"

  Code commands:
    ./click_agent_advanced.py code analyze "./script.py"
    ./click_agent_advanced.py code review "./app/"

  Orchestration:
    ./click_agent_advanced.py orchestrate "Research AI and analyze my Python code"

  Configuration:
    ./click_agent_advanced.py --model gpt-oss:120b-cloud research query "Fast research"
    ./click_agent_advanced.py --debug code analyze "test.py"
"""

import click
from agno.agent import Agent
from agno.models.ollama import Ollama


# Shared agent configuration
def create_agent(model_id, instructions, debug=False):
    """Factory function to create configured agents"""
    return Agent(
        model=Ollama(
            id=model_id,
            options={"num_ctx": 198000}
        ),
        instructions=instructions,
        markdown=True,
        debug_mode=debug,
        exponential_backoff=True,
        retries=3,
        delay_between_retries=15,
    )


@click.group()
@click.option('--model', default='glm-4.6:cloud', help='Default model for all agents')
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.pass_context
def cli(ctx, model, debug):
    """Multi-Agent AI Assistant System

    Provides specialized agents for research, code analysis, and orchestration.
    Use command groups to access different capabilities.
    """
    # Store configuration in context for all commands
    ctx.ensure_object(dict)
    ctx.obj['model'] = model
    ctx.obj['debug'] = debug


# ============================================================================
# Research Commands
# ============================================================================

@cli.group()
def research():
    """Research and information gathering commands"""
    pass


@research.command()
@click.argument('query')
@click.option('--sources', default=3, help='Number of sources to consider')
@click.pass_context
def query(ctx, query, sources):
    """Execute quick research query"""
    agent = create_agent(
        model_id=ctx.obj['model'],
        instructions=f"""
            You are a research assistant.
            Provide well-researched, factual responses based on {sources} sources.
            Cite your reasoning clearly.
        """,
        debug=ctx.obj['debug']
    )
    agent.print_response(query, stream=True)


@research.command()
@click.argument('topic')
@click.option('--depth', type=click.Choice(['shallow', 'medium', 'deep']), default='medium')
@click.pass_context
def deep(ctx, topic, depth):
    """Perform deep research with analysis"""
    agent = create_agent(
        model_id=ctx.obj['model'],
        instructions=f"""
            You are an expert researcher performing {depth} analysis.
            Provide comprehensive, well-structured research with:
            - Multiple perspectives
            - Supporting evidence
            - Critical analysis
            - Actionable conclusions
        """,
        debug=ctx.obj['debug']
    )
    prompt = f"Conduct {depth} research on: {topic}"
    agent.print_response(prompt, stream=True)


# ============================================================================
# Code Commands
# ============================================================================

@cli.group()
def code():
    """Code analysis and review commands"""
    pass


@code.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--focus', help='Specific aspect to analyze (e.g., performance, security)')
@click.pass_context
def analyze(ctx, file_path, focus):
    """Analyze code file for quality and issues"""
    agent = create_agent(
        model_id=ctx.obj['model'],
        instructions="""
            You are a code analysis expert.
            Review code for:
            - Code quality and best practices
            - Potential bugs and issues
            - Performance considerations
            - Security vulnerabilities
        """,
        debug=ctx.obj['debug']
    )

    with open(file_path, 'r') as f:
        code_content = f.read()

    focus_text = f" Focus on {focus}." if focus else ""
    prompt = f"Analyze this code:{focus_text}\n\n```\n{code_content}\n```"
    agent.print_response(prompt, stream=True)


@code.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--strict/--lenient', default=False, help='Review strictness level')
@click.pass_context
def review(ctx, path, strict):
    """Comprehensive code review"""
    agent = create_agent(
        model_id=ctx.obj['model'],
        instructions=f"""
            You are a senior code reviewer.
            Provide {'strict' if strict else 'balanced'} code review covering:
            - Architecture and design patterns
            - Code organization and structure
            - Testing coverage
            - Documentation quality
            - Maintainability concerns
        """,
        debug=ctx.obj['debug']
    )

    # For directory, would need to walk files - simplified here
    import os
    if os.path.isfile(path):
        with open(path, 'r') as f:
            code_content = f.read()
        prompt = f"Review this code:\n\n```\n{code_content}\n```"
    else:
        prompt = f"Provide code review guidance for project at: {path}"

    agent.print_response(prompt, stream=True)


# ============================================================================
# Orchestration Commands
# ============================================================================

@cli.command()
@click.argument('task')
@click.option('--agents', multiple=True, help='Specific agents to use (research, code)')
@click.pass_context
def orchestrate(ctx, task, agents):
    """Orchestrate multiple agents for complex tasks

    Coordinates between research and code agents to handle
    multi-faceted requests that require multiple capabilities.
    """
    orchestrator = create_agent(
        model_id=ctx.obj['model'],
        instructions="""
            You are an orchestration agent that coordinates multiple specialists.
            You have access to:
            - Research agent: for information gathering and analysis
            - Code agent: for code analysis and review

            Break down complex tasks and coordinate specialist agents.
            Provide comprehensive, well-organized responses.
        """,
        debug=ctx.obj['debug']
    )

    context_text = f"Available agents: {', '.join(agents)}" if agents else "All agents available"
    prompt = f"{context_text}\n\nTask: {task}"
    orchestrator.print_response(prompt, stream=True)


# ============================================================================
# Utility Commands
# ============================================================================

@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration"""
    click.echo(f"Model: {ctx.obj['model']}")
    click.echo(f"Debug: {ctx.obj['debug']}")


if __name__ == "__main__":
    cli()
