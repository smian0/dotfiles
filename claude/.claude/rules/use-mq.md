# MQ Integration Protocol for Markdown Processing

## When to Use MQ

Use `mq` (if installed) instead of plain text search or manual markdown editing when:

- **Structural markdown operations** are involved (e.g., extracting headers, code blocks, links, lists)
- **Bulk transformations** across multiple markdown files are needed
- **Complex filtering** based on markdown node types or attributes
- **Programmatic manipulation** of markdown structure is required
- **Format conversion** between markdown, HTML, or JSON
- **Batch processing** of documentation files

## MQ Command Patterns

### Basic Extraction Template:
```sh
mq '.h1' file.md                    # Extract all H1 headers
mq '.code' docs/*.md               # Extract all code blocks
mq '.link.url' file.md            # Extract all link URLs
mq '.code.lang' file.md           # Extract code block languages
```

### Filtering Templates:
```sh
mq 'select(.h1 || .h2)' file.md                    # Headers level 1-2
mq '.code | select(contains("install"))' file.md  # Code blocks containing "install"
mq 'select(!(.code.lang == "js"))' docs/*.md               # Non-JavaScript code blocks
mq '.h | select(contains("API"))' file.md         # Headers containing "API"
```

### Transformation Templates:
```sh
mq '.h | to_link("#" + to_text(.), to_text(.), "")' file.md
mq 'include "csv" | csv_parse(true) | csv_to_markdown_table()' data.csv
mq '--json .code' file.md                         # Code blocks as JSON
```

## Common Use Cases

### Documentation Maintenance
- **Extract table of contents:**
  `mq 'select(.h1 || .h2 || .h3)' README.md`
- **Find all code examples in a specific language:**
  `mq '.code | select(.lang == "python")' docs/`
- **Extract all external links:**
  `mq '.link.url | select(starts_with("http"))' file.md`

### Bulk Operations
- **Update all code block languages:**
  `mq '.code | set_attr("lang", "bash")' *.md`
- **Extract all task list items:**
  `mq '.list | select(has_attr("checked"))' TODO.md`
- **Convert markdown headers to links:**
  `mq '.h2 | to_link("#" + to_text(.), to_text(.), "")' file.md`

### Content Analysis
- **Count sections by level:**
  `mq '.h1 | len' file.md`
- **Find largest code blocks:**
  `mq '.code | sort_by(len) | reverse | first(5)' docs/`
- **Extract all images with alt text:**
  `mq '.image | {url: .url, alt: .alt}' file.md`

## Advanced Query Patterns

### Working with Sections
```sh
# Extract content under specific headers
mq 'sections(.h2)' file.md

# Group content by header level
mq 'group_by(type)' file.md
```

### Complex Filtering
```sh
# Find code blocks with specific language AND content
mq '.code | select(.lang == "python" and contains("import"))' docs/

# Extract headers that have links
mq '.h | select(children | has_link)' file.md
```

### Data Extraction
```sh
# Extract structured data from markdown
mq '--json {.h1: .h1, .code: .code | map({lang: .lang, content: .})}' file.md

# Create CSV from markdown table
mq 'include "csv" | .table | csv_to_csv()' data.md
```

## Integration Workflow

### Before using MQ:
1. **Check if MQ is installed:**
   ```sh
   command -v mq >/dev/null 2>&1 || echo "MQ not installed, falling back to text processing"
   ```
2. **Identify** if the task involves structural markdown operations
3. **Determine** the appropriate node types to target
4. **Construct** the query using MQ syntax
5. **Run** MQ to gather structured information
6. **Use** results for transformations or analysis

### Example Workflow

When asked to "extract all Python code examples from documentation":

1. **Check for MQ:**
   ```sh
   command -v mq >/dev/null 2>&1 && mq '.code | select(.lang == "python")' docs/
   ```
2. **Process** results structurally
3. **Transform** or export as needed (use `--json` for programmatic processing)
4. **Combine** with other tools for additional processing

### Combine MQ with Internal Tools

- **markdownlint-cli2** for style validation and auto-fixing
- **Grep tool** for simple text searches within extracted content
- **Read/Write tools** for file operations based on MQ results
- **Bash tool** for complex text processing pipelines

## Format Conversion

```sh
# Markdown to HTML
mq -I markdown -F html '.' file.md > file.html

# Markdown to JSON for processing
mq --json '.' file.md | jq '.h1'

# Include data modules
mq --json --yaml --csv '.' data.md  # Enable YAML/CSV processing
```

