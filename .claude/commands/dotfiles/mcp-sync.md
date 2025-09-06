# MCP Configuration Sync Automation Prompt

**Use this prompt whenever MCP server configurations need to be synced or modified in the dotfiles repository.**

---

## CONTEXT

You are working with a dotfiles repository that manages MCP (Model Context Protocol) server configurations. The user needs to sync MCP settings between Claude's global configuration and the dotfiles repository, potentially with modifications.

## YOUR TASK

When the user requests MCP configuration changes, follow this workflow:

### 1. ASSESS CURRENT STATE
```bash
# Check if configurations are in sync
scripts/mcp-check.sh

# List current MCP servers from Claude
python3 scripts/extract-mcp-config.py --list-only
```

### 2. EXTRACT & SYNC FROM CLAUDE
```bash
# Sync all MCP servers from ~/.claude.json to dotfiles
python3 scripts/extract-mcp-config.py --sync -o claude/.claude/.mcp.json --pretty --verbose
```

### 3. APPLY USER-REQUESTED MODIFICATIONS

Common modification patterns:

#### A. Disable Browser/GUI Opening
For servers that auto-open browsers or GUI windows, add appropriate flags:

**Serena**: Add `--enable-web-dashboard false --enable-gui-log-window false`
**Playwright**: Add `--headless` 
**Browser-based servers**: Add `--no-browser` or set `MCP_BROWSER_HEADLESS=true`

#### B. Environment Variables
Add or modify `env` sections for servers that need credentials:
```json
"env": {
  "API_KEY": "${API_KEY}",
  "SOME_CONFIG": "value"
}
```

#### C. Server Arguments
Modify `args` arrays to add/remove flags:
```json
"args": [
  "existing-arg",
  "--new-flag",
  "value"
]
```

#### D. Command Changes
Update `command` if the server execution method changes.

### 4. SYNC CHANGES BACK TO CLAUDE

After modifying the dotfiles `.mcp.json`, update Claude's configuration:

```bash
# For specific server modifications, use jq to update ~/.claude.json
# Example for adding flags to a server:
jq '.mcpServers.SERVERNAME.args += ["--new-flag", "value"]' ~/.claude.json > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json

# For environment variables:
jq '.mcpServers.SERVERNAME.env.NEW_VAR = "value"' ~/.claude.json > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json
```

### 5. VERIFY SYNCHRONIZATION
```bash
# Confirm configurations match
scripts/mcp-check.sh

# Verify specific server if needed
jq '.mcpServers.SERVERNAME' ~/.claude.json
jq '.mcpServers.SERVERNAME' claude/.claude/.mcp.json
```

## AVAILABLE TOOLS

### Scripts in `scripts/` directory:
- `extract-mcp-config.py` - Main extraction/sync tool
- `mcp-check.sh` - Check sync status
- `mcp-sync.sh` - Quick sync wrapper

### Zsh functions from `zsh/mcp-config.zsh`:
- `mcpls` - List MCP servers
- `mcpg` - Extract global servers
- `mcpp` - Extract project servers  
- `mcpa` - Extract all servers

### Key files:
- `~/.claude.json` - Claude's main configuration
- `claude/.claude/.mcp.json` - Dotfiles MCP configuration
- `.cursor/mcp.json` - May be symlinked from dotfiles

## COMMON SCENARIOS

### Scenario 1: "Extract MCP settings from Claude and update dotfiles"
1. Run extraction and sync
2. Verify sync status
3. Report what was synced

### Scenario 2: "Disable browser opening for MCP servers"
1. Extract and sync current config
2. Identify browser-opening servers (Serena, Playwright, etc.)
3. Add appropriate disable flags
4. Sync changes back to Claude
5. Verify sync

### Scenario 3: "Add new MCP server configuration"
1. Check current servers
2. Add new server config to dotfiles
3. Sync back to Claude
4. Verify addition

### Scenario 4: "Update existing server with new parameters"
1. Extract current config
2. Modify specific server in dotfiles
3. Sync changes back to Claude
4. Verify modification

## RESPONSE PATTERN

Always follow this pattern:

1. **Acknowledge** the user's request
2. **Check current state** with available tools
3. **Apply changes** step by step with clear explanations
4. **Verify results** and confirm sync status
5. **Summarize** what was accomplished

Use todo tracking to show progress through the steps.

## BROWSER DISABLE REFERENCE

| Server Type | Disable Method | Example |
|-------------|----------------|---------|
| Serena | `--enable-web-dashboard false --enable-gui-log-window false` | Web dashboard + GUI log window |
| Playwright | `--headless` | Browser automation |
| Browser-use | `MCP_BROWSER_HEADLESS=true` (env) | Environment variable |
| Puppeteer | `{"headless": true}` (config) | Configuration option |
| General | `--no-browser`, `--headless` | Common flags |

## ERROR HANDLING

If sync fails:
1. Check file permissions on `~/.claude.json`
2. Verify JSON syntax with `jq`
3. Use `--dry-run` to preview changes
4. Check available tools with `--help` flags

---

**Remember**: Always verify synchronization at the end and provide a clear summary of changes made.