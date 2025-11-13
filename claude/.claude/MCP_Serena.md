# Serena MCP Server

**Purpose**: Semantic code understanding with LSP integration and project memory

## Triggers
- Symbol operations: rename, find references, navigate to definition
- Code exploration in large projects (>50 files)
- Need to understand code relationships and dependencies
- Editing code semantically (replace function/class bodies)
- Token-efficient code reading (avoid reading entire files)
- **Exiting plan mode**: Automatically save plan summary to project memory

## Choose When
- **Over Read tool**: Use `get_symbols_overview` before reading files
- **Over Grep**: Use `find_symbol` for precise symbol lookup
- **For code edits**: Use `replace_symbol_body`, `insert_after_symbol`
- **For relationships**: Use `find_referencing_symbols`
- **Not for**: Simple text edits, pattern replacements, markdown files

## Examples
```
"show me the structure of user.py"
→ get_symbols_overview("user.py") (not Read!)

"find the authenticate function"
→ find_symbol("authenticate")

"who calls the login function?"
→ find_referencing_symbols("login", "auth.py")

"replace the UserManager class"
→ replace_symbol_body("UserManager", "user.py", new_code)
```

## Plan Mode Integration

**When exiting plan mode** (after user approves plan):
1. Capture the plan summary (tasks, file changes, approach)
2. Save to Serena memory with descriptive filename
3. Format: `plan_YYYY-MM-DD_[short-description].md`

**Example workflow**:
```
[Plan mode presents comprehensive implementation plan]

User: "Proceed with the plan"

Claude: "Saving plan to memory before executing..."
→ write_memory("plan_2025-11-13_authentication-refactor.md", plan_content)
→ "Plan saved. Proceeding with implementation..."
```

**Memory file structure**:
```markdown
# Plan: Authentication System Refactor
**Date**: 2025-11-13
**Status**: Approved, in progress

## Objective
[High-level goal]

## Tasks
1. [ ] Task 1 - file1.py
2. [ ] Task 2 - file2.py

## Approach
[Implementation strategy]

## Files to Change
- file1.py: [changes]
- file2.py: [changes]
```

**Benefits**:
- ✅ Plans persist across sessions
- ✅ Track implementation progress
- ✅ Reference previous decisions
- ✅ Version controlled with project
- ✅ Human-readable markdown
