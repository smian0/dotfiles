# Research Skill Agents

This directory contains specialized agents used by the research skill. These agents are symlinked to `~/.claude/agents/` to make them discoverable by Claude.

## Agent Roster

| Agent | Phase | Role | Execution |
|-------|-------|------|-----------|
| `research-web-researcher.md` | Phase 1 | Multi-source web research | Parallel (4 instances) |
| `research-fact-checker.md` | Phase 2 | Source validation & credibility | Sequential |
| `research-analyst.md` | Phase 3 | Deep analysis & insights | Sequential |
| `research-synthesizer.md` | Phase 4 | Report generation | Sequential |

## Installation

To symlink these agents to `~/.claude/agents/`:

```bash
cd ~/.claude/skills/research
./scripts/install-agents.sh
```

This creates symlinks:
- `~/.claude/agents/research-web-researcher.md` → `skills/research/agents/research-web-researcher.md`
- `~/.claude/agents/research-fact-checker.md` → `skills/research/agents/research-fact-checker.md`
- `~/.claude/agents/research-analyst.md` → `skills/research/agents/research-analyst.md`
- `~/.claude/agents/research-synthesizer.md` → `skills/research/agents/research-synthesizer.md`

## Uninstallation

To remove symlinks:

```bash
cd ~/.claude/skills/research
./scripts/uninstall-agents.sh
```

## Usage

These agents are invoked automatically by the research skill during their respective phases. They can also be invoked directly if needed.

## Execution Order

1. **Phase 0**: Initialization (no agents)
2. **Phase 1**: ⚡ **Parallel** - 4 x `research-web-researcher` (different angles)
3. **Phase 2**: Sequential - 1 x `research-fact-checker`
4. **Phase 3**: Sequential - 1 x `research-analyst`
5. **Phase 4**: Sequential - 1 x `research-synthesizer`

## Namespace

All agents are prefixed with `research-` to:
- Clearly associate them with the research skill
- Prevent naming conflicts with other skills/agents
- Enable vertical slicing (all research components in one place)
