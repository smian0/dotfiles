---
name: skill-agent-creator
description: Guide for creating effective skills with intelligent architecture assessment. Use when users want to create a new skill (or update an existing skill) that extends Claude's capabilities. This skill automatically determines whether to create a simple skill, a skill with subagent delegation, or a complete multi-agent system based on complexity analysis.
---

# Skill & Agent Creator

This skill provides guidance for creating effective skills with automatic architecture routing based on complexity requirements.

## About Skills and Multi-Agent Systems

**Skills** are modular packages that extend Claude's capabilities through specialized knowledge, workflows, and tools. They transform Claude into a specialized agent for specific domains.

**Multi-Agent Systems** are orchestrated workflows with multiple specialist agents working in coordination, suitable for complex multi-phase processes.

### Three Architecture Levels

1. **Simple Skills** - Linear workflows with scripts, references, and assets
2. **Skills with Delegation** - Single-phase workflows that occasionally need specialized help (research, validation)
3. **Multi-Agent Systems** - Complex multi-phase workflows requiring specialist roles, parallel execution, and coordination

### Skill Organization Pattern (Standard for All Skills)

**All skills use the symlink pattern** for optimal organization:

- **Source files** live in `.claude/skills/<skill-name>/` (agents, commands, scripts, references, assets)
- **Symlinks** in `.claude/agents/<skill-name>/` and `.claude/commands/<skill-name>/` point to source directories
- **Benefits**: Easy development + runtime compatibility, no duplication, clean git history, transparent access

**Example structure:**
```
.claude/
├── skills/<skill-name>/          # SOURCE FILES (edit here)
│   ├── SKILL.md
│   ├── agents/                   # Agent source files
│   ├── commands/                 # Command source files
│   ├── scripts/                  # Executable scripts
│   ├── references/               # Documentation
│   └── assets/                   # Output resources
├── agents/<skill-name> → ../skills/<skill-name>/agents/     # SYMLINK
└── commands/<skill-name> → ../skills/<skill-name>/commands/ # SYMLINK
```

This pattern will be referenced in Step 3 (Initialization) with detailed instructions.

## Skill Creation Process

### Step 0: Architecture Assessment (CRITICAL - ALWAYS START HERE)

**Before any other step, assess the architectural complexity to route to the appropriate pattern.**

Ask the user these questions to understand requirements:

1. **Workflow Complexity:**
   - "Is this a single-phase workflow or multi-phase process?"
   - "Are the steps mostly sequential or can some run in parallel?"

2. **Specialist Roles:**
   - "How many different specialist roles or perspectives are needed?"
   - "Does this require coordination between multiple specialists?"

3. **State Management:**
   - "Does this need to track state across multiple phases?"
   - "Are there intermediate results that need to be shared between specialists?"

4. **Research/Analysis Needs:**
   - "Does this require occasional deep research or validation?"
   - "Or does it need continuous multi-source analysis throughout?"

#### Architecture Decision Matrix

Based on responses, determine architecture level:

**Level 1: Simple Skill**
- ✅ Single-phase, linear workflow
- ✅ One domain of expertise
- ✅ Deterministic operations
- ✅ No parallel execution needed
- ✅ Minimal state management
- **Examples:** PDF editor, image rotator, code formatter
- **Action:** Proceed to Step 1 (continue with traditional skill creation)

**Level 2: Skill with Subagent Delegation**
- ✅ Single-phase workflow with occasional complex tasks
- ✅ One primary domain + occasional specialized help
- ✅ Needs occasional research, validation, or analysis
- ✅ Skill maintains primary control
- ✅ Simple state management
- **Examples:** MCP server builder (needs API research), code reviewer (needs security analysis)
- **Action:** Proceed to Step 1, add delegation patterns in Step 4 (see references/delegation-patterns.md)

**Level 3: Multi-Agent System**
- ✅ Multi-phase workflow
- ✅ 3+ specialist roles needed
- ✅ Parallel execution benefits
- ✅ Complex coordination requirements
- ✅ State management across phases
- **Examples:** Trading analysis (daily + 4h + 1h timeframes), research pipeline, complex automation
- **Action:** **DELEGATE TO meta-multi-agent** (see Step 0.1 below)

Load [📊 Architecture Decision Matrix](./references/architecture-decision-matrix.md) for detailed decision criteria.

#### Step 0.1: Delegate to meta-multi-agent (Level 3 Only)

If Level 3 (Multi-Agent System) is detected, immediately delegate to meta-multi-agent:

```python
# Use Task tool to spawn meta-multi-agent
Task(
    subagent_type="meta-multi-agent",
    description="Generate multi-agent system",
    prompt="""
Create a complete multi-agent system for: {domain_name}

## Requirements
{workflow_description}

## Specialist Roles Needed
{list_of_specialist_roles}

## Parallel Execution Needs
{parallel_requirements}

## Coordination Requirements
{coordination_needs}

## State Management
{state_tracking_needs}

Generate the complete .claude/ directory structure with:
- Main orchestrator command
- Specialist agents
- Parallel worker (if needed)
- Coordination rules
- Context management files
- Communication protocols
"""
)
```

**After meta-multi-agent completes:** Review the generated system and provide usage documentation to the user. The skill creation process ends here for Level 3.

