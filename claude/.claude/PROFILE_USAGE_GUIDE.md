# Claude Profile Usage Guide

This guide provides practical examples and best practices for using the Claude Profile Management System to optimize context usage and improve development efficiency.

## Quick Start

### Initial Setup
```bash
# Check available profiles
claude-profile list

# Switch to minimal profile for basic development
claude-profile switch minimal

# Start Claude with optimized context
claude  
```

### Context Usage Comparison

| Profile | Context Used | Tokens Saved | Active MCP Servers |
|---------|--------------|--------------|-------------------|
| **full** | 80k/200k (40%) | baseline | context7, markdown, playwright, sequential-thinking, serena |
| **backend** | 50k/200k (25%) | 30k tokens | context7, sequential-thinking, serena |
| **minimal** | 50k/200k (25%) | 30k tokens | context7, sequential-thinking, serena |

## Development Scenarios

### Scenario 1: Basic Code Development

**Best Profile**: `minimal`

```bash
claude-profile switch minimal
claude

# Available tools:
# ✅ serena - code analysis, symbol operations, project memory
# ✅ sequential-thinking - complex reasoning and analysis
# ✅ context7 - library documentation lookup
# ❌ playwright - browser testing (not needed)
# ❌ markdown - document processing (not needed)
```

**Use cases:**
- Writing new functions/classes
- Code refactoring and cleanup
- Basic debugging and analysis
- File operations and project navigation

### Scenario 2: Backend API Development

**Best Profile**: `backend`

```bash
claude-profile switch backend
claude

# Available tools:
# ✅ serena - code analysis and project memory
# ✅ sequential-thinking - complex problem solving
# ✅ context7 - library documentation for frameworks
# ❌ playwright - browser testing (not needed for APIs)
# ❌ markdown - document processing (not needed)
```

**Use cases:**
- Building REST APIs or microservices
- Working with databases and ORM frameworks
- Need documentation for library usage patterns
- Backend performance optimization

### Scenario 3: Full-Stack Development

**Best Profile**: `full`

```bash
claude-profile switch full
claude

# Available tools:
# ✅ All MCP servers enabled
# ✅ Project MCP servers (like streamable-mcp-server for browser automation)
```

**Use cases:**
- End-to-end testing with browser automation
- Frontend + backend integration
- Documentation generation and processing
- Complex multi-tool operations

## Profile Switching Strategies

### Development Lifecycle Approach

```bash
# 1. Planning Phase - Use minimal for code design
claude-profile switch minimal
claude
# Design architecture, write core logic

# 2. Implementation Phase - Switch to backend when you need docs
claude-profile switch backend  
# Access library documentation via context7

# 3. Testing Phase - Switch to full for E2E testing
claude-profile switch full
# Use playwright for browser automation
```

### Task-Based Switching

```bash
# Morning: Start with minimal for focused coding
claude-profile switch minimal

# Midday: Switch to backend when integrating APIs
claude-profile switch backend

# Afternoon: Switch to full for testing and documentation
claude-profile switch full
```

## Safety and Maintenance

### Creating Backups

```bash
# Manual backup before major changes
claude-profile backup

# Check backup history
claude-profile restore
# Shows available backups without restoring
```

### Emergency Recovery

```bash
# If something goes wrong, restore from backup
claude-profile restore 20240911_125302

# Or restore to a known-good profile
claude-profile switch minimal  # Always safe fallback
```

### Health Checks

```bash
# Verify current configuration
claude-profile show

# Should display:
# - Current profile name  
# - Number of active MCPs
# - Project MCPs status
# - List of loaded MCP servers
```

## Advanced Usage

### Custom Profile Creation

While the system comes with three profiles, you can create custom profiles by:

1. **Copy existing profile**:
   ```bash
   cp -r ~/.dotfiles/claude/.claude/profiles/backend ~/.dotfiles/claude/.claude/profiles/custom
   ```

2. **Modify MCP servers**:
   ```bash
   # Edit the .mcp.json to add/remove servers
   nano ~/.dotfiles/claude/.claude/profiles/custom/.mcp.json
   ```

3. **Use custom profile**:
   ```bash
   claude-profile switch custom
   ```

### Integration with Shell Scripts

```bash
#!/bin/bash
# Development workflow script

echo "Starting backend development workflow..."

# Switch to backend profile
claude-profile switch backend

# Start development server
npm run dev &

# Launch Claude with optimized context
claude

# When done, restore to minimal profile
claude-profile switch minimal
```

### Performance Monitoring

```bash
# Monitor context usage in Claude sessions
# Use /context command to see token usage

# Before profile optimization:
# 80k/200k tokens (40%) - only 120k available for work

# After switching to minimal:
# 42k/200k tokens (21%) - 158k available for work
# Net gain: 38k tokens (32% more working space)
```

## Troubleshooting

### Common Issues

**Issue**: "Profile not found"
```bash
# Solution: Check available profiles
claude-profile list
# Use exact profile name
```

**Issue**: "JSON validation failed"  
```bash
# Solution: Restore from backup
claude-profile restore [latest_backup]
# Or reset to minimal profile
```

**Issue**: "Changes not taking effect"
```bash
# Solution: Restart Claude session after profile switch
# Profile changes only apply to new Claude sessions
```

### Best Practices

1. **Start New Sessions**: Always restart Claude after profile switching
2. **Use Minimal by Default**: Start with minimal profile, upgrade when needed
3. **Regular Backups**: Create backups before experimenting with custom profiles
4. **Monitor Context**: Use `/context` command to track token usage
5. **Profile Per Project**: Consider different profiles for different project types

## Integration with Development Workflow

### Git Hooks Integration

```bash
# .git/hooks/post-checkout
#!/bin/bash
# Auto-switch profiles based on branch

if [[ $(git branch --show-current) == "main" ]]; then
    claude-profile switch minimal
elif [[ $(git branch --show-current) == "develop" ]]; then
    claude-profile switch backend
else
    claude-profile switch full
fi
```

### VS Code Integration

```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Switch to Backend Profile",
            "type": "shell",
            "command": "claude-profile switch backend",
            "group": "build"
        }
    ]
}
```

This profile system transforms Claude Code from a fixed-configuration tool into a flexible, context-aware development environment that adapts to your specific needs while maximizing available working memory.