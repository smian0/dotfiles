#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "agno",
#     "click",
# ]
# ///
"""
Example: Workflow Using Teams for Complex Market Research

This demonstrates:
1. When to use a Team within a Workflow (collaborative research phase)
2. How Teams differ from Parallel steps (shared context vs independent)
3. Combining Teams, custom executors, and individual agents in one workflow

Use Case: Market research requiring multiple specialists to collaborate,
then process findings, then generate a report.

Why Team in Workflow?
- Research needs collaboration: HN trends + web data + competitive analysis
- Team members need to see each other's findings (shared context)
- Team leader coordinates who researches what based on emerging patterns
- vs Parallel: Would run all 3 independently, no coordination, no context sharing

Pattern: Workflow → [Team Step (collaborative), Custom Executor (processing), Agent Step (report)]
"""

import click
from agno.agent import Agent
from agno.team import Team
from agno.workflow import Workflow, Step
from agno.models.ollama import Ollama
from agno.tools.hackernews import HackerNewsTools
from agno.tools.duckduckgo import DuckDuckGoTools


# ==============================================================================
# Step 1: Define Specialist Agents for the Research Team
# ==============================================================================

hn_researcher = Agent(
    name="HackerNews Researcher",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Research tech trends and discussions from Hacker News",
    tools=[HackerNewsTools()],
    instructions=[
        "Search Hacker News for discussions about the given topic.",
        "Look for trending posts, top comments, and community sentiment.",
        "Focus on technical insights and developer perspectives.",
        "Summarize key themes and concerns from the HN community.",
    ],
    markdown=True,
)

web_researcher = Agent(
    name="Web Researcher",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Research broader market context from web sources",
    tools=[DuckDuckGoTools()],
    instructions=[
        "Search the web for recent news, articles, and market data.",
        "Look for company announcements, product launches, and market trends.",
        "Identify key players, partnerships, and competitive landscape.",
        "Provide factual, well-sourced information.",
    ],
    markdown=True,
)

competitive_analyst = Agent(
    name="Competitive Analyst",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Analyze competitive positioning and market opportunities",
    instructions=[
        "Review findings from HN and web researchers.",
        "Identify competitive advantages, threats, and market gaps.",
        "Analyze positioning strategies and differentiation opportunities.",
        "Provide strategic recommendations based on research.",
    ],
    markdown=True,
)


# ==============================================================================
# Step 2: Create Collaborative Research Team
# ==============================================================================
# Why Team instead of Parallel steps?
# - Analysts need to see HN and web findings to provide strategic analysis
# - Team leader can decide: "HN first, then web, then analysis based on findings"
# - Shared context enables synthesis that independent parallel steps cannot achieve

research_team = Team(
    name="Market Research Team",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    members=[hn_researcher, web_researcher, competitive_analyst],
    instructions=[
        "You are a market research team coordinator.",
        "First, task the HackerNews researcher to find community discussions and sentiment.",
        "Second, task the Web researcher to gather market data and competitive landscape.",
        "Third, task the Competitive Analyst to synthesize findings and provide strategic recommendations.",
        "Ensure each member sees previous findings to build comprehensive analysis.",
    ],
    markdown=True,
    show_members_responses=True,  # Show all member outputs for transparency
    # Note: Using sequential delegation (default) for coordinated research
    # If we used delegate_task_to_all_members=True, all would research simultaneously
    # Sequential is better here because analyst needs to see HN + web findings first
)


# ==============================================================================
# Step 3: Custom Executor for Data Processing
# ==============================================================================

def process_research_findings(step_output):
    """
    Process team research output and extract key insights.

    This demonstrates custom executors in workflows for data transformation
    between steps. Useful when you need to reformat, filter, or summarize
    before passing to the next step.
    """
    from agno.workflow import StepOutput

    research_content = step_output.content if step_output else ""

    # Extract key sections (simplified for example)
    processed = f"""# Processed Market Research Insights

## Executive Summary
{research_content[:500]}...

## Key Findings
[Extracted from collaborative team research]

## Next Steps for Report Generation
Based on the research above, generate a comprehensive market analysis report
that synthesizes all findings into actionable insights.

---
Full Research Data:
{research_content}
"""

    return StepOutput(
        content=processed,
    )


# ==============================================================================
# Step 4: Individual Report Writer Agent
# ==============================================================================

report_writer = Agent(
    name="Report Writer",
    model=Ollama(id="glm-4.6:cloud", options={"num_ctx": 198000}),
    role="Generate comprehensive market analysis reports",
    instructions=[
        "Review the processed research insights.",
        "Generate a professional market analysis report.",
        "Include: Executive Summary, Market Overview, Competitive Analysis, Recommendations.",
        "Use clear structure with headings and bullet points.",
        "Focus on actionable insights for business decision-making.",
    ],
    markdown=True,
)


# ==============================================================================
# Step 5: Assemble Complete Workflow
# ==============================================================================

market_research_workflow = Workflow(
    name="Market Research Workflow",
    description="Complete market research pipeline with collaborative team",
    steps=[
        # Step 1: Collaborative Research Phase (Team)
        # Why Team here? Need specialists to coordinate and share context
        Step(
            name="Collaborative Research",
            team=research_team,
            description="Research team collaborates on market analysis",
        ),

        # Step 2: Data Processing (Custom Executor)
        # Why custom executor? Need to transform team output for report writer
        Step(
            name="Process Findings",
            executor=process_research_findings,
            description="Extract and format key insights",
        ),

        # Step 3: Report Generation (Individual Agent)
        # Why individual agent? Specialized writing task, no collaboration needed
        Step(
            name="Generate Report",
            agent=report_writer,
            description="Create comprehensive market analysis report",
        ),
    ],
)


# ==============================================================================
# CLI Interface
# ==============================================================================

@click.command()
@click.option(
    "--topic",
    "-t",
    default="AI agent frameworks",
    help="Market research topic",
)
@click.option(
    "--stream/--no-stream",
    default=False,
    help="Stream workflow output (note: stream=True returns generator, not result object)",
)
def main(topic: str, stream: bool):
    """
    Market research workflow using Teams for collaborative research.

    Example:
        ./workflow_with_team_research.py --topic "AI agent frameworks"
    """
    click.echo(f"🔬 Starting market research workflow for: {topic}\n")

    # Run workflow
    result = market_research_workflow.run(
        input=topic,
        stream=stream,
    )

    if stream:
        # When stream=True, result is a generator
        click.echo("\n" + "="*80)
        click.echo("✅ Market Research Workflow Streaming...")
        click.echo("="*80 + "\n")
        for chunk in result:
            if hasattr(chunk, 'content') and chunk.content:
                click.echo(chunk.content)
    elif result:
        # When stream=False, result is a WorkflowOutput object
        click.echo("\n" + "="*80)
        click.echo("✅ Market Research Workflow Complete")
        click.echo("="*80 + "\n")
        if result.content:
            click.echo(result.content)
    else:
        click.echo("❌ Workflow failed to produce results")


if __name__ == "__main__":
    main()
