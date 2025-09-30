# Claude Code Agents

This directory contains custom agents for Claude Code, organized by category.

## Directory Structure

```
.claude/agents/
├── meta/                      # Meta-framework agents (multi-agent system generation)
│   ├── context-architect.md
│   ├── domain-analyzer.md
│   ├── meta-multi-agent.md
│   ├── meta-sub-agent.md
│   ├── orchestrator-builder.md
│   └── parallel-coordinator.md
│
├── research/                  # Research and fact-checking agents
│   ├── web-researcher.md
│   ├── fact-checker.md
│   ├── research-planner.md
│   ├── research-planning-agent.md
│   ├── report-writer.md
│   ├── report-synthesizer.md
│   └── report-critique-agent.md
│
├── trading/                   # Technical analysis agents
│   ├── daily-chart-agent.md
│   ├── 4hour-chart-agent.md
│   ├── hourly-chart-agent.md
│   └── confluence-agent.md
│
└── [root-level symlinks]     # For direct @agent invocation
    ├── web-researcher.md -> research/web-researcher.md
    ├── fact-checker.md -> research/fact-checker.md
    ├── research-planner.md -> research/research-planner.md
    ├── daily-chart-agent.md -> trading/daily-chart-agent.md
    ├── 4hour-chart-agent.md -> trading/4hour-chart-agent.md
    ├── hourly-chart-agent.md -> trading/hourly-chart-agent.md
    └── confluence-agent.md -> trading/confluence-agent.md
```

## Agent Invocation Methods

### Method 1: Direct Invocation with `@agent` Syntax

For agents symlinked at root level:

```
@web-researcher Research the latest advances in quantum computing
@fact-checker Verify this claim: "Python is faster than C++"
@daily-chart-agent Analyze SPY on daily timeframe
```

**Requirements**:
- Agent file must exist at `.claude/agents/AGENT-NAME.md` (root level)
- Subdirectory agents need symlinks (already configured)

### Method 2: Via Slash Commands (Recommended for Workflows)

Use orchestrator commands that internally spawn agents:

```bash
/research How does quantum computing work?
/multi-agent Create a restaurant management system
/multi-timeframe-levels SPY QQQ
```

### Method 3: Programmatic via Task() (For Custom Workflows)

Only works for registered agent types:

```javascript
Task(
  subagent_type="context-architect",  // Must be registered
  description="Build context system",
  prompt="..."
)
```

**Registered agent types** (in Claude Code's Initial Instructions):
- ✅ `general-purpose`
- ✅ `context-architect`
- ✅ `domain-analyzer`
- ✅ `orchestrator-builder`
- ✅ `parallel-coordinator`
- ❌ `web-researcher` (use Method 1 or 2 instead)
- ❌ `meta-sub-agent` (not registered)
- ❌ All trading agents (use Method 1 or 2 instead)

## Stow Integration

This directory is managed via GNU Stow from the dotfiles repository:

```bash
# From dotfiles root
stow claude

# This creates symlinks:
~/.claude/agents/web-researcher.md -> ../../dotfiles/claude/.claude/agents/web-researcher.md
~/.claude/agents/research/ -> ../../dotfiles/claude/.claude/agents/research/
~/.claude/agents/trading/ -> ../../dotfiles/claude/.claude/agents/trading/
# ... etc
```

### Adding New Agents

**To add a new agent that can be invoked with `@agent`:**

1. Create the agent file in appropriate subdirectory:
   ```bash
   vim claude/.claude/agents/research/my-new-agent.md
   ```

2. Create symlink at root level (in dotfiles):
   ```bash
   cd claude/.claude/agents/
   ln -s research/my-new-agent.md my-new-agent.md
   ```

3. Re-stow to update home directory:
   ```bash
   cd ~/dotfiles
   stow -R claude
   ```

4. Verify:
   ```bash
   ls -la ~/.claude/agents/my-new-agent.md
   ```

**To add a new agent for slash command use only:**

1. Create the agent file in subdirectory (no symlink needed)
2. Reference it in the slash command's orchestration logic
3. Re-stow to sync changes

## Agent Categories

### Meta Agents
Used by `/multi-agent` command to generate multi-agent systems.

**Key agents**:
- `domain-analyzer`: Analyzes domain patterns and workflows
- `context-architect`: Designs context management systems
- `orchestrator-builder`: Creates command orchestrators
- `parallel-coordinator`: Designs parallel execution strategies

### Research Agents
Used by `/research` command for comprehensive research workflows.

**Key agents**:
- `web-researcher`: Universal web research specialist (⭐ use directly)
- `fact-checker`: Cross-reference and validation (⭐ use directly)
- `research-planner`: Break down research into plans (⭐ use directly)
- `report-writer`: Synthesize findings into reports
- `report-synthesizer`: Combine multiple research streams
- `report-critique-agent`: Quality assurance for reports

### Trading Agents
Used by `/multi-timeframe-levels` command for technical analysis.

**Key agents**:
- `daily-chart-agent`: Daily timeframe for swing trading (⭐ use directly)
- `4hour-chart-agent`: 4-hour timeframe for day trading (⭐ use directly)
- `hourly-chart-agent`: 1-hour timeframe for scalping (⭐ use directly)
- `confluence-agent`: Multi-timeframe synthesis

**⭐ = Available for direct `@agent` invocation**

## Agent Frontmatter Format

All agents must include YAML frontmatter:

```yaml
---
name: agent-name
description: What this agent does
tools: Tool1, Tool2, Tool3
model: sonnet
color: cyan
---

# Agent content here
```

**Required fields**:
- `name`: Agent identifier (must match filename without .md)
- `description`: Brief description of agent purpose
- `tools`: Comma-separated list of Claude Code tools
- `model`: Model to use (typically "sonnet")

**Optional fields**:
- `color`: Display color in UI

## Troubleshooting

### "Agent type 'X' not found" when using Task()

**Problem**: Only specific agents are registered in Claude Code's system.

**Solution**: Use direct `@agent` invocation or slash commands instead.

### Agent not showing up with `@` syntax

**Problem**: Agent file not at root level of `.claude/agents/`.

**Solution**: Create symlink at root level and re-stow:
```bash
cd ~/dotfiles/claude/.claude/agents/
ln -s subdirectory/agent-name.md agent-name.md
cd ~/dotfiles && stow -R claude
```

### Changes to agent not reflected

**Problem**: You edited the file in home directory instead of dotfiles.

**Solution**: Always edit in `~/dotfiles/claude/.claude/agents/`, then re-stow:
```bash
cd ~/dotfiles && stow -R claude
```

## Related Documentation

- **Commands**: `../.claude/commands/README.md`
- **Multi-Agent Framework**: `meta/README.md`
- **Research System**: `research/README-multi-agent-research.md`
- **Trading System**: `trading/README.md`

---

**Managed by**: GNU Stow from `~/dotfiles/claude/` package
**Last Updated**: 2025-09-30