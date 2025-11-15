#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "agno",
#     "click",
#     "mcp",
#     "ollama",
# ]
# ///

"""
Web Scraping Agent with Chrome DevTools MCP
Supports interactive automation, data extraction, and monitoring
"""

# Disable Agno telemetry before importing agno modules
import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
import click
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from datetime import datetime

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools
from agno.media import Image


COMET_URL = "http://127.0.0.1:9223"


def is_comet_running() -> bool:
    """Check if Comet is running with remote debugging"""
    try:
        urllib.request.urlopen(f"{COMET_URL}/json/version", timeout=2)
        return True
    except:
        return False


def get_comet_command():
    """Get Comet launch command for current platform"""
    if sys.platform == "darwin":  # macOS
        return [
            "/Applications/Comet.app/Contents/MacOS/Comet",
            "--remote-debugging-port=9223"
        ]
    elif sys.platform == "linux":
        return [
            "comet",
            "--remote-debugging-port=9223"
        ]
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def ensure_comet_running(silent: bool = False):
    """Ensure Comet is running with your default profile"""
    if is_comet_running():
        if not silent:
            click.echo("✅ Comet is running")
        return True

    if not silent:
        click.echo("🚀 Launching Comet...")

    try:
        cmd = get_comet_command()
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        # Wait for Comet to be ready (max 10 seconds)
        for _ in range(20):
            time.sleep(0.5)
            if is_comet_running():
                if not silent:
                    click.echo("✅ Comet is ready with your profile!")
                return True

        if not silent:
            click.echo("⚠️  Comet started but debugging port not ready. Waiting a bit longer...")
        time.sleep(2)
        return is_comet_running()

    except Exception as e:
        if not silent:
            click.echo(f"❌ Failed to launch Comet: {e}")
        return False


@click.group()
@click.option('--model', default='glm-4.6:cloud',
              help='Ollama model to use')
@click.option('--debug/--no-debug', default=False,
              help='Enable debug output')
@click.pass_context
def cli(ctx, model, debug):
    """
    Web Scraping Agent with Comet Browser and Chrome DevTools MCP

    Interactive automation, data extraction, and monitoring for websites.
    Uses your existing Comet default profile with all cookies and authentication.

    Comet runs on port 9223 for remote debugging.
    """
    ctx.ensure_object(dict)
    ctx.obj['model'] = model
    ctx.obj['debug'] = debug


def get_agent(ctx, additional_instructions: str = "") -> Agent:
    """Create agent with Comet and Chrome DevTools MCP tools"""
    base_instructions = """
    You are a web scraping expert with Chrome DevTools access.

    **Core Capabilities:**
    - Interactive automation (navigate, click, fill forms, wait for elements)
    - Data extraction (take snapshots, evaluate JavaScript, extract structured data)
    - Network monitoring (track requests, analyze responses)
    - Screenshot capture (full page or specific elements)

    **Scraping Workflow:**
    1. Use `new_page` to open target URL in a new tab (preserves existing tabs)
    2. Use `take_snapshot` to understand page structure (get element UIDs)
    3. Use `click`, `fill`, or `fill_form` for interaction
    4. Use `evaluate_script` to extract data with JavaScript
    5. Return structured JSON data when possible

    **Data Extraction Best Practices:**
    - Prefer `evaluate_script` for complex extractions (returns JSON-serializable data)
    - Use `take_snapshot` to identify element UIDs before interacting
    - Wait for dynamic content with `wait_for` before extraction
    - Handle pagination by clicking "next" buttons

    **JavaScript Extraction Example:**
    ```javascript
    () => {
      const items = Array.from(document.querySelectorAll('.item'));
      return items.map(item => ({
        title: item.querySelector('.title')?.innerText,
        price: item.querySelector('.price')?.innerText,
        link: item.querySelector('a')?.href
      }));
    }
    ```

    **Important:**
    - Always return structured data (JSON, arrays, objects)
    - Use meaningful names for extracted fields
    - Handle missing elements gracefully (use ?. optional chaining)
    - Report errors clearly if extraction fails
    """

    full_instructions = base_instructions
    if additional_instructions:
        full_instructions += f"\n\n**Additional Context:**\n{additional_instructions}"

    return Agent(
        name="Web Scraper",
        model=Ollama(
            id=ctx.obj['model'],
            options={"num_ctx": 198000}  # 198K context for large pages
        ),
        instructions=full_instructions,
        markdown=True,
        exponential_backoff=True,
        retries=3,
        delay_between_retries=15,
        debug_mode=ctx.obj['debug'],
    )


