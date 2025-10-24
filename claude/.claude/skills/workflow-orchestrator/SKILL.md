---
name: workflow-orchestrator
description: Creates cross-skill workflow orchestrators on demand. Use when user wants to create repeatable multi-skill workflows, chain skills together, or establish standard development/deployment/documentation processes.
---

# Workflow Orchestrator

Meta-skill for creating cross-skill workflow orchestrators that sequence multiple skills in repeatable patterns.

## When to Use

Activate this skill when user requests:
- "Create a workflow that uses multiple skills"
- "I want to chain skill A, B, and C together"
- "Set up a standard process for [feature development/deployment/documentation/etc.]"
- "How do I make skills work together in sequence?"
- "Create a repeatable workflow using [list of skills]"

## Overview

This skill generates three orchestration patterns (A, B, C) based on user's workflow needs:
- **Pattern A**: Orchestrator Skill (reusable across projects)
- **Pattern B**: Workflow Command (project-specific slash command)
- **Pattern C**: CLAUDE.md Rules (global enforcement)

User can choose which patterns to generate (default: all three).

## Workflow Creation Process

### Step 1: Analyze Workflow Requirements

Ask user to describe their workflow:

**Required Information:**
1. **Workflow name**: e.g., "Feature Development", "Deployment Process", "Documentation Creation"
2. **Workflow phases**: What are the sequential steps?
3. **Skills needed**: Which existing skills apply to each phase?
4. **Scope**: Project-specific or universal across all projects?
5. **Enforcement level**: Mandatory or optional?

**Example Questions:**
```
"What workflow do you want to create?"
"What are the main phases/steps in this workflow?"
"Which skills should be used for each phase?"
"Is this workflow project-specific or universal?"
"Should this be mandatory or optional?"
```

### Step 2: Map Skills to Phases

Create a workflow mapping table:

| Phase | Skill(s) | Trigger | Mandatory? |
|-------|----------|---------|------------|
| 1. [Phase Name] | [skill-name] | [when this phase starts] | Yes/No |
| 2. [Phase Name] | [skill-name] | [when this phase starts] | Yes/No |
| 3. [Phase Name] | [skill-name] | [when this phase starts] | Yes/No |

**Validation:**
- Each phase has at least one skill
- Skills are in logical order
- Verify all skills exist (check `.claude/skills/` directory)
- Identify any missing skills that need to be created first

### Step 3: Determine Pattern Selection

Ask user which patterns to generate (or generate all by default):

**Pattern A - Orchestrator Skill**:
- Reusable across projects
- Well-documented workflow
- Can be invoked via Skill tool
- **Best for**: Universal workflows, complex orchestration

**Pattern B - Workflow Command**:
- Project-specific
- Quick slash command invocation
- Customizable per project
- **Best for**: Project-specific workflows, team standards

**Pattern C - CLAUDE.md Rules**:
- Global enforcement
- Applies to all work
- Mandatory compliance
- **Best for**: Quality gates, universal mandates

**Default**: Generate all three patterns for maximum flexibility.

### Step 4: Generate Pattern A (Orchestrator Skill)

Use template from `assets/templates/orchestrator-skill.template.md`:

**Location**: `.claude/skills/{workflow-slug}/SKILL.md`

**Template Variables:**
- `{workflow_slug}`: kebab-case identifier (e.g., "feature-development")
- `{workflow_name}`: Human-readable name (e.g., "Feature Development")
- `{workflow_description}`: When to use this workflow
- `{phase_N}`: Phase name
- `{skill_N}`: Skill to invoke
- `{trigger_N}`: When this phase starts
- `{verification_N}`: How to verify phase completion

**Actions:**
1. Read template: `assets/templates/orchestrator-skill.template.md`
2. Substitute variables with user's workflow details
3. Write to `.claude/skills/{workflow-slug}/SKILL.md`
4. Create `.gitignore` if needed

### Step 5: Generate Pattern B (Workflow Command)

Use template from `assets/templates/workflow-command.template.md`:

**Location**: `.claude/commands/{category}/{workflow-slug}.md`

**Template Variables:**
- Same as Pattern A
- Plus: `{category}`: Command category (dev, deploy, docs, etc.)

**Actions:**
1. Read template: `assets/templates/workflow-command.template.md`
2. Substitute variables
3. Write to `.claude/commands/{category}/{workflow-slug}.md`
4. Inform user of command usage: `/{category}:{workflow-slug} <args>`

