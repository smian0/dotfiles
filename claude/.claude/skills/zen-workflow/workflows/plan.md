# Planning Workflow

**Triggers**: "zen plan", planning keywords ("implement", "build", "design", "architect")

## Execution Strategy

### Priority 1: Use Specialized Skill (if available)

Check if the project has the `zen-plan` skill:
- Look for `.claude/skills/zen-plan/SKILL.md` in the project
- If found, use: `Skill(skill="zen-plan")`

The zen-plan skill provides:
- Interactive step-by-step planning with revision and branching
- Research-backed multi-phase consensus validation (MIT approach)
- Adversarial critique to prevent "Silent Agreement"
- Automatic save to Serena memory (`.serena/memories/`)
- Post-implementation validation (Phase 4)
- 100% free Ollama Cloud models

### Priority 2: Embedded Planning Workflow (fallback)

If zen-plan skill is not available, use this embedded workflow:

#### Step 1: Interactive Planning (planner tool)

Use the `planner` tool for step-by-step planning:

```python
mcp__zen__planner(
    model="kimi-k2-thinking:cloud",  # Large context + thinking mode
    step=1,
    total_steps=1,  # Will adjust as we go
    next_step_required=True,
    step="Describe the task, problem, and scope. What are we planning to implement?",
    use_assistant_model=True  # Enable expert analysis
)
```

**Planning Steps**:
1. **Initial scope** - Describe task and requirements
2. **Break down** - Identify major components/phases
3. **Detail steps** - Specific implementation tasks
4. **Dependencies** - Order and relationships
5. **Validation** - Review for completeness

Continue planning until you have:
- Clear implementation steps
- Dependencies identified
- Resource requirements noted
- Success criteria defined

#### Step 2: Validation (consensus tool)

Validate the plan with multi-model consensus:

```python
mcp__zen__consensus(
    models=[
        {"model": "deepseek-v3.1:671b-cloud", "stance": "for"},
        {"model": "qwen3-coder:480b-cloud", "stance": "neutral"},
        {"model": "kimi-k2:1t-cloud", "stance": "against"}
    ],
    step=1,
    total_steps=1,
    next_step_required=False,
    findings="Initial plan completed. Need validation from multiple perspectives.",
    step="Evaluate this implementation plan:\n\n[INSERT PLAN HERE]\n\nAssess feasibility, identify risks, and suggest improvements."
)
```

**What consensus validates**:
- ✅ Feasibility - Can this be implemented?
- ✅ Completeness - Are any steps missing?
- ✅ Order - Is the sequence logical?
- ✅ Risks - What could go wrong?
- ✅ Improvements - How to make it better?

#### Step 3: Revise (if needed)

Based on consensus feedback:
- Revise plan using planner tool
- Address identified issues
- Add missing steps
- Reorder for better flow

#### Step 4: Final Plan

Present the final plan with:
- **Objective**: What we're implementing
- **Tasks**: Numbered steps with file changes
- **Dependencies**: What depends on what
- **Validation**: How to verify success
- **Estimated effort**: Time/complexity

## Model Selection

**Planning (planner tool)**:
- Default: `kimi-k2-thinking:cloud` (large context + thinking)
- Fallback: `deepseek-v3.1:671b-cloud` (strong reasoning)

**Validation (consensus tool)**:
- Model 1: `deepseek-v3.1:671b-cloud` (for stance)
- Model 2: `qwen3-coder:480b-cloud` (neutral/technical)
- Model 3: `kimi-k2:1t-cloud` (against/cautious)

**Escalation**:
- If context >256K → Use `gemini-2.5-pro`
- If requires extreme reasoning → Use `o3` or `gpt-5`

## Example Usage

```
User: "zen plan: implement user authentication with OAuth2"

Claude: I'm using the zen-workflow router.
→ Detected: "zen plan" (explicit trigger)
→ Routing to: PLAN workflow
→ Checking for zen-plan skill...
→ Not found. Using embedded planning workflow.

Step 1: Interactive Planning
[Using planner with kimi-k2-thinking:cloud]

Planning Step 1/5: Initial Scope
- Implement OAuth2 authentication
- Support multiple providers (Google, GitHub)
- Secure token storage
- User profile management

Planning Step 2/5: Break Down Components
1. OAuth2 provider configuration
2. Authorization flow implementation
3. Token management
4. User session handling
5. Security measures

[Continue until complete plan...]

Step 2: Validation
[Using consensus with 3 models]

deepseek (for): Plan is solid, good security practices
qwen3-coder (neutral): Consider adding rate limiting
kimi (against): Missing error handling for failed auth

Step 3: Revise Plan
[Address feedback - add rate limiting and error handling]

Step 4: Final Plan

# Implementation Plan: OAuth2 Authentication

## Objective
Implement secure OAuth2 authentication with multi-provider support

## Tasks
1. Configure OAuth2 providers (config/oauth.py)
2. Implement authorization flow (auth/oauth_handler.py)
3. Add token management (auth/token_manager.py)
4. Create user session handling (middleware/session.py)
5. Implement rate limiting (middleware/rate_limit.py)
6. Add comprehensive error handling (auth/errors.py)
7. Write tests (tests/test_auth.py)

## Dependencies
- Task 2 depends on Task 1
- Tasks 3-6 depend on Task 2
- Task 7 depends on all previous tasks

## Validation
- OAuth flow completes successfully
- Tokens stored securely
- Rate limiting prevents abuse
- Error handling covers all failure cases
- All tests pass

Cost: $0 (all Ollama Cloud models)
```

## Notes

- **Always try zen-plan first** if available in the project
- **Use planner tool** for interactive step-by-step planning
- **Validate with consensus** to catch issues early
- **Revise based on feedback** before finalizing
- **Track costs** - prefer Ollama Cloud, escalate only if needed
