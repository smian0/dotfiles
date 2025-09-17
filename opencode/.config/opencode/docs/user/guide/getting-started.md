# OpenCode Project Instructions

This file provides guidance for Claude Code when working with this OpenCode configuration.

## Project Overview

This OpenCode configuration provides seamless integration with Claude Code through automatic agent and command transformation. The system supports multiple AI providers and universal command coverage.

## Available Models

### Confirmed Available on Ollama.com (as of Sept 16, 2025)
- **gpt-oss:20b** - GPT-OSS 20B (Fast, good for quick tasks)
- **gpt-oss:120b** - GPT-OSS 120B (High quality, recommended for complex tasks)
- **deepseek-v3.1:671b** - DeepSeek V3.1 671B (Very large, advanced reasoning)

### Additional Models (Configuration Ready)
- **qwen3-coder:480b** - Qwen3 Coder 480B (Coding focus)*
- **zhipuai/glm-4.5** - Default model for transformed agents

*Check current availability with `oc models` or `opencode models`

## Command Usage Patterns

### Universal Command Support
Both commands work identically with automatic transformation:
```bash
# Using oc wrapper (secure)
oc run --agent claude-test-agent "message"
oc run "direct message" --model ollamat/gpt-oss:120b

# Using opencode directly (shell function)
opencode run --agent claude-test-agent "message"  
opencode run "direct message" --model ollamat/gpt-oss:120b
```

### Interactive Mode
```bash
oc          # Start interactive session
opencode    # Alternative command (identical functionality)
```

## Agent Transformation

### How It Works
- **Source**: Claude agents in `~/dotfiles/claude/.claude/agents/`
- **Target**: Automatically transformed to OpenCode format in `~/.config/opencode/agent/`
- **No Manual Work**: Claude agents work directly in OpenCode
- **Smart Caching**: Only transforms when source files are newer

### Claude Agent Compatibility
All Claude agents are automatically converted:
- Frontmatter format updated (name → description, tools → removed, model added)
- Content preserved
- Tool references updated for OpenCode compatibility

## Environment & Configuration

### Environment Variables
Automatically loaded via LaunchAgent:
- `OLLAMA_API_KEY` - For hosted Ollama.com models
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` - For other providers
- `GITHUB_TOKEN`, `BRAVE_API_KEY` - For additional services

### Configuration Files
- **Main Config**: `opencode.json` - Provider and model settings
- **Agent Directory**: `~/.config/opencode/agent/` - Transformed agents
- **Command Directory**: `~/.config/opencode/command/` - OpenCode commands

## Best Practices

### Model Selection
- **Quick tasks**: Use `gpt-oss:20b` for faster responses
- **Complex tasks**: Use `gpt-oss:120b` for better quality
- **Reasoning tasks**: Use `deepseek-v3.1:671b` for advanced analysis
- **Coding tasks**: Consider `qwen3-coder:480b` if available

### Performance
- Use appropriate context size (`num_ctx`) for your task
- Enable reasoning mode (`"think": true`) for complex analysis
- Set temperature based on task (0.3 for coding, 0.7 for general, 0.9 for creative)

### Debugging
- Enable debug mode: `DEBUG_MODE=true oc run "message"`
- Check transformation logs for agent loading issues
- Verify shell function: `type opencode` should show shell function

## Troubleshooting

### Common Issues
1. **Agent not found**: Check Claude agent exists in source directory
2. **Command not found**: Verify shell function with `type opencode`
3. **Transformation errors**: Check logs with debug mode
4. **Model errors**: Verify API keys with `launchctl getenv OLLAMA_API_KEY`

### Quick Fixes
```bash
# Reload shell function
exec zsh

# Force agent re-transformation
touch ~/dotfiles/claude/.claude/agents/agent-name.md

# Check available models
oc models

# Test basic functionality
oc run --agent claude-test-agent "test"
```

## Related Documentation

- **[README.md](README.md)** - Complete OpenCode configuration overview
- **[AGENT-TRANSFORMATION-ARCHITECTURE.md](AGENT-TRANSFORMATION-ARCHITECTURE.md)** - Transformation system details
- **[SHELL-FUNCTION-MAINTENANCE.md](SHELL-FUNCTION-MAINTENANCE.md)** - Shell function maintenance
- **[TESTING-PROCEDURES.md](TESTING-PROCEDURES.md)** - Testing framework

---

**Last Updated**: September 16, 2025  
**System**: Triple-mechanism transformation with universal command coverage