def get_comet_tools() -> MCPTools:
    """Initialize Chrome DevTools MCP tools for Comet"""
    return MCPTools(command=f"npx chrome-devtools-mcp@latest --browser-url={COMET_URL}")


@cli.command()
@click.argument('url')
@click.option('--output', '-o', type=click.Path(),
              help='Output file path (JSON, CSV, or Markdown)')
@click.option('--format', type=click.Choice(['json', 'csv', 'markdown']),
              default='json', help='Output format')
@click.option('--prompt', '-p', help='Custom extraction prompt')
@click.pass_context
def scrape(ctx, url, output, format, prompt):
    """
    Scrape data from a URL

    Examples:

      # Scrape and save to JSON
      ./scraper_agent.py scrape https://example.com -o data.json

      # Custom extraction
      ./scraper_agent.py scrape https://example.com \\
        --prompt "Extract all product names and prices"

      # Save as Markdown report
      ./scraper_agent.py scrape https://portfolio123.com/app/taxonomy \\
        -o report.md --format markdown
    """
    # Ensure Comet is running
    if not ensure_comet_running():
        click.echo("\n❌ Could not start Comet. Please check installation.")
        return

    async def run_scrape():
        async with get_comet_tools() as chrome_tools:
            agent = get_agent(ctx)
            agent.tools = [chrome_tools]

            # Build prompt with explicit navigation
            if prompt:
                extraction_prompt = f"First, open {url} in a new tab using the new_page tool. Then: {prompt}"
            else:
                extraction_prompt = f"First, open {url} in a new tab using the new_page tool. Then extract all relevant data as structured JSON."

            click.echo(f"\n🕷️  Scraping: {url}")
            click.echo(f"📝 Task: {extraction_prompt}\n")

            # Run agent
            # Use streaming output only in interactive terminals to avoid BlockingIOError
            import sys
            use_streaming = sys.stdout.isatty() and not output

            if use_streaming:
                click.echo()  # Blank line before agent output
                run_result = await agent.aprint_response(extraction_prompt, stream=True)
            else:
                # Non-interactive mode: use arun() without Rich console to avoid blocking
                run_result = await agent.arun(extraction_prompt)

            # Get result content
            result_content = run_result.content if run_result and hasattr(run_result, 'content') else ""

            if output and result_content:
                # Save results
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if format == 'json':
                    # Try to extract JSON from result
                    try:
                        data = json.loads(result_content)
                        output_path.write_text(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        # Save as plain JSON string
                        output_path.write_text(json.dumps({"content": result_content}, indent=2))
                else:
                    # Save as-is for markdown/csv
                    output_path.write_text(result_content)

                click.echo(f"\n✅ Saved to: {output_path}")

    asyncio.run(run_scrape())


@cli.command()
@click.argument('url')
@click.option('--interval', '-i', default=60, type=int,
              help='Check interval in seconds')
@click.option('--condition', '-c', help='Alert condition (e.g., "price < 100")')
@click.option('--alert-file', '-a', type=click.Path(),
              help='File to append alerts')
@click.option('--max-runs', default=0, type=int,
              help='Maximum number of checks (0 = infinite)')
@click.pass_context
def monitor(ctx, url, interval, condition, alert_file, max_runs):
    """
    Monitor a URL for changes

    Examples:

      # Monitor every 5 minutes
      ./scraper_agent.py monitor https://example.com -i 300

      # Alert on price changes
      ./scraper_agent.py monitor https://example.com/product \\
        --condition "price < 50" \\
        --alert-file price_alerts.txt

      # Run 10 times then exit
      ./scraper_agent.py monitor https://example.com --max-runs 10
    """
    # Ensure Comet is running
    if not ensure_comet_running():
        click.echo("\n❌ Could not start Comet. Please check installation.")
        return

    async def run_monitor():
        async with get_comet_tools() as chrome_tools:
            additional_instructions = f"""
            **Monitoring Task:**
            - Check {url} every {interval} seconds
            - Extract current state/values
            """

            if condition:
                additional_instructions += f"\n- Alert if: {condition}"

            agent = get_agent(ctx, additional_instructions)
            agent.tools = [chrome_tools]

            click.echo(f"\n👀 Monitoring: {url}")
            click.echo(f"⏱️  Interval: {interval}s")
            if condition:
                click.echo(f"🚨 Alert on: {condition}")
            click.echo("\nPress Ctrl+C to stop\n")

            run_count = 0
            previous_content = None

            try:
                while True:
                    run_count += 1
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    click.echo(f"[{timestamp}] Check #{run_count}")

                    # Extract current state
                    prompt = f"Go to {url} and extract current data"
                    if condition:
                        prompt += f". Check if: {condition}"

                    result = await agent.arun(prompt, stream=False)
                    current_content = result.content

                    # Check for changes
                    if previous_content and current_content != previous_content:
                        click.echo(f"  ⚠️  CHANGE DETECTED!")

                        if alert_file:
                            alert_msg = f"[{timestamp}] Change detected at {url}\n{current_content}\n\n"
                            Path(alert_file).write_text(
                                Path(alert_file).read_text() + alert_msg
                                if Path(alert_file).exists()
                                else alert_msg
                            )
                            click.echo(f"  💾 Alert saved to: {alert_file}")
                    else:
                        click.echo(f"  ✓ No changes")

                    previous_content = current_content

                    # Check max runs
                    if max_runs > 0 and run_count >= max_runs:
                        click.echo(f"\n✅ Completed {max_runs} checks")
                        break

                    # Wait for next interval
                    await asyncio.sleep(interval)

            except KeyboardInterrupt:
                click.echo(f"\n\n✋ Monitoring stopped after {run_count} checks")

    asyncio.run(run_monitor())


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--summarize/--no-summarize', default=True,
              help='Generate LLM summary')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for analysis')
