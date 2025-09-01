# =============================================================================
# MCP Configuration Management (Claude CLI Based)
# =============================================================================
# This file provides automatic symlinking and management support for MCP 
# (Model Context Protocol) configuration files using the official Claude CLI.
# It creates .cursor/mcp.json symlinks from .mcp.json to provide a standardized 
# location while supporting Cursor's expected configuration path.
#
# Features:
# - Auto-creates .cursor/mcp.json symlinks from .mcp.json files
# - Uses official Claude CLI for robust MCP server extraction
# - Provides management commands: mcp-init, mcp-status, mcp-sync
# - Integrates with directory change hooks for automatic detection
# - Supports migration from .cursor/mcp.json to root .mcp.json
# =============================================================================

# Auto-create .cursor/mcp.json symlink pointing to .mcp.json when it exists
# This provides a standardized location for MCP configuration while supporting Cursor's expected path
function _check_and_link_mcp() {
    # Skip system directories and home directory to avoid clutter
    if [[ "$PWD" == "/" || "$PWD" == "$HOME" || "$PWD" == "/tmp" || "$PWD" == "/usr"* || "$PWD" == "/etc"* ]]; then
        return 0
    fi
    
    # Determine if we should show messages (only in interactive shells)
    local show_messages=false
    if [[ -o interactive ]]; then
        show_messages=true
    fi
    
    if [[ -f ".mcp.json" ]]; then
        # Ensure .cursor directory exists
        if [[ ! -d ".cursor" ]]; then
            mkdir -p .cursor
            [[ "$show_messages" == "true" ]] && echo "✓ Created .cursor directory for MCP configuration"
        fi
        
        if [[ ! -e ".cursor/mcp.json" ]]; then
            # No .cursor/mcp.json exists, create symlink
            ln -s ../.mcp.json .cursor/mcp.json
            [[ "$show_messages" == "true" ]] && echo "✓ Created .cursor/mcp.json symlink to .mcp.json"
        elif [[ -L ".cursor/mcp.json" ]]; then
            # .cursor/mcp.json is a symlink, check if it points to ../.mcp.json
            local target=$(readlink .cursor/mcp.json)
            if [[ "$target" != "../.mcp.json" ]]; then
                rm .cursor/mcp.json && ln -s ../.mcp.json .cursor/mcp.json
                [[ "$show_messages" == "true" ]] && echo "✓ Updated .cursor/mcp.json symlink to point to .mcp.json"
            fi
        elif [[ -f ".cursor/mcp.json" ]]; then
            # .cursor/mcp.json is a regular file, notify user only in interactive mode
            if [[ "$show_messages" == "true" ]]; then
                echo "ℹ️  Both .mcp.json and .cursor/mcp.json exist as regular files"
                echo "   Run 'mcp-init' to manage MCP configuration files"
            fi
        fi
    elif [[ -f ".cursor/mcp.json" && ! -f ".mcp.json" ]]; then
        # .cursor/mcp.json exists but no .mcp.json - suggest migration only in interactive mode
        if [[ "$show_messages" == "true" ]]; then
            echo "🔧 .cursor/mcp.json detected - Consider creating a root .mcp.json for standardization"
            echo "   Run: mcp-init"
            echo "   This will move .cursor/mcp.json → .mcp.json and create a symlink for compatibility"
        fi
    fi
}

# Helper function to initialize MCP configuration from existing .cursor/mcp.json
function mcp-init() {
    if [[ -f ".cursor/mcp.json" && ! -f ".mcp.json" ]]; then
        # Move .cursor/mcp.json to .mcp.json and create symlink
        mv .cursor/mcp.json .mcp.json
        ln -s ../.mcp.json .cursor/mcp.json
        echo "✓ Migrated .cursor/mcp.json to .mcp.json and created symlink"
    elif [[ -f ".cursor/mcp.json" && -f ".mcp.json" ]]; then
        echo "⚠️  Both .mcp.json and .cursor/mcp.json already exist"
        echo "   Manual merge required. Consider:"
        echo "   1. Merge content from .cursor/mcp.json into .mcp.json"
        echo "   2. Run: rm .cursor/mcp.json && ln -s ../.mcp.json .cursor/mcp.json"
    elif [[ ! -f ".cursor/mcp.json" && -f ".mcp.json" ]]; then
        # Ensure .cursor directory exists
        mkdir -p .cursor
        ln -s ../.mcp.json .cursor/mcp.json
        echo "✓ Created .cursor/mcp.json symlink to existing .mcp.json"
    else
        # Create new .mcp.json with template
        cat > .mcp.json << 'EOF'
{
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
}
EOF
        mkdir -p .cursor
        ln -s ../.mcp.json .cursor/mcp.json
        echo "✓ Created new .mcp.json template and .cursor/mcp.json symlink"
    fi
}

