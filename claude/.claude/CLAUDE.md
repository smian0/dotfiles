# Core Directives

## Agent Triggers
### agents-md-manager
Launch this subagent agents-md-manager when user mentions:
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
### Priority Order - STRICTLY ENFORCE
1. **ALWAYS EDIT** existing files first - scan for existing files that serve the same purpose
2. **ANALYZE EXISTING** - before creating anything new, thoroughly check what already exists
3. **UPDATE/EXTEND** existing test files rather than creating new test suites
4. **CREATE** new files ONLY when:
   - No existing file serves the same purpose
   - Explicitly requested by user
   - Completely different functionality/domain
5. **NEVER** generate documentation (*.md, README) unless specifically requested

### File Creation Rules
- **Test Files**: Always extend existing test files unless testing completely unrelated functionality
- **Configuration**: Update existing config files rather than creating new ones
- **Scripts**: Extend existing scripts with new functions rather than new files
- **Components**: Check for similar existing components to extend before creating new ones

### Temporary Files
- When debugging a specific file: use same filename + `-debug` or `-temp` before extension (e.g., `user-service.js` → `user-service-debug.js`)
- For general debug files: use descriptive names with `-debug` or `-temp` suffix

## Response Behavior
- Be direct and concise
- Skip explanations unless asked
- Assume user awareness of their own actions
- Trust user intent without questioning

## Code Guidelines
- NO docstrings unless explicitly requested
- NO extra comments in the code unless explicitly requested
- NO print statements unless explicitly requested
- Keep code clean and minimal 