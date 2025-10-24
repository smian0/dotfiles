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

### Step 2: Gather Complete Workflow Information

**Collect all information needed for template variable derivation.**

Ask user detailed questions to populate template variables (see `references/template-variables-guide.md` for complete list):

#### 2.1: Core Workflow Details

**Questions:**
1. "What is the workflow name?" → `{workflow_name}`
2. "What is the main purpose of this workflow?" → `{workflow_purpose}`
3. "What phrase would trigger this workflow?" → `{workflow_trigger_phrase}`
   - Example: "implement a feature", "deploy to production"
4. "Is this mandatory or optional?" → `{enforcement_level}`

#### 2.2: Phases and Skills

**For each phase, ask:**

```
Phase [N]:
- "What is the phase name?" → {phase_N_name}
- "Which skill handles this?" → {phase_N_skill}
- "What is the purpose of this phase?" → {phase_N_purpose}
  Example: "Refine requirements into concrete design"
- "What does this phase output/produce?" → {phase_N_output_description}
  Example: "Concrete design document with integration points"
```

**Create mapping table:**

| # | Phase Name | Skill | Purpose | Output |
|---|------------|-------|---------|--------|
| 1 | [Name] | [skill] | [Purpose] | [Output description] |
| 2 | [Name] | [skill] | [Purpose] | [Output description] |
| 3 | [Name] | [skill] | [Purpose] | [Output description] |

#### 2.3: Trigger Examples

Ask for 2-3 concrete examples of when this workflow applies:

```
"Give me examples of when you'd use this workflow:"
→ {trigger_example_1}: "Implement user authentication"
→ {trigger_example_2}: "Add payment processing"
```

#### 2.4: Command Category (for Pattern B)

If generating Pattern B, ask:

```
"What command category should this be in?"
→ {command_category}: "dev", "deploy", "docs", etc.

"Give an example of how you'd invoke this:"
→ {example_argument}: "Add OAuth2 authentication"
```

#### 2.5: Validation

**Verify completeness:**
- [ ] Each phase has: name, skill, purpose, output
- [ ] All skills exist (check `.claude/skills/` directory)
- [ ] Phase order makes logical sense
- [ ] Trigger examples are specific and realistic

**If missing skills:**
- Identify which skills need to be created first
- Ask user if they want to create them now or use placeholders

### Step 2.6: Derive All Template Variables

**Use the complete variable derivation guide**: `references/template-variables-guide.md`

**Derivation process:**

1. **Load derivation formulas** from template variables guide
2. **Compute derived variables** from user input:
   ```python
   # Example derivations:
   workflow_slug = workflow_name.lower().replace(' ', '-')
   phase_1_objective = f"Use {phase_1_name.lower()} to {phase_1_purpose}"
   phase_1_verification_1 = f"✓ {phase_1_skill} completed successfully"
   phase_1_verification_2 = f"✓ {phase_1_output_description} produced"
   phase_1_to_phase_2_handoff = f"Pass {phase_1_output_description} to {phase_2_name}"
   # ... (see guide for all 62+ formulas)
   ```

3. **Apply smart defaults** for any missing optional variables (see guide)

