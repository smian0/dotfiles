#!/bin/bash

# Post-Edit Markdown Linting Hook - Simplified
# Automatically triggers linting for modified markdown files
# Assumes unified markdown MCP server is available

set -euo pipefail

# Function to create linting reminder
create_linting_reminder() {
    local file_path="$1"
    cat << EOF
<system-reminder>
📝 Markdown file modified: $file_path
🔧 Post-edit linting required. Run:
• mcp__marksman__lint_document('$file_path') - Analyze issues
• mcp__marksman__auto_fix_document('$file_path') - Apply automatic fixes
</system-reminder>
EOF
}

# Check if file is markdown and exists
if [[ "${1:-}" =~ \.(md|mdx|markdown)$ ]] && [[ -f "${1:-}" ]]; then
    create_linting_reminder "$1"
fi