---
name: mcp-manager
description: Comprehensive MCP server configuration management for user and project levels. Use when adding, removing, syncing, or validating MCP servers in .mcp.json files and settings.json permissions.
---

# MCP Configuration Manager

## Overview

This skill manages Model Context Protocol (MCP) server configurations using a **declarative sync model**:

**📄 `~/.claude/.mcp.json`** = Source of truth (version-controlled manifest)
**🔧 User-level MCP registration** = Runtime state (via `claude mcp add --scope user`)
**🤖 This skill** = Keeps them in sync automatically

**Use this skill when:**
- Adding or removing MCP servers
- Syncing `~/.claude/.mcp.json` to user-level registration
- Validating MCP server consistency
- Debugging MCP server issues
- Setting up new projects with MCP servers

**Key Technologies:**
- `~/.claude/.mcp.json`: Declarative manifest (version-controlled)
- `claude mcp add/remove`: Server registration CLI
- `~/.claude.json`: Runtime state (auto-managed by Claude Code)
- `jq`: JSON processing
- Stow: Dotfiles symlink management

---

## Core Concepts

### Declarative Sync Model

**How it works:**

1. **Define** servers in `~/.claude/.mcp.json` (version-controlled manifest)
2. **Run sync** script to register them at user level: `~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh`
3. **Claude Code** loads servers from user-level registration
4. **Repeat** sync whenever you modify `~/.claude/.mcp.json`

**Why this model:**
- ✅ Version-controlled: `~/.claude/.mcp.json` tracked in dotfiles
- ✅ Team-shareable: Commit and push MCP config changes
- ✅ Declarative: Manifest describes desired state
- ✅ Automated: Sync script ensures runtime matches manifest
- ✅ Stow-friendly: Symlinked to `~/dotfiles/claude/.claude/.mcp.json`

### Configuration Levels

MCP servers can be configured at multiple levels:

1. **User-level** (via `claude mcp add --scope user`)
   - Registered in `~/.claude.json` (managed by Claude Code)
   - Synced from `~/.claude/.mcp.json` manifest
   - Available to all projects
   - Example: context7, serena, zen, code analysis tools

2. **Project-level** (`<project>/.mcp.json`)
   - Project-specific servers for the team
   - Committed to git, shared via version control
   - Example: project APIs, databases, custom tools

### ⚠️ IMPORTANT: State File vs Config Files

**DO NOT EDIT:**
- `~/.claude.json` - This is Claude Code's internal state/cache file (4+ MB)
- Contains: Session history, UI state, **cached server configurations**
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

### 🔍 Understanding State File Caching

**CRITICAL: Claude Code caches MCP server configs in ~/.claude.json**

When you add servers to `.mcp.json` files, Claude Code:
1. Reads the `.mcp.json` configuration
2. **Copies the server config into `~/.claude.json` cache**
3. Launches the server processes
4. Keeps servers "connected" even if you remove them from `.mcp.json`

**This means:**
- ❌ Manual removal from `.mcp.json` alone won't disconnect the server
- ❌ Server processes may continue running (orphaned processes)
- ❌ Cache in `~/.claude.json` persists even after IDE restart
- ✅ Use `claude mcp remove <server-name>` to properly clean up both config and cache
- ✅ Use `claude mcp list` to see what's actually active (not just configured)

**Why this happens:**
- Performance optimization - cached configs load faster
- Session persistence - servers stay connected across IDE restarts
- Process management - Claude Code tracks running server processes

**When cache gets out of sync:**
1. You manually edit `.mcp.json` (add/remove servers)
2. IDE restart doesn't rebuild cache
3. Old servers remain in `~/.claude.json` and show as "connected"
4. Need `claude mcp remove` to clean up properly

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

### 1. Sync User-Level MCP Servers (PRIMARY WORKFLOW)

**When to use:** After modifying `~/.claude/.mcp.json`, or when servers aren't loading.

```bash
# Dry-run to see what would change
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh --dry-run

# Actually sync servers
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
```

**What it does:**
- Reads servers from `~/.claude/.mcp.json` manifest
- Registers each server at user level via `claude mcp add --scope user`
- Skips servers already registered
- Handles stdio, HTTP, and SSE transports
- Handles environment variables and headers
- Shows final server list with connection status

**This is the PRIMARY way to manage user-level MCP servers.**

### 2. Adding/Removing User-Level Servers

**Adding a server:**

1. Edit `~/.claude/.mcp.json` to add server definition
2. Run sync script: `~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh`
3. Verify: `claude mcp list`
4. Commit: `cd ~/dotfiles && git add claude/.claude/.mcp.json && git commit`

**Removing a server:**

1. Remove from `~/.claude/.mcp.json`
2. Run: `claude mcp remove <server-name>`
3. Commit: `cd ~/dotfiles && git add claude/.claude/.mcp.json && git commit`

