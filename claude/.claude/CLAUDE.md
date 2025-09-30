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

**IMPORTANT: Delegate web research to web-researcher subagent instead of using WebSearch/WebFetch directly**

### When to Use web-researcher Subagent

Use `Task(subagent_type="web-researcher", ...)` for:
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
- Emergency fallback if Task tool unavailable

### Standard Delegation Pattern

```
Task(subagent_type="web-researcher",
     description="Research X topic",
     prompt="Find authoritative sources on X. Focus on Y aspects.
             Synthesize key findings with source attribution...")
```

### Benefits of Delegation

- **Research rigor**: Adversarial search, source diversity, primary source tracing
- **Context preservation**: Returns concise summaries (2-5K tokens) instead of raw content
- **Quality assessment**: Evaluates source credibility and recency
- **Structured output**: Clear sections, bullet points, source URLs

### Research Agents Available

- `web-researcher`: Universal web research (use this for most cases)
- `fact-checker`: Cross-reference and validate specific claims
- `research-planner`: Break down complex research into structured plans
- `research-planning-agent`: Create detailed research plans with parallel streams

**For comprehensive research**: Use the `/research` slash command which orchestrates the full workflow automatically.

**Rule of thumb**: If you find yourself writing multiple WebSearch queries, spawn web-researcher instead.

## Emergency Recovery

If README deleted/corrupted:
1. Check `git log README.md`
2. Restore from git history
3. If no backup, ask before recreating
4. Use CLAUDE.md rules to rebuild

---
*Remember: README = What (users), CLAUDE = How (AI)*