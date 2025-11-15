# CLI Patterns Reference

**Preferred Framework**: Click (https://click.palletsprojects.com/)

Use Click for all CLI scripts to ensure consistency, proper argument handling, and professional help output.

## Why Click?

✅ **Consistency**: Standardized across all skills
✅ **Professional**: Auto-generated help, argument validation
✅ **Composability**: Command groups, subcommands, shared contexts
✅ **Maintainability**: Declarative argument definitions
✅ **Testing**: Easy to test with Click's CliRunner

## Basic Click Structure

```python
#!/usr/bin/env python3
"""
Script Name - Brief Description

Usage:
    script.py command <args>

Examples:
    script.py process file.txt
    script.py analyze --depth 3
"""

import click

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(input_file, output, verbose):
    """Process INPUT_FILE and generate output.
    
    This command processes the input file and optionally
    saves results to an output file.
    """
    if verbose:
        click.echo(f"Processing {input_file}...")
    
    # Your logic here
    result = process_file(input_file)
    
    if output:
        with open(output, 'w') as f:
            f.write(result)
        click.echo(f"✅ Saved to {output}")
    else:
        click.echo(result)


if __name__ == "__main__":
    main()
```

## Command Groups (Multi-Command CLI)

```python
#!/usr/bin/env python3
"""
Multi-Command CLI Example

Usage:
    cli.py query <args>
    cli.py analyze <args>
    cli.py export <args>
"""

import click

@click.group()
@click.pass_context
def cli(ctx):
    """Main CLI with multiple commands.
    
    A tool for querying, analyzing, and exporting data.
    """
    # Shared setup (optional)
    ctx.obj = {'config': load_config()}


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['json', 'yaml', 'text']), default='json')
@click.pass_context
def query(ctx, file_path, format):
    """Query data from FILE_PATH.
    
    Reads the file and returns data in specified format.
    """
    config = ctx.obj['config']
    result = perform_query(file_path, format, config)
    click.echo(result)


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--depth', type=int, default=1, help='Analysis depth')
@click.pass_context
def analyze(ctx, directory, depth):
    """Analyze contents of DIRECTORY.
    
    Performs deep analysis up to specified depth.
    """
    result = perform_analysis(directory, depth)
    click.echo(result)


if __name__ == "__main__":
    cli()
```

## Common Patterns

### File Paths
```python
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), help='Output path')
```

### Choices (Enums)
```python
@click.option('--format', 
              type=click.Choice(['json', 'yaml', 'csv']), 
              default='json',
              help='Output format')
```

### Flags
```python
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--dry-run', is_flag=True, help='Show what would be done')
```

### Multiple Values
```python
@click.option('--tag', multiple=True, help='Add tag (can be used multiple times)')
```

### Counting
```python
@click.option('--verbose', '-v', count=True, help='Verbosity level (-v, -vv, -vvv)')
```

### Prompts
```python
@click.option('--name', prompt='Enter name', help='User name')
@click.option('--password', prompt=True, hide_input=True, help='Password')
```

### Confirmation
```python
@click.confirmation_option(prompt='Are you sure you want to delete?')
```

## Error Handling

```python
@click.command()
def process():
    """Process data with proper error handling."""
    try:
        result = do_something()
        click.echo(f"✅ Success: {result}")
    except FileNotFoundError as e:
        click.echo(f"❌ Error: File not found - {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        raise click.Abort()
```

## Output Styling

```python
# Colors
click.echo(click.style('Success!', fg='green', bold=True))
click.echo(click.style('Warning', fg='yellow'))
click.echo(click.style('Error', fg='red'))

# Progress bars
with click.progressbar(items, label='Processing') as bar:
    for item in bar:
        process(item)

# Spinners (via click-spinner)
with click.spinner():
    expensive_operation()
```

## Testing Pattern

```python
# test_cli.py
from click.testing import CliRunner
from my_cli import cli

def test_query_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['query', 'test.txt', '--format', 'json'])
    
    assert result.exit_code == 0
    assert 'success' in result.output


def test_invalid_format():
    runner = CliRunner()
    result = runner.invoke(cli, ['query', 'test.txt', '--format', 'invalid'])
    
    assert result.exit_code != 0
```

## Template: Minimal CLI

```python
#!/usr/bin/env python3
"""Minimal Click CLI Template"""

import click

@click.command()
@click.argument('input')
@click.option('--output', '-o', help='Output file')
def main(input, output):
    """Process INPUT and optionally save to OUTPUT."""
    result = f"Processed: {input}"
    
    if output:
        with open(output, 'w') as f:
            f.write(result)
    else:
        click.echo(result)


if __name__ == "__main__":
    main()
```

## Template: Command Group

```python
#!/usr/bin/env python3
"""Command Group Template"""

import click

@click.group()
def cli():
    """Multi-command CLI."""
    pass


@cli.command()
@click.argument('name')
def greet(name):
    """Greet NAME."""
    click.echo(f"Hello, {name}!")


@cli.command()
@click.argument('x', type=int)
@click.argument('y', type=int)
def add(x, y):
    """Add X and Y."""
    click.echo(f"{x} + {y} = {x + y}")


if __name__ == "__main__":
    cli()
```

## Best Practices

1. **Always use `@click.command()` or `@click.group()`** - Never parse `sys.argv` manually
2. **Provide help text** - For commands, arguments, and options
3. **Use type validation** - `type=click.Path()`, `type=int`, `type=click.Choice()`
4. **Return exit codes** - `raise click.Abort()` for errors
5. **Use `click.echo()`** - Instead of `print()` for better test compatibility
6. **Add examples in docstrings** - Show users how to use commands
7. **Test with CliRunner** - Easy to test Click apps

## Dependencies

Add to your script dependencies:
```python
# /// script
# dependencies = [
#   "click>=8.0",
# ]
# ///
```

Or in `pyproject.toml`:
```toml
[project]
dependencies = [
    "click>=8.0",
]
```

## Anti-Patterns

❌ **Manual argument parsing**
```python
if len(sys.argv) < 2:
    print("Usage: script.py <file>")
```

❌ **String-based argument handling**
```python
if '--verbose' in sys.argv:
    verbose = True
```

❌ **Custom help messages**
```python
if args[0] == '--help':
    print("Usage: ...")
```

✅ **Use Click decorators instead** - All these patterns are handled automatically by Click.

## Migration from Manual Parsing

**Before (manual parsing)**:
```python
import sys

if len(sys.argv) < 2:
    print("Usage: script.py <file> [--output <path>]")
    sys.exit(1)

file_path = sys.argv[1]
output = sys.argv[3] if '--output' in sys.argv else None
```

**After (Click)**:
```python
import click

@click.command()
@click.argument('file_path')
@click.option('--output', '-o', help='Output path')
def main(file_path, output):
    """Process FILE_PATH."""
    # Your logic here
```

## Integration with Skill Scripts

For skill scripts in `scripts/` directory:

```python
#!/usr/bin/env python3
"""
Skill CLI Script

This script provides command-line interface for skill functions.
"""

import sys
from pathlib import Path

# Add skill modules to path if needed
sys.path.insert(0, str(Path(__file__).parent))

import click
from skill_module import process_data, analyze, export


@click.group()
def cli():
    """Skill command-line interface."""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def process(input_file):
    """Process INPUT_FILE."""
    result = process_data(input_file)
    click.echo(result)


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--depth', type=int, default=3)
def analyze(directory, depth):
    """Analyze DIRECTORY."""
    result = analyze(directory, depth)
    click.echo(result)


if __name__ == "__main__":
    cli()
```

---

**Remember**: Click provides professional, consistent, and testable CLIs with minimal code. Always prefer Click over manual argument parsing.

