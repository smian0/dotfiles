# OpenCode Delegate: Task Execution vs Code Generation

## The Core Difference

**Claude Code Subagents:**
- Get Claude Code's full system prompt
- Understand they should use tools to execute tasks
- Will WebSearch for news, not write news-fetching code

**OpenCode (default):**
- Gets "You are a coding assistant" system prompt
- Interprets tasks as "write code to solve this"
- Will create scripts, not execute tasks directly

## How to Get OpenCode to Execute Tasks (Not Write Code)

### Option 1: Use Claude Code Directly (Recommended)

If I'm already running in Claude Code, just ask me:

"Fetch top 5 technology news headlines from today"

I have WebSearch tool - no delegation needed.

### Option 2: Explicit Task Instructions

Tell OpenCode what NOT to do:

```bash
oc run -T --model "github-copilot/claude-sonnet-4.5" \
"DO NOT write code or create files. Instead, use available tools to search the web for today's top 5 technology news headlines. Return only the headlines and sources in a numbered list."
```

**Problem:** OpenCode needs WebSearch MCP to actually fetch news.

### Option 3: Add Web Search to OpenCode (Currently Disabled)

Brave Search MCP configured in opencode.json but disabled due to known hang bug.

To enable when bug is fixed:
1. Set "enabled": true for brave_search in mcp section
2. Set "mcp__brave_search__*": true in tools section  
3. Test with news query

**Status:** Waiting for OpenCode Issue #3177 fix

### Option 4: Create Custom OpenCode Agent

Create task-executor agent that prioritizes tool use over code generation.

**Problem:** Still needs web search MCP.

## Current Recommendation

**For news/web tasks:** Use Claude Code directly instead of delegating to OpenCode.

**For code tasks:** OpenCode delegation works excellently.

---
Last Updated: 2025-10-23