## Performance Considerations

- **File processing**: MQ processes files in parallel when >10 files
- **Memory usage**: Use streaming for large files
- **Caching**: MQ automatically caches parsed markdown
- **Batch operations**: Prefer single MQ command over multiple calls

## Key Benefits Over Text Processing

1. **Structure-aware** — understands markdown hierarchy and semantics
2. **Type-safe** — operates on markdown nodes, not plain text
3. **Transformative** — can modify structure while preserving validity
4. **Composable** — chain operations similar to jq
5. **Multi-format** — handles markdown, MDX, HTML, JSON, CSV, YAML

## Decision Matrix: When to Use Each Tool

| Task Type                     | Tool Choice          | Reason                        |
|-------------------------------|----------------------|-------------------------------|
| Simple text search            | grep/rg             | Fast text matching            |
| Structural markdown queries   | MQ                   | Node-aware operations         |
| Text transformations          | sed/awk              | Pattern-based editing         |
| Markdown linting              | markdownlint-cli2    | Style enforcement             |
| File editing                  | Read/Write/Edit      | Precise file modifications    |
| Complex transformations       | MQ + CLI pipelines   | Structure + composability     |

**Always prefer MQ for structural markdown operations over regex-based approaches, but only if it is installed and available.**

## CLI Tool Integration

MQ works exceptionally well with standard Unix tools to create powerful markdown processing pipelines. This approach is more reliable and consistently available than specialized MCP servers.

### Essential CLI Combinations

#### MQ + grep/ripgrep
```sh
# Extract headers, then search for specific content
mq '.h2' docs/*.md | rg "API"

# Find code blocks, then search within them
mq '.code' README.md | rg "install"

# Extract all links, then filter by domain
mq '.link.url' docs/*.md | rg "github.com"
```

#### MQ + jq (for JSON processing)
```sh
# Extract structured data as JSON, then process
mq --json 'select(.h1 || .h2)' file.md | jq '. | select(contains("Getting Started"))'

# Complex data extraction and transformation  
mq --json '.' docs/*.md | jq '{headers: [.[] | select(.h1 or .h2)], links: [.[] | .link.url], code: [.[] | .code.lang]}'

# Filter and sort extracted content
mq --json '.code' docs/*.md | jq 'group_by(.lang) | map({lang: .[0].lang, count: length})'
```

#### MQ + sed/awk
```sh
# Extract headers and format as table of contents  
mq 'select(.h1 || .h2 || .h3)' README.md | sed 's/^### /    - /' | sed 's/^## /  - /' | sed 's/^# /- /'

# Process extracted text with awk
mq '.code.lang' docs/*.md | awk '{count[$1]++} END {for (lang in count) print lang, count[lang]}'

# Clean up extracted content
mq '.link.url' file.md | sed 's/^http/- http/' | sort | uniq
```

#### MQ + markdown-it (MD→HTML conversion)
```sh
# Extract specific sections and convert to HTML
mq 'select(.h2 || .h3)' README.md > temp.md && markdown-it temp.md > sections.html && rm temp.md

# Process code blocks and convert  
mq 'select(.code)' docs/*.md > code-blocks.md && markdown-it code-blocks.md > code-examples.html && rm code-blocks.md

# Full document transformation pipeline with styling
mq 'select(.h1 || .h2)' file.md > headers.md && markdown-it headers.md | sed 's/<h1>/<h1 class="main">/' > styled.html && rm headers.md
```

### Advanced Pipeline Patterns

#### Documentation Analysis
```sh
# Comprehensive documentation audit
analyze_docs() {
  echo "=== Headers Structure ==="
  mq 'select(.h1 || .h2 || .h3)' "$1" | nl
  
  echo "=== Code Block Languages ==="
  mq '.code.lang' "$1" | sort | uniq -c | sort -nr
  
  echo "=== External Links ==="
  mq '.link.url' "$1" | rg '^https?' | sort | uniq
  
  echo "=== TODO Items ==="
  mq 'select(.list)' "$1" | rg -i 'todo|fixme'
}
```

#### Content Migration
```sh
# Migrate content while preserving structure
migrate_content() {
  local source="$1" target="$2"
  
  # Extract headers for navigation
  mq 'select(.h1 || .h2)' "$source" > headers.tmp
  
  # Extract and transform code blocks
  mq 'select(.code)' "$source" | sed 's/```bash/```shell/' > code.tmp
  
  # Reconstruct with modifications
  # (combine with other processing...)
  
  rm *.tmp
}
```

