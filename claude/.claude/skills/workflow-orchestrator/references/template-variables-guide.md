# Template Variables Guide

Complete reference for all template variables used in workflow generation, with derivation formulas and defaults.

## Overview

Templates use **62-127 variables total** depending on workflow complexity. This guide shows how to derive all variables from user input.

**Template complexity:**
- `orchestrator-skill.template.md`: 62 base variables
- `workflow-command.template.md`: 36 base variables
- `claude-md-rules.template.md`: 29 base variables

**Variable expansion**: For N phases, multiply per-phase variables by N.

---

## Variable Categories

### 1. Workflow Metadata (Core)

| Variable | Derivation | Example |
|----------|------------|---------|
| `{workflow_name}` | User provides | "Feature Development" |
| `{workflow_slug}` | Convert workflow_name to kebab-case | "feature-development" |
| `{workflow_description}` | User provides or derive | "Complete feature development workflow using brainstorming, planning, TDD, and code review" |
| `{workflow_purpose}` | Extract from description | "implementing new features" |
| `{workflow_trigger_phrase}` | Primary user request pattern | "implement a feature" |
| `{phase_count}` | Count phases from Step 2 | "4" |
| `{command_category}` | User provides or infer | "dev", "deploy", "docs" |

**Derivation formulas:**

```python
workflow_slug = workflow_name.lower().replace(' ', '-').replace('_', '-')

workflow_description = f"{workflow_name} workflow using {', '.join(phase_skills)}"

workflow_purpose = extract_verb_phrase(workflow_name)
# "Feature Development" → "developing features"
# "Deployment Process" → "deploying applications"

workflow_trigger_phrase = infer_primary_action(workflow_name)
# "Feature Development" → "implement a feature"
# "Deployment" → "deploy to production"

phase_count = len(phases)
```

---

### 2. Trigger Patterns

| Variable | Derivation | Example |
|----------|------------|---------|
| `{trigger_example_1}` | Specific user request variant 1 | "Implement user authentication" |
| `{trigger_example_2}` | Specific user request variant 2 | "Add payment processing" |
| `{trigger_pattern}` | General pattern match | "Implement [feature name]" |
| `{trigger_conditions}` | List of when to activate | "- User requests new feature\n- Task involves implementation" |

**Derivation formulas:**

```python
trigger_example_1 = f"{workflow_action} {example_feature_1}"
# workflow_action="Implement", example_feature_1="user authentication"

trigger_example_2 = f"{workflow_action} {example_feature_2}"

trigger_pattern = f"{workflow_action} [specific task]"

trigger_conditions = generate_trigger_list(workflow_purpose, phases)
# From workflow purpose, generate 2-3 trigger conditions
```

---

### 3. Per-Phase Variables (Repeat for Each Phase)

**Base pattern**: `{phase_N_*}` where N = 1, 2, 3, ...

#### Phase Identity

| Variable | Derivation | Example (Phase 1) |
|----------|------------|-------------------|
| `{phase_N_name}` | User provides | "Brainstorming" |
| `{phase_N_skill}` | User provides (exact skill name) | "superpowers:brainstorming" |
| `{phase_N_purpose}` | User provides or derive | "Refine requirements into concrete design" |
| `{phase_N_objective}` | Derive from purpose | "Use brainstorming to refine user's feature request into concrete, actionable design" |
| `{phase_N_skill_description}` | Brief skill summary | "Interactive design refinement using Socratic method" |

**Derivation formulas:**

```python
phase_N_objective = f"Use {phase_N_name.lower()} to {phase_N_purpose.lower()}"

phase_N_skill_description = lookup_skill_description(phase_N_skill)
# Read from skill's SKILL.md frontmatter if available
# Otherwise: infer from skill name
```

#### Phase Prerequisites

| Variable | Derivation | Example |
|----------|------------|---------|
| `{phase_N_prereq_1}` | First prerequisite | "User has provided feature description" |
| `{phase_N_prereq_2}` | Second prerequisite (optional) | "Context about existing system understood" |

**Derivation formulas:**

```python
# For Phase 1:
phase_1_prereq_1 = "User has provided {task_description}"
phase_1_prereq_2 = determine_context_needs(phase_1_skill)

# For Phase 2+:
phase_N_prereq_1 = f"Phase {N-1} completed successfully"
phase_N_prereq_2 = determine_additional_prereqs(phase_N_skill, previous_phase_output)
```

