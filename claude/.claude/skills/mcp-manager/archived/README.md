# MCP Server Archive

This directory contains archived MCP server configurations that have been removed from active use but preserved for future restoration.

## Purpose

- **Preserve configs** when servers are temporarily disabled
- **Reduce context usage** by removing unused servers
- **Easy restoration** when servers are needed again
- **Historical record** of past configurations

## Archive Format

Each archived server is stored as a JSON file with metadata:

```json
{
  "archived_date": "2025-10-22T03:09:48Z",
  "reason": "Why this server was archived",
  "original_location": "Where it was removed from",
  "restore_instructions": "How to restore it",
  "config": {
    // Original MCP server configuration
  }
}
```

## Restoring an Archived Server

### Option 1: Manual Restoration

```bash
# Extract config from archive
jq '.config' archived/chrome-devtools.json

# Add to ~/.mcp.json or project .mcp.json
jq '.mcpServers["chrome-devtools"] = input.config' \
  ~/.mcp.json archived/chrome-devtools.json > /tmp/mcp.json
mv /tmp/mcp.json ~/.mcp.json

# Restart Claude Code
```

### Option 2: Using claude mcp add

```bash
# Extract and format for manual addition
jq '.config' archived/chrome-devtools.json
# Copy the output and use: claude mcp add chrome-devtools
```

## Archival Workflow

When archiving an MCP server:

1. **Extract current config**
   ```bash
   jq '.mcpServers["server-name"]' ~/.mcp.json
   ```

2. **Create archive file with metadata**
   ```bash
   cat > archived/server-name.json <<EOF
   {
     "archived_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
     "reason": "Reason for archiving",
     "original_location": "~/.mcp.json or project path",
     "restore_instructions": "How to restore",
     "config": <paste config here>
   }
   EOF
   ```

3. **Remove from active config**
   ```bash
   claude mcp remove server-name
   ```

4. **Commit archive**
   ```bash
   cd ~/dotfiles
   git add claude/.claude/skills/mcp-manager/archived/
   git commit -m "chore(mcp): archive server-name"
   ```

## Current Archives

- **chrome-devtools.json** - Chrome automation server (27 tools, 17.5k tokens)
  - Archived: 2025-10-22
  - Reason: High context usage, not actively used
  - Can restore when Chrome automation is needed

## Context Savings

Archiving unused MCP servers can significantly reduce context usage:

- **chrome-devtools**: ~17.5k tokens (27 tools)
- **Future archives**: Add context savings here

## Best Practices

1. **Archive, don't delete** - Preserve configs for future use
2. **Document reasons** - Record why servers were archived
3. **Include metadata** - Date, reason, restore instructions
4. **Version control** - Commit archives to dotfiles repo
5. **Review periodically** - Clean up old archives if truly no longer needed
