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

"""Politician Trades Workflow using Perplexity Finance via Comet Browser

This workflow analyzes congressional stock trades by:
1. Extracting recent politician trades from Perplexity Finance politicians page
2. Looking up committee assignments for selected politicians
3. Analyzing connections between committee jurisdiction and trade sectors
4. Synthesizing insights into actionable trading intelligence
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


def extract_politician_trades(step_input: StepInput) -> StepOutput:
    """
    Step 1: Navigate to Perplexity Finance politicians page and extract recent trades

    Captures the politicians trading page and extracts structured trade data.
    """
    url = "https://www.perplexity.ai/finance/politicians"

    # Create temp file for extracted trades
    output_file = "/tmp/politician_trades.json"

    prompt = """Look at the politicians trading page and extract the recent transactions.
For each trade, extract:
- Politician name
- Ticker symbol
- Transaction type (Buy/Sell)
- Amount range (if visible)
- Date

Format the response as structured JSON with an array of trades."""

    try:
        # Call scraper agent to extract trades with retry on Ollama crashes
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

                    content = "# Recent Politician Trades\n\n"
                    content += "✅ Successfully extracted trades from Perplexity Finance\n\n"

                    # Parse the response content
                    response_content = data.get("content", "")
                    if response_content:
                        content += f"**Extracted Data:**\n\n{response_content}\n\n"
                    else:
                        content += "⚠️ No structured data extracted\n\n"

                    content += f"Raw data saved to: {output_file}\n"

                    return StepOutput(content=content)

                except json.JSONDecodeError:
                    return StepOutput(
                        content=f"❌ Failed to parse JSON from {output_file}",
                    )
            else:
                return StepOutput(
                    content="❌ Output file not created",
                )
        else:
            return StepOutput(
                content=f"❌ Scrape failed: {result.stderr}",
            )

    except subprocess.TimeoutExpired:
        return StepOutput(
            content="❌ Trade extraction timed out after 120s",
        )
    except Exception as e:
        return StepOutput(
            content=f"❌ Error: {str(e)}",
        )


def lookup_committee_assignments(step_input: StepInput) -> StepOutput:
    """
    Step 2: Look up congressional committee assignments for selected politicians

    For each politician from step 1, queries Perplexity to find their committee assignments.
    """
    # Extract politician names from input or use defaults from the screenshot
    # Based on the screenshot, we saw: Beyer, McClain Delaney, Moreno, Greene
    politicians = [
        "Donald S. Beyer Jr.",
        "April McClain Delaney",
        "Marjorie Taylor Greene",
    ]

    url = "https://www.perplexity.ai/finance/politicians"
    committee_results = []

    for politician in politicians:
        output_file = f"/tmp/{politician.replace(' ', '_').lower()}_committees.json"
        prompt = f"Which congressional committees is {politician} on?"

        try:
            result = run_scraper_with_retry(
                command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", output_file],
                max_retries=3,
                initial_delay=10,
                timeout=120,
            )

            if result.returncode == 0 and Path(output_file).exists():
                try:
                    with open(output_file) as f:
                        data = json.load(f)
                    committee_results.append({
                        "politician": politician,
                        "committees": data.get("content", "No committee data"),
                        "status": "success"
                    })
                except json.JSONDecodeError:
                    committee_results.append({
                        "politician": politician,
                        "committees": "Response data format error",
                        "status": "error"
                    })
            else:
                committee_results.append({
                    "politician": politician,
                    "committees": f"Scrape failed: {result.stderr[:200]}",
                    "status": "error"
                })

        except subprocess.TimeoutExpired:
            committee_results.append({
                "politician": politician,
                "committees": "Query timed out after 120s",
                "status": "timeout"
            })
        except Exception as e:
            committee_results.append({
                "politician": politician,
                "committees": f"Error: {str(e)}",
                "status": "error"
            })

    # Format results
    content = "# Committee Assignments\n\n"

    for result in committee_results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        content += f"## {result['politician']}\n"
        content += f"{status_icon} Status: {result['status']}\n\n"
        content += f"**Committees:**\n{result['committees']}\n\n"
        content += "---\n\n"

    return StepOutput(content=content)


# Create synthesis agent
synthesizer = Agent(
    name="Political Trade Analyst",
    model=Ollama(
        id="glm-4.6:cloud",
        options={"num_ctx": 198000}  # Full 198K context
    ),
    instructions=[
        "You are a political trading intelligence analyst.",
        "Review the politician trades and their committee assignments.",
        "Synthesize the data to identify potential insider trading signals.",
        "Include:",
        "- Executive Summary",
        "- Key Trades Analysis (which politicians bought/sold what)",
        "- Committee Jurisdiction Mapping (connect trades to committee power)",
        "- Sector Implications (what sectors are being favored/avoided)",
        "- Actionable Trading Insights (which stocks/sectors to watch)",
        "- Risk Assessment (are these early signals or late to party)",
        "Use clear sections with markdown formatting.",
        "Be objective and focus on correlations between committee power and trading activity.",
        "Highlight any trades that seem to align with upcoming policy areas under committee jurisdiction.",
    ],
    markdown=True,
    exponential_backoff=True,
    retries=3,
    delay_between_retries=15,
)


# Create workflow
politician_trades_workflow = Workflow(
    name="Politician Trades Workflow",
    description="Analyze congressional stock trades for trading intelligence",
    steps=[
        Step(
            name="Extract Recent Trades",
            executor=extract_politician_trades,
            description="Extract politician trades from Perplexity Finance",
        ),
        Step(
            name="Lookup Committee Assignments",
            executor=lookup_committee_assignments,
            description="Query committee assignments for key politicians",
        ),
        Step(
            name="Synthesize Trading Intelligence",
            agent=synthesizer,
            description="Generate actionable trading insights report",
        ),
    ],
)


# CLI Interface with Click
@click.group()
def cli():
    """Politician Trades Workflow - Congressional trading intelligence"""
    pass


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Save report to file')
def analyze(output):
    """Analyze recent politician trades and committee assignments

    Examples:
        ./workflow.py analyze
        ./workflow.py analyze --output politician_trades_report.md
    """
    click.echo("\n🔍 Starting politician trades analysis...\n")

    # Execute workflow
    result = politician_trades_workflow.run(
        input="Analyze recent politician trades",
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
@click.argument('politician')
@click.option('--output', '-o', type=click.Path(), help='Save committee info to file')
def committee(politician, output):
    """Look up committee assignments for a specific politician

    Examples:
        ./workflow.py committee "Donald S. Beyer Jr."
        ./workflow.py committee "Marjorie Taylor Greene" --output greene_committees.json
    """
    click.echo(f"\n🔍 Looking up committees for {politician}...\n")

    url = "https://www.perplexity.ai/finance/politicians"
    output_file = output or f"/tmp/{politician.replace(' ', '_').lower()}_committees.json"
    prompt = f"Which congressional committees is {politician} on?"

    try:
        result = run_scraper_with_retry(
            command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", output_file],
            max_retries=3,
            initial_delay=10,
            timeout=120,
        )

        if result.returncode == 0:
            if Path(output_file).exists():
                try:
                    with open(output_file) as f:
                        data = json.load(f)
                    click.echo("✅ Committee assignments retrieved:\n")
                    click.echo(data.get("content", "No committee data"))
                    click.echo(f"\n📄 Data saved to: {output_file}\n")
                except json.JSONDecodeError:
                    click.echo(f"❌ Failed to parse JSON from {output_file}\n")
            else:
                click.echo("❌ Output file not created\n")
        else:
            click.echo(f"❌ Scrape failed: {result.stderr}\n")

    except subprocess.TimeoutExpired:
        click.echo("❌ Query timed out after 120s\n")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}\n")


@cli.command()
def quick():
    """Quick screenshot of politician trades page (no analysis)

    Examples:
        ./workflow.py quick
    """
    click.echo("\n🔍 Capturing politician trades page...\n")

    url = "https://www.perplexity.ai/finance/politicians"
    output_file = "/tmp/politician_trades_quick.png"

    try:
        result = subprocess.run(
            [str(SCRAPER_AGENT), "screenshot", url, "-o", output_file],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            click.echo(f"✅ Screenshot captured: {output_file}")
            click.echo(f"\nView the Perplexity Finance politicians page at:")
            click.echo(f"  {url}\n")
        else:
            click.echo(f"❌ Failed: {result.stderr}\n")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}\n")


@cli.command()
@click.argument('politician')
@click.argument('ticker')
@click.option('--output', '-o', type=click.Path(), help='Save comprehensive analysis to file')
def analyze_trade(politician, ticker, output):
    """Comprehensive multi-question analysis of a politician's trade (WORKING VERSION)

    Runs 5 targeted research queries on Finance page and synthesizes into intelligence report.
    This is the alternative to Deep Research mode that works with current infrastructure.

    Examples:
        ./workflow.py analyze-trade "Donald S. Beyer Jr." "GDXJ"
        ./workflow.py analyze-trade "Marjorie Taylor Greene" "COIN" --output reports/greene_coin_analysis.md
    """
    click.echo(f"\n📊 Starting Comprehensive Trade Analysis...\n")
    click.echo(f"Politician: {politician}")
    click.echo(f"Ticker: {ticker}\n")

    output_file = output or f"/tmp/{politician.replace(' ', '_').lower()}_{ticker.lower()}_comprehensive.json"

    # Use Finance politicians page (proven to work)
    url = "https://www.perplexity.ai/finance/politicians"

    # Define 5 targeted research questions
    questions = [
        f"What congressional committees is {politician} on and what is their jurisdiction? Include specific policy areas they oversee.",

        f"What pending legislation or upcoming committee actions could impact {ticker}'s sector? Include any scheduled hearings or votes.",

        f"Has {politician} traded in {ticker}'s sector before? What was the timing and performance of similar past trades?",

        f"What are the major upcoming catalysts and market outlook for {ticker}'s sector in the next 3-6 months?",

        f"Analyze the insider signal strength of {politician}'s {ticker} purchase. Consider committee jurisdiction, timing, and pending legislation. Rate as Low/Medium/High/Very High."
    ]

    results = []

    click.echo("🔍 Phase 1: Multi-Question Research (5 questions)")
    click.echo("=" * 60)

    for i, question in enumerate(questions, 1):
        question_file = f"/tmp/{politician.replace(' ', '_').lower()}_{ticker.lower()}_q{i}.json"

        click.echo(f"\nQuestion {i}/5: {question[:70]}...")

        # For first question, open page normally
        # For subsequent questions, reuse the existing page to avoid timeout
        if i == 1:
            prompt = f"Open {url} in a new page. Then find the 'Ask any question about finance' search box, type '{question}' and submit it. Extract the complete response with all details and citations."
        else:
            # Tell agent to reuse existing page instead of opening new one
            prompt = f"""IMPORTANT: The Perplexity Finance page is already open from the previous question. Do NOT open a new page.

