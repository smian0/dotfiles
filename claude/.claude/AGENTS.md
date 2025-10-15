# AI Assistant Instructions

> **Note:** This CLAUDE.md file provides instructions for ANY AI assistant (Claude, OpenCode, GitHub Copilot, Cursor, GPT, etc.). The filename remains CLAUDE.md for compatibility but applies universally.

## File Roles & Distinctions

### README.md (For Humans)
**Purpose:** User-facing documentation  
**Content:** What it is, how to use it, features, installation  
**Updates:** Only when user requests or features change  

### CLAUDE.md (For AI Assistants)
**Purpose:** AI maintenance instructions
**Content:** Automation rules, update triggers, verification steps
**Never:** Duplicate README content - reference it instead

## File Editing Rules

**NEVER create new files to avoid fixing issues.**
**ALWAYS persist with the existing file, even through errors.**
Creating files is a LAST RESORT, not a solution.

## Core Reliability Rules

**NEVER state facts without verification.** Check available data/context before making claims.

**Express appropriate uncertainty.** Use 'likely', 'appears', 'seems' for moderate confidence. Reserve definitive statements for verified facts.

**For complex tasks: Break into steps, state your approach, verify each step before proceeding.**

**When an approach fails: Analyze why, try a different method. NEVER repeat the same failing approach.**

**Reference user's previous statements and established context.** Don't make them repeat information.

## README Management Rules

### Never
- Create READMEs without explicit request
- Auto-update without permission  
- Add content that belongs in CLAUDE.md

### Always
- Preserve existing style when editing
- Test commands before documenting
- Add "Last Updated" timestamp

### Update Triggers
1. User explicitly requests
2. Critical info outdated (ask first)
3. Structure significantly changed (ask first)

## Automated Monitoring

### Watch for Changes
Monitor dependency files (e.g., package.json for Node, requirements.txt for Python), build configs, CI/CD files, and directory structure changes. Use language-appropriate patterns.