**Alternative (manual):**
```bash
# Add directly (bypasses manifest)
claude mcp add --scope user <name> <command> [args...]

# But you should also update ~/.claude/.mcp.json to keep manifest in sync
```

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

**⚠️ RECOMMENDED METHOD: Use Claude CLI**

```bash
# This is the BEST way to remove a server
claude mcp remove <server-name>
```

**Why use `claude mcp remove`:**
- ✅ Removes from `.mcp.json` configuration files
- ✅ Cleans up cached config in `~/.claude.json` state file
- ✅ Kills any running server processes
- ✅ Prevents "still connected" ghost servers
- ✅ Handles all cleanup automatically

**Verify removal:**
```bash
# Check what servers are actually active
claude mcp list
```

**ALTERNATIVE: Manual Removal (Not Recommended)**

If you must manually remove (e.g., scripting, automation):

1. **Kill any running processes:**
   ```bash
   pkill -f "server-name"
   pkill -f "reloaderoo.*server-name"
   ```

2. **Remove from `.mcp.json`:**
   ```bash
   jq 'del(.mcpServers["server-name"])' ~/.claude/.mcp.json > /tmp/mcp.json
   mv /tmp/mcp.json ~/.claude/.mcp.json
   ```

3. **Remove permissions from `settings.json`:**
   ```bash
   # Remove all permissions starting with "mcp__server-name__"
   jq '.permissions.allow |= map(select(startswith("mcp__server-name__") | not))' ~/.claude/settings.json > /tmp/settings.json
   mv /tmp/settings.json ~/.claude/settings.json
   ```

4. **Clean up cache using Claude CLI:**
   ```bash
   # Even with manual removal, use this to clean cache
   claude mcp remove server-name
   ```

5. **Restart Claude Code**

**Critical:** Manual removal can leave orphaned processes and cache entries. Always use `claude mcp remove` when possible.

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

### 1. Use Claude CLI for MCP Operations

**ALWAYS use `claude mcp` commands for server management:**

```bash
# List active servers (shows actual state, not just config)
claude mcp list

# Add a server (interactive)
claude mcp add

# Remove a server (cleans up config + cache + processes)
claude mcp remove <server-name>

# Show server details
claude mcp show <server-name>
```

**Why Claude CLI over manual editing:**
- ✅ Automatically cleans up state file cache (`~/.claude.json`)
- ✅ Kills orphaned processes
- ✅ Validates configuration syntax
- ✅ Prevents ghost servers
- ✅ Ensures consistency across all config levels

**When to manually edit `.mcp.json`:**
- Bulk operations (adding multiple servers at once)
- Automation scripts
- Version control operations (syncing between machines)
- Complex environment variable configurations

**After manual edits:**
```bash
# Validate syntax
jq . ~/.claude/.mcp.json

# Restart Claude Code to pick up changes
# Then verify:
claude mcp list
```

### 2. Always Validate After Manual Editing

**Manual edits are error-prone.** After editing `.mcp.json` or `settings.json`:

```bash
./scripts/validate-mcp-config.sh
```

If validation fails, fix issues before restarting Claude Code.

### 3. Check Actual State with `claude mcp list`

**Don't trust config files alone.** Use `claude mcp list` to see what's actually running:

```bash
# What's configured (may be outdated)
jq -r '.mcpServers | keys[]' ~/.claude/.mcp.json

# What's actually active (truth)
claude mcp list
```

If there's a mismatch, you likely have:
- Cached servers in `~/.claude.json`
- Orphaned processes
- Need to use `claude mcp remove` for cleanup

### 4. Sync User Configs to Dotfiles Regularly

**Version control your MCP configurations:**

```bash
# After modifying user configs
./scripts/sync-mcp-to-dotfiles.sh

# Commit to git
cd ~/dotfiles
git add claude/.claude/.mcp.json
git commit -m "feat: add new MCP server for X"
```

### 5. Project MCP Servers Go in Project .claude/

**Don't pollute user configs with project-specific servers.**

- User level: Development tools (serena, context7, zen)
- Project level: Project-specific integrations (project APIs, databases)

### 6. Auto-Restart Configuration

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

### 7. Permission Naming Convention

Always use the format: `mcp__<server-name>__<tool-name>`

**Example:**
```json
"mcp__context7__resolve-library-id",
"mcp__context7__get-library-docs"
```

This makes it easy to find and remove all permissions for a server.

### 8. Working with Stow-Managed Configurations

**⚠️ CRITICAL: Do not break Stow symlinks!**

If your dotfiles use GNU Stow, `~/.claude/.mcp.json` is a **symlink** to `~/dotfiles/claude/.claude/.mcp.json`.

