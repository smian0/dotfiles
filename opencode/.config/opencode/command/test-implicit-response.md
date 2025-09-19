---
description: Test to show implicit response passing from subagents
---

# Test Implicit Response

I'll demonstrate how subagents implicitly return their output.

## Step 1: First Subagent Call
@researcher Please return exactly this text: "RESEARCHER_OUTPUT_12345"

## Step 2: Second Subagent Call  
@coder Please return exactly this text: "CODER_OUTPUT_67890"

## Step 3: Show Both Responses
Now I'll demonstrate that I received both responses implicitly:

From researcher: [The text above that says RESEARCHER_OUTPUT_12345]
From coder: [The text above that says CODER_OUTPUT_67890]

The subagents don't explicitly "return" values - their entire output becomes available in the conversation context automatically.