#### Bulk Content Processing
```sh
# Process multiple files in parallel
process_docs() {
  find docs -name "*.md" | parallel --jobs 4 '
    echo "Processing {}" && 
    mq ".h1" {} | sed "s/^# /## /" > {.}_headers.md &&
    mq ".code | select(.lang == \"bash\")" {} > {.}_scripts.sh
  '
}
```

### Frontmatter Operations

Essential for managing prompt and specification metadata:

```sh
# Extract YAML frontmatter
extract_frontmatter() {
  sed -n '/^---$/,/^---$/p' "$1"
}

# Get specific frontmatter field
get_field() {
  extract_frontmatter "$2" | grep "^$1:" | cut -d: -f2- | sed 's/^ *//'
}

# Update frontmatter field
update_field() {
  field="$1" value="$2" file="$3"
  sed -i '' "1,/^---$/s/^$field:.*/$field: $value/" "$file"
}

# Extract all metadata from prompt files
audit_prompts() {
  for f in prompts/*.md; do
    echo "=== $(basename "$f") ==="
    extract_frontmatter "$f" | grep -E "^(model|temperature|max_tokens):"
  done
}
```

### Section Extraction

Extract specific sections from specifications:

```sh
# Extract content under specific header
extract_section() {
  header="$1" file="$2"
  awk "/^## $header/,/^## /" "$file" | head -n -1
}

# Get all code from a specific section
get_section_code() {
  extract_section "$1" "$2" | mq '.code'
}

# Extract multiple sections
extract_sections() {
  file="$1"; shift
  for section in "$@"; do
    echo "=== $section ==="
    extract_section "$section" "$file"
  done
}
```

### Table of Contents Generation

Auto-generate navigable table of contents:

```sh
# Generate GitHub-compatible TOC
generate_toc() {
  echo "## Table of Contents"
  mq 'select(.h2 || .h3)' "$1" | while IFS= read -r line; do
    level=$(echo "$line" | sed 's/[^#]//g' | wc -c)
    text=$(echo "$line" | sed 's/^#* //')
    anchor=$(echo "$text" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 -]//g' | tr ' ' '-')
    indent=$(printf '%*s' $((level-2)) '' | tr ' ' ' ')
    echo "${indent}- [$text](#$anchor)"
  done
}

# Insert TOC after frontmatter
insert_toc() {
  file="$1"
  toc=$(generate_toc "$file")
  # Create temp file with TOC inserted
  awk '/^---$/{if(++c==2){print; print ""; print toc; next}} 1' toc="$toc" "$file" > "$file.tmp" && mv "$file.tmp" "$file"
}
```

### Task and Checklist Management

Track requirements and specifications:

```sh
# Get task statistics
task_stats() {
  total=$(mq 'select(.list)' "$1" | grep -c '\[.\]')
  done=$(mq 'select(.list)' "$1" | grep -c '\[x\]')
  pending=$((total - done))
  percent=$((done * 100 / total))
  echo "✓ Complete: $done | ⏳ Pending: $pending | Progress: $percent%"
}

# Mark task as complete
mark_done() {
  task="$1" file="$2"
  sed -i '' "/\[ \] $task/s/\[ \]/\[x\]/" "$file"
}

# Extract incomplete tasks
pending_tasks() {
  mq 'select(.list)' "$1" | grep '\[ \]' | sed 's/- \[ \] //'
}

# Toggle task state
toggle_task() {
  line="$1" file="$2"
  sed -i '' "${line}s/\[ \]/\[✓\]/; ${line}s/\[x\]/\[ \]/; ${line}s/\[✓\]/\[x\]/" "$file"
}
```

### Content Validation

Ensure specification and prompt integrity:

```sh
# Lint markdown files
markdownlint-cli2 "**/*.md" --config .markdownlint.yaml

# Auto-fix common issues
markdownlint-cli2 "**/*.md" --fix

# Validate specification structure
validate_spec() {
  echo "=== Structure Validation ==="
  
  # Check required sections
  [ -z "$(mq '.h1' "$1")" ] && echo "⚠️  Missing H1 title"
  [ -z "$(extract_frontmatter "$1")" ] && echo "⚠️  Missing frontmatter"
  
  # Lint the file
  echo "=== Style Validation ==="
  markdownlint-cli2 "$1"
  
  # Check internal links
  echo "=== Link Validation ==="
  mq '.link.url' "$1" | grep '^#' | while read -r anchor; do
    heading=$(echo "${anchor#\#}" | tr '-' ' ')
    mq 'select(.h2 || .h3)' "$1" | grep -qi "$heading" || echo "❌ Broken: $anchor"
  done
}

# Batch validation
validate_all() {
  find . -name "*.md" -type f | while read -r file; do
    echo "Validating: $file"
    markdownlint-cli2 "$file" || echo "  ⚠️ Has issues"
  done
}
```

