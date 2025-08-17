# Claude User Settings

Global Claude Code settings for user-level configuration. These settings apply to all Claude Code sessions unless overridden by project-specific settings.

## Installation

```bash
# From the dotfiles directory
stow -t ~ claude-user

# Or using the deployment script
./scripts/deploy-claude-user.sh
```

## Contents

- **`.claude/settings.json`** - Global user preferences
  - Default model selection
  - Environment variables
  - Permission defaults
  - Terminal notifications
  
- **`.claude/commands/`** - Personal commands available in all projects
  - `daily-summary` - Generate daily activity summary

## Configuration Hierarchy

These user settings are at the lowest priority and will be overridden by:
1. Project `.claude/settings.json`
2. Project `.claude/settings.local.json`
3. Command line arguments

## Customization

Modify `.claude/settings.json` to adjust:
- Default model preferences
- Global environment variables
- Permission modes
- Additional allowed directories
- Notification preferences