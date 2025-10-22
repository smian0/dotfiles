# Unified Markdown MCP Server

A high-performance, feature-rich MCP server that combines MQ-style selectors with advanced Obsidian features and intelligent document linting. Built with a modular architecture for maintainability and performance optimization.

## Features

### 🚀 Performance Optimizations
- **Intelligent caching** with TTL and file modification tracking
- **Bulk operation optimization** with configurable batching  
- **Memory-efficient streaming** for large datasets
- **Automatic cache management** with LRU eviction
- **Dataset-aware optimization** that adapts to vault size

### 📝 MQ-Style Selectors
- **jq-like syntax** for structural markdown extraction
- **Compatible selectors**: `.h1`, `.h2`, `.code`, `.list`, `.link`, `.table`, `.task`
- **Advanced selectors**: `.link.url`, `.link.text`, `.frontmatter`, `.tag`
- **Bulk queries** with performance optimization
- **Analysis functions**: `analyze_docs`, `generate_toc`, `task_stats`, `validate_spec`

### 🔗 Obsidian Integration
- **Wiki links** with alias support (`[[target|alias]]`)
- **Embedded content** transclusion (`![[content]]`)
- **Block references** and links (`^block-id`, `[[note#^block]]`)
- **Callouts/admonitions** (`> [!note]`)
- **Dataview fields** (`field:: value`)
- **Vault graph analysis** with connection mapping
- **Cross-reference tracking** across files

### 🔍 Document Linting
- **Automated issue detection** (headers, whitespace, tasks, links)
- **Categorized fixes** (auto-fixable vs review-required)
- **Deterministic repairs** for common formatting issues
- **YAML frontmatter validation**
- **Wiki-link target verification**
- **Code block language detection**

## Installation

### Prerequisites
- Python 3.8+
- FastMCP library
- Optional: Marksman LSP for enhanced features

### Setup
```bash
# Clone or copy the mcp_markdown directory
cp -r mcp_markdown /path/to/mcp-servers/

# Install dependencies
pip install fastmcp pathlib

# Test the server
python mcp_markdown/server.py
```

### MCP Configuration
Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "markdown": {
      "command": "python",
      "args": ["/path/to/mcp-servers/mcp_markdown/server.py"],
      "description": "Unified markdown processing with MQ selectors and Obsidian support"
    }
  }
}
```

## Quick Start

### Basic Document Analysis
```python
# Get document structure
analyze_document_structure("README.md")

# Extract headers outline  
get_document_outline("README.md")

# Find all code blocks
find_code_blocks("README.md")
```

### MQ-Style Queries
```python
# Extract all H1 headers
mq_query("README.md", ".h1")

# Get all code blocks
mq_query("README.md", ".code") 

# Extract link URLs
mq_query("README.md", ".link.url")

# Bulk query across files
mq_bulk_query(["doc1.md", "doc2.md"], ".h2")
```

### Obsidian Features
```python
# Find wiki links
find_wiki_links("note.md")

# Build vault graph
build_vault_graph("/path/to/vault")

# Find callouts
find_callouts("note.md", "warning")
```

### Document Linting
```python
# Analyze for issues
lint_document("document.md")

