# UV Script Generator Skill

A Claude Code skill for generating Python single-file scripts with uv dependency management.

## What It Does

This skill enables Claude to create standalone Python scripts that use [uv](https://docs.astral.sh/uv/) for automatic dependency management. The generated scripts include inline metadata (PEP 723 format) that declares dependencies, making them instantly runnable without manual environment setup.

## When It Triggers

The skill activates when you ask for:
- "Create a uv script that..."
- "Generate a Python script with uv dependencies..."
- "Make a standalone Python script for..."

## Features

- ✅ Generates scripts with proper PEP 723 inline metadata
- ✅ Includes shebang for executable scripts
- ✅ Handles dependency version constraints
- ✅ Supports Python version requirements
- ✅ Local project dependencies with file:// paths
- ✅ Lock file creation and enforcement (--locked, --frozen)
- ✅ Environment variable loading from .env files
- ✅ Alternative package indexes and custom sources
- ✅ Git dependencies and editable installs
- ✅ GUI script support (Windows .pyw files)
- ✅ Isolated and project-aware execution modes
- ✅ Provides common patterns (web scraping, CLI tools, data processing)
- ✅ Best practices and optimization tips

## Example Usage

**Request:**
```
Create a uv script that fetches JSON from an API and pretty-prints it
```

**Generated:**
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

def main():
    resp = requests.get("https://api.example.com/data")
    data = resp.json()
    pprint(data)

if __name__ == "__main__":
    main()
```

**Run it:**
```bash
chmod +x script.py
./script.py
# or
uv run script.py
```

## What's Included

- **SKILL.md**: Complete instructions for generating uv scripts
- **references/**: uv single-file scripts documentation

## Benefits of UV Scripts

1. **No manual environment management** - uv creates and manages environments automatically
2. **Portable** - Scripts declare their own dependencies
3. **Fast** - uv's Rust-based resolver is extremely quick
4. **Reproducible** - Optional lock files for exact dependency versions
5. **Simple** - One file, no boilerplate

## Related Tools

- [uv](https://docs.astral.sh/uv/) - An extremely fast Python package installer and resolver
- [PEP 723](https://peps.python.org/pep-0723/) - Inline script metadata standard

---
Last Updated: 2025-10-19
