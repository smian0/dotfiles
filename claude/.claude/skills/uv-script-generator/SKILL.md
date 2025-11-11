---
name: uv-script-generator
description: Use when user requests a Python script using uv for dependency management. Creates single-file scripts with inline metadata following PEP 723.
---

# UV Script Generator

Generate Python scripts that use uv for automatic dependency management with inline metadata (PEP 723 format).

## When to Use This Skill

Use this skill when the user requests:
- "Create a uv script that..."
- "Generate a Python script with uv dependencies..."
- "Make a standalone Python script for..."
- "Create a CLI tool that..."
- Any Python script that should be executable with `uv run`

**Default to Click CLI pattern** for any script that accepts arguments or options.

## Reference Documentation

For complete uv script capabilities, load:
- [uv Single-File Scripts Reference](./references/uv-single-file-scripts.md)

## Script Generation Process

### 1. Gather Requirements

Ask the user:
- **Purpose**: What should the script do?
- **Dependencies**: What packages are needed? (if any)
- **Python version**: Specific version required? (default: system Python)
- **Executable**: Should it have a shebang and be executable?

### 2. Generate the Script

Create the script with this structure:

**For CLI scripts with Click (RECOMMENDED):**
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "click",
#   "package-name>=version",
# ]
# requires-python = ">=3.12"
# ///

import click

@click.command()
@click.option('--option', help='Description')
@click.argument('arg')
def main(option, arg):
    """Script description here"""
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

**For multi-command CLI scripts with Click:**
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# requires-python = ">=3.12"
# ///

import click

@click.group()
def cli():
    """Multi-command script description"""
    pass

@cli.command()
@click.argument('input')
def process(input):
    """Process command"""
    pass

@cli.command()
def analyze():
    """Analyze command"""
    pass

if __name__ == "__main__":
    cli()
```

**For simple scripts without CLI:**
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["package-name"]
# requires-python = ">=3.12"
# ///

def main():
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

### 3. Key Formatting Rules

**Inline Metadata Block:**
- Must start with `# /// script`
- Must end with `# ///`
- Use valid TOML syntax inside the block
- Dependencies are a list of strings
- Each dependency can include version constraints

**Shebang:**
- Use `#!/usr/bin/env -S uv run --script` for executable scripts
- Place at the very first line
- Makes script executable without typing `uv run`

**Dependencies:**
- Format: `"package-name"` or `"package-name>=version"` or `"package-name>1,<2"`
- Local projects: `"package-name @ file:///absolute/path/to/project"`
- Each dependency on its own line in the list
- Use precise version constraints when reproducibility matters

**Python Version:**
- Optional field: `requires-python = ">=3.12"`
- Use when script needs specific Python features

### 4. After Generation

**Make executable (if requested):**
```bash
chmod +x script_name.py
```

**Show usage:**
```bash
# Run with uv
uv run script_name.py

# Or run directly if executable
./script_name.py
```

## Common Patterns

### Web Scraping CLI Script
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "click",
#   "requests<3",
#   "beautifulsoup4",
# ]
# requires-python = ">=3.12"
# ///

import click
import requests
from bs4 import BeautifulSoup

