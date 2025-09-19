---
description: Demonstrate primary agent calling subagents automatically
agent: claude-primary
---

# Multi-Agent Coordination Demo

I need you to demonstrate how primary agents can automatically invoke subagents. Here's what I want you to do:

1. **Research Task**: I need you to research the best practices for dotfiles management and GNU Stow usage patterns. This should trigger the `researcher` subagent automatically since it's a research-focused task.

2. **Coding Task**: After the research, I want you to implement a small utility script that validates dotfiles installation. This should trigger the `coder` subagent automatically since it's a coding task.

3. **Integration**: Show how you coordinate between these subagents while maintaining the overall conversation context.

The goal is to demonstrate:
- Automatic subagent invocation based on task type
- Session navigation between parent and child sessions  
- How different subagents contribute to a larger workflow

Please proceed with this demonstration, and make sure to explicitly show when you're invoking each subagent and why.