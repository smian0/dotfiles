# MQ Integration Protocol for Markdown Processing

## Version Compatibility & Installation Check

```bash
# ALWAYS check before using MQ
command -v mq >/dev/null 2>&1 && MQ_VERSION=$(mq --version 2>/dev/null) && echo "✅ MQ available: $MQ_VERSION"
```

**Verified with:** `mq 0.2.21`

## 🚨 Critical: Start Simple, Scale Progressively

### Phase 1: Basic Selectors (Always Work)
```bash
mq '.h1' file.md                # ✅ All H1 headers
mq '.h2' file.md                # ✅ All H2 headers  
mq '.code' file.md              # ✅ All code blocks
mq '.list' file.md              # ✅ All list items
mq '.link' file.md              # ✅ All links
```

### Phase 2: Simple Filtering (Test First)
```bash
mq '.list' file.md | grep "\\[ \\]"     # ✅ Filter unchecked todos
mq '.code' file.md | grep "bash"       # ✅ Filter bash code blocks  
mq '.h2' file.md | grep -i "api"       # ✅ Find API headers
```

### Phase 3: Advanced (Use with Caution)
```bash
# Test these patterns before using:
mq 'select(is_list)' file.md           # May return entire document
mq docs | grep "function_name"         # Check function availability
```

## Decision Tree: When to Use MQ vs Alternatives

### ✅ Use MQ When:
- **Extracting markdown structures**: Headers, code blocks, links, tables
- **Need clean output**: MQ preserves markdown formatting
- **Working with single files**: Performance is good
- **Basic filtering needs**: Combined with Unix tools

### ❌ Don't Use MQ When:
- **Complex filtering needed**: Use grep/ripgrep instead
- **Bulk text search**: grep/ripgrep are faster
- **Complex transformations**: sed/awk more reliable
- **Syntax is unclear**: Fall back to proven tools

## 📊 Performance Benchmarks & Strategy

### Benchmark Results (Tested on 358 MD files, 15MB)

#### Single File Performance
```
Task: Extract H1 headers from single README.md
✅ Grep:     0.003s  (fastest)
🔧 MQ:       0.006s  (2x slower)  
⚡ Ripgrep:  0.009s  (3x slower)

Result: Minimal difference for single files
```

#### Bulk Operations Performance  
```
Task: Extract H1 headers from 26 README files
⚡ Ripgrep:  0.010s  (fastest)
✅ Grep:     0.015s  (1.5x slower)
❌ MQ:       0.222s  (22x slower!)

Result: MQ significantly slower for bulk operations
```

### Performance Guidelines by Dataset Size

| File Count | Total Size | Best Tool | Strategy |
|------------|------------|-----------|----------|
| 1-5 files | <1MB | MQ acceptable | Use MQ for structural queries |
| 5-50 files | 1-5MB | Hybrid approach | MQ for specific files, grep for discovery |
| 50+ files | >5MB | Traditional tools | ripgrep/grep for bulk, MQ for cleanup |
| 200+ files | >10MB | **Avoid MQ for bulk** | Use ripgrep exclusively |

### Why MQ is Slower for Bulk Operations

1. **Per-file parsing overhead**: Full AST analysis vs simple text matching
2. **Process spawning**: Multiple MQ instances vs single grep process  
3. **Memory usage**: Higher memory footprint per file
4. **I/O patterns**: Less optimized for streaming large datasets

### Optimal Strategy by Use Case

#### ✅ **Discovery Phase** (Finding relevant files)
```bash
# Use ripgrep for fast bulk discovery
rg "- \[ \]" --type md . --files-with-matches | head -10

# Use grep for universal compatibility
grep -r "^# " --include="*.md" . -l | head -10
```

#### 🔧 **Extraction Phase** (Clean structural output)
```bash
# Use MQ on discovered files for clean extraction
rg "- \[ \]" --type md . -l | xargs -I {} mq '.list' {} | grep "\[ \]"

# Or hybrid approach
mq '.list' specific-file.md | grep "\[ \]"  # Clean todo extraction
```

#### ⚡ **Performance-Critical Scenarios**
```bash
# Fastest: ripgrep for everything
rg "^# " --type md . | head -20        # Headers
rg "- \[ \]" --type md . --count      # Todo count  
rg "```[a-z]+" --type md . -o | sort | uniq -c  # Code languages

