---
name: skill-creator
description: Guide for creating effective skills with intelligent architecture assessment. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities. Automatically determines whether to create a simple skill, a skill with subagent delegation, or a complete multi-agent system based on complexity analysis.
license: Complete terms in LICENSE.txt
---

# Skill Creator

This skill provides comprehensive guidance for creating effective skills with automatic architecture routing based on complexity requirements.

## About Skills

**Skills** are modular packages that extend Claude's capabilities through specialized knowledge, workflows, and tools. They transform Claude into a specialized agent for specific domains—like "onboarding guides" that provide procedural knowledge no model can fully possess.

### Three Architecture Levels

**Level 1: Simple Skills** - Linear workflows with scripts, references, and assets
- Single-phase, linear workflow
- One domain of expertise
- **Examples:** PDF editor, image rotator, code formatter

**Level 2: Skills with Delegation** - Skills that occasionally delegate to specialists
- Single-phase workflow + occasional specialized help
- Primary domain + delegated research/validation/analysis
- **Examples:** MCP server builder (API research), code reviewer (security analysis)

**Level 3: Multi-Agent Systems** - Complex coordinated workflows
- Multi-phase workflow with 3+ specialists
- Parallel execution and complex coordination
- **Examples:** Trading analysis, research pipelines, complex automation

## Quick Start: Skill Creation Process

### Step 0: Architecture Assessment ⚡ **START HERE**

**Before anything else, determine which level to use:**

Ask the user:
1. **Workflow**: Single-phase or multi-phase?
2. **Specialists**: How many roles needed?
3. **State**: Complex state management needed?
4. **Research**: Occasional help or continuous analysis?

**Decision:**
- **Level 1**: → Proceed to Step 1
- **Level 2**: → Proceed to Step 1 + add delegation (Step 4)
- **Level 3**: → Delegate to `meta-multi-agent` immediately

See [📊 Architecture Decision Matrix](./references/architecture-decision-matrix.md) for detailed criteria.

### Step 1: Understand with Examples

Gather concrete examples of how the skill will be used:
- "What functionality should this support?"
- "Give me examples of typical use cases"
- "What triggers this skill?"

### Step 2: Plan Reusable Contents

Identify what to include:
- **Scripts** - Repeatedly rewritten code
- **References** - Documentation loaded as needed
- **Assets** - Output resources (templates, boilerplate)
- **Workflows** - Specialized operation procedures (if 2+ distinct workflows)
- **Delegation Points** (Level 2) - When to call specialists

**For complex skills, also consider:**
- **Phases** - Sequential stages of one operation
- **Config** - Environment/settings management
- **Data** - Reference data, fixtures, schemas
- **Tests** - Validation infrastructure
- **Output** - Generated file organization

See [📦 Bundled Resources Guide](./references/bundled-resources-guide.md) for details.
See [🔄 Multi-Workflow Composition](./references/multi-workflow-composition.md) if skill handles 2+ specialized operations.
See [🏗️ Advanced Structure Patterns](./references/advanced-structure-patterns.md) for complex skills.

### Step 3: Initialize the Skill

Create directory structure using **symlink pattern**:

```bash
# Basic structure (always create these)
mkdir -p .claude/skills/<skill-name>/{scripts,references,assets,workflows,agents,commands}

# Advanced directories (create as needed - see advanced-structure-patterns.md)
# mkdir -p .claude/skills/<skill-name>/{phases,config,data,tests,output,.state,cache,archived}

# If skill has agents or commands, create symlinks:
ln -s ../skills/<skill-name>/agents .claude/agents/<skill-name>
ln -s ../skills/<skill-name>/commands .claude/commands/<skill-name>

# Note: workflows/ is used for multi-workflow skills (2+ specialized operations)
# Note: phases/ is used for sequential stages of one operation (see advanced patterns)
```

Create initial SKILL.md:
```yaml
---
name: skill-name
description: What it does and when to use it (be specific)
---
```

See [⚙️ Skill Organization](./references/skill-organization.md) for symlink pattern details.

### Step 4: Edit the Skill

**For Level 1:**
1. Create scripts/references/assets from Step 2
2. Write SKILL.md with procedural instructions
3. Use imperative form (verb-first)
4. Reference all bundled resources

**For Level 2 (add delegation):**
1. Everything from Level 1, PLUS:
2. Add Task() delegation code
3. Document when to delegate vs. handle directly
4. Show how to use subagent results

See [🔗 Delegation Patterns](./references/delegation-patterns.md) for Level 2 templates.

**For Level 3:**
Already delegated to `meta-multi-agent` in Step 0.1.

### Step 4.5: Verify & Optimize

**Ensure every file is referenced in SKILL.md - no orphaned documentation.**

```bash
# Check: does SKILL.md reference each file?
for f in $(find . -name "*.md" -o -name "*.py" -o -name "*.sh"); do
  grep -q "$(basename $f)" SKILL.md || echo "⚠️ Unreferenced: $f"
done
```

**Delete unreferenced files.** If SKILL.md doesn't load it, it's unused.

See [🔍 Skill Optimization](./references/skill-optimization.md) for detailed verification.

### Step 5: Package & Test

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Then iterate based on usage.

## Progressive Disclosure

Skills load in three levels:
1. **Metadata** - Always in context (~100 words)
2. **SKILL.md** - When triggered (<500 lines)
3. **Bundled resources** - As needed (unlimited)

## Reference Files

Load these for detailed guidance:

- [📊 Architecture Decision Matrix](./references/architecture-decision-matrix.md) - Detailed Level 1/2/3 criteria
- [🔗 Delegation Patterns](./references/delegation-patterns.md) - Level 2 Task() templates
- [📦 Bundled Resources Guide](./references/bundled-resources-guide.md) - Scripts, references, assets details
- [⚙️ Skill Organization](./references/skill-organization.md) - Symlink pattern explained
- [🔄 Multi-Workflow Composition](./references/multi-workflow-composition.md) - Directory-based workflows pattern for 2+ specialized operations
- [🏗️ Advanced Structure Patterns](./references/advanced-structure-patterns.md) - phases/, config/, data/, tests/, output/, .state/, cache/, archived/
- [🔍 Skill Optimization](./references/skill-optimization.md) - Verify all files referenced, eliminate bloat
- [📝 Skill Creation Workflow](./references/skill-creation-workflow.md) - Detailed step-by-step instructions

## Quick Reference

| Level | Workflow | Specialists | Parallel | Action |
|-------|----------|-------------|----------|---------|
| 1 | Single | 1 | No | Create skill |
| 2 | Single + help | 1 + occasional | No | Create skill + delegation |
| 3 | Multi-phase | 3+ concurrent | Yes | Delegate to meta-multi-agent |

## Writing Style

### SKILL.md Length Guidelines

**Critical principle**: When scripts exist, SKILL.md is an **invocation guide**, not an **implementation manual**.

| Situation | Target Length | Focus |
|-----------|--------------|-------|
| **Scripts handle logic** | 50-120 lines | When to use, how to invoke, key options |
| **Pure workflow (no scripts)** | 200-500 lines | Step-by-step procedures, decision points |

**Examples**:
- ❌ **Verbose** (324 lines): Detailed validation protocols, error handling procedures → Already in scripts
- ✅ **Concise** (103 lines): Quick start commands, key options table, Consultants folder integration

**Always**:
- Use **imperative/infinitive form** (verb-first)
- Be objective: "To accomplish X, do Y"
- Avoid second person ("you should")
- Reference bundled resources, don't duplicate them

---

**For complete details on any step, load the corresponding reference file above.**
