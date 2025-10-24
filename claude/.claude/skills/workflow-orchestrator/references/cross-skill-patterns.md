# Cross-Skill Orchestration Patterns

Comprehensive guide to the four patterns for coordinating multiple skills in Claude Code.

## Problem Statement

### The Gap in Skill Architecture

**What EXISTS:**
- ✅ Multi-workflow (Level 1): Multiple operations within ONE skill
- ✅ Delegation (Level 2): ONE skill delegates to subagents
- ✅ Multi-agent (Level 3): Creating NEW systems with coordinated agents

**What was MISSING:**
- ❌ Cross-skill workflows: Repeatable patterns for using Skill A + Skill B + Skill C
- ❌ Skill dependencies: Declaring "this skill requires that skill first"
- ❌ Workflow templates: Reusable cross-skill sequences

**Solution**: Four orchestration patterns (A, B, C, D) that enable cross-skill coordination.

---

## Pattern A: Orchestrator Skill

### Overview

Create a meta-skill that sequences other skills in a documented, reusable workflow.

**File structure:**
```
.claude/skills/{workflow-name}/
├── SKILL.md                 # Orchestration logic
├── references/              # Supporting docs (optional)
└── .gitignore              # If using output/ or .state/
```

### Complete Example

**Scenario**: Feature Development Workflow

**File**: `.claude/skills/feature-development/SKILL.md`

```markdown
---
name: feature-development
description: Complete feature development workflow using brainstorming, planning, TDD, and code review skills in sequence. Use when implementing any new feature.
---

# Feature Development Workflow

## When to Use

Activate this workflow when user requests:
- "Implement [feature]"
- "Add [new functionality]"
- "Create [new capability]"

## Workflow Phases

| # | Phase | Skill | Purpose |
|---|-------|-------|---------|
| 1 | Brainstorming | `superpowers:brainstorming` | Refine requirements |
| 2 | Planning | `superpowers:writing-plans` | Create implementation plan |
| 3 | Implementation | `superpowers:test-driven-development` | Write tests + code |
| 4 | Review | `superpowers:requesting-code-review` | Validate against plan |

## Phase Execution

### Phase 1: Brainstorming (MANDATORY)

1. Announce: "Starting Phase 1: Brainstorming"

2. Invoke skill:
   ```
   Skill("superpowers:brainstorming")
   ```

3. Work with user to refine idea into concrete design

**Verification**: Design document complete, user approves

---

### Phase 2: Planning (MANDATORY)

1. Announce: "Starting Phase 2: Planning"

2. Use brainstorming output as input

3. Invoke skill:
   ```
   Skill("superpowers:writing-plans")
   ```

4. Create detailed implementation plan

**Verification**: Plan has bite-sized tasks, verification steps

---

### Phase 3: Implementation (MANDATORY)

1. Announce: "Starting Phase 3: Implementation"

2. Use plan from Phase 2

3. Invoke skill:
   ```
   Skill("superpowers:test-driven-development")
   ```

4. Follow RED-GREEN-REFACTOR cycle

**Verification**: All tests pass, code implements plan

---

### Phase 4: Review (MANDATORY)

1. Announce: "Starting Phase 4: Review"

2. Invoke skill:
   ```
   Skill("superpowers:requesting-code-review")
   ```

3. Validate implementation against plan

**Verification**: Review passes, all issues addressed

---

## Completion

All phases complete → Report success to user
```

### Benefits

✅ **Reusable**: Works across all projects
✅ **Documented**: Clear workflow documentation
✅ **Discoverable**: Appears in skill list
✅ **Version controlled**: Git tracked
✅ **Referenced**: Other skills can reference it

### Limitations

❌ **Not enforced**: Claude might skip if not reminded
❌ **No project customization**: Universal, not project-specific
❌ **Manual invocation**: Must call explicitly

### When to Use

- Universal workflows across all projects
- Complex orchestration with verification
- Need detailed documentation
- Workflow will be referenced by other skills

