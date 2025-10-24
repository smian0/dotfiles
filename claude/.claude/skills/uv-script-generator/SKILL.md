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
- Any Python script that should be executable with `uv run`

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

**For scripts with dependencies:**
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "package-name>=version",
#   "another-package",
# ]
# requires-python = ">=3.12"
# ///

# Script code here
import package_name

def main():
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

**For scripts without dependencies:**
```python
#!/usr/bin/env -S uv run --script

# Script code here
import sys

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

### Web Scraping Script
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests<3",
#   "beautifulsoup4",
# ]
# ///

import requests
from bs4 import BeautifulSoup

def main():
    # Implementation
    pass

if __name__ == "__main__":
    main()
```

### CLI Tool with Rich Output
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "rich",
#   "typer",
# ]
# requires-python = ">=3.10"
# ///

from rich.console import Console
import typer

app = typer.Typer()
console = Console()

@app.command()
def main(name: str):
    console.print(f"[bold green]Hello {name}![/bold green]")

if __name__ == "__main__":
    app()
```

### Data Processing Script
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "pandas>=2.0",
#   "numpy",
# ]
# ///

import pandas as pd
import numpy as np

def main():
    # Load and process data
    pass

if __name__ == "__main__":
    main()
```

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
1. Confirm dependencies: "I'll create a uv script using `requests` for API calls and `rich` for display. Should it be executable?"
2. Generate the complete script with proper inline metadata
3. Use Write tool to create the file
4. Show how to run it: `uv run weather.py` or `chmod +x weather.py && ./weather.py`
5. Explain that uv will automatically create the environment and install dependencies

## Important Notes

- **Always include the inline metadata block** for scripts with dependencies
- **Always use proper TOML syntax** in the metadata block
- **Place shebang first** if making executable
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
