# Workflow: Wrap MCP Server with Reloaderoo (Hot-Reload)

**Purpose**: Enable automatic server restart on file changes without restarting Claude Code

**Pattern**: User is developing an MCP server and wants faster iteration

## Trigger Conditions

✅ This workflow activates when:
- User is actively developing an MCP server
- User wants to avoid restarting Claude Code for every change
- Server code changes frequently during development
- Testing MCP server functionality iteratively

## What is Reloaderoo

Reloaderoo is a proxy that watches your MCP server files and automatically restarts the server when changes are detected.

**Benefits:**
- ✅ No Claude Code restart needed after server code changes
- ✅ Faster development iteration (10x faster)
- ✅ Preserves Claude Code session state
- ✅ Automatic change detection
- ✅ Environment variables preserved across reloads

## Execution Steps

**Step 1: Install reloaderoo (if needed)**

```bash
# Test if installed
npx reloaderoo --version

# If not installed, npx will auto-download on first use
```

**Step 2: Identify current server configuration**

**Before modification:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python3",
      "args": ["server.py"],
      "type": "stdio"
    }
  }
}
```

**Step 3: Wrap command with reloaderoo**

**After modification:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["reloaderoo", "proxy", "--", "python3", "server.py"],
      "type": "stdio",
      "env": {
        "MCPDEV_PROXY_AUTO_RESTART": "true"
      }
    }
  }
}
```

**Pattern breakdown:**
- `"command": "npx"` - Use npx to run reloaderoo
- `"reloaderoo", "proxy", "--"` - Reloaderoo proxy mode with separator
- `"python3", "server.py"` - Original command follows `--`
- `"MCPDEV_PROXY_AUTO_RESTART": "true"` - Enable auto-restart (string, not boolean)

**Step 4: Apply configuration changes**

**If using sync script (user-level):**
```bash
~/.claude/skills/mcp-manager/scripts/sync-user-mcp.sh
```

**Or use Claude CLI:**
```bash
claude mcp remove my-server
claude mcp add --scope user my-server npx reloaderoo proxy -- python3 server.py
```

**Step 5: Restart Claude Code (one-time only)**

Restart Claude Code completely to load the new wrapped server.

**Step 6: Verify hot-reload works**

1. Make a change to your server code (e.g., `server.py`)
2. Save the file
3. Check Claude Code MCP server list: `claude mcp list`
4. Server should show as "connected" (no Claude Code restart needed)
5. Test the server functionality with the changes applied

**Step 7: Watch server logs (optional)**

Monitor reload activity:

```bash
# Find the reloaderoo process
ps aux | grep reloaderoo

# Check Claude Code MCP logs
tail -f ~/.claude/logs/mcp-*.log
```

You should see "Reloading..." messages when files change.

## Patterns for Different Server Types

### Node.js Server

```json
{
  "command": "npx",
  "args": ["reloaderoo", "proxy", "--", "node", "server.js"],
  "env": {
    "MCPDEV_PROXY_AUTO_RESTART": "true"
  }
}
```

### Python with uvx

```json
{
  "command": "npx",
  "args": ["reloaderoo", "proxy", "--", "uvx", "my-mcp-server"],
  "env": {
    "MCPDEV_PROXY_AUTO_RESTART": "true"
  }
}
```

### NPX Package

```json
{
  "command": "npx",
  "args": ["reloaderoo", "proxy", "--", "npx", "-y", "some-mcp-package"],
  "env": {
    "MCPDEV_PROXY_AUTO_RESTART": "true"
  }
}
```

## Advanced Reloaderoo Options

### Watch Specific Files Only

```json
{
  "args": [
    "reloaderoo",
    "proxy",
    "--watch", "server.py",
    "--watch", "handlers/*.py",
    "--",
    "python3", "server.py"
  ]
}
```

### Ignore Patterns

```json
{
  "args": [
    "reloaderoo",
    "proxy",
    "--ignore", "*.log",
    "--ignore", "__pycache__",
    "--ignore", "node_modules",
    "--",
    "python3", "server.py"
  ]
}
```

### Watch Specific Directory

```json
{
  "args": [
    "reloaderoo",
    "proxy",
    "--watch", "/Users/me/projects/my-mcp/*.py",
    "--",
    "python3", "/Users/me/projects/my-mcp/server.py"
  ]
}
```

## Complete Example

