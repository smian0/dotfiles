# VTREE Skill

Enhanced ASCII tree diagram generator for visualizing hierarchical systems with data flow, node references, and semantic indicators.

## What This Skill Does

Generates professional ASCII tree diagrams for:
- Software architectures and system design
- Business processes and workflows
- Data pipelines and ETL processes
- Multiagent systems and AI workflows
- State machines and decision trees
- API request/response flows

## Quick Start

**Trigger phrases:**
- "diagram this workflow"
- "visualize the system architecture"
- "show me a tree of the process"
- "map out the data flow"

**Example request:**
> "Diagram a user authentication flow with OAuth, token validation, and error handling"

## Skill Structure

```
vtree/
├── SKILL.md                           # Main skill instructions (concise ~125 lines)
├── references/                        # Detailed documentation (loaded as needed)
│   ├── emoji-semantics.md            # Complete emoji vocabulary
│   ├── pattern-templates.md          # 6 common patterns with examples
│   └── usage-rules.md                # Structural, semantic, flow rules
├── assets/                            # Quick-start templates
│   ├── template-basic.md             # Simple hierarchy template
│   ├── template-api-workflow.md      # API flow template
│   └── README.md                     # Template usage guide
└── README.md                          # This file
```

## Key Features

### Progressive Disclosure
- **Level 1 (always loaded)**: Skill metadata (~100 words)
- **Level 2 (when triggered)**: Main SKILL.md (~125 lines)
- **Level 3 (as needed)**: Reference files and templates (unlimited)

### Semantic Indicators
- **Emojis**: Visual operation types (📥 input, 🔄 transform, ✅ success, etc.)
- **Text styling**: *Italics* for async, **Bold** for critical paths
- **Explicit flow**: Node references show data flow (`← (source)`, `→ (target)`)

### Pattern Templates
Six ready-to-use patterns for common scenarios:
1. Linear Pipeline - Sequential processing
2. Parallel Processing - Fan-out/fan-in
3. Error Handling - Retry logic and recovery
4. Async Operations - External APIs and background jobs
5. Multiagent System - AI agent coordination
6. State Machine - State transitions

## Architecture Level: 1

This is a **Level 1 skill** (Simple Skill):
- ✅ Single-phase workflow (generate diagram)
- ✅ One domain of expertise (visualization)
- ✅ No delegation needed
- ✅ Linear process: understand → format → output

## Usage Examples

### Basic Request
```
User: "Diagram a simple data pipeline that cleans, transforms, and stores data"

Claude: [Uses vtree skill to generate Linear Pipeline pattern]
```

### Complex Request
```
User: "Show me a multiagent system with research, coding, and QA agents working in parallel"

Claude: [Uses vtree skill with Multiagent System pattern, loads pattern-templates.md reference]
```

### Custom Request
```
User: "I need a diagram for an API with OAuth auth, rate limiting, and webhook handling"

Claude: [Uses vtree skill, combines API workflow template with custom modifications]
```

## Benefits Over Original Hook

The original prompt was in a hook at `docs/hooks/universal-tree-prompt-enhanced.md`.

**As a skill, it's better because:**
1. **On-demand loading**: Only loads when needed (not every session)
2. **Progressive disclosure**: Core instructions + references loaded selectively
3. **Reusable templates**: Assets folder with quick-start templates
4. **Better organization**: Separated concerns (emojis, patterns, rules)
5. **User control**: Explicitly triggered by user request, not automatic
6. **Maintainable**: Easier to update and improve over time

## Related Hooks to Remove

You mentioned hooks that use this. You can now safely remove or disable:
- Any hooks that auto-trigger tree diagram generation
- Hooks that inject the universal tree prompt
- Pre-response hooks that activate tree visualization

Instead, users can:
- Explicitly ask for diagrams when needed
- Use natural trigger phrases
- Get better, more focused output

## Maintenance

**To update the skill:**
1. Edit `SKILL.md` for core instructions
2. Update `references/*.md` for detailed rules
3. Add new templates to `assets/` as patterns emerge
4. Keep SKILL.md concise (~100-150 lines max)

**Quality checks:**
- ✅ SKILL.md stays under 200 lines
- ✅ References loaded progressively
- ✅ Templates copy-paste ready
- ✅ Examples are clear and complete

## Installation

The skill is already in your dotfiles at:
```
claude/.claude/skills/vtree/
```

It will be available in Claude Code after the next session start.

---

**Last Updated:** 2025-10-23
**Architecture:** Level 1 Simple Skill
**Status:** ✅ Ready for use
