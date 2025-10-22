# Serena MCP Server

**Purpose**: Semantic code understanding with project memory and session persistence

## 🚀 Proactive Usage for Code Work

**ALWAYS use Serena tools when:**
- Exploring code structure (use `get_symbols_overview` before reading files)
- Finding functions/classes (use `find_symbol` instead of grep)
- Understanding relationships (use `find_referencing_symbols`)
- Editing code semantically (use `replace_symbol_body`, `insert_after_symbol`)
- Navigating large codebases (use symbolic tools for token efficiency)

**AVOID reading entire files when you can use Serena's symbolic tools instead.**

## Triggers
- Symbol operations: rename, extract, move functions/classes
- Project-wide code navigation and exploration
- Multi-language projects requiring LSP integration
- Session lifecycle: `/sc:load`, `/sc:save`, project activation
- Memory-driven development workflows
- Large codebase analysis (>50 files, complex architecture)

## Choose When
- **Over Morphllm**: For symbol operations, not pattern-based edits
- **For semantic understanding**: Symbol references, dependency tracking, LSP integration
- **For session persistence**: Project context, memory management, cross-session learning
- **For large projects**: Multi-language codebases requiring architectural understanding
- **Not for simple edits**: Basic text replacements, style enforcement, bulk operations
- **Not for markdown files**: Use Marksman MCP for all .md operations

## Works Best With
- **Morphllm**: Serena analyzes semantic context → Morphllm executes precise edits
- **Sequential**: Serena provides project context → Sequential performs architectural analysis

## Tool Usage Patterns

### Code Exploration Workflow
1. **Start broad**: `get_symbols_overview(file)` - See all top-level symbols
2. **Navigate narrow**: `find_symbol(name, depth=1)` - Get specific symbol and children
3. **Understand context**: `find_referencing_symbols()` - See how it's used
4. **Edit precisely**: `replace_symbol_body()` - Modify the symbol

**Token Efficient**: Serena symbolic tools use 10x less context than reading full files!

### When to Use Which Tool

**Serena Symbolic Tools** (Primary for code):
```python
# Exploring a new file
mcp__serena__get_symbols_overview(file)  # First step - see structure

# Finding specific code
mcp__serena__find_symbol("ClassName/methodName")  # Precise lookup

# Understanding usage
mcp__serena__find_referencing_symbols("function_name")  # Who calls this?

# Editing code
mcp__serena__replace_symbol_body()  # Replace function/class body
mcp__serena__insert_after_symbol()  # Add new function after existing
```

**Traditional Read Tool** (When necessary):
- Config files (JSON, YAML, TOML)
- Documentation files
- Files without LSP support
- When you need to see exact formatting/whitespace

## Examples
```
"rename getUserData function everywhere" → Serena (symbol operation with dependency tracking)
"find all references to this class" → Serena (semantic search and navigation)
"show me the structure of user.py" → Serena (get_symbols_overview - NOT Read tool!)
"understand how authenticate() works" → Serena (find_symbol with depth=1, see children)
"who calls the login function?" → Serena (find_referencing_symbols)
"load my project context" → Serena (/sc:load with project activation)
"save my current work session" → Serena (/sc:save with memory persistence)
"update all console.log to logger" → Morphllm (pattern-based replacement)
"analyze README.md structure" → Marksman (markdown document analysis)
"navigate to Installation header" → Marksman (markdown navigation)
"find wiki-links in documentation" → Marksman (markdown link tracking)
```

