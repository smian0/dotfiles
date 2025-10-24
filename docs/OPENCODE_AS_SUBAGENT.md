# Using OpenCode as a Subagent from Claude Code

This guide explains how to delegate tasks from Claude Code to OpenCode while maintaining context isolation.

## Overview

Claude Code can invoke OpenCode to:
- Process tasks in isolated context
- Leverage OpenCode-specific features
- Use different models/configurations
- Enable parallel processing

## Architecture

```
Claude Code (Parent)
    ↓ delegates
OpenCode (Subagent)
    ↓ returns results
Claude Code (receives & integrates)
```

**Key Benefits:**
- ✅ Context isolation (OpenCode doesn't see Claude's conversation history)
- ✅ Different tooling (OpenCode has its own MCP servers)
- ✅ Model flexibility (use different models per task)
- ✅ Parallel execution (multiple OpenCode instances)

## Implementation Options

### Option 1: Direct Bash Execution (Simplest)

**How it works**: Use Claude Code's Bash tool to run `oc` commands

**Setup**: None required (works immediately)

**Usage**:
```bash
# Basic execution
oc run "Research React 19 features"

# With command
oc run --command research "Compare Next.js vs Remix"

# With specific agent
oc run --agent python-expert "Review this code"

# With custom model
oc run --model ollamat/gpt-oss:120b "Explain quantum computing"

# JSON output for parsing
oc run --format json "Generate API documentation"
```

**Pros**:
- No setup required
- Direct control
- Fast iteration

**Cons**:
- Manual output parsing
- Less discoverable
- No tool suggestions from Claude

### Option 2: Agent Delegation (Recommended)

**How it works**: Use `@opencode-delegate` agent for structured delegation

**Setup**: Already configured at `~/.claude/agents/opencode-delegate.md`

**Usage**:
```
@opencode-delegate Research the performance characteristics of different database connection pools
```

**Pros**:
- Clear delegation pattern
- Agent appears in @ suggestions
- Context-aware instructions

**Cons**:
- Still uses Bash underneath
- Manual result handling

### Option 3: Skill-Based Delegation (Best for Complex Workflows)

**How it works**: Use `opencode-delegate` skill with patterns and best practices

**Setup**: Already configured at `~/.claude/skills/opencode-delegate/SKILL.md`

**Usage**:
```
Use the opencode-delegate skill to perform comprehensive research on React Server Components
```

**Pros**:
- Built-in workflow patterns
- Error handling guidance
- Output processing templates
- Best practices included

**Cons**:
- Requires understanding skill system
- More verbose invocation

### Option 4: MCP Server Integration (NOT RECOMMENDED ❌)

**How it works**: MCP server provides `opencode_run` tool to Claude Code

**❌ Problem**: OpenCode takes 40+ seconds to execute, but MCP client times out after ~10-30 seconds. **This approach doesn't work reliably.**

**Why it fails**:
- OpenCode startup time is inherently slow (40+ seconds even with `-T` flag)
- MCP client timeout is not configurable from server side
- FastMCP timeout settings don't help (timeout is on Claude Code's client side)

**Setup** (for reference only, not recommended):

1. **Create MCP configuration** in `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "opencode-proxy": {
      "command": "npx",
      "args": [
        "reloaderoo",
        "proxy",
        "--",
        "uvx",
        "--from",
        "fastmcp",
        "fastmcp",
        "run",
        "/Users/smian/.claude/mcp_servers/opencode_proxy/server.py"
      ],
      "env": {
        "MCPDEV_PROXY_AUTO_RESTART": "true"
      }
    }
  }
}
```

2. **Restart Claude Code**

3. **Verify tools available**:
   - `opencode_run` - Execute tasks in OpenCode
   - `opencode_list_commands` - List available commands
   - `opencode_list_agents` - List available agents

**Usage**:
```
Can you use opencode_run to research TypeScript 5.0 features?
```

Claude Code will automatically:
1. Recognize the tool is available
2. Structure the call correctly
3. Parse the JSON output
4. Present results cleanly

**Pros**:
- Native tool integration
- Automatic discovery
- Clean output parsing
- Type-safe parameters
- Best error handling

**Cons**:
- Requires MCP configuration
- Additional server process
- Slightly more complex setup

## Comparison Matrix

