# Zen MCP Server

**Purpose**: Advanced reasoning and problem-solving with multi-step workflows, extended thinking, and expert model validation

## Triggers
- Complex debugging requiring systematic investigation
- Architectural decisions needing structured analysis
- Code review before merge/PR
- Pre-commit validation of changes
- Multi-step planning for complex features
- Exploring alternatives and trade-offs
- Deep research requiring hypothesis testing
- Need expert validation from multiple models
- Challenging assumptions or playing devil's advocate

## Choose When
- **Over basic Claude**: When structured workflows provide better results
- **Over native tools**: Use Zen debug/codereview for comprehensive analysis, not simple Read/Edit
- **Over other MCPs**: Serena for code symbols, Context7 for docs, Zen for reasoning
- **Not for**: Simple questions, code symbol operations, documentation lookup, file operations

## Examples
```
"This authentication flow is broken"
→ Zen debug (systematic investigation)

"Review this PR before I merge"
→ Zen codereview (comprehensive quality assessment)

"Should we use React or Vue?"
→ Zen consensus (multi-model evaluation)

"Plan the migration from REST to GraphQL"
→ Zen planner (interactive planning)

"Check my changes before I commit"
→ Zen precommit (git validation)

"What's the Axios API for interceptors?"
→ Context7 (documentation lookup, not Zen)

"Rename this function everywhere"
→ Serena (symbol operation, not Zen)
```
