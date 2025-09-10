#!/bin/bash
# Scripts Directory Reorganization Tool (Simple Version)
# Safely reorganizes scripts into logical subdirectories with backward compatibility

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Base directory
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=${1:-"--dry-run"}

echo -e "${BLUE}🗂️ Scripts Directory Reorganization${NC}"
echo "===================================="
echo "Directory: $SCRIPTS_DIR" 
echo "Mode: $DRY_RUN"
echo ""

# Create new directory structure
create_directories() {
    echo -e "${BLUE}📁 Creating new directory structure...${NC}"
    
    local dirs="security system claude claude/oauth mcp mcp/env utils"
    
    for dir in $dirs; do
        if [[ "$DRY_RUN" != "--execute" ]]; then
            echo "  Would create: $SCRIPTS_DIR/$dir"
        else
            mkdir -p "$SCRIPTS_DIR/$dir"
            echo -e "  ${GREEN}✓${NC} Created: $dir"
        fi
    done
    echo ""
}

# Move a single file with symlink
move_file() {
    local old_name="$1"
    local new_path="$2"
    local old_path="$SCRIPTS_DIR/$old_name"
    local new_full_path="$SCRIPTS_DIR/$new_path"
    
    if [[ -f "$old_path" ]]; then
        if [[ "$DRY_RUN" != "--execute" ]]; then
            echo "  Would move: $old_name → $new_path"
            echo "  Would create symlink: $old_name → $new_path"
        else
            mv "$old_path" "$new_full_path"
            ln -s "$new_path" "$old_path"
            echo -e "  ${GREEN}✓${NC} Moved: $old_name → $new_path"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} Not found: $old_name"
    fi
}

# Move a directory with symlink
move_directory() {
    local old_name="$1"
    local new_path="$2"
    local old_path="$SCRIPTS_DIR/$old_name"
    local new_full_path="$SCRIPTS_DIR/$new_path"
    
    if [[ -d "$old_path" ]]; then
        if [[ "$DRY_RUN" != "--execute" ]]; then
            echo "  Would move: $old_name/ → $new_path/"
            echo "  Would create symlink: $old_name → $new_path"
        else
            mv "$old_path" "$new_full_path"
            ln -s "$new_path" "$old_path"
            echo -e "  ${GREEN}✓${NC} Moved: $old_name/ → $new_path/"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} Not found: $old_name/"
    fi
}

# Migrate all files
migrate_files() {
    echo -e "${BLUE}📦 Migrating files...${NC}"
    
    # Security tools
    move_file "api-key-manager.sh" "security/api-key-manager.sh"
    move_file "env-debug.sh" "security/env-debug.sh" 
    move_file "gpg-manager.sh" "security/gpg-manager.sh"
    move_file "pass-manager.sh" "security/pass-manager.sh"
    
    # System tools
    move_file "backup-restore.sh" "system/backup-restore.sh"
    move_file "install-by-environment.sh" "system/install-by-environment.sh"
    move_file "npm-packages.sh" "system/npm-packages.sh"
    move_file "os-detect.sh" "system/os-detect.sh"
    move_file "profile-manager.sh" "system/profile-manager.sh"
    move_file "validate-config.sh" "system/validate-config.sh"
    
    # Claude tools
    move_file "deploy-claude-project.sh" "claude/deploy-project.sh"
    move_file "deploy-claude-user.sh" "claude/deploy-user.sh"
    move_file "fix-claude-ssh-auth.sh" "claude/fix-ssh-auth.sh"
    
    # MCP tools
    move_file "claude-mcp-extract.sh" "mcp/extract.sh"
    move_file "extract-mcp-config.py" "mcp/extract-config.py"
    move_file "mcp-check.sh" "mcp/check.sh"
    move_file "mcp-sync.sh" "mcp/sync.sh"
    move_file "sync-mcp-config.sh" "mcp/sync-config.sh"
    
    echo ""
}

# Migrate directories
migrate_directories() {
    echo -e "${BLUE}📁 Migrating directories...${NC}"
    
    move_directory "claude-oauth" "claude/oauth"
    move_directory "mcp-env" "mcp/env"
    
    echo ""
}

# Show summary
show_summary() {
    if [[ "$DRY_RUN" != "--execute" ]]; then
        echo -e "${YELLOW}🔍 This was a dry run. To execute the reorganization:${NC}"
        echo "  scripts/reorganize-scripts-simple.sh --execute"
        echo ""
        echo -e "${BLUE}📋 Proposed changes:${NC}"
        echo "• 4 new subdirectories (security, system, claude, mcp)"
        echo "• 15 files to be moved and symlinked"
        echo "• 2 directories to be moved and symlinked"
        echo "• All original paths preserved via symlinks"
    else
        echo -e "${GREEN}✅ Scripts directory reorganization complete!${NC}"
        echo ""
        echo "📋 Summary:"
        echo "• Created organized subdirectories"
        echo "• Moved files to logical locations"
        echo "• Created backward-compatible symlinks"
        echo ""
        echo "💡 All original paths still work via symlinks"
        echo "💡 Run 'ls -la scripts/' to see the new structure"
    fi
}

# Main execution
main() {
    if [[ "${1:-}" == "--help" ]]; then
        echo "Usage: $0 [--dry-run|--execute]"
        echo ""
        echo "Options:"
        echo "  --dry-run   Show what would be done (default)"
        echo "  --execute   Actually perform the reorganization"
        echo "  --help      Show this help message"
        exit 0
    fi
    
    create_directories
    migrate_files
    migrate_directories
    show_summary
}

# Run main function
main "$@"