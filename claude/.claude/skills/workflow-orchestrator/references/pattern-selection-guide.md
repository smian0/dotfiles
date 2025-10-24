# Pattern Selection Guide

Guide for choosing which cross-skill workflow patterns to generate based on workflow requirements.

## The Four Patterns

### Pattern A: Orchestrator Skill
**Location**: `.claude/skills/{workflow-slug}/SKILL.md`
**Invocation**: `Skill("{workflow-slug}")`
**Scope**: Reusable across all projects
**Best for**: Universal workflows, detailed orchestration logic

### Pattern B: Workflow Command
**Location**: `.claude/commands/{category}/{workflow-slug}.md`
**Invocation**: `/{category}:{workflow-slug} <args>`
**Scope**: Project-specific
**Best for**: Quick invocation, team-specific processes

### Pattern C: CLAUDE.md Rules
**Location**: `CLAUDE.md` or `~/.claude/CLAUDE.md`
**Invocation**: Automatic (always enforced)
**Scope**: Global enforcement
**Best for**: Mandatory quality gates, universal standards

### Pattern D: Orchestrator Agent
**Location**: `.claude/agents/{workflow-slug}.md`
**Invocation**: `@{workflow-slug}` or `Task(subagent_type="{workflow-slug}")`
**Scope**: Complex coordination
**Best for**: Conditional logic, parallel execution, state management

---

## Decision Matrix

### Choose Pattern A When:

✅ **Workflow characteristics:**
- Universal across all projects
- Needs detailed documentation
- Multiple verification checkpoints
- Complex failure recovery
- Reusable in different contexts

✅ **Examples:**
- Feature development workflow
- Code review process
- Documentation generation
- Testing and validation

✅ **Pros:**
- Well-documented
- Version controlled
- Discoverable via Skill tool
- Can be referenced in other skills

❌ **Avoid when:**
- Workflow is project-specific
- Simple sequential invocation (use Pattern B)
- Needs mandatory enforcement (add Pattern C)

---

### Choose Pattern B When:

✅ **Workflow characteristics:**
- Project-specific customization needed
- Quick command invocation desired
- Team has standard processes
- Arguments passed via command line
- Lightweight orchestration sufficient

✅ **Examples:**
- Deploy to production (project-specific)
- Run project test suite
- Generate project documentation
- Project-specific build process

✅ **Pros:**
- Quick slash command
- Project-customizable
- Simple to use
- No skill system overhead

❌ **Avoid when:**
- Workflow universal across projects (use Pattern A)
- Needs global enforcement (use Pattern C)
- Complex conditional logic (use Pattern D)

---

### Choose Pattern C When:

✅ **Workflow characteristics:**
- MANDATORY for all work
- Quality gate / compliance requirement
- Universal standard to enforce
- Cannot be skipped or bypassed
- Simple sequential enforcement

✅ **Examples:**
- Always brainstorm before coding
- Always review before committing
- Always test before deploying
- Security review for production changes

✅ **Pros:**
- Globally enforced
- Cannot be forgotten
- Clear mandate
- Prevents shortcuts

❌ **Avoid when:**
- Optional workflow
- Project-specific rules
- Needs flexibility/customization
- Not truly mandatory

---

### Choose Pattern D When:

✅ **Workflow characteristics:**
- Conditional branches (if-then logic)
- Parallel phase execution
- Complex state management
- Multi-specialist coordination
- Dynamic workflow based on context
- Error recovery with retry logic

✅ **Examples:**
- Trading analysis (parallel timeframes)
- Research pipeline (concurrent specialists)
- Complex CI/CD with conditional deployments
- Multi-stage approval workflows

✅ **Pros:**
- Full programming logic
- Parallel execution
- State management
- Complex coordination

❌ **Avoid when:**
- Simple sequential workflow (use A, B, or C)
- No conditional logic needed
- All phases always execute

**Note**: Pattern D requires delegation to `meta-sub-agent` or `meta-multi-agent` - beyond scope of workflow-orchestrator skill.

---

## Combination Strategies

Most robust approach: **Generate multiple patterns for the same workflow**

### Recommended Combinations

#### Universal Mandatory Workflow
**Generate**: A + C
**Why**: Skill provides documentation (A), CLAUDE.md enforces compliance (C)
**Example**: Feature development workflow

```
Pattern A: .claude/skills/feature-development/SKILL.md
Pattern C: CLAUDE.md rules enforcing the workflow
Result: Well-documented AND globally enforced
```

---

#### Project-Specific Team Process
**Generate**: B + optionally A
**Why**: Command for quick use (B), optionally skill for documentation (A)
**Example**: Project deployment process

