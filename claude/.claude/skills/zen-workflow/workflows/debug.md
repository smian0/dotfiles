# Debug Workflow

**Triggers**: "zen debug", error keywords ("bug", "error", "broken", "failing", "not working")

## Execution Strategy

### Priority 1: Use Specialized Skill (if available)

Check if the project has the `zen-debug-consensus` skill:
- Look for `.claude/skills/zen-debug-consensus/SKILL.md` in the project
- If found, use: `Skill(skill="zen-debug-consensus")`

The zen-debug-consensus skill provides:
- Automatic Context7 consultation for external library issues
- Multi-model consensus debugging (deepseek-v3.1, qwen3-coder, qwen3)
- Cross-validated debugging with expert analysis
- Bridges official documentation with AI reasoning
- 100% free Ollama Cloud models

### Priority 2: Embedded Debug Workflow (fallback)

If zen-debug-consensus skill is not available, use this embedded workflow:

#### Step 1: Detect External Libraries

Check if the bug involves external libraries/frameworks:

**Look for**:
- Import statements: `import fastmcp`, `from anthropic import`, `require('express')`
- Framework keywords: FastMCP, Anthropic, Express, React, Vue, Next.js, Django, Flask
- Library-specific errors in stack traces
- API usage questions

**If external library detected** → Consult Context7 first

#### Step 2: Investigation (thinkdeep tool)

Systematic investigation of the bug with qwen3-coder:480b-cloud

**Investigation steps**:
1. Understand the error - What's failing?
2. Trace the flow - How did we get here?
3. Form hypothesis - What's the likely cause?
4. Test hypothesis - Does evidence support it?
5. Identify fix - What needs to change?

Continue investigation until confidence is "high" or "very_high".

#### Step 3: Multi-Model Consensus (consensus tool)

Validate findings with multiple models:
- deepseek-v3.1:671b-cloud
- qwen3-coder:480b-cloud
- qwen3:235b-cloud

**What consensus validates**:
- ✅ Root cause correctly identified
- ✅ Proposed fix addresses the issue
- ✅ No unintended side effects
- ✅ Better alternative approaches
- ✅ Edge cases covered

## Notes

- **Always try zen-debug-consensus first** if available in the project
- **Check for external libraries** before investigation
- **Use Context7** when external libraries involved
- **Use thinkdeep** for systematic investigation
- **Validate with consensus** to catch blind spots
- **Track costs** - prefer Ollama Cloud, escalate only if needed