# Show status of MCP configuration files
function mcp-status() {
    echo "🔧 MCP Configuration Status:"
    echo "============================"
    
    if [[ -f ".mcp.json" ]]; then
        echo "✓ .mcp.json exists (root configuration)"
        if [[ -L ".cursor/mcp.json" ]]; then
            local target=$(readlink .cursor/mcp.json)
            if [[ "$target" == "../.mcp.json" ]]; then
                echo "✓ .cursor/mcp.json → .mcp.json (correct symlink)"
            else
                echo "⚠️  .cursor/mcp.json → $target (incorrect symlink target)"
            fi
        elif [[ -f ".cursor/mcp.json" ]]; then
            echo "⚠️  .cursor/mcp.json exists as separate file (not symlinked)"
            echo "   Run 'mcp-init' to manage MCP configuration"
        else
            echo "✗ .cursor/mcp.json not found"
            echo "   Run 'mcp-sync' to create symlink"
        fi
    elif [[ -f ".cursor/mcp.json" ]]; then
        echo "✗ .mcp.json not found"
        echo "✓ .cursor/mcp.json exists (cursor-specific configuration)"
        echo "   Run 'mcp-init' to create standardized .mcp.json"
    else
        echo "✗ No MCP configuration files found"
        echo "   Run 'mcp-init' to create .mcp.json template"
    fi
    
    # Check .cursor directory
    if [[ ! -d ".cursor" ]]; then
        echo "✗ .cursor directory not found"
    else
        echo "✓ .cursor directory exists"
    fi
}

# Force sync .cursor/mcp.json symlink to .mcp.json
function mcp-sync() {
    if [[ -f ".mcp.json" ]]; then
        mkdir -p .cursor
        if [[ -L ".cursor/mcp.json" || -f ".cursor/mcp.json" ]]; then
            rm -f .cursor/mcp.json
        fi
        ln -s ../.mcp.json .cursor/mcp.json
        echo "✓ .cursor/mcp.json synced to .mcp.json"
    else
        echo "✗ .mcp.json not found. Run 'mcp-init' first"
        return 1
    fi
}

# Automatically check and link MCP configuration on directory changes
# This function is called by the directory change hook in the main shell configuration
function mcp_auto_link() {
    _check_and_link_mcp
}

# =============================================================================
# MCP Configuration Extraction using Claude CLI
# =============================================================================
# Extract MCP server configurations using the official Claude CLI commands
# This is more robust and future-proof than parsing configuration files directly
#
# TRADE-OFFS:
# ✅ Claude CLI Approach (DEFAULT):
#    - Future-proof: Won't break with Claude updates
#    - Official API: Uses supported interfaces  
#    - Reliable: Less parsing complexity
#    - Maintained: Updated by Claude team
#    - Limited info: Can't extract complete config details for all servers
#
# ⚙️  Python Script Approach (FALLBACK):
#    - Complete details: Full configuration extraction
#    - Custom control: More output format options
#    - Brittle: May break if ~/.claude.json format changes
#    - Manual maintenance: Need to update parsing logic
#
# Use mcp-extract-detailed for complete configs, mcp-extract-* for robust extraction

# Check if Claude CLI is available
function _check_claude_cli() {
    if ! command -v claude >/dev/null 2>&1; then
        echo "❌ Claude CLI not found. Please install Claude CLI first."
        echo "   Visit: https://claude.ai/downloads"
        return 1
    fi
    return 0
}