---

## Pattern B: Workflow Command

### Overview

Create a slash command that sequences skills, with project-specific customization.

**File structure:**
```
.claude/commands/{category}/
└── {workflow-name}.md       # Command with workflow logic
```

### Complete Example

**Scenario**: Feature Development Command (project-specific)

**File**: `.claude/commands/dev/feature.md`

```markdown
---
title: Feature Development
description: Complete feature workflow: brainstorm → plan → TDD → review. Project-specific customization included.
category: dev
---

# Feature Development Command

Execute complete feature workflow using $ARGUMENTS as feature description.

**Usage**: `/dev:feature <feature description>`

**Example**: `/dev:feature Add user authentication with OAuth2`

---

## Workflow Phases

1. **Brainstorming**: Refine requirements
2. **Planning**: Create implementation plan
3. **Implementation**: TDD approach
4. **Review**: Validate against plan

---

## Phase 1: Brainstorming

Invoke brainstorming skill:

```
Skill("superpowers:brainstorming")
```

**Context**: Feature description from $ARGUMENTS

**Project-specific**: Consider existing auth system at `src/auth/`

**Expected result**: Concrete design that integrates with existing architecture

---

## Phase 2: Planning

Invoke planning skill:

```
Skill("superpowers:writing-plans")
```

**Context**: Design from Phase 1

**Project-specific**: Include migration steps for existing users

**Expected result**: Step-by-step plan with verification

---

## Phase 3: Implementation

Invoke TDD skill:

```
Skill("superpowers:test-driven-development")
```

**Context**: Plan from Phase 2

**Project-specific**: Follow project's test patterns in `tests/`

**Expected result**: Tests pass, feature implemented

---

## Phase 4: Review

Invoke code review skill:

```
Skill("superpowers:requesting-code-review")
```

**Project-specific**: Check against project's security guidelines

**Expected result**: Review passes

---

## Completion

Report to user with deliverables location.
```

### Benefits

✅ **Quick invocation**: Slash command
✅ **Project-specific**: Customizable per project
✅ **Context-aware**: Can reference project structure
✅ **Fast**: Simple command syntax

### Limitations

❌ **Per-project setup**: Must create in each project
❌ **Not universal**: Changes don't propagate
❌ **Less documented**: Lighter than Pattern A

### When to Use

- Project-specific workflows
- Need quick slash command
- Team has standard processes
- Workflow varies by project

---

## Pattern C: CLAUDE.md Rules

### Overview

Add global rules to CLAUDE.md that enforce workflow automatically.

**File**: `.claude/CLAUDE.md` or `~/.claude/CLAUDE.md`

### Complete Example

**Scenario**: Mandatory Feature Development Workflow

**Added to CLAUDE.md:**

