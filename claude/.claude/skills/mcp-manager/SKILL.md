---
name: mcp-manager
description: Comprehensive MCP server configuration management with smart workflow routing for user and project levels. Use when adding, removing, syncing, validating, or wrapping MCP servers.
---

# MCP Configuration Manager

Manage Model Context Protocol (MCP) server configurations using a declarative sync model with `claude mcp` CLI as the primary interface.

## When to Use This Skill

- Syncing `~/.claude/.mcp.json` to user-level registration (including "sync to claude.json")
- Adding or removing MCP servers
- Validating MCP server consistency
- Debugging MCP server issues
- Wrapping servers with hot-reload (reloaderoo)

## Core Model

**Declarative Sync:**
- `~/.claude/.mcp.json` = Source of truth (version-controlled manifest)
- User-level registration = Runtime state (via `claude mcp add/remove`)
- `claude mcp list` = Ground truth verification
- Scripts keep manifest and registration in sync

**Key Principle:** Always verify with `claude mcp list` after changes.

## Standard Workflow

```bash
# 1. Check actual registered state (ground truth)
claude mcp list

# 2. Check manifest (desired state)
jq -r '.mcpServers | keys[]' ~/.claude/.mcp.json | sort

# 3. Sync if discrepancy found
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh

# 4. Verify sync succeeded
claude mcp list
```

## Available Scripts

All scripts in `scripts/` directory:

| Script | Purpose | Usage |
|--------|---------|-------|
| `sync-user-mcp.sh` | Sync manifest → user registration | `./sync-user-mcp.sh` |
| `check-mcp-consistency.sh` | Verify config consistency | `./check-mcp-consistency.sh [--project]` |
| `validate-mcp-config.sh` | Comprehensive validation | `./validate-mcp-config.sh [--fix]` |
| `add-mcp-server.sh` | Interactive server addition | `./add-mcp-server.sh` |
| `remove-mcp-server.sh` | Safe server removal | `./remove-mcp-server.sh <name>` |
| `sync-mcp-to-dotfiles.sh` | Sync to version control | `./sync-mcp-to-dotfiles.sh` |

**Primary script:** `sync-user-mcp.sh` - Use after editing `~/.claude/.mcp.json`

## Specialized Workflows

For detailed step-by-step procedures, reference workflow files:

- [Sync User-Level Servers](./workflows/sync-user.md) - After modifying `.mcp.json`
- [Add MCP Server](./workflows/add-server.md) - Install new server
- [Remove MCP Server](./workflows/remove-server.md) - Uninstall server
- [Validate Configuration](./workflows/validate.md) - Check config health
- [Wrap with Reloaderoo](./workflows/wrap-reloaderoo.md) - Enable hot-reload

**Routing:** Match user request to workflow pattern, load that workflow file for detailed instructions.

## Quick Commands

```bash
# Verify registration (use this first)
claude mcp list

# Sync manifest to registration
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh

# Add server (use Claude CLI - cleans up properly)
claude mcp add

# Remove server (use Claude CLI - prevents ghost servers)
claude mcp remove <server-name>

# Check consistency
~/.claude/skills/mcp-manager/scripts/check-mcp-consistency.sh

# Validate everything
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
```

## Configuration Files

**User-Level:**
- `~/.claude/.mcp.json` - Manifest (version-controlled, symlinked from dotfiles)
- `~/.claude/settings.json` - Permissions
- `~/.claude.json` - **DO NOT EDIT** (4+ MB state file, auto-managed)

**Project-Level:**
- `<project>/.mcp.json` - Team-shared servers
- `<project>/.claude/.mcp.json` - Personal project overrides

## Common Issues

### Ghost Servers (Still Connected After Removal)

**Cause:** Config removed from `.mcp.json` but cached in `~/.claude.json`

**Fix:**
```bash
claude mcp remove <server-name>  # Proper cleanup
claude mcp list                  # Verify removed
```

### Servers Not Loading

**Cause:** Broken Stow symlink or JSON syntax error

**Fix:**
```bash
# Check symlink
ls -la ~/.claude/.mcp.json  # Should be symlink

# Validate JSON
jq . ~/.claude/.mcp.json

# Re-stow if broken
cd ~/dotfiles && stow -R claude
```

### Servers Work Locally But Not for Team

**Cause:** Hardcoded paths or missing environment variables

**Fix:**
- Use `${HOME}` or relative paths in `.mcp.json`
- Document required env vars in project README
- Ensure packages available via npm/pip

## File Locations

- Manifest: `~/dotfiles/claude/.claude/.mcp.json` (symlinked to `~/.claude/.mcp.json`)
- Scripts: `~/.claude/skills/mcp-manager/scripts/`
- Workflows: `~/.claude/skills/mcp-manager/workflows/`
- Logs: `~/.claude/logs/`
- State: `~/.claude.json` (auto-managed)

## Integration with Dotfiles

Changes to `~/.claude/.mcp.json` persist to dotfiles via symlink:

```bash
# Edit manifest
vim ~/.claude/.mcp.json

# Sync to registration
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh

# Verify
claude mcp list

# Commit to version control
cd ~/dotfiles
git add claude/.claude/.mcp.json
git commit -m "feat: update MCP servers"
```

---

**For detailed procedures, load the appropriate workflow file above. For troubleshooting, use `claude mcp list` first to check actual state.**
