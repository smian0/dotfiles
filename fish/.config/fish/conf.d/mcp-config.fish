# =============================================================================
# MCP Configuration Management (Claude CLI Based)
# =============================================================================
# This file provides automatic symlinking and management support for MCP
# (Model Context Protocol) configuration files using the official Claude CLI.

# Path to the extraction script
set -gx MCP_EXTRACT_SCRIPT "$HOME/dotfiles/scripts/extract-mcp-config.py"

# Auto-create .cursor/mcp.json symlink pointing to .mcp.json when it exists
function _check_and_link_mcp
    # Skip system directories and home directory to avoid clutter
    if string match -q -r '^/(|tmp|usr.*|etc.*)$' $PWD; or test "$PWD" = "$HOME"
        return 0
    end

    # Determine if we should show messages (only in interactive shells)
    set -l show_messages false
    if status is-interactive
        set show_messages true
    end

    if test -f .mcp.json
        # Ensure .cursor directory exists
        if not test -d .cursor
            mkdir -p .cursor
            test $show_messages = true; and echo "✓ Created .cursor directory for MCP configuration"
        end

        if not test -e .cursor/mcp.json
            # No .cursor/mcp.json exists, create symlink
            ln -s ../.mcp.json .cursor/mcp.json
            test $show_messages = true; and echo "✓ Created .cursor/mcp.json symlink to .mcp.json"
        else if test -L .cursor/mcp.json
            # .cursor/mcp.json is a symlink, check if it points to ../.mcp.json
            set -l target (readlink .cursor/mcp.json)
            if test "$target" != "../.mcp.json"
                rm .cursor/mcp.json; and ln -s ../.mcp.json .cursor/mcp.json
                test $show_messages = true; and echo "✓ Updated .cursor/mcp.json symlink to point to .mcp.json"
            end
        else if test -f .cursor/mcp.json
            # .cursor/mcp.json is a regular file, notify user only in interactive mode
            if test $show_messages = true
                echo "ℹ️  Both .mcp.json and .cursor/mcp.json exist as regular files"
                echo "   Run 'mcp-init' to manage MCP configuration files"
            end
        end
    else if test -f .cursor/mcp.json; and not test -f .mcp.json
        # .cursor/mcp.json exists but no .mcp.json - suggest migration only in interactive mode
        if test $show_messages = true
            echo "🔧 .cursor/mcp.json detected - Consider creating a root .mcp.json for standardization"
            echo "   Run: mcp-init"
            echo "   This will move .cursor/mcp.json → .mcp.json and create a symlink for compatibility"
        end
    end
end