```markdown
## Feature Development Workflow (MANDATORY)

**When implementing ANY new feature**, you MUST execute the following phases in sequence:

### Phase 1: Brainstorming (MANDATORY FIRST)

**Skill**: Use `Skill("superpowers:brainstorming")`

**Purpose**: Refine user's feature request into concrete design

**Prerequisites**:
- User has provided feature description
- Context about existing system understood

**Verification before Phase 2**:
- ✓ Design document complete
- ✓ User approved design
- ✓ Integration points identified

**You cannot proceed to Phase 2 until Phase 1 verification passes.**

---

### Phase 2: Planning (MANDATORY SECOND)

**Skill**: Use `Skill("superpowers:writing-plans")`

**Purpose**: Create detailed implementation plan

**Prerequisites**:
- ✓ Phase 1 completed successfully
- Design document from Phase 1 available

**Verification before Phase 3**:
- ✓ Plan has bite-sized tasks
- ✓ Verification steps defined
- ✓ User approved plan

**You cannot proceed to Phase 3 until Phase 2 verification passes.**

---

### Phase 3: Implementation (MANDATORY THIRD)

**Skill**: Use `Skill("superpowers:test-driven-development")`

**Purpose**: Implement using TDD

**Prerequisites**:
- ✓ Phase 1 completed successfully
- ✓ Phase 2 completed successfully
- Plan from Phase 2 available

**Verification before Phase 4**:
- ✓ All tests pass
- ✓ Code implements plan
- ✓ No regressions

**You cannot proceed to Phase 4 until Phase 3 verification passes.**

---

### Phase 4: Review (MANDATORY BEFORE COMPLETION)

**Skill**: Use `Skill("superpowers:requesting-code-review")`

**Purpose**: Validate implementation against plan

**Prerequisites**:
- ✓ Phase 1 completed successfully
- ✓ Phase 2 completed successfully
- ✓ Phase 3 completed successfully

**Final Verification**:
- ✓ Review passes
- ✓ All issues addressed
- ✓ Code meets standards

**You cannot claim work is complete until all verifications pass.**

---

### Enforcement Rules

**You MUST**:
1. Execute all phases in the specified order
2. Complete verification checkpoints before proceeding
3. Use the exact skills specified
4. Announce each phase as you begin
5. Report completion only after final verification

**You MUST NOT**:
1. Skip phases (all are mandatory)
2. Proceed if verification fails
3. Reorder phases
4. Substitute different skills
5. Claim completion without all phases

### Exceptions

This workflow may be skipped ONLY if:
- User explicitly requests "skip workflow" or "just do X without workflow"
- Task is fixing a typo or trivial change (single line)

**If unsure whether workflow applies, execute it.**

---

**This is a mandatory workflow. You cannot skip it or deviate from the sequence.**
```

### Benefits

✅ **Globally enforced**: Cannot be forgotten
✅ **Automatic**: No manual invocation
✅ **Clear mandate**: Prevents shortcuts
✅ **Consistent**: Applies everywhere

### Limitations

❌ **Inflexible**: Hard to customize per project
❌ **Can be heavy**: Applies even when not needed
❌ **Less documentation**: Just rules, not detailed guide

### When to Use

- MANDATORY quality gates
- Universal standards
- Compliance requirements
- Cannot be bypassed

### Best Practice

**Combine with Pattern A**: Pattern C for enforcement, Pattern A for detailed documentation

---

## Pattern D: Orchestrator Agent

### Overview

Create a dedicated agent with full programming logic for complex coordination.

**File**: `.claude/agents/{workflow-name}.md`

**Note**: Pattern D is advanced - typically requires `meta-sub-agent` or `meta-multi-agent` to create.

### When to Use Pattern D

**Indicators**:
- ✅ Conditional branches (if-then logic)
- ✅ Parallel phase execution
- ✅ Complex state management
- ✅ Dynamic workflow based on context
- ✅ Error recovery with retry logic
- ✅ 3+ specialists coordinate

**Examples**:
- Trading analysis (parallel timeframes)
- Research pipeline (concurrent specialists)
- Complex CI/CD with conditional deployments
- Multi-stage approval workflows

### Structure

```yaml
---
name: workflow-orchestrator-agent
description: Coordinates complex multi-phase workflow with conditional logic
tools:
  - Skill
  - Task
  - TodoWrite
  - Bash
  - Read
  - Write
---

# Workflow Orchestrator Agent

[Agent-specific orchestration logic with full programming capabilities]
```

### Benefits

✅ **Full logic**: Conditional branches, loops, state
✅ **Parallel execution**: Multiple phases simultaneously
✅ **Complex coordination**: Advanced scenarios
✅ **Error handling**: Sophisticated retry/recovery

### Limitations

❌ **Complex**: Harder to create and maintain
❌ **Requires agent system**: Not just skills
❌ **Overkill for simple**: Unnecessary for sequential workflows

---

## Pattern Comparison

