#!/usr/bin/env bash
# Development npm packages for coding work

GLOBAL_PACKAGES=(
    "@anthropic-ai/claude-cli"
    "ccstatusline"  # Claude Code status lines
    "npm-check-updates"
    "nodemon"
    "http-server"
    "typescript"
    "ts-node"
)

# Source the main npm-packages script for functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRIPT="$(cd "$SCRIPT_DIR/../../scripts" && pwd)/npm-packages.sh"

if [[ -f "$MAIN_SCRIPT" ]]; then
    source "$MAIN_SCRIPT"
else
    echo "Error: Main npm-packages.sh not found"
    exit 1
fi