# Helper function to initialize MCP configuration from existing .cursor/mcp.json
function mcp-init
    if test -f .cursor/mcp.json; and not test -f .mcp.json
        # Move .cursor/mcp.json to .mcp.json and create symlink
        mv .cursor/mcp.json .mcp.json
        ln -s ../.mcp.json .cursor/mcp.json
        echo "✓ Migrated .cursor/mcp.json to .mcp.json and created symlink"
    else if test -f .cursor/mcp.json; and test -f .mcp.json
        echo "⚠️  Both .mcp.json and .cursor/mcp.json already exist"
        echo "   Manual merge required. Consider:"
        echo "   1. Merge content from .cursor/mcp.json into .mcp.json"
        echo "   2. Run: rm .cursor/mcp.json && ln -s ../.mcp.json .cursor/mcp.json"
    else if not test -f .cursor/mcp.json; and test -f .mcp.json
        # Ensure .cursor directory exists
        mkdir -p .cursor
        ln -s ../.mcp.json .cursor/mcp.json
        echo "✓ Created .cursor/mcp.json symlink to existing .mcp.json"
    else
        # Create new .mcp.json with template
        echo '{
  "mcpServers": {
    "example-server": {
      "type": "stdio",
      "command": "node",
      "args": ["path/to/your/mcp-server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}' > .mcp.json
        mkdir -p .cursor
        ln -s ../.mcp.json .cursor/mcp.json
        echo "✓ Created new .mcp.json template and .cursor/mcp.json symlink"
    end
end

# Show status of MCP configuration files
function mcp-status
    echo "🔧 MCP Configuration Status:"
    echo "============================"

    if test -f .mcp.json
        echo "✓ .mcp.json exists (root configuration)"
        if test -L .cursor/mcp.json
            set -l target (readlink .cursor/mcp.json)
            if test "$target" = "../.mcp.json"
                echo "✓ .cursor/mcp.json → .mcp.json (correct symlink)"
            else
                echo "⚠️  .cursor/mcp.json → $target (incorrect symlink target)"
            end
        else if test -f .cursor/mcp.json
            echo "⚠️  .cursor/mcp.json exists as separate file (not symlinked)"
            echo "   Run 'mcp-init' to manage MCP configuration"
        else
            echo "✗ .cursor/mcp.json not found"
            echo "   Run 'mcp-sync' to create symlink"
        end
    else if test -f .cursor/mcp.json
        echo "✗ .mcp.json not found"
        echo "✓ .cursor/mcp.json exists (cursor-specific configuration)"
        echo "   Run 'mcp-init' to create standardized .mcp.json"
    else
        echo "✗ No MCP configuration files found"
        echo "   Run 'mcp-init' to create .mcp.json template"
    end

    # Check .cursor directory
    if not test -d .cursor
        echo "✗ .cursor directory not found"
    else
        echo "✓ .cursor directory exists"
    end
end

# Force sync .cursor/mcp.json symlink to .mcp.json
function mcp-sync
    if test -f .mcp.json
        mkdir -p .cursor
        if test -L .cursor/mcp.json; or test -f .cursor/mcp.json
            rm -f .cursor/mcp.json
        end
        ln -s ../.mcp.json .cursor/mcp.json
        echo "✓ .cursor/mcp.json synced to .mcp.json"
    else
        echo "✗ .mcp.json not found. Run 'mcp-init' first"
        return 1
    end
end

# Check if Claude CLI is available
function _check_claude_cli
    if not command -v claude >/dev/null 2>&1
        echo "❌ Claude CLI not found. Please install Claude CLI first."
        echo "   Visit: https://claude.ai/downloads"
        return 1
    end
    return 0
end

# List all available MCP servers using Claude CLI
function mcp-list
    if not _check_claude_cli
        return 1
    end

    echo "🔍 Available MCP servers (via Claude CLI):"
    claude mcp list
end

# Aliases for convenience
alias mcpls='mcp-list'
alias mcps='mcp-setup'
alias mcpm='mcp-menu'
alias mcph='mcp-help'

# Extract global (user-scoped) MCP servers only
function mcp-extract-global
    set -l output_file .mcp.json
    if test (count $argv) -gt 0
        set output_file $argv[1]
    end

    echo "🌐 Extracting global MCP servers to: $output_file"

    if not _check_claude_cli
        return 1
    end

    # Get list of global servers and create JSON
    set -l server_list (claude mcp list 2>/dev/null | grep -E "^[a-zA-Z0-9_-]+:" | cut -d: -f1)

    if test -z "$server_list"
        echo "❌ No MCP servers found or Claude CLI error"
        return 1
    end

    # Build JSON (simplified version for fish)
    echo '{' > $output_file
    echo '  "mcpServers": {' >> $output_file

    set -l first true
    for server in $server_list
        set -l server_info (claude mcp get $server 2>/dev/null)
        if echo $server_info | grep -q "User config"
            if test $first != true
                echo ',' >> $output_file
            end
            set first false
            echo "    \"$server\": {}" >> $output_file
        end
    end

    echo '' >> $output_file
    echo '  }' >> $output_file
    echo '}' >> $output_file

    echo "✅ Global MCP servers extracted to: $output_file"
end

# Quick setup: extract global servers and initialize MCP in current directory
function mcp-setup
    echo "🚀 Quick MCP setup for current directory:"

    # Extract global servers to .mcp.json
    if mcp-extract-global .mcp.json
        echo "✅ Extracted global MCP servers to .mcp.json"

        # Use existing mcp-sync to create .cursor symlink
        mcp-sync

        echo "🎉 MCP setup complete!"
        echo "   - .mcp.json created with global servers"
        echo "   - .cursor/mcp.json symlinked for Cursor compatibility"
        echo "   - Run 'mcp-status' to verify setup"
    else
        echo "❌ Failed to extract MCP servers"
        return 1
    end
end

# Interactive MCP extraction menu
function mcp-menu
    echo "🔧 MCP Configuration Extraction Menu (Claude CLI)"
    echo "=================================================="
    echo "1) List available servers"
    echo "2) Extract global servers"
    echo "3) Quick setup (global servers + symlink)"
    echo "4) Show MCP status"
    echo "0) Exit"
    echo ""

    while true
        echo -n "Select option (0-4): "
        read -l choice

        switch $choice
            case 1
                mcp-list
                echo ""
            case 2
                echo -n "Output file [.mcp.json]: "
                read -l output
                if test -z "$output"
                    set output .mcp.json
                end
                mcp-extract-global $output
                echo ""
            case 3
                mcp-setup
                echo ""
            case 4
                mcp-status
                echo ""
            case 0
                echo "Goodbye! 👋"
                break
            case '*'
                echo "❌ Invalid option. Please choose 0-4."
        end
    end
end

# Help function
function mcp-help
    echo "🔧 MCP Configuration Extraction Help"
    echo "====================================="
    echo ""
    echo "QUICK START:"
    echo "   mcp-setup              # Quick setup with Claude CLI (recommended)"
    echo "   mcp-extract-global     # Extract global servers"
    echo ""
    echo "COMMANDS:"
    echo "   mcpls  = mcp-list      # List available MCP servers"
    echo "   mcps   = mcp-setup     # Quick setup"
    echo "   mcpm   = mcp-menu      # Interactive menu"
    echo "   mcph   = mcp-help      # This help"
    echo ""
end

# Hook into directory changes to auto-check for MCP configuration
function _mcp_on_directory_change --on-variable PWD
    _check_and_link_mcp
end

# Also check on shell initialization for current directory
_check_and_link_mcp
