# AI Documentation Index

This directory contains documentation for Claude Code and related AI development tools.

## Documentation Files

### Claude Code Documentation
- **[anthropic_docs_subagents.md](./anthropic_docs_subagents.md)** - Creating and using sub-agents in Claude Code
- **[anthropic_custom_slash_commands.md](./anthropic_custom_slash_commands.md)** - Custom slash command creation
- **[anthropic_output_styles.md](./anthropic_output_styles.md)** - Configuring output styles
- **[anthropic_quick_start.md](./anthropic_quick_start.md)** - Quick start guide for Claude Code
- **[claude_code_2_settings.md](./claude_code_2_settings.md)** - Claude Code 2.0 settings reference

### Hooks & Automation
- **[cc_hooks_docs.md](./cc_hooks_docs.md)** - Comprehensive hooks documentation
- **[user_prompt_submit_hook.md](./user_prompt_submit_hook.md)** - User prompt submit hook details
- **[cc_hooks_v0_repomix.xml](./cc_hooks_v0_repomix.xml)** - XML reference for hooks

### Claude Agent SDK (NEW)
- **[claude_agent_sdk_python.md](./claude_agent_sdk_python.md)** - Comprehensive Python Agent SDK guide
  - Installation and setup
  - Tool creation patterns
  - Permission handlers
  - Hooks and advanced features
  - Complete code examples
  - Best practices

- **[claude_agent_sdk_quickref.md](./claude_agent_sdk_quickref.md)** - Quick reference for Agent SDK
  - Common patterns
  - Code snippets
  - Quick lookup tables
  - Debugging tips

### Other AI Tools
- **[openai_quick_start.md](./openai_quick_start.md)** - OpenAI integration guide
- **[uv-single-file-scripts.md](./uv-single-file-scripts.md)** - UV tool for Python scripts

## How to Use This Documentation

### For Claude AI Assistant
When building agents or working with Claude Code features, reference these documents:

1. **Building Agents**: Start with `claude_agent_sdk_python.md` for comprehensive guidance
2. **Quick Lookup**: Use `claude_agent_sdk_quickref.md` for code snippets
3. **Sub-agents**: See `anthropic_docs_subagents.md` for Claude Code sub-agents
4. **Slash Commands**: Refer to `anthropic_custom_slash_commands.md` for custom commands
5. **Hooks**: Check `cc_hooks_docs.md` for automation with hooks

### For Developers
- Browse by topic using the sections above
- Most docs include working code examples
- Check "Last Updated" dates for currency

## Claude Agent SDK Overview

The Claude Agent SDK provides two main patterns:

### 1. One-Shot Queries (`query()`)
For single-task executions without maintaining context:
```python
async for msg in query("Task", options):
    process(msg)
```

### 2. Stateful Conversations (`ClaudeSDKClient`)
For interactive multi-turn conversations:
```python
async with ClaudeSDKClient() as client:
    await client.query("First question")
    # Context maintained across queries
    await client.query("Follow-up question")
```

### Key Features
- **Custom Tools**: Define tools with `@tool` decorator
- **Permission Control**: Fine-grained control over tool usage
- **Hooks**: Intercept and modify agent behavior
- **MCP Integration**: Connect to Model Context Protocol servers

## Contributing

When adding new documentation:
1. Use markdown format
2. Include working code examples
3. Add "Last Updated" timestamp
4. Update this README index
5. Follow existing naming conventions

## Related Resources

- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code
- **Agent SDK Docs**: https://docs.claude.com/en/api/agent-sdk/python
- **MCP Documentation**: https://modelcontextprotocol.io

---

*Last Updated: 2025-10-11*
*For Claude Code AI Assistant Reference*
