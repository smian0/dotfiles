#!/bin/bash
# Manage Backward Compatibility Symlinks
# Options to check, clean up, or maintain the symlinks created during reorganization

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTION=${1:-"status"}

echo -e "${BLUE}📎 Backward Compatibility Symlinks Manager${NC}"
echo "============================================="
echo ""

# Check symlink status
check_symlinks() {
    echo -e "${BLUE}📊 Symlink Status Check${NC}"
    echo "========================"
    echo ""
    
    local total_symlinks=0
    local working_symlinks=0
    local broken_symlinks=0
    
    # Find all symlinks in scripts root
    while IFS= read -r -d '' symlink; do
        ((total_symlinks++))
        local target=$(readlink "$symlink")
        local basename_link=$(basename "$symlink")
        
        if [[ -e "$symlink" ]]; then
            ((working_symlinks++))
            echo -e "  ${GREEN}✓${NC} $basename_link → $target"
        else
            ((broken_symlinks++))
            echo -e "  ${RED}✗${NC} $basename_link → $target (BROKEN)"
        fi
    done < <(find "$SCRIPTS_DIR" -maxdepth 1 -type l -print0)
    
    echo ""
    echo "📊 Summary:"
    echo "  Total symlinks: $total_symlinks"
    echo "  Working: $working_symlinks"
    echo "  Broken: $broken_symlinks"
    echo ""
    
    if [[ $broken_symlinks -gt 0 ]]; then
        echo -e "${YELLOW}⚠️ Broken symlinks need attention${NC}"
    else
        echo -e "${GREEN}✅ All symlinks working correctly${NC}"
    fi
}

# Fix broken symlinks
fix_broken_symlinks() {
    echo -e "${BLUE}🔧 Fixing Broken Symlinks${NC}"
    echo "=========================="
    echo ""
    
    local fixed=0
    
    # Find broken symlinks
    while IFS= read -r -d '' symlink; do
        if [[ ! -e "$symlink" ]]; then
            local basename_link=$(basename "$symlink")
            local target=$(readlink "$symlink")
            
            echo -e "${RED}Found broken:${NC} $basename_link → $target"
            
            # Handle specific known cases
            case "$basename_link" in
                "claude-mcp-extract.sh")
                    echo "  This script was deprecated and archived"
                    echo "  Removing broken symlink..."
                    rm "$symlink"
                    echo -e "  ${GREEN}✓${NC} Removed deprecated symlink"
                    ((fixed++))
                    ;;
                *)
                    echo -e "  ${YELLOW}⚠${NC} Unknown broken symlink - manual intervention needed"
                    ;;
            esac
        fi
    done < <(find "$SCRIPTS_DIR" -maxdepth 1 -type l -print0)
    
    echo ""
    if [[ $fixed -gt 0 ]]; then
        echo -e "${GREEN}✅ Fixed $fixed broken symlink(s)${NC}"
    else
        echo -e "${GREEN}✅ No broken symlinks to fix${NC}"
    fi
}

# List references to symlinks (help plan cleanup)
check_references() {
    echo -e "${BLUE}🔍 Finding References to Symlinks${NC}"
    echo "==================================="
    echo ""
    
    echo "Checking common locations for symlink usage..."
    echo ""
    
    # Check Makefile
    if [[ -f "$SCRIPTS_DIR/../Makefile" ]]; then
        echo -e "${BLUE}📄 Makefile references:${NC}"
        grep -n "scripts/" "$SCRIPTS_DIR/../Makefile" | head -5 || echo "  No direct script references found"
        echo ""
    fi
    
    # Check documentation
    if [[ -f "$SCRIPTS_DIR/../README.md" ]]; then
        echo -e "${BLUE}📖 README.md references:${NC}"
        grep -n "scripts/" "$SCRIPTS_DIR/../README.md" | head -5 || echo "  No direct script references found"
        echo ""
    fi
    
    # Check shell configurations
    if [[ -f "$SCRIPTS_DIR/../zsh/.zshrc" ]]; then
        echo -e "${BLUE}🐚 Shell configuration references:${NC}"
        grep -n "scripts/" "$SCRIPTS_DIR/../zsh/.zshrc" | head -5 || echo "  No direct script references found"
        echo ""
    fi
    
    echo -e "${YELLOW}💡 Tip:${NC} Search your entire project for 'scripts/' references before removing symlinks"
}

# Remove all symlinks (CAUTION!)
remove_all_symlinks() {
    echo -e "${RED}⚠️ CAUTION: Removing All Backward Compatibility Symlinks${NC}"
    echo "=========================================================="
    echo ""
    echo "This will break any existing references to scripts using old paths!"
    echo ""
    
    # Count symlinks
    local symlink_count
    symlink_count=$(find "$SCRIPTS_DIR" -maxdepth 1 -type l | wc -l | tr -d ' ')
    
    echo "Found $symlink_count symlinks to remove:"
    find "$SCRIPTS_DIR" -maxdepth 1 -type l -exec basename {} \; | sort | sed 's/^/  • /'
    echo ""
    
    read -p "Are you sure you want to remove all symlinks? (yes/no): " -r confirmation
    if [[ "$confirmation" != "yes" ]]; then
        echo "Aborted - no symlinks removed"
        return 0
    fi
    
    echo ""
    echo "Removing symlinks..."
    local removed=0
    while IFS= read -r -d '' symlink; do
        local basename_link=$(basename "$symlink")
        rm "$symlink"
        echo -e "  ${GREEN}✓${NC} Removed: $basename_link"
        ((removed++))
    done < <(find "$SCRIPTS_DIR" -maxdepth 1 -type l -print0)
    
    echo ""
    echo -e "${GREEN}✅ Removed $removed symlinks${NC}"
    echo ""
    echo -e "${YELLOW}⚠️ Important:${NC} Update any references to use new paths:"
    echo "  Old: scripts/api-key-manager.sh"
    echo "  New: scripts/security/api-key-manager.sh"
}

# Show help
show_help() {
    cat << EOF
Backward Compatibility Symlinks Manager

USAGE:
    $(basename "$0") [COMMAND]

COMMANDS:
    status          Show current symlink status (default)
    check           Check symlink status (same as status)
    fix             Fix any broken symlinks
    references      Check for references to symlinks in common files
    remove-all      Remove all symlinks (CAUTION!)
    help            Show this help message

ABOUT:
These symlinks were created during the scripts reorganization to maintain
backward compatibility. They allow existing scripts, documentation, and 
workflows to continue working without modification.

EXAMPLES:
    $(basename "$0")                    # Show status
    $(basename "$0") fix                # Fix broken symlinks
    $(basename "$0") references         # Check for usage
    $(basename "$0") remove-all         # Remove all (careful!)

SAFETY:
• Keep symlinks for backward compatibility (recommended)
• Only remove after updating all references to use new paths
• Use 'references' command to find potential usage before removal
EOF
}

# Main execution
main() {
    case "$ACTION" in
        "status"|"check")
            check_symlinks
            ;;
        "fix")
            fix_broken_symlinks
            echo ""
            echo "Rechecking status after fixes..."
            echo ""
            check_symlinks
            ;;
        "references"|"refs")
            check_references
            ;;
        "remove-all"|"remove"|"clean")
            remove_all_symlinks
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $ACTION${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main