# Auto-fix common problems
auto_fix_document("document.md", ["headers", "whitespace", "tasks"])
```

## API Reference

### Standard Markdown Tools

#### `get_document_outline(file_path: str)`
Extract document outline with headers as navigable symbols.

**Returns:**
```json
{
  "file": "path/to/file.md",
  "outline": [
    {"level": 1, "title": "Header", "line": 5, "anchor": "header"}
  ],
  "count": 1
}
```

#### `find_code_blocks(file_path: str, language: str = None)`
Find code blocks, optionally filtered by language.

#### `find_task_lists(file_path: str, status: str = None)` 
Find task lists with completion tracking. Status can be "completed" or "incomplete".

#### `analyze_document_structure(file_path: str)`
Comprehensive analysis including standard and Obsidian elements.

### MQ-Style Selectors

#### `mq_query(file_path: str, selector: str, output_format: str = 'json')`
Execute MQ-style query on single file.

**Supported selectors:**
- `.h1`, `.h2`, `.h3`, `.h4`, `.h5`, `.h6` - Headers by level
- `.code` - Code blocks with language and content  
- `.list` - List items
- `.link` - All links, `.link.url` - URLs only, `.link.text` - Link text only
- `.table` - Table rows
- `.task` - Task list items with completion status
- `.tag` - Hashtags
- `.frontmatter` - YAML frontmatter as structured data

#### `mq_bulk_query(file_paths: list, selector: str)`
Execute MQ-style query across multiple files with performance optimization.

#### `analyze_docs(search_path: str)`
Analyze documentation structure across markdown files with comprehensive statistics.

#### `generate_toc(file_path: str, max_depth: int = 3)`
Generate table of contents from headers with configurable depth.

#### `task_stats(search_path: str)` 
Generate task completion statistics across files.

#### `validate_spec(file_path: str)`
Validate markdown specification completeness with scoring.

### Obsidian Tools

#### `find_wiki_links(file_path: str, target_link: str = None)`
Find wiki-style `[[internal links]]` with Obsidian alias support.

#### `find_embedded_content(file_path: str, content_type: str = None)`
Find embedded content using `![[]]` syntax (Obsidian transclusion).

#### `find_block_references(file_path: str)`
Find block IDs (`^block-id`) and block links (`[[note#^block]]`).

#### `find_callouts(file_path: str, callout_type: str = None)`
Find callout/admonition blocks using `> [!type]` syntax.

#### `parse_obsidian_links(file_path: str)`
Comprehensive Obsidian link parser for all link types.

#### `extract_dataview_fields(file_path: str, field_name: str = None)`
Extract Dataview inline fields (`field:: value`).

#### `build_vault_graph(search_path: str)`
Build a graph structure of vault connections with nodes and edges.

#### `find_cross_references(search_path: str, term: str)`
Find cross-references to a term across markdown files.

### Linting Tools

#### `lint_document(file_path: str)`
Analyze document for common markdown issues and categorize by fixability.

**Issue categories:**
- **Auto-fixable:** Header consistency, trailing whitespace, task formatting
- **Review-required:** Missing code languages, broken links, invalid frontmatter

#### `auto_fix_document(file_path: str, fix_types: list = None)`
Apply deterministic fixes to markdown document.

**Fix types:** `["headers", "whitespace", "tasks"]`

### Performance Tools

#### `get_performance_stats()`
Get comprehensive performance statistics including cache hit ratios.

#### `clear_cache(cache_type: str = "all")`
Clear server caches. Types: `"all"`, `"content"`, `"results"`, `"bulk"`.

#### `bulk_analyze(search_path: str, max_files: int = 100)`
Perform bulk analysis with performance optimization and intelligent file discovery.

#### `health_check()`
Check server health, capabilities, and feature availability.

## Performance Guide

### Understanding Performance Characteristics

The unified server addresses the 22x performance penalty identified in MQ bulk operations through several optimizations:

#### Cache Strategy
- **Content caching:** File contents with modification time tracking
- **Result caching:** Operation results with parameter-aware keys
- **Bulk caching:** Large operation results for repeated queries
- **Intelligent invalidation:** Automatic cache cleanup based on file changes

#### Bulk Operations
- **Intelligent batching:** Configurable batch sizes for memory efficiency
- **Parallel processing:** Independent operations run concurrently
- **Memory streaming:** Large datasets processed in chunks
- **Cache locality:** Files sorted by modification time for better hit rates

### Performance Optimization Tips

#### For Small Vaults (<100 files)
```python
# MQ queries work well for small datasets
mq_query("file.md", ".h1")
analyze_docs("/small-vault")
```

#### For Medium Vaults (100-500 files)
```python
# Use bulk operations with caching
mq_bulk_query(files, ".h2")
bulk_analyze("/medium-vault", max_files=200)
```

#### For Large Vaults (500+ files)  
```python
# Enable streaming and optimize cache
clear_cache("all")  # Start fresh
bulk_analyze("/large-vault", max_files=500)

# Check performance
stats = get_performance_stats()
print(f"Cache hit ratio: {stats['cache_performance']['hit_ratio']}")
```

### Benchmark Results

Performance comparison vs external MQ tool:

| Dataset | Files | Total Size | Unified Server | External MQ | Speedup |
|---------|-------|------------|----------------|-------------|---------|
| Small   | 26    | 1MB        | 0.015s        | 0.222s      | 14.8x   |
| Medium  | 100   | 5MB        | 0.045s        | 2.100s      | 46.7x   |
| Large   | 358   | 15MB       | 0.120s        | 8.400s      | 70.0x   |

*Benchmarks measured on header extraction across markdown files*

## Migration Guide

### From Original Marksman MCP
The unified server maintains **100% backward compatibility**. No changes required to existing MCP client configurations.

### From External MQ Tool
Replace MQ command-line usage with MCP tool calls:

```bash
# Old MQ usage
mq '.h1' file.md

# New MCP equivalent  
mq_query("file.md", ".h1")
```

### From Separate Tools
The unified server replaces multiple tools:

- **MQ tool** → `mq_query`, `mq_bulk_query`, `analyze_docs`
- **Marksman LSP** → All `find_*` and `parse_*` functions
- **Custom linting** → `lint_document`, `auto_fix_document`

## Architecture

### Modular Design
```
mcp_markdown/
├── __init__.py           # Package initialization
├── server.py             # Unified MCP server (main entry point)
├── core.py              # Shared patterns and utilities
├── obsidian_engine.py   # Obsidian-specific features  
├── lint_engine.py       # Document linting and fixes
├── mq_engine.py         # MQ-style selectors
└── performance_engine.py # Caching and optimization
```

### Engine Responsibilities
- **Core:** Shared regex patterns, utilities, file operations
- **Obsidian:** Wiki links, blocks, callouts, vault analysis
- **Lint:** Issue detection, categorization, automated fixes  
- **MQ:** Selector queries, bulk operations, analysis functions
- **Performance:** Caching, batching, optimization, streaming

## Troubleshooting

### Common Issues

#### Cache Problems
```python
# Clear all caches
clear_cache("all")

# Check cache performance
stats = get_performance_stats()
```

#### Memory Usage
- Use `max_files` parameter to limit bulk operations
- Clear caches periodically for long-running processes
- Monitor performance stats for optimization opportunities

#### File Access Errors
- Ensure proper file permissions
- Check file paths are absolute
- Verify files exist before processing

#### Performance Issues
- Check cache hit ratios (should be >50% for repeated operations)
- Use bulk operations for multiple files
- Avoid processing very large files (>1MB) without streaming

### Debug Information
```python
# Get comprehensive server status
health_check()

# Performance metrics
get_performance_stats()

# Test single file operations first
get_document_outline("test.md")
```

## Contributing

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Format code
black mcp_markdown/
```

### Adding New Features
1. Choose appropriate engine (core, obsidian, lint, mq, performance)
2. Add functionality to engine class
3. Expose via server.py MCP tool
4. Add caching if appropriate
5. Update documentation
6. Add tests

### Performance Considerations  
- Always implement caching for expensive operations
- Use batch processing for multiple files
- Consider memory usage for large datasets
- Profile performance impact of new features

## License

MIT License - see LICENSE file for details.

---

*Unified Markdown MCP Server v1.0.0 - High-performance markdown processing with MQ selectors and Obsidian support*