#!/bin/bash
# Scripts Directory Reorganization Tool
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
    
    local dirs=(
        "security"
        "system" 
        "claude"
        "claude/oauth"
        "mcp"
        "mcp/env"
        "utils"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ "$DRY_RUN" != "--execute" ]]; then
            echo "  Would create: $SCRIPTS_DIR/$dir"
        else
            mkdir -p "$SCRIPTS_DIR/$dir"
            echo -e "  ${GREEN}✓${NC} Created: $dir"
        fi
    done
    echo ""
}

# File migration mapping
declare -A FILE_MOVES
FILE_MOVES=(
    # Security tools
    ["api-key-manager.sh"]="security/api-key-manager.sh"
    ["env-debug.sh"]="security/env-debug.sh"
    ["gpg-manager.sh"]="security/gpg-manager.sh"
    ["pass-manager.sh"]="security/pass-manager.sh"
    
    # System tools
    ["backup-restore.sh"]="system/backup-restore.sh"
    ["install-by-environment.sh"]="system/install-by-environment.sh"
    ["npm-packages.sh"]="system/npm-packages.sh"
    ["os-detect.sh"]="system/os-detect.sh"
    ["profile-manager.sh"]="system/profile-manager.sh"
    ["validate-config.sh"]="system/validate-config.sh"
    
    # Claude tools
    ["deploy-claude-project.sh"]="claude/deploy-project.sh"
    ["deploy-claude-user.sh"]="claude/deploy-user.sh"
    ["fix-claude-ssh-auth.sh"]="claude/fix-ssh-auth.sh"
    
    # MCP tools
    ["claude-mcp-extract.sh"]="mcp/extract.sh"
    ["extract-mcp-config.py"]="mcp/extract-config.py"
    ["mcp-check.sh"]="mcp/check.sh"
    ["mcp-sync.sh"]="mcp/sync.sh"
    ["sync-mcp-config.sh"]="mcp/sync-config.sh"
)

# Directory moves
declare -A DIR_MOVES
DIR_MOVES=(
    ["claude-oauth"]="claude/oauth"
    ["mcp-env"]="mcp/env"
)

# Move files with backward compatibility
migrate_files() {
    echo -e "${BLUE}📦 Migrating files...${NC}"
    
    for old_name in "${!FILE_MOVES[@]}"; do
        local new_path="${FILE_MOVES[$old_name]}"
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
    done
    echo ""
}

# Move directories
migrate_directories() {
    echo -e "${BLUE}📁 Migrating directories...${NC}"
    
    for old_name in "${!DIR_MOVES[@]}"; do
        local new_path="${DIR_MOVES[$old_name]}"
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
    done
    echo ""
}

# Create category README files
create_category_readmes() {
    echo -e "${BLUE}📖 Creating category README files...${NC}"
    
    if [[ "$DRY_RUN" != "--execute" ]]; then
        echo "  Would create README files for each category"
        return
    fi
    
    # Security README
    cat > "$SCRIPTS_DIR/security/README.md" << 'EOF'
# Security Scripts

Credential and security management tools.

## Scripts

- **api-key-manager.sh** - API key management via pass password store
- **env-debug.sh** - Environment variable diagnostics and troubleshooting  
- **gpg-manager.sh** - GPG key management, backup, and synchronization
- **pass-manager.sh** - Password store management with Git integration

## Usage

All scripts support `--help` for detailed usage information.
EOF

    # System README
    cat > "$SCRIPTS_DIR/system/README.md" << 'EOF'
# System Scripts

System installation, backup, and management utilities.

## Scripts

- **backup-restore.sh** - Complete backup and restoration for dotfiles
- **install-by-environment.sh** - Environment-based installation with profile detection
- **npm-packages.sh** - NPM package management and synchronization
- **os-detect.sh** - Operating system detection and environment setup
- **profile-manager.sh** - Profile-based installation management
- **validate-config.sh** - Configuration validation and integrity checking

## Usage

Most scripts support multiple operating systems (macOS and Ubuntu).
EOF

    # Claude README
    cat > "$SCRIPTS_DIR/claude/README.md" << 'EOF'
# Claude Code Scripts

Tools for Claude Code configuration and deployment.

## Scripts

- **deploy-project.sh** - Deploy Claude configuration to specific projects
- **deploy-user.sh** - Deploy Claude user-level configuration
- **fix-ssh-auth.sh** - Fix Claude Code SSH authentication issues

## Directories

- **oauth/** - OAuth 2.0 + PKCE authentication tools

## Usage

Scripts support both project-level and user-level Claude Code configurations.
EOF

    # MCP README
    cat > "$SCRIPTS_DIR/mcp/README.md" << 'EOF'
# MCP Scripts

Model Context Protocol (MCP) server management and configuration tools.

## Scripts

- **check.sh** - Validate MCP server configurations
- **extract.sh** - Extract MCP configurations from Claude Code
- **extract-config.py** - Python-based MCP configuration extraction
- **sync.sh** - Synchronize MCP configurations
- **sync-config.sh** - Advanced MCP configuration synchronization

## Directories

- **env/** - Environment variable management for MCP servers

## Usage

Primary interface is through shell functions in `zsh/mcp-config.zsh`.
EOF

    echo -e "  ${GREEN}✓${NC} Created category README files"
    echo ""
}

# Update main README
update_main_readme() {
    echo -e "${BLUE}📋 Updating main README...${NC}"
    
    if [[ "$DRY_RUN" != "--execute" ]]; then
        echo "  Would update scripts/README.md with new structure"
        return
    fi
    
    # Backup original
    cp "$SCRIPTS_DIR/README.md" "$SCRIPTS_DIR/README.md.backup"
    
    cat > "$SCRIPTS_DIR/README.md" << 'EOF'
# Scripts Directory

Organized utility scripts for dotfiles management and system configuration.

## Directory Structure

### 🔐 security/
Credential and security management tools
- API key management via pass password store
- Environment variable diagnostics  
- GPG key management and backup
- Password store management

### 🖥️ system/
System installation, backup, and management utilities
- Backup and restoration systems
- Profile-based installation management
- Operating system detection and setup
- Configuration validation

### 🤖 claude/
Claude Code specific tools and configurations
- Project and user-level deployment
- SSH authentication fixes
- OAuth authentication tools

### 🔌 mcp/
Model Context Protocol (MCP) server management
- Configuration extraction and validation
- Environment variable management
- Server synchronization tools

### 🛠️ utils/
General utility scripts (future expansion)

## Backward Compatibility

All original script paths remain available via symlinks:
```bash
# Both work identically:
scripts/api-key-manager.sh
scripts/security/api-key-manager.sh
```

## Migration

This directory was reorganized from a flat structure. Original paths are preserved for compatibility.

## Usage

Each category has its own README with detailed usage information.
All scripts support `--help` for usage details.
EOF

    echo -e "  ${GREEN}✓${NC} Updated main README"
    echo ""
}

# Main execution
main() {
    if [[ "$DRY_RUN" == "--help" ]]; then
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
    create_category_readmes
    update_main_readme
    
    if [[ "$DRY_RUN" != "--execute" ]]; then
        echo -e "${YELLOW}🔍 This was a dry run. To execute the reorganization:${NC}"
        echo "  $0 --execute"
    else
        echo -e "${GREEN}✅ Scripts directory reorganization complete!${NC}"
        echo ""
        echo "📋 Summary:"
        echo "• Created organized subdirectories"
        echo "• Moved files to logical locations"
        echo "• Created backward-compatible symlinks"
        echo "• Updated documentation"
        echo ""
        echo "💡 All original paths still work via symlinks"
    fi
}

# Run main function
main "$@"