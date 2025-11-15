#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "click",
#   "fastapi",
#   "ollama",
#   "sqlalchemy",
# ]
#
# [tool.uv.sources]
# agno = { path = "/Users/smian/github-smian0/agno-ck/libs/agno", editable = true }
# ///

"""Stock Research Workflow using Perplexity Finance via Comet Browser

This workflow automates stock research by:
1. Navigating to Perplexity Finance page for the ticker
2. Extracting recent developments and news
3. Asking custom analytical questions
4. Synthesizing findings into a comprehensive report
"""

# Disable Agno telemetry before importing agno modules
import os
os.environ["AGNO_TELEMETRY"] = "false"

import subprocess
import json
import click
import time
from pathlib import Path
from agno.agent import Agent
from agno.workflow import Workflow, Step
from agno.workflow.types import StepInput, StepOutput
from agno.models.ollama import Ollama


# Path to the scraper agent
SCRAPER_AGENT = Path(__file__).parent.parent.parent / "scraper_agent.py"


def run_scraper_with_retry(
    command: list,
    max_retries: int = 3,
    initial_delay: int = 10,
    timeout: int = 120
) -> subprocess.CompletedProcess:
    """
    Run scraper command with exponential backoff retry on Ollama failures.

    Args:
        command: Command list for subprocess.run()
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 10s)
        timeout: Timeout in seconds for each attempt (default: 120s)

    Returns:
        subprocess.CompletedProcess result

    Raises:
        Exception: If all retries are exhausted
    """
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            # Check if it's an Ollama crash (500 error in stderr)
            if result.returncode != 0 and ("status code: 500" in result.stderr or
                                           "Internal Server Error" in result.stderr):
                if attempt < max_retries - 1:
                    print(f"⚠️ Ollama crash detected (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                else:
                    print(f"❌ Ollama crash persists after {max_retries} attempts")
                    return result

            # Success or non-Ollama error - return immediately
            return result

        except subprocess.TimeoutExpired as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Timeout (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
                continue
            else:
                raise

    # This shouldn't be reached, but just in case
    raise Exception(f"Failed after {max_retries} attempts")


def extract_ticker_from_input(input_text: str) -> str:
    """Extract stock ticker from workflow input"""
    # Simple extraction - assumes ticker is the main part of the input
    # Handle formats like "AAPL", "Research AAPL", "Analyze TSLA stock"
    words = input_text.upper().split()
    for word in words:
        # Stock tickers are typically 1-5 uppercase letters
        if word.isalpha() and 1 <= len(word) <= 5:
            return word
    # Fallback: use the first word
    return words[0] if words else "AAPL"


def fetch_stock_developments(step_input: StepInput) -> StepOutput:
    """
    Step 1: Navigate to Perplexity Finance and extract recent developments

    Uses scraper_agent.py screenshot command to capture the finance page.
    """
    # Extract ticker from workflow input
    ticker = extract_ticker_from_input(step_input.input or "AAPL")
    url = f"https://www.perplexity.ai/finance/{ticker}"

    # Create temp file for screenshot
    output_file = f"/tmp/perplexity_{ticker.lower()}_developments.png"

    try:
        # Call scraper agent to capture the page
        result = subprocess.run(
            [str(SCRAPER_AGENT), "screenshot", url, "-o", output_file],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            content = f"# {ticker} - Recent Developments\n\n"
            content += "✅ Successfully captured Perplexity Finance page\n\n"
            content += f"Screenshot saved to: {output_file}\n\n"
            content += "The page shows recent developments, news, and market data for the stock.\n"

            return StepOutput(
                content=content,
            )
        else:
            return StepOutput(
                content=f"❌ Failed to capture page: {result.stderr}",
            )

    except subprocess.TimeoutExpired:
        return StepOutput(
            content="❌ Screenshot command timed out after 60s",
        )
    except Exception as e:
        return StepOutput(
            content=f"❌ Error: {str(e)}",
        )


def query_perplexity_analysis(step_input: StepInput) -> StepOutput:
    """
    Step 2: Ask analytical questions to Perplexity about the stock

    Uses scraper_agent.py scrape command to interact with Perplexity's finance interface.
    """
    # Extract ticker from previous step or input
    ticker = extract_ticker_from_input(step_input.input or "AAPL")
    url = f"https://www.perplexity.ai/finance/{ticker}"

    # Define analytical questions to ask
    questions = [
        "Is there an obvious buy signal for this stock right now?",
        "What are the key risks and opportunities?",
        "How does the current valuation compare to historical averages?",
    ]

    analysis_results = []

    for i, question in enumerate(questions, 1):
        output_file = f"/tmp/{ticker.lower()}_analysis_{i}.json"
        prompt = f"Find the 'Ask any question about finance' search box, type '{question}' and submit it. Then extract the response."

        try:
            result = run_scraper_with_retry(
                command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", output_file],
                max_retries=3,
                initial_delay=10,
                timeout=120,
            )

            if result.returncode == 0:
                # Try to read the extracted data
                if Path(output_file).exists():
                    try:
                        with open(output_file) as f:
                            data = json.load(f)
                        analysis_results.append({
                            "question": question,
                            "response": data.get("response", "No response extracted"),
                            "status": "success"
                        })
                    except json.JSONDecodeError:
                        analysis_results.append({
                            "question": question,
                            "response": "Response data format error",
                            "status": "error"
                        })
                else:
                    analysis_results.append({
                        "question": question,
                        "response": "Output file not created",
                        "status": "error"
                    })
            else:
                analysis_results.append({
                    "question": question,
                    "response": f"Scrape failed: {result.stderr[:200]}",
                    "status": "error"
                })

        except subprocess.TimeoutExpired:
            analysis_results.append({
                "question": question,
                "response": "Query timed out after 120s",
                "status": "timeout"
            })
        except Exception as e:
            analysis_results.append({
                "question": question,
                "response": f"Error: {str(e)}",
                "status": "error"
            })

    # Format results
    content = f"# {ticker} - Perplexity Analysis\n\n"

    for i, result in enumerate(analysis_results, 1):
        status_icon = "✅" if result["status"] == "success" else "❌"
        content += f"## Question {i}: {result['question']}\n"
        content += f"{status_icon} Status: {result['status']}\n\n"
        content += f"**Response:**\n{result['response']}\n\n"
        content += "---\n\n"

    return StepOutput(
        content=content,
    )


# Create synthesis agent
synthesizer = Agent(
    name="Stock Research Synthesizer",
    model=Ollama(
        id="glm-4.6:cloud",
        options={"num_ctx": 198000}  # Full 198K context
    ),
    instructions=[
        "You are a professional stock research analyst.",
        "Review the gathered data from Perplexity Finance and synthesize it into a comprehensive investment report.",
        "Include:",
        "- Executive Summary",
        "- Recent Developments Analysis",
        "- Key Findings from Q&A",
        "- Investment Thesis",
        "- Risk Assessment",
        "- Recommendation (Buy/Hold/Sell) with rationale",
        "Use clear sections with markdown formatting.",
        "Be objective and data-driven in your analysis.",
    ],
    markdown=True,
    exponential_backoff=True,
    retries=3,
    delay_between_retries=15,
)


# Create workflow
stock_research_workflow = Workflow(
    name="Stock Research Workflow",
    description="Automated stock research using Perplexity Finance",
    steps=[
        Step(
            name="Fetch Recent Developments",
            executor=fetch_stock_developments,
            description="Navigate to Perplexity Finance and capture recent developments",
        ),
        Step(
            name="Query Analytical Insights",
            executor=query_perplexity_analysis,
            description="Ask key analytical questions to Perplexity",
        ),
        Step(
            name="Synthesize Research Report",
            agent=synthesizer,
            description="Generate comprehensive investment report",
        ),
    ],
)


# CLI Interface with Click
@click.group()
def cli():
    """Stock Research Workflow - Automated analysis using Perplexity Finance"""
    pass


@cli.command()
@click.argument('ticker')
@click.option('--output', '-o', type=click.Path(), help='Save report to file')
def research(ticker, output):
    """Research a stock ticker (e.g., AAPL, TSLA, NVDA)

    Examples:
        ./workflow.py research AAPL
        ./workflow.py research TSLA --output tsla_report.md
    """
    click.echo(f"\n🔍 Starting research for {ticker.upper()}...\n")

    # Execute workflow
    result = stock_research_workflow.run(
        input=f"Research {ticker.upper()} stock",
        stream=False,
    )

    # Display result
    if result and result.content:
        click.echo("\n" + "="*80)
        click.echo(result.content)
        click.echo("="*80 + "\n")

        # Save to file if requested
        if output:
            output_path = Path(output)
            output_path.write_text(result.content)
            click.echo(f"✅ Report saved to: {output}\n")
    else:
        click.echo("❌ Workflow returned no content\n")


@cli.command()
@click.argument('ticker')
def quick(ticker):
    """Quick research (developments only, no deep questions)

    Examples:
        ./workflow.py quick AAPL
    """
    click.echo(f"\n🔍 Quick research for {ticker.upper()}...\n")

    # Execute only first step
    url = f"https://www.perplexity.ai/finance/{ticker.upper()}"
    output_file = f"/tmp/perplexity_{ticker.lower()}_quick.png"

    try:
        result = subprocess.run(
            [str(SCRAPER_AGENT), "screenshot", url, "-o", output_file],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            click.echo(f"✅ Screenshot captured: {output_file}")
            click.echo(f"\nView the Perplexity Finance page for {ticker.upper()} at:")
            click.echo(f"  {url}\n")
        else:
            click.echo(f"❌ Failed: {result.stderr}\n")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}\n")


if __name__ == "__main__":
    cli()
