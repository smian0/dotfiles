# MCP Configuration Manager Skill

Comprehensive MCP server configuration management for Claude Code.

## Quick Start

```bash
# From anywhere in your dotfiles repo
cd ~/dotfiles/claude/.claude/skills/mcp-manager/scripts

# Check consistency
./check-mcp-consistency.sh

# Validate configuration
./validate-mcp-config.sh

# Add new server (interactive)
./add-mcp-server.sh

# Remove server
./remove-mcp-server.sh <server-name>

# Sync user config to dotfiles
./sync-mcp-to-dotfiles.sh
```

## Usage in Claude Code

To use this skill, simply invoke it:

```
Use the mcp-manager skill to add a new MCP server
```

or

```
Use the mcp-manager skill to validate my MCP configuration
```

Claude will follow the comprehensive guidelines in SKILL.md to manage your MCP servers properly.

## What This Skill Does

- **Validates** MCP server configurations and permissions
- **Syncs** configurations between user and dotfiles
- **Adds/Removes** servers safely with consistency checks
- **Detects** orphaned permissions and configuration mismatches
- **Automates** common MCP management tasks

## Scripts Available

| Script | Purpose |
|--------|---------|
| `check-mcp-consistency.sh` | Quick consistency check between .mcp.json and settings.json |
| `validate-mcp-config.sh` | Comprehensive validation with syntax, structure, and consistency checks |
| `add-mcp-server.sh` | Interactive wizard to add new MCP servers |
| `remove-mcp-server.sh` | Safely remove MCP servers and cleanup permissions |
| `sync-mcp-to-dotfiles.sh` | Sync user MCP config to dotfiles for version control |

## File Locations

- User config: `~/.claude/.mcp.json`
- Dotfiles config: `~/dotfiles/claude/.claude/.mcp.json`
- Settings: `~/.claude/settings.json` or `~/dotfiles/claude/.claude/settings.json`

## See Also

- **SKILL.md** - Complete documentation with workflows, examples, and troubleshooting
- **scripts/** - Self-contained scripts for MCP management

## Integration with Dotfiles

This skill is designed to work seamlessly with the dotfiles Stow-based configuration management system. All changes can be version controlled and synced across machines.
