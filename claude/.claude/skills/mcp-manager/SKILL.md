---
name: mcp-manager
description: Comprehensive MCP server configuration management for user and project levels. Use when adding, removing, syncing, or validating MCP servers in .mcp.json files and settings.json permissions.
---

# MCP Configuration Manager

## Overview

This skill manages Model Context Protocol (MCP) server configurations across user and project levels. It ensures consistency between `.mcp.json` (server definitions) and `settings.json` (tool permissions), provides sync workflows, and validates configurations.

**Use this skill when:**
- Adding or removing MCP servers
- Syncing configurations between user and project levels
- Validating MCP server consistency
- Debugging MCP server issues
- Setting up new projects with MCP servers

**Key Technologies:**
- `.mcp.json`: Server definitions (command, args, env)
- `settings.json`: Tool permissions and hooks
- jq: JSON processing
- Stow: Dotfiles symlink management

---

## Core Concepts

### Configuration Hierarchy

MCP configurations exist at multiple levels (in order of precedence):

1. **User Global** (`~/.mcp.json`)
   - Personal utility servers available everywhere
   - Lowest priority (can be overridden)
   - Example: web-search, personal API tools

2. **Claude Global** (`~/.claude/.mcp.json`)
   - Claude Code global development tools
   - Available to all Claude Code sessions
   - Example: context7, serena, code analysis tools

3. **Project Shared** (`<project>/.mcp.json`)
   - Project-specific servers for the team
   - Committed to git, shared via version control
   - Overrides user-level configs

4. **Project Private** (`<project>/.claude/.mcp.json`)
   - Your private project-specific overrides
   - Usually gitignored (personal to you)
   - Highest priority

### ⚠️ IMPORTANT: State File vs Config Files

**DO NOT EDIT:**
- `~/.claude.json` - This is Claude Code's internal state/cache file (4+ MB)
- Contains: Session history, UI state, cached server info
- Managed automatically by Claude Code
- Editing this file can corrupt your Claude Code installation

**DO EDIT (for MCP configuration):**
- `~/.mcp.json` - User-level MCP servers
- `~/.claude/.mcp.json` - Global Claude Code MCP servers
- `<project>/.mcp.json` - Project-level MCP servers
- `<project>/.claude/.mcp.json` - Private project MCP servers