# Parse Claude CLI output to extract server configuration
function _parse_mcp_server_config() {
    local server_name="$1"
    local server_info
    
    # Get detailed server information
    server_info=$(claude mcp get "$server_name" 2>/dev/null)
    
    if [[ $? -ne 0 || -z "$server_info" ]]; then
        echo "  \"$server_name\": { \"error\": \"Could not retrieve configuration\" }"
        return 1
    fi
    
    # Parse the output to extract configuration details
    local command=$(echo "$server_info" | grep "  Command:" | sed 's/.*Command: //')
    local args=$(echo "$server_info" | grep "  Args:" | sed 's/.*Args: //')
    local type=$(echo "$server_info" | grep "  Type:" | sed 's/.*Type: //')
    
    # Build JSON configuration
    echo -n "  \"$server_name\": {"
    
    local has_fields=false
    
    # Add type if present
    if [[ -n "$type" && "$type" != "" ]]; then
        echo -n "\"type\": \"$type\""
        has_fields=true
    fi
    
    # Add command
    if [[ -n "$command" && "$command" != "" ]]; then
        [[ "$has_fields" == "true" ]] && echo -n ", "
        echo -n "\"command\": \"$command\""
        has_fields=true
    fi
    
    # Add args if present
    if [[ -n "$args" && "$args" != "" ]]; then
        [[ "$has_fields" == "true" ]] && echo -n ", "
        
        # Convert space-separated args to JSON array
        local json_args=""
        local arg_count=0
        # Split args on spaces, handling quoted arguments
        while IFS= read -r arg; do
            if [[ -n "$arg" ]]; then
                [[ $arg_count -gt 0 ]] && json_args+=", "
                json_args+="\"$arg\""
                ((arg_count++))
            fi
        done <<< "$(echo "$args" | tr ' ' '\n')"
        
        echo -n "\"args\": [$json_args]"
        has_fields=true
    fi
    
    # Add empty env object for consistency
    [[ "$has_fields" == "true" ]] && echo -n ", "
    echo -n "\"env\": {}"
    
    echo -n "}"
}

# Extract MCP servers using Claude CLI
function _extract_mcp_servers_cli() {
    local scope_filter="$1"  # "user" for global, "project" for project-specific, or empty for all
    
    if ! _check_claude_cli; then
        return 1
    fi
    
    echo "🔍 Fetching MCP server list from Claude CLI..."
    
    # Get list of servers
    local server_list
    server_list=$(claude mcp list 2>/dev/null | grep -E "^[a-zA-Z0-9_-]+:" | cut -d: -f1)
    
    if [[ -z "$server_list" ]]; then
        echo "❌ No MCP servers found or Claude CLI error"
        return 1
    fi
    
    # Start building JSON
    echo "{"
    echo "  \"mcpServers\": {"
    
    local first_server=true
    local server_count=0
    
    while IFS= read -r server_name; do
        [[ -z "$server_name" ]] && continue
        
        # Get server details to check scope
        local server_info=$(claude mcp get "$server_name" 2>/dev/null)
        local server_scope=""
        
        if echo "$server_info" | grep -q "User config"; then
            server_scope="user"
        elif echo "$server_info" | grep -q "Project config"; then
            server_scope="project"
        fi
        
        # Apply scope filter
        if [[ -n "$scope_filter" && "$server_scope" != "$scope_filter" ]]; then
            continue
        fi
        
        # Add comma for subsequent servers
        if [[ "$first_server" != "true" ]]; then
            echo ","
        fi
        first_server=false
        
        # Parse and add server configuration
        _parse_mcp_server_config "$server_name"
        ((server_count++))
        
    done <<< "$server_list"
    
    echo ""
    echo "  }"
    echo "}"
    
    echo "✅ Extracted $server_count MCP servers" >&2
    return 0
}

# List all available MCP servers using Claude CLI
function mcp-list() {
    if ! _check_claude_cli; then
        return 1
    fi
    
    echo "🔍 Available MCP servers (via Claude CLI):"
    claude mcp list
}

# Extract global (user-scoped) MCP servers only
function mcp-extract-global() {
    local output_file="${1:-.mcp.json}"
    echo "🌐 Extracting global MCP servers to: $output_file"
    
    _extract_mcp_servers_cli "user" > "$output_file"
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Global MCP servers extracted to: $output_file"
        return 0
    else
        echo "❌ Failed to extract global MCP servers"
        return 1
    fi
}