| Feature | Bash | Agent | Skill | MCP |
|---------|------|-------|-------|-----|
| Setup Required | None | None | None | MCP Config |
| Discoverability | Low | Medium | Medium | High |
| Output Parsing | Manual | Manual | Guided | Automatic |
| Error Handling | Basic | Basic | Guided | Robust |
| Context Awareness | None | Medium | High | High |
| Tool Suggestions | No | Yes (@) | Yes | Yes (tool) |
| Best For | Quick tasks | Delegation | Workflows | Production |

## Recommended Approach by Use Case

### Quick One-Off Tasks
**Use**: Direct Bash
```bash
oc run "Quick research query"
```

### Structured Delegation
**Use**: Agent
```
@opencode-delegate Perform this task
```

### Complex Multi-Step Workflows
**Use**: Skill
```
Use opencode-delegate skill for this complex workflow
```

### Production/Frequent Use
**Use**: MCP Server
```
Use opencode_run tool to process this
```

## Complete Example Workflow

### Scenario: Research → Implement → Review

**Step 1: Research (via OpenCode)**
```bash
# Claude Code delegates research to OpenCode
oc run --command research "Best practices for PostgreSQL connection pooling"

# OpenCode performs web research in isolation
# Returns structured findings
```

**Step 2: Implement (in Claude Code)**
```
# Claude Code implements based on research
# Uses its full context and conversation history
```

**Step 3: Review (via OpenCode with different model)**
```bash
# Send implementation to OpenCode for review with different model
oc run --agent security-engineer --model ollamat/deepseek-v3.1:671b "Review security of this connection pool implementation"
```

## Advanced Patterns

### Parallel Processing
```bash
# Start multiple OpenCode instances for independent tasks
oc run --command analyze "Analyze module A" &
PID1=$!

oc run --command analyze "Analyze module B" &
PID2=$!

# Wait for both
wait $PID1 $PID2
```

### File-Based Communication (for large outputs)
```bash
# Redirect output to file
oc run --command research "Complex query" > /tmp/oc-result.txt

# Claude Code reads file
# Read /tmp/oc-result.txt
```

### Chained Delegation
```bash
# Research
research_result=$(oc run --command research "Topic X")

# Use research to inform next task
oc run "Based on this research: $research_result, generate implementation"
```

## Environment & Configuration

### OpenCode Inherits
- API keys from `oc` wrapper script
- MCP server configurations from sync
- Skills from symlinked directory
- Commands from synced directory

### OpenCode Does NOT Inherit
- Claude Code's conversation history
- Claude Code's accumulated context
- Current task/todo state
- User's specific instructions in active session

## Troubleshooting

### Issue: OpenCode not found
```bash
which oc  # Should show ~/dotfiles/bin/oc
```

### Issue: No output returned
- Check OpenCode logs
- Test manually: `oc run "test message"`
- Verify command exists: `oc command list`

### Issue: Context pollution
- This is **by design** - contexts are isolated
- If you need shared context, use Claude Code directly
- Use file-based communication for data sharing

### Issue: Timeout
- Default timeout: 5 minutes
- Increase in MCP server.py if needed
- Break into smaller sub-tasks

## Files Created

```
dotfiles/
├── claude/.claude/
│   ├── agents/
│   │   └── opencode-delegate.md          # Agent for delegation
│   ├── skills/
│   │   └── opencode-delegate/
│   │       └── SKILL.md                   # Skill with patterns
│   └── mcp_servers/
│       └── opencode_proxy/
│           ├── server.py                  # MCP server
│           ├── pyproject.toml            # Dependencies
│           └── README.md                 # MCP docs
└── docs/
    └── OPENCODE_AS_SUBAGENT.md          # This file
```

## Next Steps

1. **Try direct execution**: `oc run "Hello from Claude Code"`
2. **Test agent**: `@opencode-delegate Research something`
3. **Set up MCP** (optional): Add to `.mcp.json` and restart
4. **Experiment with workflows**: Combine approaches as needed

## See Also

- [OpenCode Configuration](../opencode/.config/opencode/opencode.json)
- [Sync Script](../opencode/.config/opencode/scripts/sync-claude.sh)
- [Agent Transformation](../opencode/.config/opencode/scripts/transform-claude-to-opencode.sh)