4. **Validate completeness**:
   - All required variables populated (see guide's validation checklist)
   - Derived variables make logical sense
   - No placeholder/undefined values remain

**Output**: Complete variable dictionary ready for template substitution

**Verification**: Run checklist from `template-variables-guide.md` before proceeding

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

**Use template**: `assets/templates/orchestrator-skill.template.md`

**Location**: `.claude/skills/{workflow-slug}/SKILL.md`

**Actions:**

1. **Load all derived variables** from Step 2.6

2. **Read template**: `assets/templates/orchestrator-skill.template.md`

3. **Substitute all 62+ variables** using derivations from Step 2.6:
   - See `references/template-variables-guide.md` for complete variable list
   - All variables must be populated (required + defaults for optional)
   - Verify no `{undefined}` placeholders remain

4. **Create skill directory**:
   ```bash
   mkdir -p .claude/skills/{workflow-slug}
   ```

5. **Write generated SKILL.md**:
   ```bash
   # Write fully-substituted content
   cat > .claude/skills/{workflow-slug}/SKILL.md
   ```

6. **Create .gitignore** (if skill might generate outputs):
   ```bash
   cat > .claude/skills/{workflow-slug}/.gitignore << 'EOF'
   # Generated test outputs
   test-*/
   *.tmp
   EOF
   ```

**Verification:**
```bash
# Check file exists
test -f .claude/skills/{workflow-slug}/SKILL.md && echo "✅ Pattern A created"

# Verify no undefined variables
! grep -q '{[a-z_]*}' .claude/skills/{workflow-slug}/SKILL.md || echo "⚠️ Undefined variables remain"
```

### Step 5: Generate Pattern B (Workflow Command)

**Use template**: `assets/templates/workflow-command.template.md`

**Location**: `.claude/commands/{category}/{workflow-slug}.md`

**Actions:**

1. **Load all derived variables** from Step 2.6 (includes `{command_category}`)

2. **Read template**: `assets/templates/workflow-command.template.md`

3. **Substitute all 36+ variables** using derivations:
   - See `references/template-variables-guide.md` section "Pattern B Specific"
   - Includes command-specific variables: `example_argument`, `arguments_description`, `estimated_duration`

4. **Create command directory**:
   ```bash
   mkdir -p .claude/commands/{command_category}
   ```

5. **Write generated command file**:
   ```bash
   cat > .claude/commands/{command_category}/{workflow-slug}.md
   ```

**Verification:**
```bash
test -f .claude/commands/{command_category}/{workflow-slug}.md && echo "✅ Pattern B created"
```

**Inform user of usage**:
```
Command created: /{command_category}:{workflow-slug} <args>
Example: /{command_category}:{workflow-slug} {example_argument}
```

### Step 6: Generate Pattern C (CLAUDE.md Rules)

**Use template**: `assets/templates/claude-md-rules.template.md`

**Output**: Suggested additions to CLAUDE.md (NOT auto-appended)

**Actions:**

1. **Load all derived variables** from Step 2.6

2. **Read template**: `assets/templates/claude-md-rules.template.md`

3. **Substitute all 29+ variables** using derivations:
   - See `references/template-variables-guide.md` section "Pattern C Specific"
   - Includes: `workflow_trigger_condition`, `enforcement_level`, `exception_condition_1`, `exception_condition_2`

4. **Display generated rules to user**:
   ```markdown
   ## Suggested CLAUDE.md Addition:

   [Show fully-substituted template content]
   ```

5. **Ask user**: "Would you like me to add these rules to CLAUDE.md?"
   - If YES:
     ```bash
     # Determine location
     if [ -f .claude/CLAUDE.md ]; then
       target=".claude/CLAUDE.md"
     else
       target="~/.claude/CLAUDE.md"
     fi

     # Append rules
     cat >> $target << 'EOF'
     [Generated rules content]
     EOF
     ```
   - If NO: Skip, user can add manually later

**Verification (if added)**:
```bash
grep -q "{workflow_name} Workflow" $target && echo "✅ Pattern C added"
```

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

## Complete Worked Example

**User request**: "Create a feature development workflow"

### Step-by-Step Execution

**Step 1: Analyze Requirements** ✓

User provides:
- Workflow name: "Feature Development"
- Purpose: "Implementing new features"
- Trigger: "implement a feature"
- Enforcement: Mandatory

**Step 2: Gather Information** ✓

Phases collected:
1. Brainstorming → superpowers:brainstorming → "Refine requirements" → Output: "Design document"
2. Planning → superpowers:writing-plans → "Create implementation plan" → Output: "Task list with verification"
3. Implementation → superpowers:test-driven-development → "Implement using TDD" → Output: "Feature with tests"
4. Review → superpowers:requesting-code-review → "Validate implementation" → Output: "Approval"

Trigger examples:
- "Implement user authentication"
- "Add payment processing"

Command category: "dev"
Example argument: "Add OAuth2 authentication"

**Step 2.6: Derive Variables** ✓

Using `template-variables-guide.md` formulas:

```yaml
# Core (7 variables)
workflow_name: "Feature Development"
workflow_slug: "feature-development"  # Derived: lowercase + hyphens
workflow_description: "Complete feature development workflow using brainstorming, planning, TDD, and code review"
workflow_purpose: "implementing new features"
workflow_trigger_phrase: "implement a feature"
phase_count: "4"
command_category: "dev"

# Triggers (4 variables)
trigger_example_1: "Implement user authentication"
trigger_example_2: "Add payment processing"
trigger_pattern: "Implement [feature name]"
trigger_conditions: "- User requests new feature\n- Task involves implementation"

# Phase 1 (21 variables)
phase_1_name: "Brainstorming"
phase_1_skill: "superpowers:brainstorming"
phase_1_purpose: "Refine requirements into concrete design"
phase_1_objective: "Use brainstorming to refine user's feature request into concrete, actionable design"
phase_1_skill_description: "Interactive design refinement using Socratic method"
phase_1_prereq_1: "User has provided feature description"
phase_1_prereq_2: "Context about existing system understood"
phase_1_output_description: "Concrete design document with integration points"
phase_1_result_summary: "Design approved by user"
phase_1_verification_1: "✓ Design document complete"
phase_1_verification_2: "✓ User approved design"
phase_1_verification_3: "✓ Integration points identified"
phase_1_verification_brief: "Design complete and approved"
phase_1_to_phase_2_handoff: "Pass design document to planning phase"
phase_1_failure_action: "Return to requirements gathering, clarify with user"
phase_1_recovery_step_1: "Review brainstorming conversation for gaps"
phase_1_recovery_step_2: "Ask user for additional context"
phase_1_brief_description: "Refine requirements"
phase_1_context_item_1: "Consider existing architecture"
phase_1_context_item_2: "Follow project design patterns"
phase_1_expected_result: "Design integrates with existing system"

# Phase 2 (21 variables) - Similar structure
# Phase 3 (21 variables) - Similar structure
# Phase 4 (21 variables) - Similar structure

# Completion (8 variables)
deliverable_1_description: "Implemented feature with comprehensive tests"
deliverable_2_description: "Design and implementation plan documents"
deliverable_3_description: "Code review approval"
output_location: "src/features/"
final_verification_command_1: "pytest tests/ && echo '✅ Tests pass'"
final_verification_command_2: "git status && echo '✅ Changes staged'"
next_step_1: "Deploy to staging environment"
next_step_2: "Update user documentation"

# Pattern C specific (5 variables)
workflow_trigger_description: "implementing any new feature"
workflow_trigger_condition: "When implementing ANY new feature"
enforcement_level: "MANDATORY"
exception_condition_1: "User explicitly requests 'skip workflow'"
exception_condition_2: "Task is trivial (single line fix)"

# Total: 91 variables for 4-phase workflow
```

**Step 3: Pattern Selection** ✓

User chooses: All three patterns (A, B, C)

**Step 4: Generate Pattern A** ✓

1. Read `orchestrator-skill.template.md`
2. Substitute all 91 variables
3. Write to `.claude/skills/feature-development/SKILL.md`
4. Create `.gitignore`

Result: 200+ line orchestrator skill with complete phase instructions

**Step 5: Generate Pattern B** ✓

1. Read `workflow-command.template.md`
2. Substitute 40+ variables (subset + command-specific)
3. Write to `.claude/commands/dev/feature-development.md`

Result: Command invocable as `/dev:feature-development "Add OAuth"`

**Step 6: Generate Pattern C** ✓

1. Read `claude-md-rules.template.md`
2. Substitute 30+ variables
3. Display to user, ask permission
4. User approves, append to `CLAUDE.md`

Result: MANDATORY workflow rules enforced globally

**Step 7: Verification** ✓

```bash
✅ Pattern A created: .claude/skills/feature-development/SKILL.md
✅ Pattern B created: .claude/commands/dev/feature-development.md
✅ Pattern C added to CLAUDE.md
✅ No undefined variables
✅ All skills exist and validated
```

**Final Output:**

```markdown
## Created Workflow: Feature Development

### Pattern A: Orchestrator Skill
**Location**: .claude/skills/feature-development/SKILL.md
**Usage**: Invoke with `Skill("feature-development")`

### Pattern B: Workflow Command
**Location**: .claude/commands/dev/feature-development.md
**Usage**: `/dev:feature-development <feature description>`
**Example**: `/dev:feature-development Add OAuth2 authentication`

### Pattern C: CLAUDE.md Rules
**Added to**: CLAUDE.md
**Enforcement**: MANDATORY for all feature implementation

## Workflow Phases
1. Brainstorming → superpowers:brainstorming
2. Planning → superpowers:writing-plans
3. Implementation → superpowers:test-driven-development
4. Review → superpowers:requesting-code-review

## Next Steps
- Test workflow: `Skill("feature-development")` or `/dev:feature-development "test feature"`
- Customize templates in generated files if needed
- Share with team
```

---

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
