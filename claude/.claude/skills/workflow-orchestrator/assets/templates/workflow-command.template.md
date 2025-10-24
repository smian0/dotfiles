---
title: {workflow_name}
description: {workflow_description}. Executes {phase_count}-phase workflow: {phase_1_name} → {phase_2_name} → {phase_3_name}
category: {command_category}
---

# {workflow_name} Workflow Command

Executes complete {workflow_name} workflow using $ARGUMENTS as context.

**Usage**: `/{command_category}:{workflow_slug} <description>`

**Example**: `/{command_category}:{workflow_slug} {example_argument}`

---

## What This Command Does

Automatically executes the following workflow phases:

1. **{phase_1_name}**: {phase_1_brief_description}
2. **{phase_2_name}**: {phase_2_brief_description}
3. **{phase_3_name}**: {phase_3_brief_description}

**Input**: $ARGUMENTS contains: {arguments_description}

**Output**: {final_output_description}

---

## Workflow Execution

### Phase 1: {phase_1_name}

Use Skill tool to invoke {phase_1_skill}:

```
Skill("{phase_1_skill}")
```

**Context to provide**:
- Task description from $ARGUMENTS
- {phase_1_context_item_1}
- {phase_1_context_item_2}

**Expected result**: {phase_1_expected_result}

**Verification before Phase 2**:
{phase_1_verification_brief}

---

### Phase 2: {phase_2_name}

Use Skill tool to invoke {phase_2_skill}:

```
Skill("{phase_2_skill}")
```

**Context to provide**:
- Output from Phase 1 ({phase_1_output})
- {phase_2_context_item_1}
- {phase_2_context_item_2}

**Expected result**: {phase_2_expected_result}

**Verification before Phase 3**:
{phase_2_verification_brief}

---

### Phase 3: {phase_3_name}

Use Skill tool to invoke {phase_3_skill}:

```
Skill("{phase_3_skill}")
```

**Context to provide**:
- Output from Phase 2 ({phase_2_output})
- {phase_3_context_item_1}
- {phase_3_context_item_2}

**Expected result**: {phase_3_expected_result}

**Final verification**:
{phase_3_verification_brief}

---

<!-- GENERATION NOTE: Add more phases by replicating Phase 2/3 structure -->

---

## Completion

After all phases complete successfully, report to user:

```
✅ {workflow_name} workflow completed for: $ARGUMENTS

Results:
- {phase_1_name}: {phase_1_result}
- {phase_2_name}: {phase_2_result}
- {phase_3_name}: {phase_3_result}

Deliverables: {deliverables_location}
```

## Failure Handling

If any phase fails:
1. Report which phase failed
2. Show phase-specific error
3. Ask user if they want to:
   - Retry failed phase
   - Skip and continue (if safe)
   - Abort workflow

**Do not proceed to next phase if current phase fails verification.**

## Quick Reference

**Command**: `/{command_category}:{workflow_slug} <args>`

**Phases**: {phase_1_name} → {phase_2_name} → {phase_3_name}

**Skills used**: {phase_1_skill}, {phase_2_skill}, {phase_3_skill}

**Estimated time**: {estimated_duration}

## Project Customization

To customize this command for your project:

1. Edit phase context items to include project-specific requirements
2. Modify verification criteria for your standards
3. Add project-specific checks or gates
4. Extend with additional phases as needed

This file is project-specific - changes here won't affect other projects.
