---
description: Quick MCP server status check
---

# MCP Server Status

Check the status of configured MCP servers in OpenCode.

## Task

1. Read the global OpenCode configuration at ~/.config/opencode/opencode.json
2. Read the project-local configuration at .opencode/opencode.json if it exists
3. List all configured MCP servers with their:
   - Name
   - Type (local/remote)
   - Enabled status
   - Command (for local) or URL (for remote)

Use jq to parse the JSON files efficiently:

```bash
echo "=== Global MCP Servers ==="
cat ~/.config/opencode/opencode.json | jq -r '.mcp | to_entries[] | "\(.key): type=\(.value.type), enabled=\(.value.enabled)"'

echo ""
echo "=== Project MCP Servers ==="
if [[ -f .opencode/opencode.json ]]; then
    cat .opencode/opencode.json | jq -r '.mcp | to_entries[] | "\(.key): type=\(.value.type), enabled=\(.value.enabled)"'
else
    echo "No project-local configuration found"
fi

echo ""
echo "=== MCP Tools Configuration ==="
cat ~/.config/opencode/opencode.json | jq -r '.tools | to_entries[] | select(.key | startswith("mcp__")) | "\(.key): \(.value)"'
```

Provide a summary of:
- Total MCP servers configured
- How many are enabled vs disabled
- How many are local vs remote