#!/bin/bash
# Fix path calculations broken by scripts reorganization
# Scripts moved to subdirectories need updated DOTFILES_DIR calculations

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=${1:-"--dry-run"}

echo -e "${BLUE}🔧 Fixing Script Paths After Reorganization${NC}"
echo "=============================================="
echo "Mode: $DRY_RUN"
echo ""

# Scripts that need path fixes (moved to subdirectories)
declare -a SCRIPTS_TO_FIX=(
    "claude/deploy-project.sh"
    "claude/deploy-user.sh"
    "mcp/sync.sh"
    "mcp/sync-config.sh"
    "mcp/check.sh"
)

fix_dotfiles_dir_calculation() {
    local script_path="$1"
    local full_path="$SCRIPTS_DIR/$script_path"
    
    if [[ ! -f "$full_path" ]]; then
        echo -e "  ${RED}✗${NC} Not found: $script_path"
        return 1
    fi
    
    # Check if script has the problematic pattern
    if ! grep -q 'DOTFILES_DIR="$(dirname "$SCRIPT_DIR")"' "$full_path" 2>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} No fix needed: $script_path"
        return 0
    fi
    
    if [[ "$DRY_RUN" != "--execute" ]]; then
        echo -e "  ${BLUE}Would fix:${NC} $script_path"
        echo "    Change: DOTFILES_DIR=\"\$(dirname \"\$SCRIPT_DIR\")\""
        echo "    To:     DOTFILES_DIR=\"\$(dirname \"\$(dirname \"\$SCRIPT_DIR\")\")\"" 
        return 0
    fi
    
    # Create backup
    cp "$full_path" "${full_path}.backup"
    
    # Fix the path calculation
    sed -i '' 's/DOTFILES_DIR="$(dirname "$SCRIPT_DIR")"/DOTFILES_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"/g' "$full_path"
    
    echo -e "  ${GREEN}✓${NC} Fixed: $script_path"
}

# Fix other specific issues
fix_pass_manager_repo_url() {
    local script_path="security/pass-manager.sh"
    local full_path="$SCRIPTS_DIR/$script_path"
    
    if ! grep -q "pass-store.git" "$full_path" 2>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} No fix needed: $script_path (repo URL)"
        return 0
    fi
    
    if [[ "$DRY_RUN" != "--execute" ]]; then
        echo -e "  ${BLUE}Would fix:${NC} $script_path (repo URL)"
        echo "    Change: git@github.com:smian0/pass-store.git"
        echo "    To:     git@github.com:smian0/pass.git"
        return 0
    fi
    
    # Create backup
    cp "$full_path" "${full_path}.backup"
    
    # Fix the repo URL
    sed -i '' 's/pass-store\.git/pass.git/g' "$full_path"
    
    echo -e "  ${GREEN}✓${NC} Fixed: $script_path (repo URL)"
}

# Remove deprecated scripts
remove_deprecated_script() {
    local script_path="$1"
    local full_path="$SCRIPTS_DIR/$script_path"
    
    if [[ ! -f "$full_path" ]]; then
        echo -e "  ${YELLOW}⚠${NC} Already removed: $script_path"
        return 0
    fi
    
    if [[ "$DRY_RUN" != "--execute" ]]; then
        echo -e "  ${BLUE}Would remove:${NC} $script_path (deprecated)"
        return 0
    fi
    
    # Move to backup location instead of deleting
    mv "$full_path" "${full_path}.deprecated"
    
    echo -e "  ${GREEN}✓${NC} Removed: $script_path (moved to .deprecated)"
}

# Main execution
main() {
    if [[ "${1:-}" == "--help" ]]; then
        echo "Usage: $0 [--dry-run|--execute]"
        echo ""
        echo "Fixes script path calculations broken by reorganization:"
        echo "• Updates DOTFILES_DIR calculations for moved scripts"
        echo "• Fixes pass-manager.sh repo URL reference"  
        echo "• Removes deprecated scripts"
        echo ""
        echo "Options:"
        echo "  --dry-run   Show what would be done (default)"
        echo "  --execute   Actually perform the fixes"
        echo "  --help      Show this help message"
        exit 0
    fi
    
    echo -e "${BLUE}📁 Fixing DOTFILES_DIR calculations...${NC}"
    for script in "${SCRIPTS_TO_FIX[@]}"; do
        fix_dotfiles_dir_calculation "$script"
    done
    echo ""
    
    echo -e "${BLUE}🔗 Fixing repository references...${NC}"
    fix_pass_manager_repo_url
    echo ""
    
    echo -e "${BLUE}🗑️ Removing deprecated scripts...${NC}"
    remove_deprecated_script "mcp/extract.sh"
    echo ""
    
    if [[ "$DRY_RUN" != "--execute" ]]; then
        echo -e "${YELLOW}🔍 This was a dry run. To execute the fixes:${NC}"
        echo "  scripts/fix-paths-after-reorganization.sh --execute"
        echo ""
        echo -e "${BLUE}📋 Summary of issues found:${NC}"
        echo "• ${#SCRIPTS_TO_FIX[@]} scripts with broken DOTFILES_DIR paths"
        echo "• 1 script with outdated repo URL"
        echo "• 1 deprecated script to remove"
    else
        echo -e "${GREEN}✅ Script path fixes complete!${NC}"
        echo ""
        echo "📋 Summary:"
        echo "• Fixed DOTFILES_DIR calculations in subdirectory scripts"
        echo "• Updated pass-manager.sh repository URL"
        echo "• Removed deprecated extract.sh script"
        echo ""
        echo "💡 Backups created with .backup extension"
        echo "💡 Run a test to verify scripts still work correctly"
    fi
}

# Run main function
main "$@"