**WRONG - Breaks symlink:**
```bash
# This overwrites the symlink with a regular file!
jq '.mcpServers["new-server"] = {...}' ~/.claude/.mcp.json > /tmp/mcp.json
mv /tmp/mcp.json ~/.claude/.mcp.json  # ❌ Destroys symlink
```

**RIGHT - Preserves symlink:**
```bash
# Option 1: Modify the source file in dotfiles
jq '.mcpServers["new-server"] = {...}' ~/dotfiles/claude/.claude/.mcp.json > /tmp/mcp.json
mv /tmp/mcp.json ~/dotfiles/claude/.claude/.mcp.json

# Option 2: Use sponge (moreutils package)
jq '.mcpServers["new-server"] = {...}' ~/.claude/.mcp.json | sponge ~/.claude/.mcp.json

# Option 3: Edit in place with temporary file in same directory
jq '.mcpServers["new-server"] = {...}' ~/.claude/.mcp.json > ~/.claude/.mcp.json.tmp
mv ~/.claude/.mcp.json.tmp ~/.claude/.mcp.json
```

**If you accidentally break the symlink:**
```bash
# 1. Remove the regular file
rm ~/.claude/.mcp.json ~/.claude/MCP_*.md

# 2. Re-stow to recreate symlinks
cd ~/dotfiles
stow -R claude

# 3. Verify symlinks
ls -la ~/.claude/.mcp.json  # Should show -> ../dotfiles/...
```

**Verification:**
```bash
# Check if file is a symlink
ls -la ~/.claude/.mcp.json

# Should show: lrwxr-xr-x ... .mcp.json -> ../dotfiles/claude/.claude/.mcp.json
# NOT: -rw-r--r-- ... .mcp.json
```

**Why this matters:**
- Stow symlinks keep configs version-controlled
- Breaking symlinks creates drift between `~/.claude/` and `~/dotfiles/`
- Claude Code may not detect configuration changes properly
- MCP servers may fail to load

---

## Common Issues & Troubleshooting

### Issue: Server Still Shows as "Connected" After Removal

**Symptoms:** Removed server from `.mcp.json` but still appears in MCP server list with status "✔ connected".

**Root Cause:** Server config cached in `~/.claude.json` state file, orphaned processes still running.

**Solutions (in order):**

1. **Use Claude CLI to remove properly:**
   ```bash
   claude mcp remove <server-name>
   claude mcp list  # Verify it's gone
   ```

2. **If still showing, kill orphaned processes:**
   ```bash
   # Find all processes for this server
   ps aux | grep -i "server-name"

   # Kill them
   pkill -f "server-name/server.py"
   pkill -f "reloaderoo.*server-name"
   ```

3. **Restart Claude Code completely** (not just reload window)

4. **Last resort - manual cache cleanup:**
   ```bash
   # ⚠️ DANGEROUS - Only if above steps fail
   # Backup first!
   cp ~/.claude.json ~/.claude.json.backup

   # Remove server from cache using jq
   jq 'del(.mcpServers["server-name"])' ~/.claude.json > /tmp/claude.json
   mv /tmp/claude.json ~/.claude.json

   # Restart Claude Code
   ```

**Prevention:**
- ✅ Always use `claude mcp remove` instead of manual editing
- ✅ Use `claude mcp list` to check actual state (not just config files)
- ❌ Don't manually edit `.mcp.json` for removals

### Issue: MCP Servers Not Loading After Configuration Changes

**Symptoms:** Servers configured in `.mcp.json` but not appearing in `claude mcp list`.

**Root Cause:** Broken Stow symlink - `.mcp.json` is a regular file instead of symlink.

**Detection:**
```bash
ls -la ~/.claude/.mcp.json

# Bad (regular file):  -rw-r--r-- ... .mcp.json
# Good (symlink):      lrwxr-xr-x ... .mcp.json -> ../dotfiles/...
```

**Solution:**
```bash
# 1. Verify dotfiles source has correct config
jq -r '.mcpServers | keys[]' ~/dotfiles/claude/.claude/.mcp.json

# 2. Remove broken regular file
rm ~/.claude/.mcp.json

# 3. Re-stow to recreate symlink
cd ~/dotfiles && stow -R claude

# 4. Verify symlink
ls -la ~/.claude/.mcp.json  # Should be symlink now

# 5. Restart Claude Code
```

### Issue: MCP Server Not Loading

**Symptoms:** Server defined in `.mcp.json` but not available in Claude Code.

**Solutions:**
1. Check if symlink is broken: `ls -la ~/.claude/.mcp.json`
2. Check JSON syntax: `jq . ~/.claude/.mcp.json`
3. Verify command exists: `which npx` or `which uvx`
4. Test command manually: `npx -y package-name --help`
5. Check Claude Code logs: `~/.claude/logs/`
6. Restart Claude Code completely

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