@click.command()
@click.argument('url')
@click.option('--selector', default='p', help='CSS selector to extract')
def scrape(url, selector):
    """Scrape content from URL using CSS selector"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    elements = soup.select(selector)
    for el in elements:
        click.echo(el.get_text())

if __name__ == "__main__":
    scrape()
```

### CLI Tool with Rich Output
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "click",
#   "rich",
# ]
# requires-python = ">=3.12"
# ///

import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """CLI tool with rich output"""
    pass

@cli.command()
@click.argument('name')
def greet(name):
    """Greet someone"""
    console.print(f"[bold green]Hello {name}![/bold green]")

@cli.command()
@click.argument('message')
def display(message):
    """Display formatted message"""
    console.print(f"[cyan]{message}[/cyan]")

if __name__ == "__main__":
    cli()
```

### Data Processing CLI Script
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "click",
#   "pandas>=2.0",
#   "numpy",
# ]
# requires-python = ">=3.12"
# ///

import click
import pandas as pd
import numpy as np

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), help='Output file path')
@click.option('--format', type=click.Choice(['csv', 'json']), default='csv')
def process(input_file, output, format):
    """Process data file and save results"""
    df = pd.read_csv(input_file)
    # Process data
    result = df.describe()

    if output:
        if format == 'csv':
            result.to_csv(output)
        else:
            result.to_json(output)
        click.echo(f"Results saved to {output}")
    else:
        click.echo(result)

if __name__ == "__main__":
    process()
```

## CLI Organization with Click

### When to Use Click Command Groups

Use Click command groups when your script needs:
- Multiple related commands (like git: commit, push, pull)
- Subcommands with different options
- Shared configuration across commands
- Professional CLI organization

### Single Command Pattern

For scripts with one main action:
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# requires-python = ">=3.12"
# ///

import click

@click.command()
@click.argument('input')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--output', '-o', type=click.Path(), help='Output file')
def process(input, verbose, output):
    """Process input and optionally save to output file"""
    if verbose:
        click.echo(f"Processing {input}...")
    # Implementation
    result = f"Processed: {input}"

    if output:
        with open(output, 'w') as f:
            f.write(result)
        click.echo(f"Saved to {output}")
    else:
        click.echo(result)

if __name__ == "__main__":
    process()
```

### Command Group Pattern

For scripts with multiple commands:
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["click"]
# requires-python = ">=3.12"
# ///

import click

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.pass_context
def cli(ctx, debug):
    """Multi-command CLI tool"""
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug

@cli.command()
@click.argument('source')
@click.pass_context
def fetch(ctx, source):
    """Fetch data from source"""
    if ctx.obj['debug']:
        click.echo(f"Debug: Fetching from {source}")
    # Implementation
    click.echo(f"Fetched data from {source}")

@cli.command()
@click.argument('data')
@click.option('--format', type=click.Choice(['json', 'csv']), default='json')
@click.pass_context
def export(ctx, data, format):
    """Export data in specified format"""
    if ctx.obj['debug']:
        click.echo(f"Debug: Exporting as {format}")
    # Implementation
    click.echo(f"Exported {data} as {format}")

if __name__ == "__main__":
    cli()
```

### Naming Convention for CLI Scripts

Use `_cli.py` suffix for scripts with CLI interfaces:
```bash
# Good - immediately recognizable as CLI scripts
data_processor_cli.py
web_scraper_cli.py
file_converter_cli.py

# For simple non-CLI utilities
calculate_stats.py
parse_config.py
```

**Usage:**
```bash
# Single command
./data_processor_cli.py input.txt --output result.txt

# Command groups
./web_scraper_cli.py fetch https://example.com
./web_scraper_cli.py export data.json --format csv
```

### Click Features Reference

**Arguments vs Options:**
- `@click.argument()` - Required positional parameters
- `@click.option()` - Optional flags and values

**Common Option Types:**
```python
@click.option('--count', type=int, default=1, help='Number of times')
@click.option('--name', prompt='Your name', help='User name')
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.option('--format', type=click.Choice(['json', 'xml']), default='json')
@click.option('--file', type=click.Path(exists=True), help='Input file')
```

**Passing Context:**
- `@click.pass_context` - Access Click context (for shared data)
- `@click.pass_obj` - Pass custom object between commands

**Built-in Utilities:**
- `click.echo()` - Print output (better than print)
- `click.style()` - Colored output
- `click.confirm()` - Yes/No prompts
- `click.progressbar()` - Progress bars

## Advanced Features

### Local Project Dependencies
For scripts that depend on local projects or packages in development:
```python
# /// script
# dependencies = [
#   "agno @ file:///Users/username/projects/agno",
#   "requests>=2.31",
# ]
# ///
```
**Note:** Use absolute paths for local dependencies. The path should point to the project root containing `pyproject.toml` or `setup.py`.

### Alternative Package Index
If using a private or alternative PyPI index, add to metadata:
```python
# /// script
# dependencies = ["custom-package"]
# [[tool.uv.index]]
# url = "https://example.com/simple"
# ///
```

### Advanced Dependency Sources
Configure specific sources for dependencies:
```python
# /// script
# dependencies = [
#   "httpx",
#   "my-private-package",
# ]
#
# [tool.uv.sources]
# my-private-package = { git = "https://github.com/org/repo", tag = "v1.0.0" }
# ///
```

**Source types supported:**
- Git: `{ git = "https://...", tag = "v1.0" }` or `{ git = "...", rev = "abc123" }`
- Path: `{ path = "/absolute/path" }` or `{ path = "relative/path" }`
- URL: `{ url = "https://example.com/package.whl" }`

### Reproducibility with exclude-newer
Lock dependencies to packages released before a specific date:
```python
# /// script
# dependencies = ["requests"]
# [tool.uv]
# exclude-newer = "2024-01-01T00:00:00Z"
# ///
```

### Lock Files
Inform user they can create a lock file for reproducibility:
```bash
uv lock --script script_name.py
```
This creates `script_name.py.lock` adjacent to the script.

**Lock file enforcement:**
```bash
# Verify lock file is up-to-date
uv lock --script script_name.py --check

# Run with locked dependencies only
uv run --locked script_name.py

# Assert lock file exists without checking freshness
uv run --frozen script_name.py
```

### Environment Variables
Load environment variables from a `.env` file:
```bash
uv run --env-file .env script_name.py
```

Or specify in the script to always load:
```python
# /// script
# dependencies = ["python-dotenv"]
# ///

from dotenv import load_dotenv
load_dotenv()
```

### Editable Local Dependencies
For development workflows with local packages:
```bash
# Run with editable install
uv run --with-editable ./local-package script_name.py
```

Or in metadata:
```python
# /// script
# dependencies = [
#   "mypackage @ file:///path/to/package",
# ]
# ///
```

### Requirements Files
Use existing requirements.txt files:
```bash
uv run --with-requirements requirements.txt script_name.py
```

### Isolated Execution
Run in completely isolated environment (ignores project):
```bash
uv run --isolated script_name.py
```

### GUI Scripts (Windows)
For Windows GUI applications, use `.pyw` extension:
```python
# script.pyw
#!/usr/bin/env -S uv run --gui-script
# /// script
# dependencies = ["tkinter"]
# ///

import tkinter as tk
# GUI code...
```

Or run explicitly:
```bash
uv run --gui-script script.pyw
```

### Initialize Scripts with uv
Generate a new script template:
```bash
# Basic script
uv init --script my_script.py --python 3.12

# With name and description
uv init --script my_tool.py --name "My Tool" --description "Does something useful"
```

## Workflow Example

**User request:**
"Create a script that fetches weather data from an API and displays it nicely"

**Your response:**
1. Confirm details: "I'll create a uv CLI script using `click` for the interface, `requests` for API calls, and `rich` for display. Should it support multiple cities as commands?"
2. Generate the complete script with Click CLI pattern and proper inline metadata
3. Use Write tool to create `weather_cli.py` (note the `_cli.py` suffix)
4. Show usage examples:
   ```bash
   # Make executable
   chmod +x weather_cli.py

   # Get help
   ./weather_cli.py --help

   # Fetch weather
   ./weather_cli.py fetch "San Francisco"

   # Or with uv run
   uv run weather_cli.py fetch "New York" --format json
   ```
5. Explain that uv will automatically create the environment and install dependencies on first run

## Important Notes

- **Use Click for CLI scripts** - Provides professional argument parsing and help text
- **Use `_cli.py` suffix** for scripts with CLI interfaces
- **Always include the inline metadata block** for scripts with dependencies
- **Always use proper TOML syntax** in the metadata block
- **Place shebang first** if making executable
- **Include `click` in dependencies** for any script with CLI arguments
- **Use `if __name__ == "__main__":` pattern** for proper script structure
- **Test commands are copy-pasteable** - verify syntax before showing to user

## Tips & Best Practices

### 1. Running Scripts in Projects
If running a script in a directory with `pyproject.toml`, uv will install the project first. To skip this:
```bash
uv run --no-project script.py
```

### 2. Quick Testing Without Metadata
For quick testing without adding to metadata:
```bash
uv run --with requests --with rich script.py
```

### 3. Combining Flags
Multiple runtime options can be combined:
```bash
uv run --isolated --env-file .env --with-requirements deps.txt script.py
```

### 4. Version Constraints Best Practices
- Use `>=` for libraries you control: `"mylib>=1.2"`
- Use `<` for upper bounds: `"requests>=2.28,<3"`
- Pin exact versions for reproducibility: `"numpy==1.24.0"`
- For local dev, use file paths: `"mypackage @ file:///absolute/path"`

### 5. Script Arguments
Pass arguments after the script name:
```bash
uv run script.py --arg1 value1 --arg2 value2
```

### 6. Python Version Management
Specify Python version at runtime (overrides metadata):
```bash
uv run --python 3.11 script.py
```

### 7. Module Execution
Run a script as a module:
```bash
uv run -m script_name
```

### 8. Caching
uv automatically caches environments. For a fresh environment:
```bash
uv cache clean
uv run script.py
```

## Skip This Skill If

- User wants a full Python project (not a single-file script)
- User needs a uv project with `pyproject.toml` (different workflow)
- Script is part of a larger codebase (use regular imports instead)