# Extract project-scoped MCP servers only
function mcp-extract-project() {
    local output_file="${1:-project-mcp.json}"
    echo "📁 Extracting project MCP servers to: $output_file"
    
    _extract_mcp_servers_cli "project" > "$output_file"
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Project MCP servers extracted to: $output_file"
        return 0
    else
        echo "❌ Failed to extract project MCP servers"
        return 1
    fi
}

# Extract all MCP servers (global + project)
function mcp-extract-all() {
    local output_file="${1:-.mcp.json}"
    echo "📋 Extracting all MCP servers to: $output_file"
    
    _extract_mcp_servers_cli "" > "$output_file"
    
    if [[ $? -eq 0 ]]; then
        echo "✅ All MCP servers extracted to: $output_file"
        return 0
    else
        echo "❌ Failed to extract MCP servers"
        return 1
    fi
}

# Preview what would be extracted without writing file
function mcp-preview() {
    local scope="${1:-all}"
    echo "👀 Preview of MCP extraction (scope: $scope):"
    echo "============================================="
    
    case "$scope" in
        "global"|"user")
            _extract_mcp_servers_cli "user"
            ;;
        "project")
            _extract_mcp_servers_cli "project"
            ;;
        "all"|*)
            _extract_mcp_servers_cli ""
            ;;
    esac
}

# Quick setup: extract global servers and initialize MCP in current directory
function mcp-setup() {
    echo "🚀 Quick MCP setup for current directory:"
    
    # Extract global servers to .mcp.json
    if mcp-extract-global ".mcp.json"; then
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
    fi
}

# Interactive MCP extraction menu
function mcp-menu() {
    echo "🔧 MCP Configuration Extraction Menu (Claude CLI)"
    echo "=================================================="
    echo "1) List available servers"
    echo "2) Extract global servers only"
    echo "3) Extract project servers only"
    echo "4) Extract all servers"
    echo "5) Preview extraction"
    echo "6) Quick setup (global servers + symlink)"
    echo "7) Show MCP status"
    echo "0) Exit"
    echo ""
    
    while true; do
        echo -n "Select option (0-7): "
        read choice
        
        case $choice in
            1)
                mcp-list
                echo ""
                ;;
            2)
                echo -n "Output file [.mcp.json]: "
                read output
                mcp-extract-global "${output:-.mcp.json}"
                echo ""
                ;;
            3)
                echo -n "Output file [project-mcp.json]: "
                read output
                mcp-extract-project "${output:-project-mcp.json}"
                echo ""
                ;;
            4)
                echo -n "Output file [.mcp.json]: "
                read output
                mcp-extract-all "${output:-.mcp.json}"
                echo ""
                ;;
            5)
                echo "Preview options:"
                echo "  global - Preview global servers only"
                echo "  project - Preview project servers only"
                echo "  all - Preview all servers (default)"
                echo -n "Scope [all]: "
                read scope
                mcp-preview "${scope:-all}"
                echo ""
                ;;
            6)
                mcp-setup
                echo ""
                ;;
            7)
                mcp-status
                echo ""
                ;;
            0)
                echo "Goodbye! 👋"
                break
                ;;
            *)
                echo "❌ Invalid option. Please choose 0-7."
                ;;
        esac
    done
}

# =============================================================================
# Detailed Extraction using Python Script (Fallback)
# =============================================================================
# These functions provide access to the original Python script for complete config details

# Path to the extraction script
export MCP_EXTRACT_SCRIPT="$HOME/dotfiles/scripts/extract-mcp-config.py"

# Detailed extraction with complete configuration information
function mcp-extract-detailed() {
    if [[ ! -f "$MCP_EXTRACT_SCRIPT" ]]; then
        echo "❌ Detailed extraction script not found at: $MCP_EXTRACT_SCRIPT"
        echo "   Using Claude CLI approach instead..."
        return 1
    fi
    
    echo "🔧 Using detailed extraction (Python script) for complete configuration..."
    python3 "$MCP_EXTRACT_SCRIPT" "$@"
}