Instead:
1. Use `list_pages` to see all open pages
2. Find the page with URL containing 'perplexity.ai/finance'
3. Use `select_page` to switch to that page
4. Then find the 'Ask any question about finance' search box, type '{question}' and submit it
5. Extract the complete response with all details and citations

Remember: DO NOT use `new_page` - the page is already open, just select it!"""

        try:
            result = run_scraper_with_retry(
                command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", question_file],
                max_retries=3,
                initial_delay=10,
                timeout=120,
            )

            if result.returncode == 0 and Path(question_file).exists():
                try:
                    with open(question_file) as f:
                        data = json.load(f)
                    results.append({
                        "question": question,
                        "response": data.get("content", "No response"),
                        "status": "success"
                    })
                    click.echo(f"  ✅ Completed")
                except json.JSONDecodeError:
                    results.append({
                        "question": question,
                        "response": "Failed to parse response",
                        "status": "error"
                    })
                    click.echo(f"  ❌ Parse error")
            else:
                results.append({
                    "question": question,
                    "response": f"Scrape failed: {result.stderr[:200]}",
                    "status": "error"
                })
                click.echo(f"  ❌ Scrape failed")

        except subprocess.TimeoutExpired:
            results.append({
                "question": question,
                "response": "Query timed out",
                "status": "timeout"
            })
            click.echo(f"  ⏱️  Timeout")
        except Exception as e:
            results.append({
                "question": question,
                "response": f"Error: {str(e)}",
                "status": "error"
            })
            click.echo(f"  ❌ Error: {str(e)[:50]}")

    click.echo(f"\n{'=' * 60}")
    click.echo("🧠 Phase 2: Synthesizing Intelligence Report...\n")

    # Build synthesis prompt
    synthesis_input = f"""# Comprehensive Trade Analysis: {politician} - {ticker}