### Step 6: Generate Pattern C (CLAUDE.md Rules)

Use template from `assets/templates/claude-md-rules.template.md`:

**Output**: Suggested additions to `.claude/CLAUDE.md`

**Template Variables:**
- Same as Pattern A/B

**Actions:**
1. Read template: `assets/templates/claude-md-rules.template.md`
2. Substitute variables
3. **Display suggested rules to user** (don't auto-append to CLAUDE.md)
4. Ask: "Would you like me to add these rules to CLAUDE.md?"
5. If yes, append to `.claude/CLAUDE.md` or `~/.claude/CLAUDE.md`

### Step 7: Verification & Documentation

**Run verification checks:**

```bash
# Verify Pattern A exists
test -f .claude/skills/{workflow-slug}/SKILL.md && echo "✅ Pattern A created"

# Verify Pattern B exists
test -f .claude/commands/{category}/{workflow-slug}.md && echo "✅ Pattern B created"

# Check CLAUDE.md if Pattern C was added
grep -q "{workflow-name} Workflow" .claude/CLAUDE.md 2>/dev/null && echo "✅ Pattern C added"
```

**Create usage documentation:**

Present to user:
```markdown
## Created Workflow: {Workflow Name}

### Pattern A: Orchestrator Skill
**Location**: .claude/skills/{workflow-slug}/SKILL.md
**Usage**: Invoke with `Skill("{workflow-slug}")`

### Pattern B: Workflow Command
**Location**: .claude/commands/{category}/{workflow-slug}.md
**Usage**: `/{category}:{workflow-slug} <args>`

### Pattern C: CLAUDE.md Rules
[If added] Rules enforced globally in CLAUDE.md

## Workflow Phases
1. {Phase 1}: {Skill 1}
2. {Phase 2}: {Skill 2}
3. {Phase 3}: {Skill 3}

## Next Steps
- Test the workflow with a real task
- Customize templates if needed
- Share with team (if applicable)
```

## Advanced: Pattern D (Orchestrator Agent)

For complex workflows with conditional logic, parallel execution, or state management, suggest creating an orchestrator agent:

**Indicators for Pattern D:**
- Workflow has conditional branches
- Some phases can run in parallel
- Complex state tracking needed
- Multiple specialists coordinate
- Error recovery logic required

**Guidance**: Delegate to `meta-sub-agent` skill to create dedicated orchestrator agent.

## Templates

All pattern templates are in `assets/templates/`:
- `orchestrator-skill.template.md` - Pattern A template
- `workflow-command.template.md` - Pattern B template
- `claude-md-rules.template.md` - Pattern C template

## References

See `references/` for detailed guidance:
- `cross-skill-patterns.md` - Complete documentation of all four patterns
- `pattern-selection-guide.md` - Decision matrix for choosing patterns

## Examples

**Example 1: Feature Development Workflow**
```
Phases:
1. Brainstorming → superpowers:brainstorming
2. Planning → superpowers:writing-plans
3. Implementation → superpowers:test-driven-development
4. Review → superpowers:requesting-code-review

Generated:
- .claude/skills/feature-development/SKILL.md
- .claude/commands/dev/feature-development.md
- CLAUDE.md rules for mandatory workflow
```

**Example 2: Deployment Workflow**
```
Phases:
1. Testing → superpowers:verification-before-completion
2. Build → [custom build skill]
3. Security Review → superpowers:receiving-code-review
4. Deploy → [custom deploy skill]

Generated:
- .claude/skills/deployment-workflow/SKILL.md
- .claude/commands/deploy/production.md
```

## Workflow Naming Conventions

**Skill slugs**: `{purpose}-workflow` (e.g., "feature-development-workflow")
**Command names**: `{purpose}` without "-workflow" suffix (e.g., "feature-development")
**CLAUDE.md sections**: "## {Purpose} Workflow" (e.g., "## Feature Development Workflow")

## Quality Guidelines

**Orchestrator skills should:**
- Use MANDATORY for required phases
- Include verification checkpoints between phases
- Reference skill names exactly (use Skill tool syntax)
- Document prerequisites clearly
- Specify failure/rollback procedures

**Avoid:**
- Duplicating skill content in orchestrator
- Hardcoding implementation details
- Skipping verification steps
- Assuming skills exist without checking