### Tool Selection Matrix (CLI-focused)

| Task Type | Primary Tool | Secondary Tool | Pipeline |
|-----------|--------------|----------------|----------|
| Header extraction | `mq '.h1'` | `grep -E "^#"` | `mq → sed → sort` |
| Code analysis | `mq '.code'` | `rg '```'` | `mq → jq → awk` |
| Link validation | `mq '.link.url'` | `grep -o 'https\?://[^)]+'` | `mq → curl → grep` |
| Content stats | `mq --json '.'` | `wc -l` | `mq → jq → bc` |
| Format conversion | `mq → markdown-it` | `pandoc` | `mq → sed → markdown-it` |

### Performance Considerations

- **Parallel processing**: Use `parallel` or `xargs -P` for bulk operations
- **Memory efficiency**: Stream large files through pipelines instead of loading entirely
- **Caching**: MQ caches parsed markdown, but CLI tools don't - consider intermediate files
- **Error handling**: Always check exit codes in complex pipelines

### Cross-Platform Compatibility

```sh
# macOS/Linux compatible patterns
command -v gawk >/dev/null && AWK=gawk || AWK=awk
command -v gsed >/dev/null && SED=gsed || SED=sed
command -v parallel >/dev/null && PARALLEL=parallel || PARALLEL="xargs -n1 -P4"

# Universal header extraction
mq 'select(.h1 || .h2)' docs/*.md | $SED 's/^## /  - /' | $SED 's/^# /- /' | sort
```

### Integration Benefits

1. **Reliability** — Standard Unix tools are universally available
2. **Composability** — Easy to chain and combine operations
3. **Performance** — Native tools optimized for text processing
4. **Debugging** — Each step can be tested independently
5. **Scriptability** — Easy to automate and version control

## Error Handling

- MQ provides clear error messages for syntax issues
- Use `mq docs` to reference available functions
- Test queries on single files before bulk operations
- Use `--json` output for better error handling in scripts

## Tips and Best Practices

1. **Start simple** with basic selectors like `.h1` or `.code`
2. **Chain operations** using pipe `|` for complex transformations
3. **Use select()** for filtering instead of manual conditionals
4. **Leverage built-in functions** for common operations (contains, starts_with, etc.)
5. **Test with --json** when debugging complex queries
6. **Use include statements** for CSV/YAML/JSON data processing

## Examples Based on This Repository

```sh
# Extract all bash commands from README
mq 'select(.code)' README.md | grep bash

# Find all installation sections  
mq 'select(.h2)' *.md | grep -i install

# Extract all TODO items
mq 'select(.list)' TODO.md | rg -i 'todo|fixme'

# Generate table of contents
mq 'select(.h1 || .h2 || .h3)' README.md | sed 's/^### /    - /' | sed 's/^## /  - /' | sed 's/^# /- /'
```

## Final Recommendations

### Start Simple, Scale Up
1. **Begin with basic extraction**: `mq '.h1'` or `mq '.code'`
2. **Add Unix tools gradually**: pipe to `grep`, `sed`, `awk` as needed
3. **Build complex pipelines incrementally**: test each step independently

### Tool Selection Strategy
- **Use MQ for**: Structural markdown operations, node-aware filtering
- **Use grep/rg for**: Text search within extracted content  
- **Use sed/awk for**: Text transformations and formatting
- **Use jq for**: Complex data processing (when MQ JSON output works)
- **Avoid**: MCP servers unless you need AI-powered semantic understanding

### Best Practices
- **Test queries on single files first** before bulk operations
- **Use `command -v tool` checks** for cross-platform compatibility
- **Prefer streaming pipelines** over loading large files into memory
- **Document complex pipelines** as shell functions for reuse
- **Always handle errors** in production scripts

### When to Choose CLI Over MCP
✅ **CLI Tools**: Universal availability, reliability, composability, performance  
❌ **MCP Servers**: Setup overhead, dependency management, debugging complexity

The CLI approach with MQ + Unix tools provides 90% of markdown processing capabilities with maximum reliability and zero configuration overhead.