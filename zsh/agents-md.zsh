# =============================================================================
# AGENTS.md Standardization Support
# =============================================================================
# This file provides automatic symlinking and migration support for the 
# AGENTS.md standard, which unifies AI agent configuration across different
# tools (Claude, Cursor, Windsurf, etc.)
#
# More info: https://www.linkedin.com/pulse/goodbye-config-hell-hello-agentsmd-vladislav-guzey-rpchc/
# =============================================================================

# Auto-create CLAUDE.md symlink pointing to AGENTS.md when it exists
# This supports the AGENTS.md standard while maintaining Claude Code compatibility
function _check_and_link_agents() {
    # Skip system directories and home directory to avoid clutter
    if [[ "$PWD" == "/" || "$PWD" == "$HOME" || "$PWD" == "/tmp" || "$PWD" == "/usr"* || "$PWD" == "/etc"* ]]; then
        return 0
    fi
    
    # Determine if we should show messages (only in interactive shells)
    local show_messages=false
    if [[ -o interactive ]]; then
        show_messages=true
    fi
    
    if [[ -f "AGENTS.md" ]]; then
        if [[ ! -e "CLAUDE.md" ]]; then
            # No CLAUDE.md exists, create symlink
            ln -s AGENTS.md CLAUDE.md
            [[ "$show_messages" == "true" ]] && echo "✓ Created CLAUDE.md symlink to AGENTS.md"
        elif [[ -L "CLAUDE.md" ]]; then
            # CLAUDE.md is a symlink, check if it points to AGENTS.md
            local target=$(readlink CLAUDE.md)
            if [[ "$target" != "AGENTS.md" ]]; then
                rm CLAUDE.md && ln -s AGENTS.md CLAUDE.md
                [[ "$show_messages" == "true" ]] && echo "✓ Updated CLAUDE.md symlink to point to AGENTS.md"
            fi
        elif [[ -f "CLAUDE.md" ]]; then
            # CLAUDE.md is a regular file, notify user only in interactive mode
            if [[ "$show_messages" == "true" ]]; then
                echo "ℹ️  Both AGENTS.md and CLAUDE.md exist as regular files"
                echo "   Run 'agents-init' to migrate CLAUDE.md content to AGENTS.md"
            fi
        fi
    elif [[ -f "CLAUDE.md" && ! -f "AGENTS.md" ]]; then
        # CLAUDE.md exists but no AGENTS.md - suggest migration only in interactive mode
        if [[ "$show_messages" == "true" ]]; then
            echo "📋 CLAUDE.md detected - Consider migrating to AGENTS.md standard"
            echo "   Run: agents-init"
            echo "   This will convert CLAUDE.md → AGENTS.md and create a symlink for compatibility"
        fi
    fi
}

# Helper function to initialize AGENTS.md from existing CLAUDE.md
function agents-init() {
    if [[ -f "CLAUDE.md" && ! -f "AGENTS.md" ]]; then
        # Move CLAUDE.md to AGENTS.md and create symlink
        mv CLAUDE.md AGENTS.md
        ln -s AGENTS.md CLAUDE.md
        echo "✓ Migrated CLAUDE.md to AGENTS.md and created symlink"
    elif [[ -f "CLAUDE.md" && -f "AGENTS.md" ]]; then
        echo "⚠️  Both AGENTS.md and CLAUDE.md already exist"
        echo "   Manual merge required. Consider:"
        echo "   1. Merge content from CLAUDE.md into AGENTS.md"
        echo "   2. Run: rm CLAUDE.md && ln -s AGENTS.md CLAUDE.md"
    elif [[ ! -f "CLAUDE.md" && -f "AGENTS.md" ]]; then
        ln -s AGENTS.md CLAUDE.md
        echo "✓ Created CLAUDE.md symlink to existing AGENTS.md"
    else
        # Create new AGENTS.md with template
        cat > AGENTS.md << 'EOF'
# AGENTS.md - AI Agent Configuration

This file provides instructions for AI coding agents (Claude, Cursor, Windsurf, etc.) 
on how to interact with this project.

## Project Overview
[Describe your project here]

## Setup Instructions
[Include setup commands and requirements]

## Code Style Guidelines
[Define coding standards and conventions]

## Testing Procedures
[Explain how to run tests]

## Custom Notes
[Any project-specific instructions]

---
*Using the AGENTS.md standard for unified AI agent configuration*
EOF
        ln -s AGENTS.md CLAUDE.md
        echo "✓ Created new AGENTS.md template and CLAUDE.md symlink"
    fi
}

# Show status of AGENTS.md and CLAUDE.md files
function agents-status() {
    echo "📄 Agent Configuration Status:"
    echo "=============================="
    
    if [[ -f "AGENTS.md" ]]; then
        echo "✓ AGENTS.md exists (standard configuration)"
        if [[ -L "CLAUDE.md" ]]; then
            local target=$(readlink CLAUDE.md)
            if [[ "$target" == "AGENTS.md" ]]; then
                echo "✓ CLAUDE.md → AGENTS.md (correct symlink)"
            else
                echo "⚠️  CLAUDE.md → $target (incorrect symlink target)"
            fi
        elif [[ -f "CLAUDE.md" ]]; then
            echo "⚠️  CLAUDE.md exists as separate file (not symlinked)"
            echo "   Run 'agents-init' to migrate to AGENTS.md standard"
        else
            echo "✗ CLAUDE.md not found"
            echo "   Run 'agents-sync' to create symlink"
        fi
    elif [[ -f "CLAUDE.md" ]]; then
        echo "✗ AGENTS.md not found"
        echo "✓ CLAUDE.md exists (legacy configuration)"
        echo "   Run 'agents-init' to migrate to AGENTS.md standard"
    else
        echo "✗ No agent configuration files found"
        echo "   Run 'agents-init' to create AGENTS.md template"
    fi
    
    # Check for other common agent config files
    local other_configs=()
    [[ -f ".cursorrules" ]] && other_configs+=(".cursorrules")
    [[ -f "CURSOR.md" ]] && other_configs+=("CURSOR.md")
    [[ -f "WINDSURF.md" ]] && other_configs+=("WINDSURF.md")
    [[ -f ".aide" ]] && other_configs+=(".aide")
    
    if [[ ${#other_configs[@]} -gt 0 ]]; then
        echo ""
        echo "Other agent configs found:"
        for config in "${other_configs[@]}"; do
            echo "  - $config"
        done
        echo "Consider consolidating into AGENTS.md"
    fi
}

# Force sync CLAUDE.md symlink to AGENTS.md
function agents-sync() {
    if [[ -f "AGENTS.md" ]]; then
        if [[ -L "CLAUDE.md" || -f "CLAUDE.md" ]]; then
            rm -f CLAUDE.md
        fi
        ln -s AGENTS.md CLAUDE.md
        echo "✓ CLAUDE.md synced to AGENTS.md"
    else
        echo "✗ AGENTS.md not found. Run 'agents-init' first"
        return 1
    fi
}

# Combined function to check both AGENTS.md and MCP configuration
function _check_and_link_all() {
    _check_and_link_agents
    
    # Source MCP configuration script and run MCP auto-link
    if [[ -f "$HOME/dotfiles/zsh/mcp-config.zsh" ]]; then
        source "$HOME/dotfiles/zsh/mcp-config.zsh"
        mcp_auto_link
    fi
}

# Hook into directory changes to auto-check for AGENTS.md and MCP configuration
autoload -U add-zsh-hook
add-zsh-hook chpwd _check_and_link_all

# Also check on shell initialization for current directory
_check_and_link_all