#!/bin/bash
# ⚠️  DEPRECATED: Use zsh/mcp-config.zsh functions instead (mcpg, mcpls, etc.)
# Simple wrapper for extract-mcp-config.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACT_SCRIPT="$SCRIPT_DIR/extract-mcp-config.py"

# Default values
OUTPUT_FILE=".cursor/mcp.json"
GLOBAL_ONLY=false
DRY_RUN=false
PRETTY=true

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Extract MCP server configurations from Claude Code config to mcp.json

Options:
    -o, --output FILE       Output file (default: .cursor/mcp.json)
    -g, --global-only       Extract only global MCP servers
    -p, --project NAME      Extract from specific project
    -l, --list              List available servers only
    -d, --dry-run           Show output without writing file
    -n, --no-pretty         Don't pretty-print JSON
    -h, --help              Show this help

Examples:
    $(basename "$0")                    # Extract all servers to .cursor/mcp.json
    $(basename "$0") -g                 # Extract only global servers
    $(basename "$0") -l                 # List available servers
    $(basename "$0") -o my-mcp.json     # Custom output file
    $(basename "$0") -p vectorbt        # Extract from projects matching 'vectorbt'
    $(basename "$0") -d                 # Dry run to preview output

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -g|--global-only)
            GLOBAL_ONLY=true
            shift
            ;;
        -p|--project)
            PROJECT="$2"
            shift 2
            ;;
        -l|--list)
            python3 "$EXTRACT_SCRIPT" --list-only
            exit 0
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -n|--no-pretty)
            PRETTY=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 '$EXTRACT_SCRIPT' --output '$OUTPUT_FILE'"

if [[ "$GLOBAL_ONLY" == "true" ]]; then
    CMD="$CMD --global-only"
fi

if [[ -n "$PROJECT" ]]; then
    CMD="$CMD --project '$PROJECT'"
fi

if [[ "$DRY_RUN" == "true" ]]; then
    CMD="$CMD --dry-run"
fi

if [[ "$PRETTY" == "true" ]]; then
    CMD="$CMD --pretty"
fi

# Execute command
echo "Extracting MCP configuration..."
eval "$CMD"
