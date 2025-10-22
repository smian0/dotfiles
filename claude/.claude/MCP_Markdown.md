# Markdown MCP Server

**Purpose**: Markdown document analysis, Obsidian vault operations, and structured content extraction

## Triggers
- Working with `.md`, `.markdown` files
- Obsidian vault operations (wiki-links, graph, cross-references)
- Documentation analysis and navigation
- Task list extraction and tracking
- Code block extraction from documentation
- Markdown structure validation and linting
- Generating table of contents

## Choose When
- **Over Read tool**: When you need structured markdown analysis (outline, frontmatter, tasks)
- **Over Grep**: When searching markdown-specific elements (wiki-links, code blocks, tasks)
- **For Obsidian**: Vault graph, cross-references, backlinks, wiki-link parsing
- **For documentation**: TOC generation, structure validation, spec compliance
- **For task management**: Extract and track TODO items across markdown files
- **Not for simple reads**: Use Read tool for basic markdown file content

## Works Best With
- **Serena**: mcp_markdown extracts code blocks → Serena analyzes/edits the code
- **Write/Edit**: mcp_markdown analyzes structure → Edit/Write makes targeted changes
- **Grep**: For keyword search → mcp_markdown for structural search

## Tool Categories

### Document Structure
- `get_document_outline`: Extract heading hierarchy
- `analyze_document_structure`: Comprehensive structural analysis
- `generate_toc`: Generate table of contents

### Obsidian Vault
- `find_obsidian_elements`: Find callouts, tags, wiki-links
- `parse_obsidian_links`: Parse and validate wiki-links
- `build_vault_graph`: Build knowledge graph from vault
- `find_cross_references`: Find backlinks and forward links

### Content Extraction
- `extract_frontmatter`: Parse YAML frontmatter
- `find_code_blocks`: Extract code blocks by language
- `find_task_lists`: Extract TODO/checkbox items
- `task_stats`: Statistics on task completion

### Querying & Search
- `mq_query`: Markdown Query language for advanced searches
- `mq_bulk_query`: Batch queries across multiple files

### Validation
- `lint_document`: Lint markdown for style/syntax issues
- `validate_spec`: Validate against CommonMark/GFM spec

### Utilities
- `analyze_docs`: Batch analyze multiple markdown files
- `bulk_analyze`: Performance-optimized bulk operations
- `health_check`: Server health status
- `get_performance_stats`: Performance metrics
- `clear_cache`: Clear server cache

## Examples

**Markdown-specific tasks (use mcp_markdown):**
```
"Show me the outline of this markdown file" → mcp_markdown (get_document_outline)
"Find all wiki-links in my vault" → mcp_markdown (parse_obsidian_links)
"Extract all TODO items from these docs" → mcp_markdown (find_task_lists)
"Find all Python code blocks" → mcp_markdown (find_code_blocks)
"Build a graph of my Obsidian vault" → mcp_markdown (build_vault_graph)
"Generate TOC for README.md" → mcp_markdown (generate_toc)
"Validate this markdown against CommonMark" → mcp_markdown (validate_spec)
"Find documents that link to this note" → mcp_markdown (find_cross_references)
```

**Not markdown-specific (use other tools):**
```
"Read this markdown file" → Read tool (simple file read)
"Search for 'API' in markdown files" → Grep (keyword search)
"Edit this heading" → Edit tool (text replacement)
"Find files containing 'config'" → Glob (file search)
```

## Common Workflows

### Obsidian Vault Navigation
```
1. mcp_markdown build_vault_graph → Understand vault structure
2. mcp_markdown find_cross_references → Find related notes
3. mcp_markdown parse_obsidian_links → Validate links
```

### Documentation Maintenance
```
1. mcp_markdown analyze_document_structure → Check organization
2. mcp_markdown lint_document → Find style issues
3. mcp_markdown generate_toc → Update table of contents
4. Edit tool → Apply fixes
```

### Task Management
```
1. mcp_markdown find_task_lists → Extract all TODOs
2. mcp_markdown task_stats → Get completion metrics
3. Edit tool → Update task statuses
```

### Code Extraction
```
1. mcp_markdown find_code_blocks → Extract code by language
2. Serena tools → Analyze/edit extracted code
3. Edit tool → Update code blocks in markdown
```

## Best Practices

1. **Use for structure, not content** - mcp_markdown excels at structural analysis, not full-text reading
2. **Obsidian-first** - Leverages Obsidian conventions (wiki-links, callouts, tags)
3. **Combine with other tools** - Extract structure with mcp_markdown, edit with Edit tool
4. **Markdown Query (mq)** - Use for complex queries beyond simple grep
5. **Vault operations** - Build graphs and cross-references for large documentation sets

## Context Usage

**Current: ~11.5k tokens (20 tools)**

Consider removing if:
- Not using Obsidian vaults
- Not working with markdown documentation
- Simple markdown edits (use Read/Edit instead)

Can archive and restore when needed for documentation-heavy projects.
