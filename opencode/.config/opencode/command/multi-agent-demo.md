---
description: Demonstrates invoking multiple subagents to collaborate on a task
---

# Multi-Agent Demo Command

You are a project coordinator. When asked to create something, coordinate between two specialized agents:

## Sequential Agent Coordination

**Note: OpenCode executes @mentions sequentially, not in parallel. True parallel agent execution is not currently supported.**

### Step 1: Research Phase
@researcher Please research best practices and patterns for implementing {{TASK}}. Focus on:
- Common implementation approaches
- Performance considerations  
- Best practices and anti-patterns
- Relevant libraries or frameworks

### Step 2: Implementation Phase
Based on the research above, @coder please implement {{TASK}} by:
- Using the best practices identified
- Following the recommended patterns
- Creating clean, efficient code
- Adding appropriate error handling

## How to achieve parallel-like behavior in OpenCode:

1. **Use tool batching**: Tools (like bash commands) can run in parallel when called in a single message
2. **Single agent with parallel tools**: Have one agent execute multiple tools simultaneously
3. **External orchestration**: Use the OpenCode API to manage multiple agent sessions programmatically

## Limitations:
- @mentions in a single message execute sequentially
- Each subagent waits for the previous one to complete
- No native support for concurrent agent execution within a command