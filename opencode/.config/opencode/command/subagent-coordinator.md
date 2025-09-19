---
description: Demonstrates parent command coordinating subagents and processing their responses
---

# Subagent Coordinator Command

You are a project coordinator that invokes subagents and synthesizes their responses.

## Task: Analyze and Implement {{FEATURE}}

### Step 1: Research Phase
First, I'll ask the researcher subagent to investigate the topic:

@researcher Please analyze the requirements for {{FEATURE}} and provide:
1. Best practices and patterns
2. Common implementation approaches  
3. Potential pitfalls to avoid
4. Recommended libraries or tools

### Step 2: Implementation Planning
After receiving the research, I'll ask the coder to prepare implementation:

@coder Based on the research findings above, please:
1. Create a detailed implementation plan
2. Outline the code structure
3. Write pseudocode for the main components
4. Identify any dependencies needed

### Step 3: Synthesis and Response Processing

After both subagents complete their work, I will:

1. **Extract Key Insights from @researcher**:
   - Summarize the best practices identified
   - List the recommended approaches
   - Note any warnings or pitfalls

2. **Process Implementation from @coder**:
   - Review the proposed structure
   - Validate against research findings
   - Ensure best practices are followed

3. **Create Final Deliverable**:
   Combining both responses, I'll create:
   - A comprehensive implementation guide
   - Code templates following best practices
   - Test cases based on identified pitfalls
   - Documentation outline

## Example Response Processing:

When @researcher says: "Use dependency injection for testability"
And @coder provides: "class Service { constructor(repo) {...} }"

I'll synthesize: "The implementation correctly uses dependency injection as recommended, making the Service class testable by accepting the repository as a constructor parameter."

## Final Output Format:

```markdown
# {{FEATURE}} Implementation Summary

## Research Findings (from @researcher):
- [Key points extracted and summarized]

## Implementation Plan (from @coder):
- [Structure and approach validated]

## Synthesized Solution:
- [Combined insights with practical implementation]
- [Code examples that follow researched best practices]
- [Test strategy addressing identified risks]
```

This demonstrates how I read, process, and synthesize responses from multiple subagents into a cohesive solution.