### On Change Detection
1. Identify project type and language
2. Check if README needs updating
3. Alert user if mismatch found
4. Suggest fix (don't auto-apply)

## Package-Specific Rules

### AI Configuration Package (Example: Claude)
When configuration files change:
```bash
# Run verification script if exists
bash ~/dotfiles/scripts/verify-*-stow.sh
# Update README status section with results
# Alert if symlinks/configs broken
```

### Status Section Format
```markdown
## Current Status
- **Last Verified:** YYYY-MM-DD HH:MM
- **Status:** ✅ Working / ⚠️ Issues
- **Details:** See [CLAUDE.md] for maintenance
```

## MCP Server Development Workflow

### Hot-Reload Instead of Restart
When working with MCP (Model Context Protocol) server code:

**NEVER suggest restarting Claude Code** for MCP server changes.

**ALWAYS use the `restart_server` tool instead:**
1. Make code changes to MCP server files
2. Call the `restart_server` tool (automatically available when using reloaderoo)
3. Test changes immediately - no Claude Code restart needed

### Auto-Restart Configuration (CRITICAL)
**IMPORTANT: When an MCP server is configured with `MCPDEV_PROXY_AUTO_RESTART: "true"` in the `.mcp.json` file:**

**DO NOT suggest ANY restart actions - neither Claude Code restart nor manual `restart_server` tool calls.**

**The server automatically restarts when source files change. You should:**
1. **Acknowledge that changes are saved** and the server will auto-reload
2. **Proceed immediately to test or use the updated functionality**
3. **NEVER wait or ask the user to restart anything**
4. **Simply state:** "The server will automatically reload with your changes. Let me test the updated functionality now."

**This applies to ANY MCP server using reloaderoo with auto-restart enabled, including:**
- Local development servers (e.g., `mcp_markdown`, custom Python/JS servers)
- Servers with `"env": { "MCPDEV_PROXY_AUTO_RESTART": "true" }`
- Any server wrapped with `npx reloaderoo proxy --`

### MCP Server File Patterns
Watch for these patterns that indicate MCP server development:
- Files ending in `*server.py`, `*mcp.py`, `*_server.js`, etc.
- Files in directories like `mcp_servers/`, `servers/`, or containing "mcp" in path
- Files with MCP-related imports (fastmcp, @modelcontextprotocol/sdk, etc.)

### Development Commands
```bash
# Instead of: "Restart Claude Code to pick up changes"
# Use: "Call restart_server tool to reload MCP server"

# Setup pattern in .mcp.json:
"command": "npx",
"args": ["reloaderoo", "proxy", "--", "python3", "server.py"]
```

### Exceptions
Only suggest Claude Code restart when:
- Changing `.mcp.json` configuration file itself
- Adding/removing MCP servers (not modifying existing ones)
- MCP server fails to start initially

## Sub-Agent Development Workflow

**When the user requests to create or edit a Claude Code sub-agent:**

**ALWAYS consult `~/.claude/agents/meta/meta-sub-agent.md` for the authoritative guide on:**
- Proper sub-agent frontmatter structure (name, description, tools, model, color)
- Available tools and when to use them
- Writing effective delegation descriptions
- System prompt best practices
- Advanced features (hooks, output styles, background tasks)

**Quick Reference:**
- Use `@meta-sub-agent` to delegate sub-agent creation
- Follow the documented output format exactly
- Select minimal required tools from available core tools
- Write action-oriented descriptions for automatic delegation

**Location:** `~/.claude/agents/meta/meta-sub-agent.md`

## Cross-References

### In README.md
```markdown
*For maintenance instructions, see [CLAUDE.md]*
```

### In CLAUDE.md  
```markdown
*For user documentation, see [README.md]*
```

## Quick Decision Tree

**User asks about feature?** → Point to README
**User asks about maintenance?** → Point to CLAUDE.md
**Need to document for users?** → Update README
**Need to add automation?** → Update CLAUDE.md
**Content could go either place?** → README for what, CLAUDE for how

## Development Principles

### DRY (Don't Repeat Yourself) & YAGNI (You Aren't Gonna Need It)
- **DRY**: Avoid duplicating code patterns - use functions, templates, or shared utilities instead
- **YAGNI**: Only add features/complexity when actually needed, not "just in case"
- Examples: Reuse existing scripts, reference shared configs, add features only when there's an immediate use case

### Real-World Testing Over Mocking
Prioritize understanding root causes and real end-user scenarios:
- **Avoid mock objects/data** - Use real configurations, real files, real environment conditions
- **Test actual user workflows** - Simulate complete operations from start to finish
- **Debug root causes** - Investigate why something fails instead of mocking around problems
- **End-to-end validation** - Test entire workflows, not just isolated components

### Clean Code & Self-Documentation

**Core Principle: Code should explain itself through clarity, not comments.**

#### Self-Documenting Code First
- Use descriptive names: `calculate_monthly_payment(principal, rate, months)` not `calc(p, r, m)`
- Structure reveals intent: Small, focused functions with clear purposes
- Type hints over type documentation: Use language-native annotations
- Named constants over magic numbers: `MAX_RETRIES = 3` not `3` with a comment

#### Minimal, Purposeful Comments
**Only comment when code cannot be made clearer.**

Use comments ONLY for:
- Non-obvious business logic or domain rules
- Complex algorithms that need explanation
- "Why" decisions were made (not "what" the code does)
- Workarounds or edge cases that aren't apparent

**Never comment:**
- What the code obviously does
- Type information (use type hints)
- Function entry/exit
- Variable assignments that are self-explanatory

#### Lean Docstrings
**Skip redundant descriptions. Document the non-obvious.**

Good docstrings:
- Brief purpose statement for public APIs
- Unexpected behavior or side effects
- Important constraints or requirements
- When to use vs alternatives

Skip:
- Obvious parameter descriptions
- Return types already in type hints
- Restating the function name in prose
- Generic filler text

#### Strategic Logging
**Log meaningful events, not execution traces.**

Good logging:
- State changes: "User authentication failed: invalid token"
- Important decisions: "Falling back to cache, API unavailable"
- Errors with context: "Failed to parse config: missing required field 'api_key'"

Avoid:
- Function entry/exit logs
- Debug breadcrumbs in production code
- Logging every variable value
- Redundant success messages

#### Code Structure Over Comments
**If you need comments to explain code sections, refactor instead.**

Bad:
```python
# Calculate the total with tax
subtotal = sum(item.price for item in cart)
tax_rate = 0.08
tax = subtotal * tax_rate
total = subtotal + tax
```

Good:
```python
def calculate_total_with_tax(cart, tax_rate=0.08):
    subtotal = sum(item.price for item in cart)
    return subtotal * (1 + tax_rate)
```

#### Examples

**❌ Over-Commented Verbose Code:**
```python
def process_user(user_id):
    """
    Process a user by their ID.

    Args:
        user_id (int): The ID of the user to process

    Returns:
        dict: A dictionary containing the processed user data
    """
    # Log that we're starting to process the user
    logger.debug(f"Starting to process user {user_id}")

    # Get the user from the database
    user = db.get_user(user_id)

    # Check if user exists
    if not user:
        # Log error if user not found
        logger.error(f"User {user_id} not found")
        return None

    # Process the user data
    processed = {
        'name': user.name,  # Get user name
        'email': user.email,  # Get user email
        'active': True  # Set active status
    }

    # Log success
    logger.debug(f"Successfully processed user {user_id}")

    # Return the processed data
    return processed
```

**✅ Clean Self-Documenting Code:**
```python
def process_user(user_id: int) -> dict | None:
    user = db.get_user(user_id)

    if not user:
        logger.warning(f"User {user_id} not found")
        return None

    return {
        'name': user.name,
        'email': user.email,
        'active': True
    }
```

**When Comments ARE Appropriate:**
```python
def calculate_compound_interest(principal: float, rate: float, years: int) -> float:
    # Using continuous compounding formula: A = Pe^(rt)
    # More accurate for high-frequency compounding than discrete formula
    return principal * math.exp(rate * years)

def retry_with_backoff(func, max_attempts: int = 3):
    # Exponential backoff prevents thundering herd problem
    # when multiple clients retry failed requests simultaneously
    for attempt in range(max_attempts):
        try:
            return func()
        except TransientError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    raise MaxRetriesExceeded()
```

## README Quality Standards

### Universal Structure
```markdown
# Project Name
One-line description

## Quick Start / TLDR
Fastest way to get running (3-5 lines max)

## Features / What's Included
- Bullet points
- Key capabilities
- What makes it unique

## Installation
Step-by-step, tested commands

## Usage
Most common use cases with examples

## Configuration (if needed)
Only essential settings

## Troubleshooting (if needed)
Common issues only

---
Last Updated: DATE
```

### Quality Checklist
- [ ] Title describes what it does
- [ ] Quick start works in <30 seconds
- [ ] All commands copy-pasteable
- [ ] Examples show real usage
- [ ] No duplicate of code comments
- [ ] Links work
- [ ] No user-specific paths

### By Project Type

**CLI Tool:**
Focus on: Commands, flags, examples, output samples

**Library/Package:**
Focus on: API, imports, code examples, types

**Application:**
Focus on: Screenshots, features, requirements, deployment

**Configuration (dotfiles, etc):**
Focus on: What it configures, prerequisites, effects

### Length Guidelines
- **Small project:** 50-100 lines
- **Medium project:** 100-200 lines  
- **Large project:** 200-300 lines max
- **Complex:** Link to docs/ folder

### Never Include
- Implementation details (that's code comments)
- Internal architecture (unless contributing guide)
- Changelog (separate file)
- Personal information
- Untested commands

## Web Research Policy

**IMPORTANT: Delegate web research to @web-researcher agent instead of using WebSearch/WebFetch directly**

### When to Use @web-researcher Agent

Use `@web-researcher` for:
- ✅ Documentation lookup requiring multiple sources
- ✅ Comprehensive research on any topic
- ✅ Comparing tools, frameworks, or approaches
- ✅ Finding code examples and implementation patterns
- ✅ Investigating best practices or recent developments
- ✅ Any research requiring 3+ sources or deep analysis

### When Direct WebSearch/WebFetch Is OK

Use WebSearch/WebFetch directly ONLY for:
- Single fact verification (e.g., "What's the current Fed Funds rate?")
- Quick URL validation (checking if a link works)
- Immediate simple queries during active work

### Benefits of Delegating to @web-researcher

- **Research rigor**: Adversarial search, source diversity, primary source tracing
- **Context preservation**: Returns concise summaries (2-5K tokens) instead of raw content
- **Quality assessment**: Evaluates source credibility and recency
- **Structured output**: Clear sections, bullet points, source URLs

**Rule of thumb**: Use `@web-researcher` for comprehensive research. Use direct tools for quick single-fact lookups.

## Emergency Recovery

If README deleted/corrupted:
1. Check `git log README.md`
2. Restore from git history
3. If no backup, ask before recreating
4. Use CLAUDE.md rules to rebuild

---
*Remember: README = What (users), CLAUDE = How (AI)*

# ===================================================
# SuperClaude Framework Components
# ===================================================

# Core Framework
@PRINCIPLES.md
@RESEARCH_CONFIG.md
@RULES.md

# Behavioral Modes
@MODE_Brainstorming.md
@MODE_Business_Panel.md
@MODE_DeepResearch.md
@MODE_Introspection.md
@MODE_Orchestration.md
@MODE_Task_Management.md
@MODE_Token_Efficiency.md

# MCP Documentation
@MCP_Context7.md
@MCP_Serena.md
