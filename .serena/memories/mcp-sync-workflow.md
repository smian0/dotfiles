# MCP Configuration Sync Workflow

## Overview
Systematic workflow for syncing MCP (Model Context Protocol) server configurations between Claude's global configuration and the dotfiles repository.

## Key Files
- `~/.claude.json` - Claude's main configuration
- `/Users/smian/dotfiles/claude/.claude/.mcp.json` - Dotfiles MCP configuration  
- `/Users/smian/dotfiles/.mcp.json` - Repository root MCP config

## Essential Scripts
- `scripts/mcp-check.sh` - Check sync status between configurations
- `scripts/extract-mcp-config.py` - Extract and sync MCP configs
- `scripts/sync-mcp-config.sh` - Quick sync wrapper
- `python3 scripts/extract-mcp-config.py --list-only` - List current servers

## Standard Workflow

### 1. Assessment Phase
```bash
# Check current sync status
scripts/mcp-check.sh

# List servers in Claude config
python3 scripts/extract-mcp-config.py --list-only
```

### 2. Server Removal Process
When removing MCP servers:

**Method 1: Direct JSON editing with jq**
```bash
# Remove specific servers from Claude config
jq 'del(.mcpServers.memory, .mcpServers.time)' ~/.claude.json > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json
```

**Method 2: Manual editing**
- Edit dotfiles configuration first
- Then sync changes back to Claude

### 3. Browser Disable Modifications
Common servers that need browser/GUI disabling:

| Server | Disable Flags | Purpose |
|--------|---------------|---------|
| Serena | `--enable-web-dashboard false --enable-gui-log-window false` | Disable web UI |
| Playwright | `--headless` | Headless browser mode |
| Browser-use | `MCP_BROWSER_HEADLESS=true` (env var) | Environment control |

### 4. Verification
```bash
# Final sync check
scripts/mcp-check.sh

# List final server count
jq '.mcpServers | keys[]' ~/.claude.json
```

## Recent Changes (2025-09-08)
- Removed `memory` MCP server (mcp-knowledge-graph)
- Removed `time` MCP server (mcp-server-time)
- Maintained 5 core servers: context7, marksman, playwright, sequential-thinking, serena
- Verified Serena has proper browser disable flags

## Current Active Servers
1. **context7** - Official library documentation lookup
2. **marksman** - Markdown document analysis & linting
3. **playwright** - Browser automation & E2E testing  
4. **sequential-thinking** - Multi-step reasoning engine
5. **serena** - Semantic code analysis & project memory

## Best Practices
1. Always check sync status before making changes
2. Use TodoWrite to track multi-step operations
3. Remove servers from both Claude config and dotfiles
4. Verify final sync with `scripts/mcp-check.sh`
5. Document significant changes in this memory
6. Test browser disable flags to prevent unwanted UI popups

## Common Issues
- JSON syntax errors after manual editing (use `jq` validation)
- Permissions issues with `~/.claude.json` 
- Leftover trailing commas in JSON after removals
- Servers present in one config but not the other

## Usage Commands
```bash
# Quick status check
scripts/mcp-check.sh

# Sync from Claude to dotfiles
python3 scripts/extract-mcp-config.py --sync -o claude/.claude/.mcp.json --pretty --verbose

# Remove specific server
jq 'del(.mcpServers.SERVERNAME)' ~/.claude.json > ~/.claude.json.tmp && mv ~/.claude.json.tmp ~/.claude.json
```