@click.pass_context
def analyze(ctx, file, summarize, output):
    """
    Analyze scraped data with LLM

    Examples:

      # Analyze and summarize
      ./scraper_agent.py analyze data.json

      # Save analysis to file
      ./scraper_agent.py analyze data.json -o analysis.md

      # Just show data (no summary)
      ./scraper_agent.py analyze data.json --no-summarize
    """
    async def run_analyze():
        # Load data
        data_path = Path(file)
        content = data_path.read_text()

        if not summarize:
            click.echo(content)
            return

        # Create agent without Chrome tools (just LLM)
        agent = Agent(
            name="Data Analyzer",
            model=Ollama(
                id=ctx.obj['model'],
                options={"num_ctx": 198000}
            ),
            instructions="""
            You are a data analysis expert.

            Analyze the provided data and create a comprehensive summary:
            - Key findings and patterns
            - Statistical insights
            - Anomalies or interesting observations
            - Actionable recommendations

            Format your analysis in clear Markdown with sections and bullet points.
            """,
            markdown=True,
            debug_mode=ctx.obj['debug'],
        )

        click.echo(f"\n📊 Analyzing: {file}\n")

        prompt = f"Analyze this scraped data and provide insights:\n\n{content}"
        result = await agent.arun(prompt, stream=True)

        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result.content)
            click.echo(f"\n✅ Analysis saved to: {output_path}")

    asyncio.run(run_analyze())