## Research Findings

"""

    for i, result in enumerate(results, 1):
        status_icon = "✅" if result["status"] == "success" else "❌"
        synthesis_input += f"### Question {i}: {result['question']}\n"
        synthesis_input += f"{status_icon} **Response:**\n{result['response']}\n\n"
        synthesis_input += "---\n\n"

    synthesis_input += """
## Task

Synthesize the above research into a comprehensive political trading intelligence report.

**Required Sections:**

1. **Executive Summary** (3-5 bullet points of key findings)

2. **Politician Profile**
   - Committee assignments and jurisdiction
   - Policy focus areas relevant to this trade
   - Trading history and patterns

3. **Trade Analysis**
   - What: Ticker, sector, timing
   - Why: Potential motivations and signals
   - Committee-Trade Correlation

4. **Legislative Context**
   - Pending bills and hearings
   - Committee jurisdiction overlap
   - Timeline of upcoming actions

5. **Sector Outlook**
   - Market sentiment
   - Upcoming catalysts
   - Risk factors

6. **Insider Signal Assessment**
   - Signal Strength: Low/Medium/High/Very High
   - Confidence Level: 1-10
   - Justification with specific evidence

7. **Risk Assessment**
   - What could go wrong
   - Timing considerations
   - Alternative explanations

8. **Recommended Action** (if signal is Medium or higher)
   - Entry strategy
   - Price targets
   - Time horizon
   - Position sizing guidance