**Original server configuration:**
```json
{
  "mcpServers": {
    "custom-api": {
      "command": "python3",
      "args": ["/Users/me/projects/my-mcp/server.py"],
      "type": "stdio",
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**Wrapped with reloaderoo:**
```json
{
  "mcpServers": {
    "custom-api": {
      "command": "npx",
      "args": [
        "reloaderoo",
        "proxy",
        "--watch", "/Users/me/projects/my-mcp/*.py",
        "--",
        "python3",
        "/Users/me/projects/my-mcp/server.py"
      ],
      "type": "stdio",
      "env": {
        "API_KEY": "${API_KEY}",
        "MCPDEV_PROXY_AUTO_RESTART": "true"
      }
    }
  }
}
```

**Result:**
- Server code changes auto-reload
- No Claude Code restart needed
- API_KEY preserved across reloads
- Development iteration 10x faster

## Troubleshooting

### Server Not Auto-Restarting

**Checklist:**
1. ✅ Check `MCPDEV_PROXY_AUTO_RESTART` is `"true"` (string, not boolean)
2. ✅ Verify reloaderoo in args: `["reloaderoo", "proxy", "--", ...]`
3. ✅ Check file is being watched (not in ignore patterns)
4. ✅ Ensure file changes are being saved (not just in editor buffer)

**Debug:**
```bash
# Test reloaderoo manually outside Claude Code
npx reloaderoo proxy -- python3 server.py
# Make a change to server.py
# Should see "Reloading..." in output
```

### Server Crashes on Restart

**Causes:**
- Syntax errors in your changes
- Import errors
- Missing dependencies
- Runtime exceptions

**Solutions:**
1. Test server manually: `python3 server.py`
2. Check syntax errors in your changes
3. Review MCP logs: `~/.claude/logs/mcp-*.log`
4. Fix errors and save again (auto-reload will retry)

### Reloaderoo Not Installed

**Symptoms:** `command not found: reloaderoo`

**Solutions:**
```bash
# Install globally (optional)
npm install -g reloaderoo

# Or let npx handle it automatically (recommended)
npx reloaderoo --version
```

### Changes Not Being Detected

**Possible causes:**
- File in ignored pattern
- Watching wrong directory
- File saved to different location

**Debug:**
```bash
# Check what reloaderoo is watching
ps aux | grep reloaderoo
# Shows command line with --watch patterns

# Test file watcher
npx reloaderoo proxy --watch "server.py" -- python3 server.py
# Make change and verify "Reloading..." appears
```

### Environment Variables Not Preserved

**Issue:** Environment variables reset after reload

**Solution:** Ensure env vars are in server configuration, not shell:

```json
{
  "env": {
    "API_KEY": "${API_KEY}",
    "DEBUG": "true",
    "MCPDEV_PROXY_AUTO_RESTART": "true"
  }
}
```

## Integration with Main Skill

**Related workflows:**
- Add Server: How to initially configure the server
- Sync User: How to apply configuration changes
- Validate: How to verify configuration is correct

**Related best practices (see main skill):**
- Best Practice #6: Using Reloaderoo for Development Servers
- Troubleshooting: "Auto-Restart Not Working"

**Related concepts (see main skill):**
- Configuration Files: Understanding `.mcp.json` structure
- Environment Variables: How to use ${VAR} syntax

## Checklist

**Setup:**
- [ ] reloaderoo installed or accessible via npx
- [ ] Server configuration backed up
- [ ] Know which files to watch

**Configuration:**
- [ ] Command wrapped: `npx reloaderoo proxy -- <original-command>`
- [ ] Auto-restart enabled: `MCPDEV_PROXY_AUTO_RESTART: "true"`
- [ ] Watch patterns configured (if needed)
- [ ] Ignore patterns configured (if needed)
- [ ] Environment variables preserved

**Verification:**
- [ ] Configuration validated
- [ ] Claude Code restarted (one-time)
- [ ] Server shows as connected
- [ ] File change triggers reload
- [ ] Functionality works after reload
- [ ] No crashes or errors in logs

**Optional:**
- [ ] Monitor logs to see reload activity
- [ ] Test with various file changes
- [ ] Optimize watch/ignore patterns

## When to Remove Reloaderoo

**Production:** Remove reloaderoo wrapper before deploying to production or committing final configuration.

**Revert to original:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python3",
      "args": ["server.py"],
      "type": "stdio"
    }
  }
}
```

**When development is done:**
- Remove reloaderoo wrapper
- Remove `MCPDEV_PROXY_AUTO_RESTART` from env
- Sync/commit final configuration
- Restart Claude Code with production config