@cli.command()
@click.pass_context
def chat(ctx):
    """
    Interactive chat mode for ad-hoc scraping

    Example:
      ./scraper_agent.py chat
      > Go to portfolio123.com and extract the taxonomy categories
    """
    # Ensure Comet is running
    if not ensure_comet_running():
        click.echo("\n❌ Could not start Comet. Please check installation.")
        return

    async def run_chat():
        async with get_comet_tools() as chrome_tools:
            agent = get_agent(ctx)
            agent.tools = [chrome_tools]

            click.echo("\n🕷️  Web Scraping Agent - Interactive Mode")
            click.echo("=" * 50)
            click.echo("\nTell me what to scrape, and I'll handle it!")
            click.echo("Type 'exit' or 'quit' to stop.\n")

            while True:
                try:
                    user_input = click.prompt('>', type=str, prompt_suffix=' ')

                    if user_input.lower() in ['exit', 'quit', 'q']:
                        click.echo("\n👋 Goodbye!")
                        break

                    # Run agent
                    await agent.aprint_response(user_input, stream=True)
                    click.echo()  # Blank line after response

                except (EOFError, KeyboardInterrupt):
                    click.echo("\n\n👋 Goodbye!")
                    break

    asyncio.run(run_chat())


@cli.command()
@click.argument('url', required=False)
@click.option('--prompt', '-p', help='Analysis prompt (what to look for)')
@click.option('--output', '-o', type=click.Path(),
              help='Save screenshot to file')
@click.option('--analyze/--no-analyze', default=True,
              help='Analyze screenshot with vision model')
