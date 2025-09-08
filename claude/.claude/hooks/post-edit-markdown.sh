#!/bin/bash

# Post-Edit Markdown Linting Hook (Dotfiles Version)
# Automatically detects markdown file modifications and invokes marksman linting
# Usage: Called automatically by Claude Code after file operations

set -euo pipefail

# Configuration - Auto-detect marksman server location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_CLAUDE_DIR="$(dirname "$SCRIPT_DIR")"

# Try multiple locations for marksman server
MARKSMAN_LOCATIONS=(
    "$DOTFILES_CLAUDE_DIR/mcp_servers/marksman_mcp_server.py"
    "$(dirname "$DOTFILES_CLAUDE_DIR")/bin/marksman_mcp_server.py" 
    "$HOME/.local/bin/marksman_mcp_server.py"
    "./mcp_servers/marksman_mcp_server.py"
)

MARKSMAN_SERVER=""
for location in "${MARKSMAN_LOCATIONS[@]}"; do
    if [[ -f "$location" ]]; then
        MARKSMAN_SERVER="$location"
        break
    fi
done

LOG_FILE="/tmp/markdown-lint-hook.log"
MAX_LOG_SIZE=1048576  # 1MB

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log messages
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$LOG_FILE"
    
    # Rotate log if too large
    if [[ -f "$LOG_FILE" ]] && [[ $(wc -c < "$LOG_FILE") -gt $MAX_LOG_SIZE ]]; then
        tail -n 500 "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
}

# Function to check if file is markdown
is_markdown_file() {
    local file="$1"
    [[ "$file" =~ \.(md|mdx|markdown)$ ]]
}

# Function to call marksman linting via MCP
lint_with_marksman() {
    local file_path="$1"
    
    if [[ -z "$MARKSMAN_SERVER" ]] || [[ ! -f "$MARKSMAN_SERVER" ]]; then
        log_message "ERROR: Marksman server not found. Searched locations:"
        for location in "${MARKSMAN_LOCATIONS[@]}"; do
            log_message "  - $location"
        done
        return 1
    fi
    
    # Note: This is a simplified version. In practice, you would need to:
    # 1. Start the MCP server
    # 2. Send JSON-RPC requests to call lint_document
    # 3. Parse the response
    # For now, we'll just log that linting should occur
    
    log_message "INFO: Markdown file modified: $file_path"
    log_message "INFO: Using marksman server at: $MARKSMAN_SERVER"
    log_message "INFO: Linting recommended - Claude should run lint_document('$file_path')"
    
    # Create a system reminder for Claude
    cat << EOF
<system-reminder>
Markdown file was modified: $file_path
Post-edit linting required. Please run:
1. lint_document('$file_path') to analyze issues
2. Review categorized issues (auto-fixable vs review-required)  
3. Apply auto_fix_document() for deterministic fixes
4. Address review-required issues based on context
</system-reminder>
EOF
    
    return 0
}

# Function to detect recently modified markdown files
check_recent_modifications() {
    local project_root="$1"
    local minutes_ago="${2:-5}"  # Default to 5 minutes
    
    # Find markdown files modified in the last N minutes
    local modified_files
    modified_files=$(find "$project_root" -name "*.md" -o -name "*.mdx" -o -name "*.markdown" -type f -mmin -"$minutes_ago" 2>/dev/null || true)
    
    if [[ -n "$modified_files" ]]; then
        echo -e "${BLUE}🔍 Recently modified markdown files detected:${NC}"
        while IFS= read -r file; do
            if [[ -n "$file" ]]; then
                echo -e "${YELLOW}  → $(basename "$file")${NC}"
                lint_with_marksman "$file"
            fi
        done <<< "$modified_files"
        return 0
    else
        log_message "INFO: No recently modified markdown files found"
        return 1
    fi
}

# Function to watch for file modifications (if fswatch is available)
watch_modifications() {
    local project_root="$1"
    
    if command -v fswatch &> /dev/null; then
        echo -e "${GREEN}📁 Watching for markdown file modifications...${NC}"
        log_message "INFO: Starting file modification watch"
        
        fswatch -r --event=Updated --include='.*\.(md|mdx|markdown)$' "$project_root" | while read file; do
            if is_markdown_file "$file"; then
                echo -e "${YELLOW}📝 Modified:${NC} $(basename "$file")"
                lint_with_marksman "$file"
            fi
        done
    else
        echo -e "${RED}⚠️  fswatch not available. Install with: brew install fswatch${NC}"
        return 1
    fi
}

# Main execution
main() {
    local project_root="${1:-$(pwd)}"
    local mode="${2:-check}"
    
    echo -e "${BLUE}🔧 Markdown Linting Hook (Dotfiles)${NC}"
    log_message "INFO: Hook execution started - mode: $mode, project: $project_root"
    log_message "INFO: Marksman server location: $MARKSMAN_SERVER"
    
    case "$mode" in
        "check")
            echo -e "${GREEN}Checking for recent modifications...${NC}"
            check_recent_modifications "$project_root" 5
            ;;
        "watch")
            echo -e "${GREEN}Starting file modification watcher...${NC}"
            watch_modifications "$project_root"
            ;;
        "lint")
            if [[ -n "${3:-}" ]] && [[ -f "$3" ]] && is_markdown_file "$3"; then
                echo -e "${GREEN}Linting specific file:${NC} $3"
                lint_with_marksman "$3"
            else
                echo -e "${RED}Error: Please provide a valid markdown file path${NC}"
                exit 1
            fi
            ;;
        *)
            cat << EOF
${GREEN}Usage:${NC}
  $0 [project_root] [mode] [file]
  
${GREEN}Modes:${NC}
  check  - Check for recently modified markdown files (default)
  watch  - Watch for file modifications in real-time
  lint   - Lint a specific markdown file
  
${GREEN}Examples:${NC}
  $0                           # Check current directory
  $0 /path/to/project check    # Check specific project
  $0 . watch                   # Watch current directory
  $0 . lint README.md          # Lint specific file

${GREEN}Dotfiles Integration:${NC}
  Automatically detects marksman server location from dotfiles structure
  Searches multiple common installation paths for maximum compatibility
EOF
            ;;
    esac
    
    log_message "INFO: Hook execution completed"
}

# Ensure log file exists
touch "$LOG_FILE"

# Run main function with all arguments
main "$@"