```
Pattern B: .claude/commands/deploy/production.md
Pattern A: .claude/skills/deployment-workflow/SKILL.md (optional)
Result: Quick command + detailed reference
```

---

#### Quality Gate with Flexibility
**Generate**: A + C
**Why**: Skill for detailed process (A), CLAUDE.md for mandatory triggers (C)
**Example**: Code review workflow

```
Pattern A: .claude/skills/code-review-workflow/SKILL.md
Pattern C: CLAUDE.md rule: "Before any git commit, use code-review-workflow"
Result: Flexible documentation + mandatory enforcement
```

---

#### Universal + Project-Specific
**Generate**: A + B
**Why**: Skill for base workflow (A), command for project customization (B)
**Example**: Documentation workflow

```
Pattern A: .claude/skills/doc-generation/SKILL.md (universal base)
Pattern B: .claude/commands/docs/generate.md (project-specific overrides)
Result: Reusable base + project customization
```

---

## Quick Selection Flowchart

```
Start: Need cross-skill workflow
│
├─ Is it MANDATORY for all work, no exceptions?
│  YES → Generate Pattern C (+ optionally Pattern A for documentation)
│  NO  → Continue
│
├─ Is it project-specific or universal?
│  PROJECT → Generate Pattern B (+ optionally Pattern A for reference)
│  UNIVERSAL → Continue
│
├─ Does it need conditional logic or parallel execution?
│  YES → Use Pattern D (delegate to meta-multi-agent)
│  NO  → Generate Pattern A (+ optionally Pattern B for quick access)
│
└─ Done
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Pattern C for Optional Workflows
Don't enforce optional workflows in CLAUDE.md - users will work around it.

**Wrong**:
```markdown
## Documentation Workflow (MANDATORY)
You MUST generate docs for every function...
```

**If docs are sometimes needed**: Use Pattern A or B instead.

---

### ❌ Pattern B for Universal Workflows
Don't create project commands for universal processes - wastes repetition.

**Wrong**: Create `/dev:feature-workflow.md` in every project

**Better**: Create Pattern A skill once, reuse everywhere

---

### ❌ Pattern A Without Pattern C for Mandates
Don't rely on skill alone for mandatory compliance - Claude might skip it.

**Wrong**: Create feature-workflow skill, hope Claude uses it

**Better**: Pattern A (documentation) + Pattern C (enforcement)

---

### ❌ Over-engineering Simple Sequences
Don't create orchestrator for 2 simple sequential skills.

**Wrong**: Create orchestrator skill for "use skill X then skill Y"

**Better**: Just document the sequence in CLAUDE.md or README

---

## Default Recommendations

When user doesn't specify preferences:

**For universal workflows**: Generate A + C
**For project workflows**: Generate B (+ optionally A)
**For mandatory gates**: Generate C (+ A for documentation)
**For complex logic**: Suggest Pattern D, delegate to meta-multi-agent

**Always ask user to confirm pattern selection before generating.**

---

## Pattern Feature Comparison

| Feature | Pattern A | Pattern B | Pattern C | Pattern D |
|---------|-----------|-----------|-----------|-----------|
| **Reusable across projects** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Quick invocation** | ⚠️ Via Skill() | ✅ Slash command | ✅ Automatic | ⚠️ Via @ or Task() |
| **Enforced automatically** | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Detailed documentation** | ✅ Yes | ⚠️ Moderate | ❌ No | ✅ Yes |
| **Project customization** | ❌ No | ✅ Yes | ❌ No | ⚠️ Moderate |
| **Conditional logic** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Parallel execution** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Version controlled** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Discovery** | ✅ Skill list | ⚠️ Command list | ✅ Always active | ⚠️ Agent list |

---

## Examples by Domain

### Development Workflows
- **Feature development**: A + C
- **Bug fixing**: A + B
- **Code review**: A + C
- **Refactoring**: A + B

### Deployment Workflows
- **Production deploy**: B (project-specific)
- **Staging deploy**: B (project-specific)
- **Deployment gates**: C (mandatory checks)

### Documentation Workflows
- **API docs**: A (universal)
- **Project README**: B (project-specific)
- **Release notes**: A + B

### Quality Workflows
- **Pre-commit checks**: C (mandatory)
- **Security audit**: A + C
- **Performance review**: A (optional)

---

## Summary

**Pattern A**: Universal, reusable, well-documented skills
**Pattern B**: Project-specific, quick commands
**Pattern C**: Mandatory enforcement, quality gates
**Pattern D**: Complex coordination, conditional logic

**Best practice**: Generate multiple patterns (A+C or A+B or B+C) for robustness and flexibility.

**Always confirm** pattern selection with user before generating workflows.