**Legacy names (don't use):**
- `claude.json`, `claude_config.json`, `claude_desktop_config.json`
- These are old naming conventions - use `.mcp.json` instead

### Configuration Files

#### `.mcp.json` Structure
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "type": "stdio",
      "description": "What this server does",
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

#### `settings.json` Permissions
```json
{
  "permissions": {
    "allow": [
      "mcp__server-name__tool_name",
      "mcp__server-name__another_tool"
    ]
  }
}
```

### Consistency Requirements

For each MCP server:
1. ✅ Defined in `.mcp.json`
2. ✅ Has matching permissions in `settings.json`
3. ✅ All tools from that server are permitted
4. ❌ No orphaned permissions (permissions without server definitions)

---

## Workflows

### 1. Check Configuration Consistency

**When to use:** Before committing changes, after editing MCP configs, during troubleshooting.

```bash
# Check user-level consistency
./scripts/check-mcp-consistency.sh

# Check project-level consistency
./scripts/check-mcp-consistency.sh --project
```

**What it checks:**
- `.mcp.json` servers have matching `settings.json` permissions
- No orphaned permissions
- Valid JSON syntax
- Required fields present

### 2. Sync User ↔ Dotfiles

**When to use:** After modifying `~/.claude/.mcp.json`, to version control changes.

```bash
# Sync from user to dotfiles
./scripts/sync-mcp-to-dotfiles.sh

# Sync from dotfiles to user (after pulling changes)
./scripts/sync-dotfiles-to-mcp.sh
```

**What it does:**
- Copies `.mcp.json` between locations
- Preserves formatting
- Creates backup before overwriting
- Validates syntax

### 3. Add MCP Server

**When to use:** Installing a new MCP server.

**Steps:**

1. **Determine scope** (user or project)
2. **Add server definition to `.mcp.json`**
3. **Add tool permissions to `settings.json`**
4. **Validate consistency**
5. **Restart Claude Code**

**Example: Adding a new server**

```json
// Add to .mcp.json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"],
      "type": "stdio",
      "description": "My custom MCP server",
      "env": {}
    }
  }
}

// Add to settings.json permissions.allow
"mcp__my-server__tool1",
"mcp__my-server__tool2"
```

### 4. Remove MCP Server

**When to use:** Uninstalling an MCP server.

**Steps:**

1. **Remove from `.mcp.json`**
2. **Remove all permissions from `settings.json`**
3. **Validate no orphaned references**
4. **Restart Claude Code**

**Critical:** Must remove BOTH server definition AND permissions to maintain consistency.

### 5. Validate Configuration

**When to use:** After any manual edits, before committing, during CI/CD.

```bash
# Full validation (both files)
./scripts/validate-mcp-config.sh

# Check syntax only
./scripts/validate-mcp-config.sh --syntax-only

# Check consistency only
./scripts/validate-mcp-config.sh --consistency-only
```

**Validation checks:**
- JSON syntax validity
- Required fields present
- Server-permission consistency
- No duplicate server names
- Valid command paths
- Environment variable format

---

## Available Scripts

All scripts are self-contained in `skills/mcp-manager/scripts/`:

### `check-mcp-consistency.sh`
Checks if `.mcp.json` and `settings.json` are in sync.

**Usage:**
```bash
./scripts/check-mcp-consistency.sh [--project]
```

**Options:**
- `--project`: Check project-level instead of user-level
- `--verbose`: Show detailed differences

**Exit codes:**
- `0`: Consistent
- `1`: Inconsistent (shows differences)

### `sync-mcp-to-dotfiles.sh`
Syncs user MCP config to dotfiles for version control.

**Usage:**
```bash
./scripts/sync-mcp-to-dotfiles.sh [--dry-run]
```

**Options:**
- `--dry-run`: Show what would be synced without making changes
- `--backup`: Create backup before overwriting

### `add-mcp-server.sh`
Interactive wizard to add a new MCP server.

**Usage:**
```bash
./scripts/add-mcp-server.sh
```

**Prompts:**
1. Server name
2. Command (npx, uvx, node, python3)
3. Arguments
4. Description
5. Environment variables
6. Scope (user or project)

**Automatically:**
- Validates server name uniqueness
- Adds to `.mcp.json`
- Creates permission placeholders in `settings.json`
- Validates final configuration

### `remove-mcp-server.sh`
Safely removes an MCP server.

**Usage:**
```bash
./scripts/remove-mcp-server.sh <server-name>
```

**Options:**
- `--keep-permissions`: Remove server but keep permissions (for testing)
- `--force`: Skip confirmation prompts

**Safety features:**
- Creates backup before removal
- Shows what will be removed
- Confirms before making changes
- Validates final state

### `validate-mcp-config.sh`
Comprehensive validation of MCP configurations.

**Usage:**
```bash
./scripts/validate-mcp-config.sh [options]
```

**Options:**
- `--syntax-only`: Only check JSON syntax
- `--consistency-only`: Only check server-permission consistency
- `--fix`: Attempt to auto-fix common issues
- `--report`: Generate detailed validation report

---

## Best Practices

### 1. Always Validate After Editing

**Manual edits are error-prone.** After editing `.mcp.json` or `settings.json`:

```bash
./scripts/validate-mcp-config.sh
```

If validation fails, fix issues before restarting Claude Code.

### 2. Use Scripts for Add/Remove Operations

**Don't manually edit JSON files** for adding/removing servers. Use the provided scripts:

```bash
# Add server
./scripts/add-mcp-server.sh

# Remove server
./scripts/remove-mcp-server.sh my-server
```

Scripts ensure consistency and prevent orphaned permissions.

### 3. Sync User Configs to Dotfiles Regularly

**Version control your MCP configurations:**

```bash
# After modifying user configs
./scripts/sync-mcp-to-dotfiles.sh

# Commit to git
cd ~/dotfiles
git add claude/.claude/.mcp.json
git commit -m "feat: add new MCP server for X"
```

### 4. Project MCP Servers Go in Project .claude/

**Don't pollute user configs with project-specific servers.**

- User level: Development tools (serena, context7, zen)
- Project level: Project-specific integrations (project APIs, databases)

### 5. Auto-Restart Configuration

For MCP servers under active development:

```json
{
  "mcpServers": {
    "my-dev-server": {
      "command": "npx",
      "args": ["reloaderoo", "proxy", "--", "python3", "server.py"],
      "env": {
        "MCPDEV_PROXY_AUTO_RESTART": "true"
      }
    }
  }
}
```

**Benefit:** Server auto-restarts on file changes without IDE restart.

### 6. Permission Naming Convention

Always use the format: `mcp__<server-name>__<tool-name>`

**Example:**
```json
"mcp__context7__resolve-library-id",
"mcp__context7__get-library-docs"
```

This makes it easy to find and remove all permissions for a server.

---

## Common Issues & Troubleshooting

### Issue: MCP Server Not Loading

**Symptoms:** Server defined in `.mcp.json` but not available in Claude Code.

**Solutions:**
1. Check JSON syntax: `jq . ~/.claude/.mcp.json`
2. Verify command exists: `which npx` or `which uvx`
3. Test command manually: `npx -y package-name --help`
4. Check Claude Code logs: `~/.claude/logs/`
5. Restart Claude Code completely

### Issue: Orphaned Permissions

**Symptoms:** Permissions in `settings.json` for non-existent servers.

**Detection:**
```bash
./scripts/check-mcp-consistency.sh --verbose
```

**Fix:**
```bash
# Manual: Remove from settings.json
# Or use script:
./scripts/validate-mcp-config.sh --fix
```

### Issue: Inconsistent Configs After Stow

**Symptoms:** User config and dotfiles config don't match.

**Cause:** Direct edits to `~/.claude/.mcp.json` without syncing to dotfiles.

**Solution:**
```bash
# Sync user changes to dotfiles
./scripts/sync-mcp-to-dotfiles.sh

# Or overwrite user from dotfiles
cd ~/dotfiles
stow -R claude
```

### Issue: Server Works Locally But Not in Team

**Symptoms:** Server works on your machine but not for team members.

**Common causes:**
1. **Hardcoded paths** in `.mcp.json`
   - ❌ `/Users/you/projects/server.py`
   - ✅ `${HOME}/projects/server.py`
   - ✅ Relative paths in project `.claude/`

2. **Missing environment variables**
   - Document required env vars in project README
   - Use `.env.example` for templates

3. **Local-only MCP packages**
   - Ensure packages are available via npm/pip
   - Document installation steps

### Issue: Auto-Restart Not Working

**Symptoms:** Server changes don't take effect automatically.

**Checklist:**
1. ✅ `MCPDEV_PROXY_AUTO_RESTART: "true"` in env
2. ✅ Using `reloaderoo proxy` wrapper
3. ✅ Watching correct source files
4. ✅ reloaderoo installed: `npx reloaderoo --version`

**Debug:**
```bash
# Test reloaderoo manually
npx reloaderoo proxy -- python3 server.py
# Make a change to server.py
# Should see "Reloading..." in output
```

---

## Workflow Examples

### Example 1: Setting Up New Project

```bash
# 1. Initialize project Claude config
mkdir -p myproject/.claude
cd myproject

# 2. Copy user MCP servers as starting point (optional)
cp ~/.claude/.mcp.json .claude/.mcp.json

# 3. Add project-specific server
../claude/.claude/skills/mcp-manager/scripts/add-mcp-server.sh

# 4. Validate
../claude/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh --project

# 5. Commit to git
git add .claude/
git commit -m "feat: add project MCP configuration"
```

### Example 2: Syncing Team Changes

```bash
# 1. Pull latest changes
git pull origin main

# 2. Check what changed in .mcp.json
git diff HEAD~1 .claude/.mcp.json

# 3. Validate configuration
./scripts/validate-mcp-config.sh --project

# 4. Restart Claude Code to load new servers
```

### Example 3: Removing Unused Server

```bash
# 1. Check current servers
./scripts/check-mcp-consistency.sh --verbose

# 2. Remove server
./scripts/remove-mcp-server.sh old-server

# 3. Verify removal
./scripts/validate-mcp-config.sh

# 4. Sync to dotfiles (if user-level)
./scripts/sync-mcp-to-dotfiles.sh

# 5. Commit
git add claude/.claude/.mcp.json claude/.claude/settings.json
git commit -m "chore: remove old-server MCP"
```

---

## Checklist

When working with MCP configurations, use this checklist:

**Before Adding a Server:**
- [ ] Determine scope (user or project)
- [ ] Test server command manually
- [ ] Check for naming conflicts
- [ ] Have API keys/credentials ready

**After Adding a Server:**
- [ ] Validate JSON syntax
- [ ] Check consistency (servers + permissions)
- [ ] Restart Claude Code
- [ ] Test server functionality
- [ ] Document configuration (if project-level)

**Before Removing a Server:**
- [ ] Check for dependencies (other configs using it)
- [ ] Create backup
- [ ] Identify all permissions to remove

**After Removing a Server:**
- [ ] Validate no orphaned permissions
- [ ] Check consistency
- [ ] Restart Claude Code
- [ ] Update documentation

**Before Committing Changes:**
- [ ] Run full validation
- [ ] Check git diff for unintended changes
- [ ] Ensure no hardcoded paths
- [ ] Update CLAUDE.md if needed

---

## File Locations

**User Global (Personal):**
- Config: `~/.mcp.json`
- Purpose: Personal utility servers everywhere
- Priority: Lowest

**Claude Global (Development Tools):**
- Config: `~/.claude/.mcp.json`
- Settings: `~/.claude/settings.json`
- Logs: `~/.claude/logs/`
- Purpose: Core Claude Code tooling
- Priority: Medium-low

**Dotfiles (Version Control):**
- Config: `~/dotfiles/claude/.claude/.mcp.json` (symlinked to `~/.claude/.mcp.json`)
- Settings: `~/dotfiles/claude/.claude/settings.json`
- Scripts: `~/dotfiles/claude/.claude/skills/mcp-manager/scripts/`
- Purpose: Version-controlled configs

**Project Shared (Team):**
- Config: `<project>/.mcp.json`
- Purpose: Team-shared project servers
- Priority: Medium-high
- Committed to git: Yes

**Project Private (Personal):**
- Config: `<project>/.claude/.mcp.json`
- Settings: `<project>/.claude/settings.json`
- Purpose: Your private project overrides
- Priority: Highest
- Committed to git: No (gitignored)

**State File (DO NOT EDIT):**
- File: `~/.claude.json`
- Size: 4+ MB
- Purpose: Claude Code internal state/cache
- Managed by: Claude Code automatically

---

## Quick Reference

### Common Commands

```bash
# Check consistency
./scripts/check-mcp-consistency.sh

# Add server (interactive)
./scripts/add-mcp-server.sh

# Remove server
./scripts/remove-mcp-server.sh <name>

# Validate everything
./scripts/validate-mcp-config.sh

# Sync to dotfiles
./scripts/sync-mcp-to-dotfiles.sh

# List all servers
jq -r '.mcpServers | keys[]' ~/.claude/.mcp.json

# List all MCP permissions
jq -r '.permissions.allow[] | select(startswith("mcp__"))' ~/.claude/settings.json | sort
```

### JSON Queries

```bash
# Get server definition
jq '.mcpServers["server-name"]' ~/.claude/.mcp.json

# Count servers
jq '.mcpServers | length' ~/.claude/.mcp.json

# List server commands
jq -r '.mcpServers[] | .command' ~/.claude/.mcp.json

# Find servers with auto-restart
jq -r '.mcpServers | to_entries[] | select(.value.env.MCPDEV_PROXY_AUTO_RESTART == "true") | .key' ~/.claude/.mcp.json

# Get all permissions for a server
jq -r '.permissions.allow[] | select(startswith("mcp__server-name__"))' ~/.claude/settings.json
```

---

## Integration with Dotfiles

This skill is designed to work with the dotfiles Stow-based configuration management:

1. **Version Control:** MCP configs are tracked in `~/dotfiles/claude/.claude/`
2. **Stow Deployment:** `stow claude` creates symlinks from `~/.claude/` to dotfiles
3. **Sync Scripts:** Keep user changes in sync with version-controlled configs

**Workflow:**
```bash
# Make changes to user config
vim ~/.claude/.mcp.json

# Sync to dotfiles for version control
./scripts/sync-mcp-to-dotfiles.sh

# Commit
cd ~/dotfiles
git add claude/.claude/.mcp.json
git commit -m "feat: configure MCP server for X"
git push

# On another machine
cd ~/dotfiles
git pull
stow -R claude
```

---

## Summary

This skill provides comprehensive MCP configuration management:

✅ **Consistency:** Ensures `.mcp.json` and `settings.json` stay in sync
✅ **Safety:** Validation and backups before making changes
✅ **Automation:** Scripts for common operations (add, remove, validate)
✅ **Version Control:** Integration with dotfiles for config management
✅ **Troubleshooting:** Detailed diagnostics and fix procedures

**Always use this skill when working with MCP server configurations to maintain consistency and avoid issues.**
