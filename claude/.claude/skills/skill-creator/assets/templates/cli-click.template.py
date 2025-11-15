#!/usr/bin/env python3
"""
{skill_name} CLI - Command-line interface

Usage:
    {skill_name} command <args>

Examples:
    {skill_name} process file.txt
    {skill_name} analyze --verbose
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import click


@click.group()
def cli():
    """{skill_title} command-line interface.
    
    A collection of commands for working with {skill_name}.
    Run '{skill_name} COMMAND --help' for detailed help on any command.
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def process(input_file, output, verbose):
    """Process INPUT_FILE and optionally save results.
    
    Processes the input file and performs transformations.
    
    Examples:
        {skill_name} process data.txt
        {skill_name} process data.txt --output result.txt
        {skill_name} process data.txt -o result.txt -v
    """
    if verbose:
        click.echo(f"📄 Processing {{input_file}}...")
    
    # TODO: Implement your processing logic
    result = f"Processed: {{input_file}}"
    
    if output:
        with open(output, 'w') as f:
            f.write(result)
        if verbose:
            click.echo(f"✅ Saved to {{output}}")
    else:
        click.echo(result)


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--depth', type=int, default=3, help='Analysis depth')
@click.option('--format', type=click.Choice(['json', 'text', 'csv']), default='text', help='Output format')
def analyze(directory, depth, format):
    """Analyze contents of DIRECTORY.
    
    Performs analysis of directory contents up to specified depth.
    
    Examples:
        {skill_name} analyze ./data
        {skill_name} analyze ./data --depth 5
        {skill_name} analyze ./data --format json
    """
    click.echo(f"🔍 Analyzing {{directory}} (depth={{depth}}, format={{format}})")
    
    # TODO: Implement your analysis logic
    result = f"Analysis of {{directory}} complete"
    click.echo(result)


@cli.command()
def info():
    """Display information about this CLI.
    
    Shows version, available commands, and usage examples.
    """
    click.echo(click.style("{skill_title} CLI", fg='green', bold=True))
    click.echo("\nAvailable commands:")
    click.echo("  process  - Process files")
    click.echo("  analyze  - Analyze directories")
    click.echo("  info     - This help message")
    click.echo("\nRun '{skill_name} COMMAND --help' for detailed help")


if __name__ == "__main__":
    cli()

