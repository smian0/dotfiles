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

**NEVER automatically create analysis, summary, or documentation files.**
Only create these when the user explicitly requests them with phrases like:
- "Create an analysis document"
- "Write a summary"
- "Generate a report"
- "Document this"

**DO NOT** use phrases like "Let me create a comprehensive analysis..." or "I'll document this..." unless explicitly asked.

**NEVER add docstrings or comments to code unless explicitly requested.**
Write self-documenting code instead:
- Use clear, descriptive variable and function names
- Keep functions focused and simple
- Only add comments/docstrings when the user specifically asks for documentation

## Core Reliability Rules

**NEVER state facts without verification.** Check available data/context before making claims.

**Express appropriate uncertainty.** Use 'likely', 'appears', 'seems' for moderate confidence. Reserve definitive statements for verified facts.

**For complex tasks: Break into steps, state your approach, verify each step before proceeding.**

**When an approach fails: Analyze why, try a different method. NEVER repeat the same failing approach.**

**Reference user's previous statements and established context.** Don't make them repeat information.

## Refactoring Policy

**Do NOT maintain backwards compatibility unless explicitly requested.**

Make breaking changes freely:
- Use modern language features and best practices
- Remove deprecated patterns
- Prioritize clean, idiomatic code

## File Path References

**Use project-relative paths in responses** (e.g., `src/app.py`, `.claude/config.json`)

**Why:** Clickable in IDE. Bare filenames and absolute paths often aren't.

**Exceptions:**
- Current directory files when context is clear
- Hypothetical examples
- Tool arguments (follow tool requirements)

## README Management Rules

### Never
- Create READMEs without explicit request
- Auto-update without permission  
- Add content that belongs in CLAUDE.md
- Create analysis, summary, or report files proactively
- Offer to "create a comprehensive analysis" unless asked

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

**NEVER suggest IDE restart for MCP server code changes.**

**With auto-restart enabled** (`MCPDEV_PROXY_AUTO_RESTART: "true"` in `.mcp.json`):
- Server auto-reloads on file save
- Proceed immediately to test - no restart needed

**Without auto-restart:**
- Use `restart_server` tool (when using reloaderoo)
- Test changes immediately

**MCP server file patterns:**
- `*server.py`, `*mcp.py`, `*_server.js`
- Directories: `mcp_servers/`, `servers/`, or paths containing "mcp"
- MCP imports: `fastmcp`, `@modelcontextprotocol/sdk`

**Only suggest IDE restart when:**
- Changing `.mcp.json` configuration itself
- Adding/removing MCP servers
- Initial MCP server startup failure

## AI Agent Development Workflow

**When the user requests to create or edit AI assistant agents/personas:**

**If using Claude Code:** Consult `~/.claude/agents/meta/meta-sub-agent.md` for the authoritative guide on:
- Proper agent frontmatter structure (name, description, tools, model, color)
- Available tools and when to use them
- Writing effective delegation descriptions
- System prompt best practices
- Advanced features (hooks, output styles, background tasks)

**For other IDEs (Cursor, etc.):** Adapt the following principles:
- Define clear agent purpose and capabilities
- Specify available tools/functions for the agent
- Write concise, action-oriented descriptions
- Follow IDE-specific agent configuration formats

**IDE-Specific Configuration Locations:**
- **Claude Code:** `~/.claude/agents/` or project `.claude/agents/`
- **Cursor:** `.cursorrules` or `.cursor/agents/`
- **Other IDEs:** Consult IDE-specific documentation for agent configuration

### Available Cloud Models for Agents

Ollama cloud models available at `http://localhost:11434` or `http://localhost:11434/v1`.

| Model ID | Context | Tok/s | Best For | Tools | Notes |
|----------|---------|-------|----------|-------|-------|
| `gpt-oss:120b-cloud` | 128K | **174** | General purpose, research, high-throughput | ✅ | Fastest, most verbose |
| `deepseek-v3.1:671b-cloud` | 160K | **56** | Reasoning, analysis, balanced tasks | ✅ | Hybrid thinking mode |
| `qwen3-coder:480b-cloud` | 256K | **39** | Code generation, software engineering | ✅ | Best for coding |
| `glm-4.6:cloud` | 198K | **25** | Autonomous agents, search, structured output | ✅ | Requires `ollama pull` first |
| `kimi-k2:1t-cloud` | 256K | **15** | Frontend dev, UI tasks, concise responses | ❓ | Slowest, 1T MoE |
| `qwen3-vl:235b-cloud` | 125K | N/A | Vision, OCR, GUI, multimodal | ✅ | Images/video, 32-lang OCR |

**Usage:** Free under preview caps • Requires Ollama v0.12+ • Performance varies by system load

## Skill Development Rules

**When creating or modifying Claude Code skills:**

### File Verification (MANDATORY)

**Every file in a skill MUST be referenced in SKILL.md or deleted.**

