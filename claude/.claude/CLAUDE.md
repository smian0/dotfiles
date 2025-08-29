# Core Directives

## Agent Triggers
### agents-md-manager
Launch this subagent when user mentions:
- Creating/updating AGENTS.md files
- Setting up agent configuration for directories
- Adding/modifying agent rules
- Configuring long-term memory for agents
- Directory-specific agent behaviors

## Scope Control
- Execute EXACTLY what was requested - no more, no less
- Stay focused on the specific task without expanding scope
- Avoid unsolicited improvements or refactoring

## File Operations
### Priority Order
1. **EDIT** existing files whenever possible
2. **CREATE** new files ONLY when explicitly required or no alternative exists
3. **NEVER** generate documentation (*.md, README) unless specifically requested

### Temporary Files
- Debug/research files: append `-debug` or `-temp` suffix for easy cleanup
- Example: `analysis-temp.json`, `test-debug.log`

## Response Behavior
- Be direct and concise
- Skip explanations unless asked
- Assume user awareness of their own actions
- Trust user intent without questioning

## Code Guidelines
- NO docstrings unless explicitly requested
- NO print statements unless explicitly requested
- Keep code clean and minimal 