**Defaults** (if user doesn't provide):
- `phase_1_prereq_1`: "User has provided task description"
- `phase_1_prereq_2`: "Relevant context is available"
- `phase_N_prereq_2` (N>1): "Output from Phase {N-1} is ready"

#### Phase Execution

| Variable | Derivation | Example |
|----------|------------|---------|
| `{phase_N_output_description}` | What this phase produces | "Concrete design document with integration points" |
| `{phase_N_result_summary}` | Brief result description | "Design approved by user" |

**Derivation formulas:**

```python
phase_N_output_description = infer_output(phase_N_skill, phase_N_purpose)
# "superpowers:brainstorming" + "refine requirements" → "Concrete design document"

phase_N_result_summary = summarize_expected_result(phase_N_purpose)
# "Refine requirements" → "Requirements refined and approved"
```

**Defaults**:
- `phase_N_output_description`: "{phase_N_name} artifacts ready for next phase"
- `phase_N_result_summary`: "{phase_N_name} completed successfully"

#### Phase Verification

| Variable | Derivation | Example |
|----------|------------|---------|
| `{phase_N_verification_1}` | Primary success criterion | "✓ Design document complete" |
| `{phase_N_verification_2}` | Secondary criterion | "✓ User approved design" |
| `{phase_N_verification_3}` | Tertiary criterion (optional) | "✓ Integration points identified" |
| `{phase_N_verification_brief}` | One-line verification | "Design complete and approved" |

**Derivation formulas:**

```python
phase_N_verification_1 = f"✓ {phase_N_skill} completed successfully"
phase_N_verification_2 = f"✓ {phase_N_output_description} produced"
phase_N_verification_3 = derive_quality_check(phase_N_skill, phase_N_purpose)

phase_N_verification_brief = f"{phase_N_result_summary}"
```

**Defaults**:
- `phase_N_verification_1`: "✓ {phase_N_skill} completed"
- `phase_N_verification_2`: "✓ Output ready for next phase"
- `phase_N_verification_3`: "✓ Quality checks passed"

#### Phase Handoff

| Variable | Derivation | Example |
|----------|------------|---------|
| `{phase_N_to_phase_N+1_handoff}` | How output flows to next phase | "Pass design document from brainstorming to planning" |
| `{previous_to_phase_N_handoff}` | Multiple previous phases → current | "Use design and plan from Phases 1-2" |

**Derivation formulas:**

```python
phase_N_to_phase_N1_handoff = f"Pass {phase_N_output_description} to {phase_N1_name}"

# For Phase 3+:
previous_to_phase_N_handoff = f"Use {', '.join(prev_outputs)} from Phases {phase_range}"
```

**Defaults**:
- `phase_N_to_phase_N+1_handoff`: "Use output from {phase_N_name}"
- `previous_to_phase_N_handoff`: "Use previous phase outputs"

#### Phase Failure Handling

| Variable | Derivation | Example |
|----------|------------|---------|
| `{phase_N_failure_action}` | What to do if phase fails | "Return to requirements gathering, clarify with user" |
| `{phase_N_recovery_step_1}` | First recovery step | "Review brainstorming conversation for gaps" |
| `{phase_N_recovery_step_2}` | Second recovery step | "Ask user for additional context" |

**Derivation formulas:**

```python
phase_N_failure_action = determine_failure_response(phase_N_skill, phase_N_purpose)
# For early phases: "Clarify requirements with user"
# For later phases: "Review previous phase outputs"

phase_N_recovery_step_1 = f"Review {phase_N_name.lower()} output for issues"
phase_N_recovery_step_2 = f"Consult {phase_N_skill} documentation"
```

**Defaults**:
- `phase_N_failure_action`: "Stop workflow and report issue to user"
- `phase_N_recovery_step_1`: "Review {phase_N_name} for errors"
- `phase_N_recovery_step_2`: "Ask user for guidance"

---

### 4. Workflow Completion

| Variable | Derivation | Example |
|----------|------------|---------|
| `{deliverable_1_description}` | Primary deliverable | "Implemented feature with tests" |
| `{deliverable_2_description}` | Secondary deliverable | "Design and implementation plan documents" |
| `{deliverable_3_description}` | Tertiary deliverable (optional) | "Code review approval" |
| `{output_location}` | Where deliverables are | "src/features/{feature-name}/" |
| `{final_verification_command_1}` | Bash command to verify | "test -f src/auth.py && echo '✅ Feature file exists'" |
| `{final_verification_command_2}` | Second verification | "pytest tests/ && echo '✅ Tests pass'" |
| `{next_step_1}` | Optional next step | "Deploy to staging environment" |
| `{next_step_2}` | Optional next step | "Update documentation" |

**Derivation formulas:**

```python
deliverable_1_description = extract_primary_output(final_phase_output)
deliverable_2_description = extract_secondary_output(all_phases)
deliverable_3_description = extract_approval_artifact(workflow_phases)

output_location = infer_output_directory(workflow_purpose)
# "feature development" → "src/features/"
# "deployment" → "deployed to {environment}"

final_verification_command_1 = generate_file_check(deliverable_1)
final_verification_command_2 = generate_test_command(workflow_purpose)

next_step_1 = infer_logical_next_step(workflow_purpose)
next_step_2 = suggest_documentation_update(workflow_purpose)
```

**Defaults**:
- `deliverable_1_description`: "{workflow_name} completed successfully"
- `deliverable_2_description`: "All phases produced expected outputs"
- `deliverable_3_description`: "" (optional)
- `output_location`: "Project directory"
- `final_verification_command_1`: "# Manual verification required"
- `final_verification_command_2`: "# Check deliverables"
- `next_step_1`: "" (optional)
- `next_step_2`: "" (optional)

---

### 5. Pattern B Specific (Command)

| Variable | Derivation | Example |
|----------|------------|---------|
| `{phase_N_brief_description}` | One-line phase summary | "Refine requirements" |
| `{arguments_description}` | What $ARGUMENTS contains | "Feature description and requirements" |
| `{example_argument}` | Example command usage | "Add user authentication with OAuth2" |
| `{phase_N_context_item_1}` | Project-specific context 1 | "Consider existing auth system at src/auth/" |
| `{phase_N_context_item_2}` | Project-specific context 2 | "Follow project's security guidelines" |
| `{phase_N_expected_result}` | Expected outcome | "Design integrates with existing auth" |
| `{estimated_duration}` | Time estimate | "30-60 minutes" |
| `{deliverables_location}` | Command output location | "{output_location}" |

**Derivation formulas:**

```python
phase_N_brief_description = extract_verb_phrase(phase_N_purpose)
# "Refine requirements into concrete design" → "Refine requirements"

arguments_description = determine_command_inputs(workflow_purpose)
example_argument = generate_example_input(workflow_purpose)

phase_N_context_item_1 = "Consider project-specific requirements"
phase_N_context_item_2 = "Follow project standards"

phase_N_expected_result = phase_N_result_summary

estimated_duration = estimate_time(phase_count, complexity)
# 3-4 phases × 10-15min each = "30-60 minutes"
```

---

### 6. Pattern C Specific (CLAUDE.md Rules)

| Variable | Derivation | Example |
|----------|------------|---------|
| `{workflow_trigger_description}` | When workflow applies | "implementing any new feature" |
| `{workflow_trigger_condition}` | Condition statement | "When implementing ANY new feature" |
| `{enforcement_level}` | Mandatory/Optional | "MANDATORY" |
| `{exception_condition_1}` | First exception | "User explicitly requests 'skip workflow'" |
| `{exception_condition_2}` | Second exception | "Task is trivial (single line fix)" |

**Derivation formulas:**

```python
workflow_trigger_description = workflow_purpose.lower()
workflow_trigger_condition = f"When {workflow_trigger_description}"
enforcement_level = "MANDATORY" if user_specifies_mandatory else "RECOMMENDED"

exception_condition_1 = f"User explicitly requests 'skip {workflow_slug}'"
exception_condition_2 = determine_trivial_exception(workflow_purpose)
```

---

## Complete Derivation Example

**User Input:**
```
Workflow name: "Feature Development"
Phases:
1. Brainstorming → superpowers:brainstorming
2. Planning → superpowers:writing-plans
3. Implementation → superpowers:test-driven-development
4. Review → superpowers:requesting-code-review
Scope: Universal
Enforcement: Mandatory
```

**Derived Variables (62 total):**

```yaml
# Workflow Metadata
workflow_name: "Feature Development"
workflow_slug: "feature-development"
workflow_description: "Complete feature development workflow using brainstorming, planning, TDD, and code review in sequence"
workflow_purpose: "implementing new features"
workflow_trigger_phrase: "implement a feature"
phase_count: "4"
command_category: "dev"

# Triggers
trigger_example_1: "Implement user authentication"
trigger_example_2: "Add payment processing"
trigger_pattern: "Implement [feature name]"
trigger_conditions: "- User requests new feature\n- Task involves implementation"

# Phase 1: Brainstorming
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

# Phase 2: Planning
phase_2_name: "Planning"
phase_2_skill: "superpowers:writing-plans"
phase_2_purpose: "Create detailed implementation plan"
phase_2_objective: "Use planning to create step-by-step implementation plan with verification"
phase_2_skill_description: "Create detailed implementation plans with bite-sized tasks"
phase_2_prereq_1: "Phase 1 completed successfully"
phase_2_prereq_2: "Design document from Phase 1 available"
phase_2_output_description: "Implementation plan with tasks and verification steps"
phase_2_result_summary: "Plan approved with clear tasks"
phase_2_verification_1: "✓ Plan has bite-sized tasks"
phase_2_verification_2: "✓ Verification steps defined"
phase_2_verification_3: "✓ User approved plan"
phase_2_verification_brief: "Plan complete with verification steps"
phase_2_to_phase_3_handoff: "Use plan to guide TDD implementation"
phase_2_failure_action: "Review design, ensure completeness"
phase_2_recovery_step_1: "Check if design provides enough detail"
phase_2_recovery_step_2: "Ask user to clarify requirements"
phase_2_brief_description: "Create implementation plan"
phase_2_context_item_1: "Include migration steps if needed"
phase_2_context_item_2: "Follow project task breakdown standards"
phase_2_expected_result: "Actionable plan ready for implementation"

# Phase 3: Implementation
phase_3_name: "Implementation"
phase_3_skill: "superpowers:test-driven-development"
phase_3_purpose: "Implement feature using TDD"
phase_3_objective: "Use TDD to implement feature following RED-GREEN-REFACTOR cycle"
phase_3_skill_description: "Write tests first, implement to pass"
phase_3_prereq_1: "Plan from Phase 2 available"
phase_3_output_description: "Implemented feature with passing tests"
phase_3_result_summary: "Feature implemented, all tests pass"
phase_3_verification_1: "✓ All tests pass"
phase_3_verification_2: "✓ Feature implements plan"
phase_3_verification_3: "" # Can be omitted
previous_to_phase_3_handoff: "Use design and plan from Phases 1-2"
phase_3_failure_action: "Review tests and implementation"
phase_3_recovery_step_1: "Check test coverage"
phase_3_recovery_step_2: "Verify implementation matches plan"
phase_3_brief_description: "Implement using TDD"
phase_3_context_item_1: "Follow project's test patterns"
phase_3_context_item_2: "Maintain code quality standards"
phase_3_expected_result: "Working feature with test coverage"

# Phase 4: Review (similar structure)
# ... (phase_4_* variables)

# Completion
deliverable_1_description: "Implemented feature with comprehensive tests"
deliverable_2_description: "Design and implementation plan documents"
deliverable_3_description: "Code review approval"
output_location: "src/features/"
final_verification_command_1: "pytest tests/ && echo '✅ Tests pass'"
final_verification_command_2: "git status && echo '✅ Changes staged'"
next_step_1: "Deploy to staging environment"
next_step_2: "Update user documentation"

# Pattern C specific
workflow_trigger_description: "implementing any new feature"
workflow_trigger_condition: "When implementing ANY new feature"
enforcement_level: "MANDATORY"
exception_condition_1: "User explicitly requests 'skip workflow'"
exception_condition_2: "Task is trivial (single line fix)"
```

---

## Variable Validation Checklist

Before generating workflows, verify all required variables are populated:

**Core (Required for all patterns):**
- [ ] workflow_name
- [ ] workflow_slug
- [ ] workflow_description
- [ ] phase_count
- [ ] For each phase N:
  - [ ] phase_N_name
  - [ ] phase_N_skill
  - [ ] phase_N_purpose

**Pattern A (Orchestrator Skill) - Additional Required:**
- [ ] workflow_trigger_phrase
- [ ] trigger_example_1, trigger_example_2
- [ ] For each phase N:
  - [ ] phase_N_objective
  - [ ] phase_N_prereq_1
  - [ ] phase_N_output_description
  - [ ] phase_N_verification_1, phase_N_verification_2

**Pattern B (Command) - Additional Required:**
- [ ] command_category
- [ ] example_argument
- [ ] arguments_description
- [ ] estimated_duration

**Pattern C (CLAUDE.md) - Additional Required:**
- [ ] workflow_trigger_condition
- [ ] enforcement_level
- [ ] exception_condition_1

**Optional (can use defaults):**
- phase_N_verification_3
- deliverable_3_description
- next_step_1, next_step_2
- phase_N_context_item_2

---

## Fallback Strategy

If user doesn't provide specific details:

1. **Use smart defaults** from this guide
2. **Derive from phase names** using heuristics
3. **Generate generic but functional** variables
4. **Note gaps** in final output, suggest user customization

**Example**:
```
User only provides:
- Workflow: "Deploy"
- Phases: test → build → deploy

Auto-derive:
- workflow_slug: "deploy"
- phase_1_objective: "Use testing to verify application works"
- phase_1_verification_1: "✓ All tests pass"
- phase_1_output_description: "Test results confirming application works"
```

This ensures workflows are always generatable, even with minimal input.