Before claiming skill work is complete:
```bash
# Check for unreferenced files (checks all relevant file types)
cd .claude/skills/<skill-name>
find . -type f \( \
  -name "*.md" -o -name "*.py" -o -name "*.sh" -o \
  -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o \
  -name "*.txt" -o -name "*.template" -o \
  -name "Dockerfile" -o -name "docker-compose.yml" \
\) ! -name "SKILL.md" ! -path "*/output/*" ! -path "*/.state/*" ! -path "*/cache/*" | \
while read f; do
  grep -q "$(basename "$f")" SKILL.md || echo "⚠️ Unreferenced: $f"
done
```

**If SKILL.md doesn't load or reference a file, that file is orphaned - DELETE IT.**

### No Redundant Documentation

**Do NOT duplicate content across files:**
- ❌ Copy script implementation details into SKILL.md
- ❌ Duplicate reference file content in SKILL.md
- ❌ Create "for Claude" documentation that SKILL.md never loads
- ✅ Reference bundled resources: `See [file](./path/to/file.md)`
- ✅ Scripts handle implementation, SKILL.md explains invocation

### SKILL.md Length Guidelines

**With scripts:** 50-120 lines (invocation guide)
**Without scripts:** 200-500 lines (workflow procedures)

**If SKILL.md exceeds these with scripts present → likely has duplication → refactor.**

### Optimization Mindset

**Lean skills load only what's needed:**
- Each file serves a documented purpose
- SKILL.md references all bundled resources
- Reference files loaded on demand, not duplicated inline
- Delete files that serve no clear purpose

## Development Principles

### DRY & YAGNI
- **DRY**: Avoid duplicating code patterns - use functions, templates, or shared utilities
- **YAGNI**: Only add features when actually needed, not "just in case"

### Real-World Testing Over Mocking
- Use real configurations, files, and environment conditions
- Test actual user workflows end-to-end
- Debug root causes instead of mocking around problems

### Clean Code & Self-Documentation

**Code should explain itself through clarity, not comments.**

**Self-documenting practices:**
- Descriptive names: `calculate_monthly_payment(principal, rate, months)` not `calc(p, r, m)`
- Type hints over documentation: Use language-native annotations
- Named constants: `MAX_RETRIES = 3` not magic numbers
- Small, focused functions with clear purposes

**Comments only for:**
- Non-obvious business logic or algorithms
- "Why" decisions (not "what" code does)
- Workarounds or edge cases

**Never comment:**
- Obvious code behavior
- Type information (use type hints)
- Function entry/exit
- Self-explanatory assignments

**Lean docstrings:**
- Brief purpose for public APIs
- Unexpected behavior or constraints
- Skip obvious parameters and return types already in type hints

**Strategic logging:**
- Log state changes and errors with context
- Avoid function entry/exit logs and debug breadcrumbs

## README Quality Standards

### Required Sections
1. Title + one-line description
2. Quick start (<30 seconds to run)
3. Features/capabilities
4. Installation (tested commands)
5. Usage examples
6. "Last Updated" timestamp

### Quality Checklist
- [ ] All commands copy-pasteable and tested
- [ ] Examples show real usage
- [ ] No user-specific paths
- [ ] Links work
- [ ] No code implementation details

### Length Guidelines
- Small: 50-100 lines
- Medium: 100-200 lines
- Large: 200-300 max (link to docs/ if longer)

### Never Include
- Implementation details (use code comments)
- Internal architecture (unless contributing)
- Untested commands
- Personal information

## Web Research Policy

**IMPORTANT: Delegate complex web research to specialized research agents/tools instead of using basic web search directly**

### When to Use Specialized Research Agents

Use research agents/delegation (e.g., `@web-researcher` in Claude Code) for:
- ✅ Documentation lookup requiring multiple sources
- ✅ Comprehensive research on any topic
- ✅ Comparing tools, frameworks, or approaches
- ✅ Finding code examples and implementation patterns
- ✅ Investigating best practices or recent developments
- ✅ Any research requiring 3+ sources or deep analysis

### When Direct Web Search Is OK

Use basic web search tools directly ONLY for:
- Single fact verification (e.g., "What's the current Fed Funds rate?")
- Quick URL validation (checking if a link works)
- Immediate simple queries during active work

### Benefits of Delegating Research

- **Research rigor**: Multiple sources, adversarial search, source diversity
- **Context preservation**: Returns concise summaries instead of raw content
- **Quality assessment**: Evaluates source credibility and recency
- **Structured output**: Clear sections, bullet points, source URLs

**Rule of thumb**: Use specialized research agents for comprehensive research. Use direct web search tools for quick single-fact lookups.

**IDE-Specific Research Capabilities:**
- **Claude Code:** `@web-researcher` agent with WebSearch/WebFetch tools
- **Cursor:** Web search via Composer or custom agents
- **Other IDEs:** Consult documentation for research/web search capabilities

## Emergency Recovery

If README deleted/corrupted:
1. Check `git log README.md`
2. Restore from git history
3. If no backup, ask before recreating
4. Use CLAUDE.md rules to rebuild

---
*Remember: README = What (users), CLAUDE = How (AI)*

# MCP Documentation
@MCP_Context7.md
@MCP_Serena.md
@MCP_Zen.md
@MCP_PrivacyPDF.md