@click.pass_context
def screenshot(ctx, url, prompt, output, analyze):
    """
    Take screenshot and analyze with Qwen3 VL model

    Examples:

      # Take screenshot and analyze current page
      ./scraper_agent.py screenshot

      # Navigate to URL then screenshot
      ./scraper_agent.py screenshot https://portfolio123.com/app/taxonomy

      # Custom analysis prompt
      ./scraper_agent.py screenshot https://example.com \\
        --prompt "Identify all form fields and their labels"

      # Just save screenshot without analysis
      ./scraper_agent.py screenshot https://example.com \\
        -o page.png --no-analyze
    """
    # Ensure Comet is running
    if not ensure_comet_running():
        click.echo("\n❌ Could not start Comet. Please check installation.")
        return

    async def run_screenshot():
        async with get_comet_tools() as chrome_tools:
            # Navigate if URL provided
            if url:
                click.echo(f"\n📸 Opening new tab: {url}")
                nav_agent = Agent(
                    model=Ollama(id="qwen3-vl:235b-instruct-cloud", options={"num_ctx": 256000}),
                    instructions="Open URLs in new tabs using new_page tool",
                    markdown=False,
                    debug_mode=False
                )
                nav_agent.tools = [chrome_tools]
                await nav_agent.arun(f"Open {url} in a new tab using new_page tool", stream=False)
                click.echo("✅ New tab opened")
            else:
                click.echo("\n📸 Analyzing current Chrome page...")

            # Take screenshot using simplified agent
            click.echo("📸 Taking screenshot...")
            import tempfile
            temp_path = Path(tempfile.mktemp(suffix='.png'))

            # Use vision-capable model for screenshot capture
            simple_agent = Agent(
                model=Ollama(id="qwen3-vl:235b-instruct-cloud", options={"num_ctx": 256000}),
                instructions="Call take_screenshot with the provided file path",
                markdown=False,
                debug_mode=False
            )
            simple_agent.tools = [chrome_tools]

            try:
                await simple_agent.arun(f"Take a screenshot and save it to: {temp_path}", stream=False)
                click.echo("✅ Screenshot captured")
            except Exception as e:
                click.echo(f"⚠️  Screenshot error: {e}")
                return

            # Read the screenshot file
            screenshot_bytes = None
            if temp_path.exists():
                screenshot_bytes = temp_path.read_bytes()

                # Save if output specified
                if output:
                    output_path = Path(output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(screenshot_bytes)
                    click.echo(f"💾 Saved to: {output_path}")

                # Clean up temp file
                temp_path.unlink()

            # Analyze with vision model if requested
            if analyze and screenshot_bytes:
                click.echo("\n🔍 Analyzing screenshot with Qwen3 VL model...")

                # Analysis prompt
                analysis_prompt = prompt or "Analyze this screenshot thoroughly. Describe the layout, identify all UI elements, extract any visible text or data, and provide structured insights."

                click.echo(f"📋 Analysis: {analysis_prompt}\n")

                # Use Agno's native vision support
                try:
                    # Create vision agent with Qwen3 VL
                    vision_agent = Agent(
                        model=Ollama(id="qwen3-vl:235b-instruct-cloud", options={"num_ctx": 256000}),
                        instructions="""You are a visual analysis expert.

Analyze screenshots and provide detailed insights:
- Overall page layout and structure
- UI components (buttons, forms, menus, navigation)
- Text content, headings, and labels
- Visual hierarchy and design patterns
- Interactive elements and their purposes
- Data tables, lists, or structured content
- Colors, branding, and visual style

Extract any visible data in structured format when possible.
Provide comprehensive analysis in clear markdown format.""",
                        markdown=True,
                        debug_mode=ctx.obj['debug'],
                    )

                    # Use Agno's native Image support
                    screenshot_image = Image(content=screenshot_bytes)

                    click.echo("=" * 80)
                    vision_agent.print_response(
                        analysis_prompt,
                        images=[screenshot_image],
                        stream=True
                    )
                    click.echo("\n" + "=" * 80)

                except Exception as e:
                    click.echo(f"\n⚠️  Vision analysis failed: {str(e)}")
                    click.echo("    The model may not support vision or there was a server error")

            elif analyze and not screenshot_bytes:
                click.echo("\n⚠️  Could not extract screenshot data for analysis")
                click.echo("    Screenshot may have been taken but data extraction failed")

    asyncio.run(run_screenshot())


@cli.command()
def start_comet():
    """Launch Comet with your default profile and remote debugging enabled"""
    # Check if Comet is already running
    if is_comet_running():
        click.echo("✅ Comet is already running with remote debugging")
        click.echo(f"   Connected to: {COMET_URL}")
        return

    click.echo("🚀 Launching Comet with your default profile and remote debugging...")
    click.echo("   This will use your actual default profile with all cookies and logins")

    if not ensure_comet_running():
        click.echo("❌ Failed to launch Comet")
        click.echo("\n💡 You can start Comet manually:")
        click.echo("   ./scraper_agent.py setup")
        sys.exit(1)

    click.echo(f"\n💡 You can now run scraping commands:")
    click.echo("   ./scraper_agent.py scrape https://example.com")


@cli.command()
def setup():
    """
    Show setup instructions for Comet + MCP
    """
    instructions = """
╔══════════════════════════════════════════════════════════════════════╗
║                   Comet Browser DevTools MCP Setup                   ║
╚══════════════════════════════════════════════════════════════════════╝

1️⃣  Start Comet with Remote Debugging (uses your default profile with cookies/logins)

   macOS:
   /Applications/Comet.app/Contents/MacOS/Comet \\
     --remote-debugging-port=9223

   Linux:
   comet --remote-debugging-port=9223

   Or use the built-in launcher:
   ./scraper_agent.py start-comet

2️⃣  Verify Comet is Running

   Open: http://127.0.0.1:9223/json
   You should see a JSON list of open tabs

3️⃣  Configure MCP Server (if needed)

   Add to your .mcp.json:
   {
     "mcpServers": {
       "chrome-devtools": {
         "command": "npx",
         "args": [
           "chrome-devtools-mcp@latest",
           "--browser-url=http://127.0.0.1:9223"
         ]
       }
     }
   }

4️⃣  Test the Agent

   ./scraper_agent.py scrape https://example.com

5️⃣  Interactive Mode

   ./scraper_agent.py chat
   > Go to portfolio123.com and show me the page structure

📚 Documentation: https://github.com/modelcontextprotocol/servers
    """
    click.echo(instructions)


if __name__ == "__main__":
    cli()
