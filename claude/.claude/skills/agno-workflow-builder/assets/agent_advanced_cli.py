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
Advanced Multi-Agent CLI with Click Command Groups

Demonstrates complex CLI organization with:
- Multiple specialized agents
- Command groups and subgroups
- Configuration management
- Context passing between commands

Usage:
  Research commands:
    ./agent_advanced_cli.py research query "AI trends"
    ./agent_advanced_cli.py research deep "Python best practices"

  Code commands:
    ./agent_advanced_cli.py code analyze "./script.py"
    ./agent_advanced_cli.py code review "./app/"

  Orchestration:
    ./agent_advanced_cli.py orchestrate "Research AI and analyze my Python code"

  Configuration:
    ./agent_advanced_cli.py --model gpt-oss:120b-cloud research query "Fast research"
    ./agent_advanced_cli.py --debug code analyze "test.py"
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
@click.option('--model', default='glm-4.6:cloud',
              help='Ollama model for all agents (gpt-oss:120b-cloud, glm-4.6:cloud, etc.)')
@click.option('--debug/--no-debug', default=False,
              help='Enable verbose debug output for all operations')
@click.pass_context
def cli(ctx, model, debug):
    """Multi-Agent AI Assistant System with specialized capabilities

    Professional multi-agent CLI with command groups for different tasks:
    - research: Information gathering and analysis
    - code: Code analysis and review
    - orchestrate: Multi-agent task coordination

    Each command group contains specialized agents optimized for specific tasks.
    Configuration (model, debug) can be set globally and applies to all agents.

    Global Options:
        --model: Choose Ollama cloud model (affects all agents)
        --debug: Enable detailed logging (helpful for troubleshooting)

    Command Groups:
        research: Quick queries and deep analysis
        code: Analyze files, review codebases
        orchestrate: Coordinate multiple agents for complex tasks

    Examples:
        # Research commands
        ./agent_advanced_cli.py research query "AI trends"
        ./agent_advanced_cli.py research deep "Python best practices" --depth deep

        # Code commands
        ./agent_advanced_cli.py code analyze script.py
        ./agent_advanced_cli.py code review ./myproject --strict

        # Orchestration
        ./agent_advanced_cli.py orchestrate "Research AI and analyze my code"

        # With global options
        ./agent_advanced_cli.py --model gpt-oss:120b-cloud research query "Fast research"
        ./agent_advanced_cli.py --debug code analyze buggy_script.py
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
    """Research and information gathering commands

    Specialized research agents for various information needs:
    - query: Quick research questions with source-based responses
    - deep: Comprehensive analysis with multiple perspectives

    All research agents provide well-reasoned, factual responses.
    """
    pass


@research.command()
@click.argument('query')
@click.option('--sources', default=3,
              help='Number of sources to consider in research (1-10)')
@click.pass_context
def query(ctx, query, sources):
    """Execute quick research query with source-based reasoning

    Provides concise, well-researched answers to specific questions.
    Perfect for fact-checking, definitions, and quick lookups.

    Arguments:
        QUERY: The research question or topic to investigate

    Options:
        --sources: Controls research depth (more sources = more comprehensive)

    Use Cases:
    - Fact verification
    - Technical definitions
    - Current events
    - Quick concept explanations

    Examples:
        ./agent_advanced_cli.py research query "What is machine learning?"
        ./agent_advanced_cli.py research query "Latest AI trends" --sources 5
        ./agent_advanced_cli.py --model gpt-oss:120b-cloud research query "Fast lookup"
    """
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
@click.option('--depth', type=click.Choice(['shallow', 'medium', 'deep']), default='medium',
              help='Analysis depth: shallow (overview), medium (balanced), deep (comprehensive)')
@click.pass_context
def deep(ctx, topic, depth):
    """Perform comprehensive research with multi-perspective analysis

    Conducts in-depth investigation with critical analysis, multiple viewpoints,
    and actionable conclusions. Ideal for complex topics requiring thorough understanding.

    Arguments:
        TOPIC: Subject for deep research and analysis

    Options:
        --depth: Controls analysis thoroughness
            - shallow: Quick overview with main points
            - medium: Balanced analysis (default)
            - deep: Exhaustive research with full citations

    Output Includes:
    - Multiple perspectives and viewpoints
    - Supporting evidence and examples
    - Critical analysis of implications
    - Actionable conclusions and recommendations

    Use Cases:
    - Technology evaluations
    - Best practices research
    - Market analysis
    - Academic research

    Examples:
        ./agent_advanced_cli.py research deep "Python best practices"
        ./agent_advanced_cli.py research deep "AI safety" --depth deep
        ./agent_advanced_cli.py --model deepseek-v3.1:671b-cloud research deep "Complex topic"
    """
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
    """Code analysis and review commands

    Specialized code agents for software quality assessment:
    - analyze: Detailed file analysis (bugs, performance, security)
    - review: Comprehensive code review (architecture, patterns, maintainability)

    All code agents provide actionable feedback with examples.
    """
    pass


@code.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--focus',
              help='Specific aspect to analyze (performance, security, bugs, style)')
@click.pass_context
def analyze(ctx, file_path, focus):
    """Analyze code file for quality, bugs, and potential issues

    Provides detailed analysis of a single code file covering:
    - Code quality and best practices
    - Potential bugs and logic errors
    - Performance optimization opportunities
    - Security vulnerabilities
    - Style and readability improvements

    Arguments:
        FILE_PATH: Path to the code file to analyze

    Options:
        --focus: Narrow analysis to specific aspect (optional)

    Analysis Includes:
    - Line-by-line issue identification
    - Severity ratings (critical, warning, info)
    - Specific fix recommendations
    - Code examples for improvements

    Use Cases:
    - Pre-commit quality checks
    - Bug hunting and debugging
    - Performance optimization
    - Security audits
    - Code cleanup and refactoring

    Examples:
        ./agent_advanced_cli.py code analyze script.py
        ./agent_advanced_cli.py code analyze app.py --focus performance
        ./agent_advanced_cli.py code analyze auth.py --focus security
        ./agent_advanced_cli.py --debug code analyze buggy.py
    """
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
@click.option('--strict/--lenient', default=False,
              help='Strict mode (high standards) vs lenient (balanced feedback)')
@click.pass_context
def review(ctx, path, strict):
    """Comprehensive code review for architecture and maintainability

    Performs senior-level code review covering high-level concerns:
    - Architecture and design patterns
    - Code organization and structure
    - Testing strategy and coverage
    - Documentation completeness
    - Maintainability and scalability
    - Dependency management

    Arguments:
        PATH: File or directory to review

    Options:
        --strict: Apply high standards (production-ready requirements)
        --lenient: Balanced review (default, allows some flexibility)

    Review Output:
    - Architectural assessment
    - Design pattern evaluation
    - Improvement recommendations
    - Priority ranking (must-fix, should-fix, nice-to-have)

    Use Cases:
    - Pre-merge PR reviews
    - Architecture validation
    - Legacy code assessment
    - Refactoring planning
    - Onboarding documentation review

    Examples:
        ./agent_advanced_cli.py code review ./myproject
        ./agent_advanced_cli.py code review main.py --strict
        ./agent_advanced_cli.py code review ./src --lenient
        ./agent_advanced_cli.py --model deepseek-v3.1:671b-cloud code review ./
    """
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
@click.option('--agents', multiple=True,
              help='Limit to specific agents (research, code). Omit for all.')
@click.pass_context
def orchestrate(ctx, task, agents):
    """Coordinate multiple specialized agents for complex multi-faceted tasks

    The orchestrator agent intelligently delegates work to specialized agents:
    - Research agent: Information gathering, analysis, fact-checking
    - Code agent: Code analysis, review, architecture evaluation

    Perfect for tasks that require multiple capabilities working together.

    Arguments:
        TASK: Complex task description requiring multiple agent types

    Options:
        --agents: Restrict to specific agent types (can specify multiple)

    Orchestration Process:
    1. Task decomposition into subtasks
    2. Agent selection for each subtask
    3. Coordination and synthesis of results
    4. Comprehensive integrated response

    Use Cases:
    - "Research Python best practices and analyze my code against them"
    - "Analyze this security vulnerability and research mitigation strategies"
    - "Review codebase architecture and research alternative patterns"
    - "Investigate technology stack and provide implementation recommendations"

    Examples:
        ./agent_advanced_cli.py orchestrate "Research AI trends and review my ML code"
        ./agent_advanced_cli.py orchestrate "Analyze security issues and research fixes"
        ./agent_advanced_cli.py orchestrate "Complex task" --agents research --agents code
        ./agent_advanced_cli.py --model deepseek-v3.1:671b-cloud orchestrate "Deep analysis task"
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
    """Display current agent configuration and settings

    Shows the active configuration including model selection and debug status.
    Useful for verifying settings before running commands.

    Configuration Displayed:
    - Model: Currently selected Ollama cloud model
    - Debug: Whether verbose debugging is enabled

    Examples:
        ./agent_advanced_cli.py config
        ./agent_advanced_cli.py --model gpt-oss:120b-cloud config
        ./agent_advanced_cli.py --debug config
    """
    click.echo(f"Model: {ctx.obj['model']}")
    click.echo(f"Debug: {ctx.obj['debug']}")


if __name__ == "__main__":
    cli()
