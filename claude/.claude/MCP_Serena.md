# Serena MCP Server

**Purpose**: Semantic code understanding with LSP integration and project memory

## Triggers
- Symbol operations: rename, find references, navigate to definition
- Code exploration in large projects (>50 files)
- Need to understand code relationships and dependencies
- Editing code semantically (replace function/class bodies)
- Token-efficient code reading (avoid reading entire files)

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
