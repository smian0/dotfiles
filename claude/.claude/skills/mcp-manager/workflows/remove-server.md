# Workflow: Remove MCP Server

**Purpose**: Safely remove an MCP server from user or project configuration

**Pattern**: User wants to uninstall/remove an existing MCP server

## Trigger Conditions

✅ This workflow activates when:
- User asks to remove/uninstall an MCP server
- Server is no longer needed
- Server is causing conflicts or issues
- Cleaning up unused servers

## ⚠️ RECOMMENDED METHOD: Use Claude CLI

**This is the BEST way to remove a server:**

```bash
claude mcp remove <server-name>
```

**Why Claude CLI is preferred:**
- ✅ Removes from `.mcp.json` configuration files
- ✅ Cleans up cached config in `~/.claude.json` state file
- ✅ Kills any running server processes
- ✅ Prevents "still connected" ghost servers
- ✅ Handles all cleanup automatically

## Execution Steps (Claude CLI Method)

**Step 1: List current servers**

```bash
claude mcp list
```

Identify the server name to remove.

**Step 2: Remove server using CLI**

```bash
claude mcp remove <server-name>
```

Expected output: Confirmation that server was removed.

**Step 3: Verify removal**

```bash
claude mcp list | grep <server-name>
```

Expected: Server no longer appears in list.

**Step 4: Check for orphaned processes**

```bash
ps aux | grep -i "<server-name>"
```

If any processes remain:
```bash
pkill -f "<server-name>"
```

**Step 5: Remove permissions from settings.json**

Edit `settings.json`:
```bash
vim ~/.claude/settings.json  # or project settings.json
```

Remove lines like:
```json
"mcp__server-name__*",
"mcp__server-name__tool1",
"mcp__server-name__tool2"
```

**Step 6: Validate consistency**

```bash
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
```

Expected: No orphaned permissions.

**Step 7: Commit changes**

**User-level:**
```bash
cd ~/dotfiles
git add claude/.claude/.mcp.json claude/.claude/settings.json
git commit -m "chore: remove <server-name> MCP server"
```

**Project-level:**
```bash
git add .mcp.json .claude/settings.json
git commit -m "chore: remove <server-name> MCP server"
```

## Alternative: Manual Removal (Not Recommended)

**Only use if Claude CLI is unavailable or fails.**

**Step 1: Kill running processes**

```bash
pkill -f "server-name"
pkill -f "reloaderoo.*server-name"
```

**Step 2: Remove from `.mcp.json`**

```bash
jq 'del(.mcpServers["server-name"])' ~/.claude/.mcp.json > /tmp/mcp.json
mv /tmp/mcp.json ~/.claude/.mcp.json
```

**Step 3: Remove permissions from `settings.json`**

```bash
jq '.permissions.allow |= map(select(startswith("mcp__server-name__") | not))' ~/.claude/settings.json > /tmp/settings.json
mv /tmp/settings.json ~/.claude/settings.json
```

**Step 4: Clean up cache using Claude CLI**

Even with manual removal, use this to clean cache:
```bash
claude mcp remove server-name
```

**Step 5: Restart Claude Code**

Restart completely (not just reload).

**Critical:** Manual removal can leave orphaned processes and cache entries. Always use `claude mcp remove` when possible.

## Alternative: Using Remove Script

For guided removal:

```bash
~/.claude/skills/mcp-manager/scripts/remove-mcp-server.sh <server-name>
```

**Options:**
- `--keep-permissions`: Remove server but keep permissions (for testing)
- `--force`: Skip confirmation prompts

**Script automatically:**
- Creates backup before removal
- Shows what will be removed
- Confirms before making changes
- Validates final state

## Integration with Main Skill

**Before removing (see main skill):**
- Check dependencies: Other configs using this server
- Review what the server provides
- Identify all tools/permissions to remove

**After removing (see main skill):**
- Troubleshooting: "Server Still Shows as Connected"
- State File Caching: Why manual removal leaves ghosts
- Validation: Checking for orphaned permissions

## Error Handling

**Server not found:**
- Check spelling: `claude mcp list`
- Server may already be removed
- Check both user and project configs

**"Still connected" after removal:**
- See main skill troubleshooting: "Server Still Shows as Connected After Removal"
- Kill orphaned processes: `pkill -f "server-name"`
- Clean cache manually if needed

**Orphaned permissions remain:**
- Use consistency check: `./scripts/check-mcp-consistency.sh`
- Remove manually from `settings.json`
- Or use validation script with `--fix` flag

**Stow symlink broken after removal:**
- See main skill: "Working with Stow-Managed Configurations"
- Re-stow: `cd ~/dotfiles && stow -R claude`

## Example: Removing Old Server

```bash
# 1. Check current servers
claude mcp list

# 2. Remove server
claude mcp remove old-server
# Expected: Server removed successfully

# 3. Verify removal
claude mcp list | grep old-server
# Expected: (no output)

# 4. Check for orphaned processes
ps aux | grep old-server
# Kill if any remain
pkill -f "old-server"

# 5. Remove permissions
vim ~/.claude/settings.json
# Delete lines starting with "mcp__old-server__"

# 6. Validate
~/.claude/skills/mcp-manager/scripts/validate-mcp-config.sh
# Expected: ✅ Configuration valid

# 7. Commit
cd ~/dotfiles
git add claude/.claude/.mcp.json claude/.claude/settings.json
git commit -m "chore: remove old-server MCP (no longer needed)"
```

## Troubleshooting

**Server still appears after removal:**
1. Check cached state: `~/.claude.json` may have stale entry
2. Kill all processes: `pkill -f "server-name"`
3. Restart Claude Code completely
4. Last resort: Manual cache cleanup (see main skill troubleshooting)

**Permissions won't delete:**
- Ensure editing correct `settings.json` (user vs project)
- Check if Stow symlink is broken
- Verify JSON syntax after edit: `jq . settings.json`

**Can't find server to remove:**
- List all configured: `jq -r '.mcpServers | keys[]' ~/.claude/.mcp.json`
- List all active: `claude mcp list`
- Check project `.mcp.json` if not in user config

## Checklist

**Before removing:**
- [ ] Check dependencies (other configs using it)
- [ ] Create backup
- [ ] Identify all permissions to remove

**After removing:**
- [ ] Server no longer in `claude mcp list`
- [ ] No orphaned processes running
- [ ] No orphaned permissions in `settings.json`
- [ ] Configuration validated
- [ ] Claude Code restarted
- [ ] Changes committed to git
