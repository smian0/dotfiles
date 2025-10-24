# Workflow: Sync User-Level MCP Servers

**Purpose**: Sync MCP server definitions from `~/.claude/.mcp.json` manifest to user-level registration

**Pattern**: After modifying `~/.claude/.mcp.json`, or when servers aren't loading

## Trigger Conditions

✅ This workflow activates when:
- User modifies `~/.claude/.mcp.json` manifest file
- User asks to sync MCP servers
- Servers defined in manifest aren't loading
- After pulling dotfiles changes with new server definitions

## Execution Steps

**Step 1: Dry-run to preview changes**

```bash
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh --dry-run
```

Expected output shows:
- Servers that will be added
- Servers already registered (skipped)
- Servers to be removed (if any)

**Step 2: Review dry-run output**

Check for:
- ✅ New servers to add
- ✅ Existing servers (no changes needed)
- ⚠️ Unexpected removals (investigate before proceeding)

**Step 3: Execute sync**

```bash
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
```

**Step 4: Verify registration**

```bash
claude mcp list
```

Expected: All servers from `~/.claude/.mcp.json` appear in the list with connection status.

**Step 5: Restart Claude Code (if needed)**

If new servers don't appear:
1. Restart Claude Code completely (not just reload)
2. Check `claude mcp list` again
3. Review logs: `~/.claude/logs/mcp-*.log`

## What This Script Does

**Internally:**
- Reads servers from `~/.claude/.mcp.json` manifest
- Registers each server at user level via `claude mcp add --scope user`
- Skips servers already registered
- Handles stdio, HTTP, and SSE transports
- Handles environment variables and headers
- Shows final server list with connection status

**This is the PRIMARY way to manage user-level MCP servers.**

## When to Use This Workflow

**Common scenarios:**

1. **After editing manifest:**
   ```bash
   vim ~/.claude/.mcp.json
   # Add new server definition
   ~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
   ```

2. **After pulling dotfiles:**
   ```bash
   cd ~/dotfiles && git pull
   stow -R claude
   ~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
   ```

3. **Servers not loading:**
   ```bash
   # Check what's configured
   jq -r '.mcpServers | keys[]' ~/.claude/.mcp.json

   # Check what's actually registered
   claude mcp list

   # Sync to fix mismatch
   ~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
   ```

## Integration with Main Skill

**Shared protocols (see main skill):**
- File locations (where `.mcp.json` lives)
- Stow symlink management
- Dotfiles integration
- Best practices for server configuration

**After syncing:**
- See main skill for validation: `validate-mcp-config.sh`
- See main skill for troubleshooting common issues
- See main skill for committing to dotfiles

## Error Handling

**Script fails with "command not found":**
- Ensure `claude` CLI is in PATH: `which claude`
- Install Claude CLI if missing
- Check script has execute permissions

**Servers still not loading after sync:**
- Verify JSON syntax: `jq . ~/.claude/.mcp.json`
- Check symlink not broken: `ls -la ~/.claude/.mcp.json`
- Restart Claude Code completely
- Review main skill troubleshooting section

**Sync script shows unexpected removals:**
- Don't proceed - investigate why servers are being removed
- Check if manifest was accidentally edited
- Review git diff: `cd ~/dotfiles && git diff claude/.claude/.mcp.json`

## Example

```bash
# 1. Add new server to manifest
jq '.mcpServers["new-tool"] = {
  "command": "npx",
  "args": ["-y", "some-mcp-package"],
  "type": "stdio"
}' ~/.claude/.mcp.json | sponge ~/.claude/.mcp.json

# 2. Preview changes
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh --dry-run

# 3. Apply sync
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh

# 4. Verify
claude mcp list | grep new-tool

# 5. Commit to dotfiles
cd ~/dotfiles
git add claude/.claude/.mcp.json
git commit -m "feat: add new-tool MCP server"
```