# When you need counts across large datasets
find . -name "*.md" -exec grep -c "^#" {} + | awk -F: '{sum+=$2} END {print sum}'
```

### Dataset Size Decision Matrix

| Your Vault Size | Recommended Approach | Tools Priority |
|------------------|---------------------|----------------|
| **Small** (<100 files) | MQ-friendly | 1. MQ 2. grep 3. ripgrep |
| **Medium** (100-500 files) | **Hybrid** | 1. ripgrep 2. MQ 3. grep |
| **Large** (500+ files) | Traditional tools | 1. ripgrep 2. grep 3. MQ (rare) |

### Performance-Optimized Patterns

#### Fast Bulk Analysis
```bash
# Quick vault overview (fastest method)
analyze_vault_fast() {
    echo "=== Vault Stats (Fast Method) ==="
    echo "Files: $(find . -name '*.md' | wc -l)"
    echo "H1 Headers: $(rg '^# ' --type md . -c | awk -F: '{sum+=$2} END {print sum}')"
    echo "Todos: $(rg '- \[ \]' --type md . -c | awk -F: '{sum+=$2} END {print sum}')" 
    echo "Code blocks: $(rg '^```' --type md . -c | awk -F: '{sum+=$2} END {print sum}')"
}

# Execution time: ~0.05s for 358 files
```

#### Targeted MQ Usage  
```bash
# Use MQ only where its structural analysis adds value
smart_mq_usage() {
    local file="$1"
    
    # Quick text-based filtering first
    if rg -q "- \[ \]" "$file"; then
        echo "=== Todos in $file ==="
        mq '.list' "$file" | grep "\[ \]"  # Clean structural output
    fi
    
    if rg -q '^```' "$file"; then  
        echo "=== Code blocks in $file ==="
        mq '.code' "$file"  # Preserves full code block structure
    fi
}
```

### Memory Usage Guidelines

```bash
# Monitor memory usage for large operations
check_memory_usage() {
    echo "Testing MQ memory usage..."
    
    # Small dataset: MQ is fine
    if [ $(find . -name "*.md" | wc -l) -lt 50 ]; then
        echo "✅ Small dataset, MQ memory usage acceptable"
    
    # Large dataset: prefer streaming tools
    elif [ $(find . -name "*.md" | wc -l) -gt 200 ]; then
        echo "⚠️ Large dataset, prefer ripgrep for memory efficiency"
        echo "MQ estimated memory: ~$(( $(find . -name "*.md" | wc -l) * 2 ))MB"
        echo "ripgrep estimated memory: ~50MB"
    fi
}
```

### Updated Tool Selection Matrix

| Task Type | Small Vault (<100 files) | Medium Vault (100-500) | Large Vault (500+) |
|-----------|-------------------------|------------------------|-------------------|
| Header extraction | `mq '.h1'` | `rg '^# '` ✅ | `rg '^# '` ✅ |
| Todo discovery | `mq '.list' \| grep '\[ \]'` | `rg '- \[ \]'` ✅ | `rg '- \[ \]'` ✅ |
| Code analysis | `mq '.code'` | `rg '^```'` + `mq` targeted | `rg '^```'` ✅ |
| Bulk stats | `mq` acceptable | `rg` + `awk` ✅ | `rg` + `awk` ✅ |
| Clean extraction | `mq` ✅ | `mq` on specific files | `mq` on specific files |

**Key Insight:** MQ shines for **clean extraction** on **specific files**, while ripgrep dominates **bulk discovery** and **statistics**.

## Robust Workflow Pattern

### 1. Test-First Approach
```bash
# ALWAYS test on single file first
test_mq() {
    local query="$1" file="$2"
    echo "Testing: mq '$query' $file"
    mq "$query" "$file" 2>/dev/null || {
        echo "❌ MQ failed, falling back to grep/sed"
        return 1
    }
}
```

### 2. Graceful Fallback
```bash
# Extract headers with fallback
extract_headers() {
    local file="$1"
    mq '.h1' "$file" 2>/dev/null || {
        echo "⚠️ MQ failed, using grep fallback"
        grep -E "^#+ " "$file"
    }
}
```

### 3. Hybrid Approach (Recommended)
```bash
# Use MQ for structure, Unix tools for processing
analyze_markdown() {
    local file="$1"
    
    echo "=== Headers ==="
    mq '.h1' "$file" 2>/dev/null | nl
    
    echo "=== Todo Items ==="  
    mq '.list' "$file" 2>/dev/null | grep -E "\- \[ \]" | wc -l
    
    echo "=== Code Languages ==="
    mq '.code' "$file" 2>/dev/null | grep -o '```[a-z]*' | sort | uniq -c
}
```

## Verified Working Examples

### Basic Extraction (100% Reliable)
```bash
# Headers by level
mq '.h1' README.md              # Get all H1 headers
mq '.h2' docs/*.md              # Get all H2 headers from multiple files

# Code blocks
mq '.code' file.md              # Get all code blocks
mq '.code' docs/ | head -5      # First 5 code blocks from directory

# Lists and links
mq '.list' TODO.md              # Get all list items  
mq '.link' file.md              # Get all links
```

### Combined with Unix Tools (Recommended)
```bash
# Find unchecked todos
mq '.list' file.md | grep "\[ \]" | wc -l

# Code block statistics
mq '.code' docs/*.md | grep -o '```[a-z]*' | sort | uniq -c | sort -nr

# Header table of contents
mq '.h2' README.md | sed 's/^## /- /' | nl

# Find specific content in headers
mq '.h1' docs/*.md | grep -i "installation"
```

## Error Handling & Troubleshooting

### Common Error Patterns
```bash
# ❌ These patterns don't work in mq 0.2.21:
mq 'select(.type == "list")'            # No .type syntax
mq '.[0:5]'                             # No slice notation  
mq 'map(select(contains(., "text")))'   # Complex syntax fails
```

### Debugging Strategy
```bash
# Step-by-step debugging
debug_mq() {
    local query="$1" file="$2"
    
    # 1. Check basic syntax
    echo "Testing basic: mq '$query' $file"
    mq "$query" "$file" 2>&1 | head -3
    
    # 2. Check file exists and is readable
    [ -r "$file" ] || echo "❌ File not readable: $file"
    
    # 3. Fallback
    echo "Fallback available: grep, sed, awk"
}
```

## Performance Considerations

### File Size Guidelines
```bash
# Check file size before using MQ
check_file_size() {
    local file="$1"
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    
    if [ "$size" -gt 1048576 ]; then  # 1MB
        echo "⚠️ Large file ($size bytes), consider grep instead"
        return 1
    fi
}
```

### Batch Processing
```bash
# Process multiple files efficiently
process_docs() {
    find docs -name "*.md" | while read -r file; do
        echo "Processing: $file"
        mq '.h1' "$file" 2>/dev/null || echo "❌ Skipped: $file"
    done
}
```

## Integration with Existing Tools

### Marksman MCP Integration
```bash
# Use MQ for basic extraction, Marksman MCP for semantic operations
extract_then_analyze() {
    local file="$1"
    
    # Quick structure with MQ
    mq '.h1' "$file" > headers.tmp
    mq '.code' "$file" > code.tmp
    
    # Semantic analysis with Marksman MCP (if available)
    # ... use MCP tools for complex operations
    
    # Cleanup
    rm -f *.tmp
}
```

### CLI Pipeline Patterns
```bash
# MQ → grep → sed → sort pipeline
markdown_stats() {
    local dir="$1"
    
    echo "=== Documentation Analysis ==="
    find "$dir" -name "*.md" -exec mq '.h1' {} \; | \
        grep -v '^#' | \
        sed 's/^# //' | \
        sort | \
        uniq -c | \
        sort -nr
}
```

## Tool Selection Matrix (Updated)

| Task Type | Primary Tool | Fallback | Reason |
|-----------|-------------|-----------|--------|
| Header extraction | `mq '.h1'` | `grep '^# '` | MQ preserves formatting |
| Todo extraction | `mq '.list' \| grep '\[ \]'` | `grep '\- \[ \]'` | Hybrid approach works best |
| Code block extraction | `mq '.code'` | `grep -A10 '\`\`\`'` | MQ handles structure better |
| Complex filtering | `grep/ripgrep` | `mq + unix` | grep faster for complex patterns |
| Bulk text search | `ripgrep` | `grep` | Performance over structure |
| Format conversion | `mq + pandoc` | `pandoc` | MQ for preprocessing |

## Key Lessons Learned

### ✅ MQ Strengths
1. **Clean markdown extraction** - Preserves formatting perfectly
2. **Simple selectors work reliably** - `.h1`, `.code`, `.list` always work
3. **Good for single files** - Performance is acceptable
4. **Combines well with Unix tools** - Excellent in pipelines

### ⚠️ MQ Limitations  
1. **Complex syntax is brittle** - Advanced queries often fail
2. **Not exactly like jq** - Don't assume jq patterns work
3. **Error messages can be cryptic** - Hard to debug complex queries
4. **Version-dependent behavior** - Test before deploying

### 🔧 Best Practices
1. **Start simple** - Use basic selectors first
2. **Test incrementally** - Build complexity gradually
3. **Have fallbacks** - Always provide grep alternatives
4. **Combine tools** - MQ + Unix tools = powerful
5. **Document working patterns** - Save verified examples

## Emergency Fallback Commands

When MQ fails, use these reliable alternatives:

```bash
# Headers
grep -E "^#+\\s" file.md

# Code blocks  
grep -E "^\\`{3}" file.md

# Todo items
grep -E "^\\s*- \\[.\\]" file.md

# Links
grep -oE "\\[.*\\]\\(.*\\)" file.md
```

## Final Recommendation

**Progressive Enhancement Approach:**

1. **Start with MQ basics** - Use simple selectors
2. **Combine with Unix tools** - Leverage the best of both  
3. **Test before trusting** - Verify complex patterns work
4. **Keep fallbacks ready** - Always have grep alternatives
5. **Document successes** - Save working patterns for reuse

**Use MQ for structure, Unix tools for processing** - This hybrid approach provides the most reliable results.