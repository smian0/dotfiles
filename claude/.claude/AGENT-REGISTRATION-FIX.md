# Agent Registration Fix

## Problem

Custom agents like `web-researcher`, `fact-checker`, trading agents, etc. are **not automatically discovered** by Claude Code's Task tool. When trying to use them:

```
Task(subagent_type="web-researcher", ...)
```

You get:
```
Error: Agent type 'web-researcher' not found. Available agents: general-purpose,
statusline-setup, output-style-setup, parallel-coordinator, ...
```

## Root Cause

Claude Code's Initial Instructions (system prompt) contain a hardcoded list of agent types. Custom agents in `.claude/agents/` subdirectories are **not automatically added** to this list.

The built-in agents are:
- `general-purpose`
- `statusline-setup`
- `output-style-setup`
- `parallel-coordinator`
- `context-architect`
- `domain-analyzer`
- `orchestrator-builder`
- `meta-multi-agent`
- `meta-sub-agent`

Custom agents like `web-researcher` exist as files but aren't registered as usable agent types.

## Solutions

### Solution 1: Use Slash Commands (Recommended)

The **proper way** to use custom multi-agent systems is through slash commands:

```bash
# For research workflows
/research [your research query]

# For multi-agent system generation
/multi-agent Create a system for [domain]

# For multi-timeframe trading analysis
/multi-timeframe-levels SPY QQQ
```

These commands internally spawn the correct agents using proper orchestration.

### Solution 2: Use `general-purpose` Agent with Custom Prompts

If you need custom agent behavior in your own workflows:

```python
# Instead of this (won't work):
Task(subagent_type="web-researcher", ...)

# Do this:
Task(
  subagent_type="general-purpose",
  description="Comprehensive web research",
  prompt="""
You are a web research specialist with the following capabilities:

1. Adversarial search: Query multiple angles
2. Source diversity: Check 5+ different sources
3. Primary source tracing: Find original data

Your task: [specific research request]

Research requirements:
- Use WebSearch for broad discovery
- Use WebFetch for detailed content
- Cross-reference findings across sources
- Cite all sources with URLs
- Return concise summary (2-5K tokens)

[Include rest of web-researcher.md instructions here]
  """
)
```

### Solution 3: Direct Tool Usage

For simple cases, use tools directly without agents:

```python
# Simple web search
WebSearch(query="latest inflation data September 2025")

# Fetch specific URL
WebFetch(url="https://example.com/article", prompt="Summarize key points")

# Grounded search (best for current data)
mcp__web-search-prime__webSearchPrime(
  search_query="SPY technical analysis",
  content_size="medium",
  count=10
)
```

## Why Not Just Register Custom Agents?

Claude Code doesn't currently support registering custom agent types through configuration files. The agent type list is **hardcoded in the Initial Instructions**.

Attempts to register via:
- `.agents.json` ❌ (not a Claude Code feature)
- `settings.json` ❌ (no agent registration mechanism)
- Custom MCP server ❌ (agents != MCP tools)

**The only way** to use custom agents is:
1. Through slash commands that orchestrate them
2. By embedding their logic in `general-purpose` agent prompts

## Workarounds for Each Custom Agent

### Web Research Agents

```bash
# Use the /research command instead
/research [query]
```

Or embed in general-purpose:
```python
Task(
  subagent_type="general-purpose",
  description="Research topic X",
  prompt=f"""
{read_file('~/.claude/agents/research/web-researcher.md')}

Your specific task: {research_query}
  """
)
```

### Trading Agents

```bash
# Use the /multi-timeframe-levels command instead
/multi-timeframe-levels SPY
```

Or for individual timeframe:
```python
Task(
  subagent_type="general-purpose",
  description="Daily chart analysis",
  prompt=f"""
{read_file('~/.claude/agents/trading/daily-chart-agent.md')}

Ticker: {ticker}
Output: {output_file}
  """
)
```

## Best Practices

### ✅ DO: Use Slash Commands

```bash
/research How does the Federal Reserve influence interest rates?
/multi-agent Create restaurant management system
/multi-timeframe-levels SPY QQQ
```

**Why**: These commands properly orchestrate custom agents with correct tooling, error handling, and workflow.

### ✅ DO: Use `general-purpose` for Custom Workflows

```python
# When building your own multi-agent system
Task(
  subagent_type="general-purpose",
  description="Analyze data",
  prompt="[Include full agent instructions inline]"
)
```

**Why**: This works reliably and gives you full control over agent behavior.

### ✅ DO: Use Tools Directly for Simple Tasks

```python
# Quick fact lookup
WebSearch(query="What is the current Fed Funds rate?")

# Fetch specific content
WebFetch(url="https://docs.example.com", prompt="Extract API examples")
```

**Why**: Simpler, faster, less overhead for straightforward tasks.

### ❌ DON'T: Try to Use Unregistered Agent Types

```python
# This will fail:
Task(subagent_type="web-researcher", ...)
Task(subagent_type="fact-checker", ...)
Task(subagent_type="daily-chart-agent", ...)
```

**Why**: These agent types aren't registered in Claude Code's system.

### ❌ DON'T: Expect Agent Auto-Discovery

```python
# Won't work even if file exists
# File: ~/.claude/agents/custom/my-agent.md
Task(subagent_type="my-agent", ...)  # Error!
```

**Why**: Claude Code doesn't scan for custom agents automatically.

## Future Improvements

Ideally, Claude Code would support:
1. **Agent registration** via `settings.json`:
   ```json
   {
     "customAgents": {
       "web-researcher": {
         "path": "agents/research/web-researcher.md"
       }
     }
   }
   ```

2. **Automatic agent discovery** from standard directories:
   - `.claude/agents/**/*.md` files auto-registered
   - Agent name derived from YAML frontmatter `name:` field

3. **Agent inheritance** for extending built-in agents:
   ```yaml
   extends: general-purpose
   name: web-researcher
   additionalTools: [WebSearch, WebFetch]
   ```

Until these features exist, use the workarounds above.

## Summary

| Agent Type | How to Use It |
|------------|---------------|
| **web-researcher** | `/research` command or `general-purpose` + instructions |
| **fact-checker** | `/research` command or `general-purpose` + instructions |
| **daily-chart-agent** | `/multi-timeframe-levels` command or `general-purpose` + instructions |
| **4hour-chart-agent** | `/multi-timeframe-levels` command or `general-purpose` + instructions |
| **hourly-chart-agent** | `/multi-timeframe-levels` command or `general-purpose` + instructions |
| **confluence-agent** | `/multi-timeframe-levels` command or `general-purpose` + instructions |

**Golden Rule**: If a custom agent exists, there's probably a slash command for it. Use the command instead of trying to spawn the agent directly.

---

**Last Updated**: 2025-09-30
**Issue**: Custom agents not auto-registered
**Status**: ✅ Workarounds documented