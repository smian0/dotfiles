#!/usr/bin/env bash
# sync-user-mcp.sh - Sync ~/.claude/.mcp.json to user-level MCP registration
#
# This script ensures that all MCP servers defined in ~/.claude/.mcp.json
# are registered at the user level using `claude mcp add --scope user`.
#
# Usage:
#   ./sync-user-mcp.sh [--dry-run]
#
# Options:
#   --dry-run    Show what would be done without making changes

set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo ""
fi

MCP_JSON="$HOME/.claude/.mcp.json"

if [[ ! -f "$MCP_JSON" ]]; then
    echo "❌ Error: $MCP_JSON not found"
    exit 1
fi

echo "📋 Reading MCP servers from: $MCP_JSON"
echo ""

# Get list of servers from ~/.claude/.mcp.json
SERVERS=$(jq -r '.mcpServers | keys[]' "$MCP_JSON")

if [[ -z "$SERVERS" ]]; then
    echo "✅ No servers defined in $MCP_JSON"
    exit 0
fi

# Get currently registered user-level servers
REGISTERED=$(claude mcp list 2>/dev/null | grep -E "^\S+:" | cut -d: -f1 || true)

echo "Servers in $MCP_JSON:"
echo "$SERVERS" | sed 's/^/  - /'
echo ""

for SERVER in $SERVERS; do
    echo "🔧 Processing: $SERVER"

    # Check if already registered
    if echo "$REGISTERED" | grep -q "^${SERVER}$"; then
        echo "   ✅ Already registered at user level"
        echo ""
        continue
    fi

    # Get server config
    TYPE=$(jq -r ".mcpServers[\"$SERVER\"].type // \"stdio\"" "$MCP_JSON")
    COMMAND=$(jq -r ".mcpServers[\"$SERVER\"].command // empty" "$MCP_JSON")
    ARGS=$(jq -r ".mcpServers[\"$SERVER\"].args // [] | join(\" \")" "$MCP_JSON")

    # Build claude mcp add command
    if [[ "$TYPE" == "http" ]]; then
        URL=$(jq -r ".mcpServers[\"$SERVER\"].url" "$MCP_JSON")
        HEADERS=$(jq -r ".mcpServers[\"$SERVER\"].headers // {} | to_entries[] | \"-H \\\"\" + .key + \": \" + .value + \"\\\"\"" "$MCP_JSON" | tr '\n' ' ')

        CMD="claude mcp add --scope user --transport http $SERVER $URL"
        if [[ -n "$HEADERS" ]]; then
            CMD="$CMD $HEADERS"
        fi
    else
        # stdio transport
        ENV_VARS=$(jq -r ".mcpServers[\"$SERVER\"].env // {} | to_entries[] | \"--env \" + .key + \"=\" + .value" "$MCP_JSON" | tr '\n' ' ')

        if [[ -z "$COMMAND" ]]; then
            echo "   ⚠️  No command specified, skipping"
            echo ""
            continue
        fi

        CMD="claude mcp add --scope user --transport stdio $SERVER"
        if [[ -n "$ENV_VARS" ]]; then
            CMD="$CMD $ENV_VARS"
        fi
        CMD="$CMD -- $COMMAND $ARGS"
    fi

    echo "   Command: $CMD"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "   [DRY RUN] Would execute above command"
    else
        if eval "$CMD"; then
            echo "   ✅ Registered successfully"
        else
            echo "   ❌ Failed to register"
        fi
    fi
    echo ""
done

if [[ "$DRY_RUN" == "true" ]]; then
    echo "🔍 DRY RUN COMPLETE - No changes were made"
    echo "   Run without --dry-run to apply changes"
else
    echo "✅ Sync complete!"
    echo ""
    echo "Active MCP servers:"
    claude mcp list
fi
