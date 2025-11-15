# Example Query Patterns

Common markdown query patterns for various use cases.

## Documentation Analysis

### Extract All Headers for Navigation
```python
# Get complete document structure
outline = get_document_outline("README.md")

# Generate navigable TOC
toc = generate_toc("docs/guide.md", max_depth=3)
```

### Find All Code Examples
```python
# All code blocks
query("tutorial.md", ".code")

# Specific language
query("tutorial.md", ".code.python")
query("tutorial.md", ".code.javascript")
```

### Link Validation
```python
# Extract all links
links = query("README.md", ".link")

# Just URLs for checking
urls = query("README.md", ".link.url")
```

## Obsidian Vault Workflows

### Knowledge Graph Building
```python
# Build complete vault graph
graph = build_vault_graph("/vault")

# Nodes: files with incoming/outgoing connections
# Edges: wiki links between notes
# Stats: orphaned notes, hub notes, total connections
```

### Find Broken Links
```python
# Get all wiki links
all_links = bulk_query("/vault", ".link")

# Lint to find broken targets
for md_file in Path("/vault").rglob("*.md"):
    issues = lint_document(str(md_file))
    broken = [i for i in issues["issues"]["review_required"] 
              if i["type"] == "broken_wiki_link"]
    if broken:
        print(f"{md_file}: {len(broken)} broken links")
```

### Extract Metadata
```python
# Get all dataview fields
bulk_query("/vault", ".frontmatter")

# Or inline fields
for note in vault_notes:
    fields = extract_dataview_fields(note)
    # fields["fields"] contains field:: value pairs
```

## Content Management

### Task Tracking
```python
# Get task completion stats
stats = task_stats("/project")

# All incomplete tasks
incomplete = bulk_query("/project", ".task")
incomplete_only = [t for t in incomplete if not t["completed"]]
```

### Format Cleanup
```python
# Clean all markdown files
from pathlib import Path

for md_file in Path(".").rglob("*.md"):
    # Check for issues
    result = lint_document(str(md_file))
    
    # Auto-fix if problems found
    if result["counts"]["auto_fixable"] > 0:
        auto_fix(str(md_file), ["headers", "whitespace", "tasks"])
        print(f"Fixed {result['counts']['auto_fixable']} issues in {md_file}")
```

### Documentation Validation
```python
# Ensure spec completeness
spec_result = validate_spec("SPECIFICATION.md", "completeness")

# Check requirements extraction
requirements = validate_spec("SPEC.md", "requirements")

# Analyze dependencies
deps = validate_spec("DESIGN.md", "dependencies")
```

## Cross-Reference Analysis

### Find All Mentions
```python
# Find all references to a topic
refs = find_cross_references("/vault", "API Design")

# Returns:
# - Files containing the term
# - Line numbers and context
# - Wiki links to pages with that term
```

### Backlinks Analysis
```python
# Find what links to a note
target = "important-concept"
graph = build_vault_graph("/vault")

# Filter edges pointing to target
backlinks = [e for e in graph["edges"] if target in e["target"]]
```

## Bulk Operations

### Extract All Headers from Multiple Files
```python
# Directory query (auto-finds .md files)
all_headers = bulk_query("/docs", ".h2")

# Specific file list
files = ["doc1.md", "doc2.md", "doc3.md"]
headers = bulk_query(files, ".h1")
```

### Analyze Large Vaults
```python
# Limit scope for performance
bulk_analyze("/large-vault", max_files=500)

# Monitor cache performance
stats = get_performance_stats()
print(f"Cache hit ratio: {stats['cache_performance']['hit_ratio']:.2%}")
```

## Advanced Patterns

### Combine Multiple Queries
```python
# Get structure overview
doc_stats = analyze_docs("/project/docs")

# Extract specific elements
code_blocks = bulk_query("/project/docs", ".code")
wiki_links = bulk_query("/project/docs", ".link")

# Combine results
overview = {
    "stats": doc_stats,
    "code_examples": len(code_blocks),
    "total_links": len(wiki_links)
}
```

### Selective Processing
```python
# Process only files with issues
from pathlib import Path

for md_file in Path("/vault").rglob("*.md"):
    issues = lint_document(str(md_file))
    
    # Only fix files with many issues
    if issues["counts"]["auto_fixable"] > 5:
        print(f"Fixing {md_file}")
        auto_fix(str(md_file))
```

### Custom Filters
```python
# Get all tasks, then filter by content
all_tasks = bulk_query("/project", ".task")

# High priority tasks (contains "P0" or "URGENT")
urgent = [t for t in all_tasks 
          if "P0" in t["text"] or "URGENT" in t["text"]]

# Group by completion status
completed = [t for t in all_tasks if t["completed"]]
pending = [t for t in all_tasks if not t["completed"]]
```

