---
name: {workflow_slug}
description: {workflow_description}. Use when user requests "{workflow_trigger_phrase}"
---

# {workflow_name} Workflow

Orchestrates multiple skills in coordinated sequence for {workflow_purpose}.

## When to Use

Activate this workflow when user requests:
- "{trigger_example_1}"
- "{trigger_example_2}"
- Any task matching: {trigger_pattern}

## Workflow Phases

This workflow executes **{phase_count} mandatory phases** in sequence:

| # | Phase | Skill | Purpose |
|---|-------|-------|---------|
| 1 | {phase_1_name} | `{phase_1_skill}` | {phase_1_purpose} |
| 2 | {phase_2_name} | `{phase_2_skill}` | {phase_2_purpose} |
| 3 | {phase_3_name} | `{phase_3_skill}` | {phase_3_purpose} |

**Critical Rule**: Phases must execute in order. Do not skip phases.

---

## Phase Execution

<!-- GENERATION NOTE: Replicate this phase structure for each phase in the workflow -->

### Phase 1: {phase_1_name} (MANDATORY)

**Objective**: {phase_1_objective}

**Prerequisites**:
- {phase_1_prereq_1}
- {phase_1_prereq_2}

**Execution**:

1. **Announce phase**: "Starting Phase 1: {phase_1_name}"

2. **Invoke skill** using Skill tool:
   ```
   Skill("{phase_1_skill}")
   ```

3. **Follow skill instructions** completely until skill completes

4. **Collect output**: {phase_1_output_description}

**Verification Checkpoint**:

Before proceeding to Phase 2, verify:
- ✓ {phase_1_verification_1}
- ✓ {phase_1_verification_2}
- ✓ {phase_1_verification_3}

**If verification fails**: {phase_1_failure_action}

**Phase 1 Complete** ✅

---

### Phase 2: {phase_2_name} (MANDATORY)

**Objective**: {phase_2_objective}

**Prerequisites**:
- ✓ Phase 1 completed successfully
- {phase_2_prereq_1}
- {phase_2_prereq_2}

**Execution**:

1. **Announce phase**: "Starting Phase 2: {phase_2_name}"

2. **Use Phase 1 output** as input: {phase_1_to_phase_2_handoff}

3. **Invoke skill** using Skill tool:
   ```
   Skill("{phase_2_skill}")
   ```

4. **Follow skill instructions** completely until skill completes

5. **Collect output**: {phase_2_output_description}

**Verification Checkpoint**:

Before proceeding to Phase 3, verify:
- ✓ {phase_2_verification_1}
- ✓ {phase_2_verification_2}
- ✓ {phase_2_verification_3}

**If verification fails**: {phase_2_failure_action}

**Phase 2 Complete** ✅

---

### Phase 3: {phase_3_name} (MANDATORY)

**Objective**: {phase_3_objective}

**Prerequisites**:
- ✓ Phase 1 completed successfully
- ✓ Phase 2 completed successfully
- {phase_3_prereq_1}

**Execution**:

1. **Announce phase**: "Starting Phase 3: {phase_3_name}"

2. **Use previous outputs** as input: {previous_to_phase_3_handoff}

3. **Invoke skill** using Skill tool:
   ```
   Skill("{phase_3_skill}")
   ```

4. **Follow skill instructions** completely until skill completes

5. **Collect output**: {phase_3_output_description}

**Verification Checkpoint**:

Verify final workflow completion:
- ✓ {phase_3_verification_1}
- ✓ {phase_3_verification_2}
- ✓ All phases completed successfully

**If verification fails**: {phase_3_failure_action}

**Phase 3 Complete** ✅

---

<!-- GENERATION NOTE: Add more phases by replicating Phase 2/3 structure -->

## Workflow Completion

After all phases complete:

**Final Verification**:
```bash
{final_verification_command_1}
{final_verification_command_2}
```

**Report to User**:
```
✅ {workflow_name} Workflow Completed Successfully

Phases executed:
1. ✅ {phase_1_name} - {phase_1_result_summary}
2. ✅ {phase_2_name} - {phase_2_result_summary}
3. ✅ {phase_3_name} - {phase_3_result_summary}

Deliverables:
{deliverable_1_description}
{deliverable_2_description}
{deliverable_3_description}

Location: {output_location}
```

**Next Steps** (optional):
{next_step_1}
{next_step_2}

## Failure Recovery

**If Phase 1 fails**:
1. {phase_1_recovery_step_1}
2. {phase_1_recovery_step_2}
3. Retry Phase 1 or abort workflow

**If Phase 2 fails**:
1. {phase_2_recovery_step_1}
2. {phase_2_recovery_step_2}
3. Option: Rollback to Phase 1 or abort

**If Phase 3 fails**:
1. {phase_3_recovery_step_1}
2. {phase_3_recovery_step_2}
3. Option: Retry Phase 3 or seek user guidance

**General Recovery**:
- Check skill availability: `ls ~/.claude/skills/`
- Verify prerequisites met
- Consult individual skill documentation
- Ask user for clarification if workflow requirements unclear

## Customization for Specific Projects

To adapt this workflow:

1. **Add project-specific phases**: Insert new phase sections
2. **Modify verification**: Enhance verification checkpoints
3. **Add conditional logic**: Create branches based on context
4. **Integrate tools**: Add tool invocations within phases
5. **Extend deliverables**: Define additional outputs

## Skills Referenced

This workflow uses the following skills:
- [{phase_1_skill}](./../{phase_1_skill}/SKILL.md) - {phase_1_skill_description}
- [{phase_2_skill}](./../{phase_2_skill}/SKILL.md) - {phase_2_skill_description}
- [{phase_3_skill}](./../{phase_3_skill}/SKILL.md) - {phase_3_skill_description}

Verify all skills exist before executing workflow.
