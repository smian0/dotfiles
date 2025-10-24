---
name: tech-stack-advisor
description: Advises on technology stack choices through comparative analysis. Use when comparing frameworks, libraries, or technical approaches.
---

# Tech Stack Advisor

This skill helps choose between technology options by delegating research to specialists and synthesizing recommendations.

## When to Use This Skill

Use when a user asks to compare technical options:
- "Should I use React or Vue?"
- "What's better: PostgreSQL or MongoDB?"
- "Which testing framework should I choose?"

## Workflow

### Phase 1: Understand Requirements

Ask the user:
1. What is the project type? (web app, mobile, API, etc.)
2. What are the key requirements? (performance, scalability, ease of use)
3. What is the team's experience level?
4. Are there any constraints? (existing stack, time, budget)

### Phase 2: Research Technology Options (DELEGATION)

For each technology option, delegate comprehensive research:

```python
from Task import Task

# Research Option A
Task(
    subagent_type="web-researcher",
    description=f"Research {option_A}",
    prompt=f"""
Research {option_A} comprehensively:

Required Information:
1. Official documentation and current version
2. Learning curve and developer experience
3. Performance characteristics
4. Community size and ecosystem maturity
5. Job market demand
6. Known limitations or drawbacks
7. Best use cases
8. Recent updates and roadmap
9. Enterprise adoption examples
10. Integration with common tools

Provide a structured summary with:
- Key strengths (bullet points)
- Key weaknesses (bullet points)
- Ideal use cases
- Not recommended for
- Sources (official docs, authoritative blogs)
"""
)

# Research Option B
Task(
    subagent_type="web-researcher",
    description=f"Research {option_B}",
    prompt=f"""
Research {option_B} comprehensively:

[Same requirements as Option A]
"""
)
```

### Phase 3: Comparative Analysis

After receiving research results from both subagents:

1. **Create comparison matrix:**
   - Learning curve: Which is easier to learn?
   - Performance: Which is faster?
   - Ecosystem: Which has better libraries/tools?
   - Community: Which has better support?
   - Job market: Which has more demand?
   - Fit for project: Which matches requirements?

2. **Identify trade-offs:**
   - What do you gain with Option A?
   - What do you give up with Option A?
   - What do you gain with Option B?
   - What do you give up with Option B?

3. **Consider project context:**
   - Does team experience favor one option?
   - Do project requirements clearly favor one?
   - Are there timeline or budget constraints?

### Phase 4: Recommendation

Provide clear recommendation:

```markdown
## Recommendation: [Option A/B]

### Why [Option X]:
- Reason 1 (with evidence from research)
- Reason 2 (with evidence from research)
- Reason 3 (with evidence from research)

### Trade-offs Accepted:
- Trade-off 1
- Trade-off 2

### When to Reconsider:
- Condition 1
- Condition 2

### Next Steps:
1. [Specific action]
2. [Specific action]
3. [Specific action]

### Resources:
- [Documentation links from research]
- [Tutorial links from research]
- [Community links from research]
```

## Example Usage

**User:** "Should I use React or Vue for my dashboard project?"

**Skill Response:**
1. Ask clarifying questions about project requirements
2. Delegate research to web-researcher for both React and Vue
3. Analyze results using comparison matrix
4. Provide recommendation based on project fit
5. Include next steps and learning resources

## Decision Criteria: When to Delegate vs. Handle Directly

**Delegate when:**
- ✅ Comparing 2+ technologies requiring current information
- ✅ Need to research ecosystem, community, performance data
- ✅ Require official documentation and best practices

**Handle directly when:**
- ❌ Simple, well-known differences (e.g., "What is React?")
- ❌ User has already researched and just needs synthesis
- ❌ Options are clearly defined in skill knowledge

## Best Practices

1. **Always research both options** - Don't bias toward one
2. **Use current information** - Delegate to get latest data
3. **Consider project context** - Requirements matter more than "best"
4. **Acknowledge trade-offs** - Every choice has pros/cons
5. **Provide actionable next steps** - Help user get started