**Format:**
- Use markdown with clear section headers
- Include specific dates, numbers, and facts
- Cite evidence from the research responses
- Be objective - mark speculation clearly
- Focus on actionable intelligence

**Critical:** Only recommend action if insider signal is Medium or higher with concrete evidence."""

    # Run synthesis with GLM-4.6
    synthesizer = Agent(
        name="Political Trading Intelligence Analyst",
        model=Ollama(
            id="glm-4.6:cloud",
            options={"num_ctx": 198000}
        ),
        instructions=[
            "You are an elite political trading intelligence analyst.",
            "Synthesize research findings into actionable trading intelligence.",
            "Be objective, evidence-based, and mark speculation clearly.",
            "Prioritize quality over quantity - focus on high-confidence signals.",
        ],
        markdown=True,
        exponential_backoff=True,
        retries=3,
        delay_between_retries=15,
    )

    try:
        click.echo("  Analyzing patterns and correlations...")
        intelligence_report = synthesizer.run(synthesis_input)

        # Save full report
        full_report = {
            "politician": politician,
            "ticker": ticker,
            "research_results": results,
            "intelligence_report": intelligence_report.content if intelligence_report else "Synthesis failed"
        }

        with open(output_file, 'w') as f:
            json.dump(full_report, f, indent=2)

        click.echo("\n✅ Analysis Complete!\n")
        click.echo("=" * 80)
        if intelligence_report and intelligence_report.content:
            click.echo(intelligence_report.content)
        else:
            click.echo("❌ Synthesis failed - showing raw research instead")
            for i, result in enumerate(results, 1):
                click.echo(f"\n### Question {i}")
                click.echo(result["response"][:500])
        click.echo("=" * 80)
        click.echo(f"\n📄 Full report saved to: {output_file}\n")

    except Exception as e:
        click.echo(f"\n❌ Synthesis error: {str(e)}\n")
        click.echo("Saving raw research results instead...\n")

        raw_output = {
            "politician": politician,
            "ticker": ticker,
            "research_results": results,
            "synthesis_error": str(e)
        }

        with open(output_file, 'w') as f:
            json.dump(raw_output, f, indent=2)

        click.echo(f"📄 Raw results saved to: {output_file}\n")


@cli.command()
@click.argument('politician')
@click.argument('ticker')
@click.option('--output', '-o', type=click.Path(), help='Save deep research report to file')
def deep_research(politician, ticker, output):
    """Deep research analysis of a politician's trade using Perplexity Deep Research

    Proof of concept for comprehensive multi-source analysis.

    Examples:
        ./workflow.py deep-research "Donald S. Beyer Jr." "GDXJ"
        ./workflow.py deep-research "Marjorie Taylor Greene" "COIN" --output reports/greene_coin.md
    """
    click.echo(f"\n🔬 Starting Deep Research analysis...\n")
    click.echo(f"Politician: {politician}")
    click.echo(f"Ticker: {ticker}\n")

    # Navigate to Perplexity main page for Deep Research mode
    url = "https://www.perplexity.ai"
    output_file = output or f"/tmp/{politician.replace(' ', '_').lower()}_{ticker.lower()}_deep_research.json"

    # Construct comprehensive deep research query
    research_query = f"""Analyze Representative {politician}'s recent purchase of {ticker} stock.