---

### Step 1: Understanding the Skill with Concrete Examples

**Skip this step if:**
- Level 3 (already delegated to meta-multi-agent)
- Skill usage patterns are already clearly understood

To create an effective Level 1 or Level 2 skill, clearly understand concrete examples of how it will be used.

Ask targeted questions:
- "What functionality should this skill support?"
- "Can you give some examples of typical use cases?"
- "What would a user say that should trigger this skill?"

**Avoid overwhelming users** - Start with most important questions, follow up as needed.

Conclude when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

**For Level 1 & 2 skills**, analyze each example to identify:

1. **Scripts** - Code that gets rewritten repeatedly or needs deterministic reliability
2. **References** - Documentation that should be loaded as needed (schemas, policies, API docs)
3. **Assets** - Output resources (templates, boilerplate code, images)

**For Level 2 skills**, additionally identify:
4. **Delegation Points** - Where the skill needs specialized help (research, validation, analysis)
   - Load [🔗 Delegation Patterns](./references/delegation-patterns.md) for guidance

### Step 3: Initializing the Skill

**Level 1 & 2 only** - Create the skill directory structure using the **symlink pattern** for optimal organization:

#### Directory Organization Pattern

**SOURCE FILES**: Create all skill content in `.claude/skills/<skill-name>/`:

```bash
mkdir -p .claude/skills/<skill-name>/{scripts,references,assets,agents,commands}
```

**SYMLINKS**: Create directory-level symlinks for Claude Code discovery:

```bash
# If skill has agents
ln -s ../skills/<skill-name>/agents .claude/agents/<skill-name>

# If skill has commands
ln -s ../skills/<skill-name>/commands .claude/commands/<skill-name>
```

**Benefits of this pattern:**
- ✅ **Easy development**: Edit source files directly in skill directory
- ✅ **Easy runtime**: Claude Code finds agents/commands via symlinks
- ✅ **No duplication**: Single source of truth for all files
- ✅ **Clean git history**: Changes only in source files, symlinks unchanged
- ✅ **Transparent access**: Navigating symlinks shows all source files
- ✅ **Organized structure**: All skill components packaged together

Create initial SKILL.md in `.claude/skills/<skill-name>/SKILL.md` with proper frontmatter:
```yaml
---
name: skill-name
description: When to use this skill (be specific and action-oriented)
---
```

### Step 4: Edit the Skill

#### For Level 1 (Simple Skills)

Follow traditional skill creation:
1. Create scripts, references, and assets as identified in Step 2
2. Write SKILL.md with clear procedural instructions
3. Use imperative/infinitive form (verb-first instructions)
4. Reference all bundled resources so Claude knows how to use them

#### For Level 2 (Skills with Delegation)

In addition to Level 1 steps, add delegation capabilities:

1. **Import Task tool in SKILL.md:**
```markdown
## Using Subagent Delegation

When [condition requiring specialized help]:

```python
from Task import Task

Task(
    subagent_type="<appropriate-agent>",
    description="<specific-task>",
    prompt="""
    <detailed-prompt-for-subagent>
    """
)
```
```

2. **Document when to delegate vs handle directly:**
   - Load [🔗 Delegation Patterns](./references/delegation-patterns.md) for templates
   - Be explicit about decision criteria

3. **Show how to use subagent results:**
   - How to extract information from returned data
   - How to proceed with the skill's workflow

**Available subagents for delegation:**
- `web-researcher` - Comprehensive multi-source research
- `deep-research-agent` - Deep analysis with adaptive strategies
- `code-reviewer` - Code quality, security, performance review
- `security-engineer` - Security vulnerability analysis
- `performance-engineer` - Performance bottleneck analysis
- `root-cause-analyst` - Systematic problem investigation
- And others - see `~/.claude/agents/` for available agents

### Step 5: Packaging (Optional)

If packaging scripts are available:
```bash
scripts/package_skill.py <path/to/skill-folder>
```

Otherwise, ensure the skill directory is complete and documented.

### Step 6: Iterate

After testing:
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify improvements to SKILL.md or bundled resources
4. Implement changes and test again

---

## Writing Style Guidelines

- Use **imperative/infinitive form** (verb-first instructions)
- Be objective and instructional: "To accomplish X, do Y"
- Avoid second person ("you should")
- Keep SKILL.md under 5k words (move details to references/)

## Progressive Disclosure

Skills use three-level loading:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude

---

## Reference Files

Load these as needed during skill creation:

- [📊 Architecture Decision Matrix](./references/architecture-decision-matrix.md) - Detailed decision criteria for Level 1/2/3
- [🔗 Delegation Patterns](./references/delegation-patterns.md) - Templates and patterns for Level 2 delegation

---

## Quick Reference: When to Use Each Level

| Characteristic | Level 1 | Level 2 | Level 3 |
|----------------|---------|---------|---------|
| Workflow phases | Single | Single + help | Multi-phase |
| Specialist roles | 1 | 1 + occasional | 3+ concurrent |
| Parallel execution | No | No | Yes |
| State management | Minimal | Simple | Complex |
| Coordination | None | None | Required |
| **Action** | Create skill | Create skill + delegation | Delegate to meta-multi-agent |