# Detailed extraction of global servers with complete config
function mcp-extract-global-detailed() {
    local output_file="${1:-.mcp.json}"
    echo "🌐 Extracting global MCP servers (detailed) to: $output_file"
    
    if mcp-extract-detailed --global-only --pretty --output "$output_file"; then
        echo "✅ Detailed global MCP servers extracted to: $output_file"
        return 0
    else
        echo "⚠️  Detailed extraction failed, falling back to Claude CLI..."
        mcp-extract-global "$output_file"
    fi
}

# Compare Claude CLI vs detailed extraction outputs
function mcp-compare-methods() {
    local temp_cli="/tmp/mcp-cli-output.json"
    local temp_detailed="/tmp/mcp-detailed-output.json"
    
    echo "📊 Comparing Claude CLI vs Detailed extraction methods..."
    echo "==========================================================="
    
    echo ""
    echo "🔍 Claude CLI approach:"
    if mcp-extract-global "$temp_cli" >/dev/null 2>&1; then
        echo "✅ Claude CLI extraction successful"
        echo "   Servers found: $(jq '.mcpServers | keys | length' "$temp_cli" 2>/dev/null || echo "unknown")"
    else
        echo "❌ Claude CLI extraction failed"
    fi
    
    echo ""
    echo "🔧 Detailed Python script approach:"
    if mcp-extract-global-detailed "$temp_detailed" >/dev/null 2>&1; then
        echo "✅ Detailed extraction successful"
        echo "   Servers found: $(jq '.mcpServers | keys | length' "$temp_detailed" 2>/dev/null || echo "unknown")"
        
        echo ""
        echo "📋 Configuration completeness comparison:"
        if command -v jq >/dev/null 2>&1; then
            echo "   CLI method config keys:"
            jq -r '.mcpServers | to_entries[0] | .value | keys | join(", ")' "$temp_cli" 2>/dev/null || echo "   Unable to parse"
            echo "   Detailed method config keys:"  
            jq -r '.mcpServers | to_entries[0] | .value | keys | join(", ")' "$temp_detailed" 2>/dev/null || echo "   Unable to parse"
        fi
    else
        echo "❌ Detailed extraction failed"
    fi
    
    # Clean up temp files
    rm -f "$temp_cli" "$temp_detailed" 2>/dev/null
}

# Help function explaining the different approaches
function mcp-help() {
    echo "🔧 MCP Configuration Extraction Help"
    echo "====================================="
    echo ""
    echo "AVAILABLE APPROACHES:"
    echo ""
    echo "1️⃣  CLAUDE CLI APPROACH (Recommended - Future-proof)"
    echo "   Commands: mcp-extract-global, mcp-extract-project, mcp-extract-all"
    echo "   ✅ Future-proof and maintained by Claude team"
    echo "   ✅ Uses official supported APIs"
    echo "   ⚠️  Limited configuration details for some servers"
    echo ""
    echo "2️⃣  DETAILED PYTHON SCRIPT APPROACH (Complete info)"
    echo "   Commands: mcp-extract-detailed, mcp-extract-global-detailed"
    echo "   ✅ Complete configuration extraction" 
    echo "   ✅ Full control over output format"
    echo "   ⚠️  May break if Claude changes internal formats"
    echo ""
    echo "QUICK START:"
    echo "   mcp-setup              # Quick setup with Claude CLI (recommended)"
    echo "   mcp-extract-global-detailed  # Complete config details"
    echo "   mcp-compare-methods    # Compare both approaches"
    echo ""
    echo "ALIASES:"
    echo "   mcps  = mcp-setup      mcpg  = mcp-extract-global"
    echo "   mcpls = mcp-list       mcpv  = mcp-preview"
    echo "   mcpm  = mcp-menu       mcph  = mcp-help"
}

# Aliases for convenience
alias mcpls='mcp-list'
alias mcpg='mcp-extract-global'
alias mcpp='mcp-extract-project'
alias mcpa='mcp-extract-all'
alias mcpv='mcp-preview'
alias mcps='mcp-setup'
alias mcpm='mcp-menu'
alias mcph='mcp-help'
alias mcpgd='mcp-extract-global-detailed'
alias mcpd='mcp-extract-detailed'
alias mcpc='mcp-compare-methods'
