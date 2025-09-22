#!/bin/bash

# Transform Claude .mcp.json to OpenCode mcp configuration format
# This merges MCP servers into the existing opencode.json

set -euo pipefail

CLAUDE_MCP="$1"
OPENCODE_JSON="$2"

if [[ ! -f "$CLAUDE_MCP" ]]; then
    echo "No Claude .mcp.json found at $CLAUDE_MCP"
    exit 0
fi

if [[ ! -f "$OPENCODE_JSON" ]]; then
    echo "OpenCode config not found at $OPENCODE_JSON"
    exit 1
fi

# Create a temporary file for the transformed MCP config
TEMP_MCP=$(mktemp)

# Transform Claude MCP format to OpenCode format using jq
# Note: OpenCode doesn't support description field in MCP config
# Handle different server types: stdio/local -> local, http -> remote
jq '
.mcpServers | to_entries | map({
    key: .key,
    value: (
        if .value.type == "http" then
            {
                type: "remote",
                url: .value.url,
                enabled: true
            } + (if .value.headers then {headers: .value.headers} else {} end)
        else
            {
                command: (
                    if .value.args then
                        ([.value.command] + .value.args)
                    else
                        [.value.command]
                    end
                ),
                type: "local",
                enabled: true
            } + (if .value.env then {environment: .value.env} else {} end)
        end
    )
}) | from_entries
' "$CLAUDE_MCP" > "$TEMP_MCP"

# Replace the MCP config in opencode.json (handles deletions)
jq --slurpfile mcp "$TEMP_MCP" '
.mcp = ($mcp[0] // {})
' "$OPENCODE_JSON" > "${OPENCODE_JSON}.tmp"

# Update tools section to enable MCP tools (replace existing MCP tools)
jq '
if .mcp then
    # Get existing non-MCP tools (remove old MCP tools)
    (.tools // {} | to_entries | map(select(.key | startswith("mcp__") | not)) | from_entries) as $non_mcp_tools |
    # Create new MCP tool entries
    (.mcp | keys | map({
        key: ("mcp__" + gsub("-"; "_") + "__*"),
        value: true
    }) | from_entries) as $new_mcp_tools |
    # Replace tools with non-MCP tools + new MCP tools
    .tools = $non_mcp_tools + $new_mcp_tools
else . end
' "${OPENCODE_JSON}.tmp" > "${OPENCODE_JSON}.new"

# Replace the original file
mv "${OPENCODE_JSON}.new" "$OPENCODE_JSON"
rm -f "${OPENCODE_JSON}.tmp" "$TEMP_MCP"

echo "✓ Merged MCP servers from Claude to OpenCode"