Research the following and synthesize into a comprehensive trading intelligence report:

1. POLITICIAN BACKGROUND:
   - What congressional committees is {politician} on?
   - What is their committee's jurisdiction and policy focus areas?
   - What is their recent legislative activity?

2. TRADE ANALYSIS:
   - When did {politician} buy {ticker}?
   - What sector/industry does {ticker} operate in?
   - What is the current market sentiment for {ticker}?

3. LEGISLATION CORRELATION:
   - What pending legislation could impact {ticker}'s sector?
   - Does {politician}'s committee have jurisdiction over this legislation?
   - Are there upcoming committee hearings or votes related to this sector?

4. HISTORICAL CONTEXT:
   - Has {politician} traded in this sector before?
   - What was the performance of similar trades?
   - Is there a pattern of well-timed trades before committee actions?

5. SECTOR CATALYSTS:
   - What upcoming events could impact {ticker}'s performance?
   - Are there regulatory changes on the horizon?
   - What is the market outlook for this sector?

Provide a structured analysis with:
- Executive Summary (key findings)
- Insider Signal Strength (Low/Medium/High/Very High)
- Committee-Trade Correlation
- Pending Legislation Impact
- Risk Assessment
- Recommended Action (if any)

Include specific citations and sources for all claims."""

    prompt = f"""Navigate to the Perplexity Deep Research mode and conduct comprehensive research.

Steps:
1. Go to https://www.perplexity.ai
2. Look for "Deep Research" mode or button (it may be labeled "Research", "Deep Dive", or similar)
3. Click to activate Deep Research mode
4. Enter this research query: "{research_query}"
5. Wait for the multi-step research to complete (this may take several minutes)
6. Extract the complete research report with all findings and citations
7. Format the output as a comprehensive markdown report

The research should be thorough, multi-source, and include proper citations."""

    click.echo("🔬 Initiating Deep Research mode...")
    click.echo("⏱️  This may take 5-10 minutes for comprehensive analysis...\n")

    try:
        result = run_scraper_with_retry(
            command=[str(SCRAPER_AGENT), "scrape", url, "--prompt", prompt, "-o", output_file],
            max_retries=3,
            initial_delay=10,
            timeout=600,  # 10 minutes timeout for deep research
        )

        if result.returncode == 0:
            if Path(output_file).exists():
                try:
                    with open(output_file) as f:
                        data = json.load(f)

                    click.echo("✅ Deep Research analysis completed!\n")
                    click.echo("="*80)
                    click.echo(data.get("content", "No research data"))
                    click.echo("="*80)
                    click.echo(f"\n📄 Full report saved to: {output_file}\n")

                except json.JSONDecodeError:
                    click.echo(f"❌ Failed to parse JSON from {output_file}\n")
            else:
                click.echo("❌ Output file not created\n")
        else:
            click.echo(f"❌ Deep Research failed: {result.stderr}\n")

    except subprocess.TimeoutExpired:
        click.echo("❌ Deep Research timed out after 10 minutes\n")
        click.echo("This might indicate:\n")
        click.echo("  - Deep Research mode is taking longer than expected")
        click.echo("  - The scraper couldn't find Deep Research UI elements")
        click.echo("  - Network or browser issues\n")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}\n")


if __name__ == "__main__":
    cli()
