## {workflow_name} Workflow (MANDATORY)

**When to use**: {workflow_trigger_description}

**Enforcement level**: {enforcement_level}

### Workflow Phases (Must Execute in Order)

When {workflow_trigger_condition}, you MUST execute the following phases in sequence:

#### Phase 1: {phase_1_name} (MANDATORY FIRST)

**Skill**: Use `Skill("{phase_1_skill}")`

**Purpose**: {phase_1_purpose}

**Prerequisites**:
- {phase_1_prereq_1}
- {phase_1_prereq_2}

**Verification before Phase 2**:
- ✓ {phase_1_verification_1}
- ✓ {phase_1_verification_2}

**You cannot proceed to Phase 2 until Phase 1 verification passes.**

---

#### Phase 2: {phase_2_name} (MANDATORY SECOND)

**Skill**: Use `Skill("{phase_2_skill}")`

**Purpose**: {phase_2_purpose}

**Prerequisites**:
- ✓ Phase 1 completed successfully
- {phase_2_prereq_1}
- {phase_2_prereq_2}

**Verification before Phase 3**:
- ✓ {phase_2_verification_1}
- ✓ {phase_2_verification_2}

**You cannot proceed to Phase 3 until Phase 2 verification passes.**

---

#### Phase 3: {phase_3_name} (MANDATORY THIRD)

**Skill**: Use `Skill("{phase_3_skill}")`

**Purpose**: {phase_3_purpose}

**Prerequisites**:
- ✓ Phase 1 completed successfully
- ✓ Phase 2 completed successfully
- {phase_3_prereq_1}

**Final Verification**:
- ✓ {phase_3_verification_1}
- ✓ {phase_3_verification_2}
- ✓ All workflow phases completed

**You cannot claim work is complete until all verifications pass.**

---

<!-- GENERATION NOTE: Add more phases by replicating Phase 2/3 structure -->

---

### Enforcement Rules

**You MUST**:
1. Execute all phases in the specified order
2. Complete verification checkpoints before proceeding
3. Use the exact skills specified for each phase
4. Announce each phase as you begin it
5. Report completion only after final verification passes

**You MUST NOT**:
1. Skip phases (all phases are mandatory)
2. Proceed to next phase if verification fails
3. Reorder phases
4. Substitute different skills without explicit user approval
5. Claim completion without executing all phases

### Exceptions

**This workflow may be skipped only if**:
{exception_condition_1}
{exception_condition_2}

**If unsure whether workflow applies, err on the side of executing it.**

### Failure Recovery

**If Phase {N} fails**:
1. Report failure to user with specific error
2. Do not proceed to Phase {N+1}
3. Ask user if they want to:
   - Retry Phase {N}
   - Modify requirements and retry
   - Abort workflow

**Never silently skip a failed phase.**

### Workflow Summary

**Quick Reference**:
```
{workflow_trigger_condition}
  ↓
Phase 1: {phase_1_name} → Skill("{phase_1_skill}")
  ↓ (verify {phase_1_verification_brief})
Phase 2: {phase_2_name} → Skill("{phase_2_skill}")
  ↓ (verify {phase_2_verification_brief})
Phase 3: {phase_3_name} → Skill("{phase_3_skill}")
  ↓ (verify {phase_3_verification_brief})
✅ Complete
```

**This is a mandatory workflow. You cannot skip it or deviate from the sequence.**

---

<!-- GENERATION NOTE: This section gets added to CLAUDE.md -->
<!-- Location: Add under "## Workflow Rules" or similar section -->
<!-- Integration: Ensure this doesn't conflict with existing workflows -->
