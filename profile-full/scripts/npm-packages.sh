#!/usr/bin/env bash
# Full npm packages for complete development setup

GLOBAL_PACKAGES=(
    "@anthropic-ai/claude-cli"
    "ccstatusline"  # Claude Code status lines
    "npm-check-updates"
    "nodemon"
    "http-server"
    "typescript"
    "ts-node"
    "@vue/cli"
    "create-react-app"
    "vite"
    "pm2"
    "serve"
    "prettier"
    "eslint"
    "jest"
    "mocha"
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