| Aspect | Pattern A | Pattern B | Pattern C | Pattern D |
|--------|-----------|-----------|-----------|-----------|
| **Complexity** | Moderate | Simple | Simple | High |
| **Reusability** | High | Low | High | High |
| **Enforcement** | None | None | Automatic | None |
| **Customization** | Low | High | None | Moderate |
| **Documentation** | Excellent | Good | Minimal | Excellent |
| **Invocation** | `Skill()` | Slash command | Automatic | `@agent` or `Task()` |
| **Scope** | Universal | Project | Global | Universal |
| **Conditional logic** | No | No | No | Yes |
| **Parallel execution** | No | No | No | Yes |
| **State management** | Minimal | Minimal | None | Advanced |
| **Best for** | Universal workflows | Project workflows | Mandatory gates | Complex coordination |

---

## Combination Strategies

### Recommended Combinations

**Most Robust**: Generate multiple patterns for same workflow

#### 1. Universal Mandatory Workflow
**Patterns**: A + C
**Structure**:
- Pattern A: `.claude/skills/feature-development/SKILL.md` (documentation)
- Pattern C: `CLAUDE.md` rules (enforcement)

**Benefits**: Well-documented AND enforced

---

#### 2. Project-Specific with Reference
**Patterns**: A + B
**Structure**:
- Pattern A: `.claude/skills/deployment-workflow/SKILL.md` (base workflow)
- Pattern B: `.claude/commands/deploy/production.md` (project customization)

**Benefits**: Universal base + project specifics

---

#### 3. Quality Gate with Documentation
**Patterns**: A + C
**Structure**:
- Pattern A: `.claude/skills/code-review-workflow/SKILL.md` (detailed process)
- Pattern C: `CLAUDE.md` rule: "Before any commit, use code-review-workflow"

**Benefits**: Flexible documentation + mandatory compliance

---

## Implementation Checklist

When creating cross-skill workflow:

### Planning Phase
- [ ] Identify workflow name and purpose
- [ ] Map skills to phases
- [ ] Determine sequence and dependencies
- [ ] Identify verification checkpoints
- [ ] Choose pattern(s) to generate

### Generation Phase
- [ ] Generate Pattern A (if universal/documented)
- [ ] Generate Pattern B (if project-specific)
- [ ] Generate Pattern C (if mandatory)
- [ ] Consider Pattern D (if complex)

### Validation Phase
- [ ] Verify all referenced skills exist
- [ ] Test workflow with real scenario
- [ ] Confirm verification checkpoints work
- [ ] Document failure recovery

### Documentation Phase
- [ ] Add usage examples
- [ ] Document exceptions
- [ ] Create troubleshooting guide
- [ ] Share with team (if applicable)

---

## Anti-Patterns to Avoid

### ❌ Don't: Enforce Optional Workflows in CLAUDE.md
**Problem**: Users will work around it
**Solution**: Use Pattern A or B for optional workflows

### ❌ Don't: Create Per-Project Commands for Universal Workflows
**Problem**: Duplication, inconsistency
**Solution**: Use Pattern A, reference from projects

### ❌ Don't: Rely on Pattern A Alone for Mandates
**Problem**: Claude might skip skill
**Solution**: Add Pattern C for enforcement

### ❌ Don't: Over-Engineer Simple Sequences
**Problem**: Unnecessary complexity
**Solution**: Document in README or CLAUDE.md instead

---

## Summary

**Pattern A**: Universal, reusable, documented orchestrator skills
- **Use for**: Cross-project workflows, complex orchestration
- **Invocation**: `Skill("{workflow-name}")`

**Pattern B**: Project-specific workflow commands
- **Use for**: Team processes, project standards
- **Invocation**: `/{category}:{workflow-name}`

**Pattern C**: Global CLAUDE.md enforcement rules
- **Use for**: Mandatory gates, universal compliance
- **Invocation**: Automatic

**Pattern D**: Complex orchestrator agents
- **Use for**: Conditional logic, parallel execution, advanced coordination
- **Invocation**: `@{agent-name}` or `Task()`

**Best Practice**: Generate multiple patterns (A+C or A+B or B+C) for robust, flexible workflows.
