---
name: markdown-query
description: Advanced markdown processing with MQ-style selectors, Obsidian features, and intelligent linting. Use for querying markdown files, extracting structured data, analyzing vaults, and fixing common issues.
---

# Markdown Query Skill

High-performance markdown processing with MQ selectors, Obsidian features, and document linting.

## Quick Start

### Command-Line Interface (Click-based)

```bash
# Query operations
./scripts/mdquery query README.md .h1             # Extract H1 headers
./scripts/mdquery bulk /vault .h2                 # Multi-file queries
./scripts/mdquery outline README.md               # Get document structure

# Obsidian features
./scripts/mdquery wiki note.md                    # Find wiki links
./scripts/mdquery graph /vault                    # Build vault graph

# Linting (with pretty output)
./scripts/mdquery lint file.md                    # Detect issues + summary
./scripts/mdquery fix file.md --types headers,whitespace --dry-run
./scripts/mdquery toc README.md --depth 3         # Generate TOC

# Get help for any command
./scripts/mdquery --help                          # List all commands
./scripts/mdquery query --help                    # Command-specific help
```

### Python API

```python
from .scripts.cli import query, bulk_query, find_wiki_links, lint_document

query("README.md", ".h1")          # Extract H1 headers
bulk_query("/vault", ".h2")        # Multi-file queries
find_wiki_links("note.md")         # Wiki links with aliases
lint_document("file.md")           # Detect issues
```

## Key Functions

**Extraction**: `query()`, `bulk_query()`, `analyze_docs()`, `generate_toc()`, `task_stats()`  
**Obsidian**: `find_wiki_links()`, `build_vault_graph()`, `find_callouts()`, `extract_dataview_fields()`  
**Linting**: `lint_document()`, `auto_fix()`, `validate_spec()`  
**Performance**: `get_performance_stats()`, `clear_cache()`, `bulk_analyze()`

## MQ Selectors

`.h1` `.h2` `.h3` `.h4` `.h5` `.h6` `.code` `.list` `.link` `.link.url` `.link.text` `.table` `.task` `.tag` `.frontmatter`

## Performance

Intelligent caching optimizes for vault size:
- Small (<100 files): Direct queries
- Medium (100-500): Bulk operations with caching  
- Large (500+): Streaming with memory management

```python
# Monitor cache efficiency
stats = get_performance_stats()

# Clear if needed
clear_cache("all")
```

## Common Workflows

### Documentation Analysis
```python
# Get structure overview
analyze_docs("/docs")

# Generate TOC for navigation
generate_toc("README.md", max_depth=3)

# Check task completion
task_stats("/project")
```

### Vault Management
```python
# Find all wiki links
bulk_query("/vault", ".link")

# Analyze connections
graph = build_vault_graph("/vault")

# Find cross-references
find_cross_references("/vault", "important-topic")
```

### Content Cleanup
```python
# Lint all markdown files
for md_file in Path(".").rglob("*.md"):
    issues = lint_document(str(md_file))
    if issues["counts"]["auto_fixable"] > 0:
        auto_fix(str(md_file))
```

## Implementation

**CLI Script**: `scripts/mdquery` - Click-based command-line interface with:
- Professional help system (`--help` on any command)
- Type validation (file paths, choices, integers)
- Pretty output for lint and stats
- 14 commands covering all functionality

**Core engines** in `scripts/`:
- `mdquery` - Command-line executable (main interface)
- `cli.py` - Python API functions
- `__init__.py` - Package initialization
- `core.py` - Shared patterns and utilities
- `mq_engine.py` - MQ-style selector implementation
- `obsidian_engine.py` - Obsidian features (wiki links, embeds, etc.)
- `lint_engine.py` - Document linting and auto-fixing
- `spec_engine.py` - Specification validation
- `performance_engine.py` - Caching and optimization

Run `./scripts/mdquery help` for complete CLI reference

## References

Load these for detailed guidance:

- [mq-selectors.md](./references/mq-selectors.md) - Complete selector syntax and query patterns
- [obsidian-features.md](./references/obsidian-features.md) - Wiki links, embeds, blocks, callouts
- [linting-rules.md](./references/linting-rules.md) - Issue detection and auto-fix capabilities
- [performance-tips.md](./references/performance-tips.md) - Caching strategies and optimization
- [example-queries.md](./assets/example-queries.md) - Common query patterns and workflows

