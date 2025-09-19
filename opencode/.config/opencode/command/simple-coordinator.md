---
description: Simple demonstration of reading subagent responses
---

# Simple Coordinator

I'll coordinate two subagents and show how I process their responses.

## Step 1: Ask researcher
@researcher What are the best practices for implementing {{TASK}}?

## Step 2: Ask coder  
@coder Based on the above research, provide a code outline for {{TASK}}.

## Step 3: Process Responses
After receiving both responses, I will:
- Quote key points from @researcher's response
- Reference specific code suggestions from @coder
- Combine them into a final recommendation

The final output will explicitly show:
"Based on @researcher's finding that '[quote from researcher]' and @coder's implementation of '[quote from coder]', the recommended approach is..."