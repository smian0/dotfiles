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
function _check_and_link_agents
    # Skip system directories and home directory to avoid clutter
    if string match -q -r '^/(|tmp|usr.*|etc.*)$' $PWD; or test "$PWD" = "$HOME"
        return 0
    end

    # Determine if we should show messages (only in interactive shells)
    set -l show_messages false
    if status is-interactive
        set show_messages true
    end

    if test -f AGENTS.md
        if not test -e CLAUDE.md
            # No CLAUDE.md exists, create symlink
            ln -s AGENTS.md CLAUDE.md
            test $show_messages = true; and echo "✓ Created CLAUDE.md symlink to AGENTS.md"
        else if test -L CLAUDE.md
            # CLAUDE.md is a symlink, check if it points to AGENTS.md
            set -l target (readlink CLAUDE.md)
            if test "$target" != "AGENTS.md"
                rm CLAUDE.md; and ln -s AGENTS.md CLAUDE.md
                test $show_messages = true; and echo "✓ Updated CLAUDE.md symlink to point to AGENTS.md"
            end
        else if test -f CLAUDE.md
            # CLAUDE.md is a regular file, notify user only in interactive mode
            if test $show_messages = true
                echo "ℹ️  Both AGENTS.md and CLAUDE.md exist as regular files"
                echo "   Run 'agents-init' to migrate CLAUDE.md content to AGENTS.md"
            end
        end
    else if test -f CLAUDE.md; and not test -f AGENTS.md
        # CLAUDE.md exists but no AGENTS.md - suggest migration only in interactive mode
        if test $show_messages = true
            echo "📋 CLAUDE.md detected - Consider migrating to AGENTS.md standard"
            echo "   Run: agents-init"
            echo "   This will convert CLAUDE.md → AGENTS.md and create a symlink for compatibility"
        end
    end
end

# Helper function to initialize AGENTS.md from existing CLAUDE.md
function agents-init
    if test -f CLAUDE.md; and not test -f AGENTS.md
        # Move CLAUDE.md to AGENTS.md and create symlink
        mv CLAUDE.md AGENTS.md
        ln -s AGENTS.md CLAUDE.md
        echo "✓ Migrated CLAUDE.md to AGENTS.md and created symlink"
    else if test -f CLAUDE.md; and test -f AGENTS.md
        echo "⚠️  Both AGENTS.md and CLAUDE.md already exist"
        echo "   Manual merge required. Consider:"
        echo "   1. Merge content from CLAUDE.md into AGENTS.md"
        echo "   2. Run: rm CLAUDE.md && ln -s AGENTS.md CLAUDE.md"
    else if not test -f CLAUDE.md; and test -f AGENTS.md
        ln -s AGENTS.md CLAUDE.md
        echo "✓ Created CLAUDE.md symlink to existing AGENTS.md"
    else
        # Create new AGENTS.md with template
        echo '# AGENTS.md - AI Agent Configuration

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
*Using the AGENTS.md standard for unified AI agent configuration*' > AGENTS.md
        ln -s AGENTS.md CLAUDE.md
        echo "✓ Created new AGENTS.md template and CLAUDE.md symlink"
    end
end

# Show status of AGENTS.md and CLAUDE.md files
function agents-status
    echo "📄 Agent Configuration Status:"
    echo "=============================="

    if test -f AGENTS.md
        echo "✓ AGENTS.md exists (standard configuration)"
        if test -L CLAUDE.md
            set -l target (readlink CLAUDE.md)
            if test "$target" = "AGENTS.md"
                echo "✓ CLAUDE.md → AGENTS.md (correct symlink)"
            else
                echo "⚠️  CLAUDE.md → $target (incorrect symlink target)"
            end
        else if test -f CLAUDE.md
            echo "⚠️  CLAUDE.md exists as separate file (not symlinked)"
            echo "   Run 'agents-init' to migrate to AGENTS.md standard"
        else
            echo "✗ CLAUDE.md not found"
            echo "   Run 'agents-sync' to create symlink"
        end
    else if test -f CLAUDE.md
        echo "✗ AGENTS.md not found"
        echo "✓ CLAUDE.md exists (legacy configuration)"
        echo "   Run 'agents-init' to migrate to AGENTS.md standard"
    else
        echo "✗ No agent configuration files found"
        echo "   Run 'agents-init' to create AGENTS.md template"
    end

    # Check for other common agent config files
    set -l other_configs
    test -f .cursorrules; and set -a other_configs .cursorrules
    test -f CURSOR.md; and set -a other_configs CURSOR.md
    test -f WINDSURF.md; and set -a other_configs WINDSURF.md
    test -f .aide; and set -a other_configs .aide

    if test (count $other_configs) -gt 0
        echo ""
        echo "Other agent configs found:"
        for config in $other_configs
            echo "  - $config"
        end
        echo "Consider consolidating into AGENTS.md"
    end
end

# Force sync CLAUDE.md symlink to AGENTS.md
function agents-sync
    if test -f AGENTS.md
        if test -L CLAUDE.md; or test -f CLAUDE.md
            rm -f CLAUDE.md
        end
        ln -s AGENTS.md CLAUDE.md
        echo "✓ CLAUDE.md synced to AGENTS.md"
    else
        echo "✗ AGENTS.md not found. Run 'agents-init' first"
        return 1
    end
end

# Hook into directory changes to auto-check for AGENTS.md
function _agents_on_directory_change --on-variable PWD
    _check_and_link_agents
end

# Also check on shell initialization for current directory
_check_and_link_agents
