# MQ Selector Reference

jq-like syntax for structural markdown extraction.

## Basic Selectors

### Headers
```python
query("file.md", ".h1")  # All level 1 headers
query("file.md", ".h2")  # All level 2 headers
# ... through .h6
```

**Returns**: `{"level": 1, "title": "Header Text", "line": 5, "anchor": "header-text"}`

### Code Blocks
```python
query("file.md", ".code")           # All code blocks
query("file.md", ".code.python")    # Specific language
```

**Returns**: `{"language": "python", "code": "...", "line": 10, "length": 5}`

### Lists
```python
query("file.md", ".list")  # All list items
```

**Returns**: List items with content and line numbers

### Links
```python
query("file.md", ".link")       # All links (full objects)
query("file.md", ".link.url")   # URLs only
query("file.md", ".link.text")  # Link text only
```

**Returns**: `{"text": "Link Text", "url": "https://...", "line": 15}`

### Tables
```python
query("file.md", ".table")  # Table rows
```

### Tasks
```python
query("file.md", ".task")  # Task list items with completion status
```

**Returns**: `{"completed": false, "text": "Task description", "line": 20}`

### Tags
```python
query("file.md", ".tag")  # Hashtags (including nested #parent/child)
```

### Frontmatter
```python
query("file.md", ".frontmatter")  # YAML frontmatter as structured data
```

## Bulk Operations

Query multiple files efficiently:

```python
# Directory (finds all .md files)
bulk_query("/path/to/vault", ".h2")

# Specific file list
bulk_query(["doc1.md", "doc2.md"], ".code")
```

**Performance**: Uses intelligent batching and caching for large datasets.

## Analysis Functions

### Document Analysis
```python
analyze_docs("/path/to/docs")
```

Returns comprehensive statistics: headers, code blocks, links, tasks per file.

### Table of Contents
```python
generate_toc("file.md", max_depth=3)
```

Generates navigable TOC from headers.

### Task Statistics
```python
task_stats("/path/to/vault")
```

Aggregates task completion rates across files.

## Output Formats

```python
query("file.md", ".h1", output_format="json")      # Structured data (default)
query("file.md", ".h1", output_format="markdown")  # Raw markdown text
```

## Best Practices

**Small datasets (<100 files)**: Use `query()` for single files
**Medium datasets (100-500)**: Use `bulk_query()` with caching
**Large datasets (500+)**: Use `bulk_analyze()` with `max_files` limit

See [Performance Tips](./performance-tips.md) for optimization details.

