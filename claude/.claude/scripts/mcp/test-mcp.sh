#!/bin/bash
set -euo pipefail

# Dynamic MCP Server Testing Script with Tool Discovery
# Usage: ./test-mcp-dynamic.sh [options] <server_path_or_name>

DEFAULT_TIMEOUT=120
MCP_CONFIG_FILE="$HOME/.claude/.claude/config.toml"
GLOBAL_MCP_CONFIG=".mcp.json"
# No external pattern file needed - using built-in patterns

usage() {
    echo "Dynamic MCP Server Testing Script"
    echo "Usage: $0 [options] <server_path_or_name>"
    echo ""
    echo "Options:"
    echo "  --config FILE      Use specific MCP config file"
    echo "  --discover         Force tool discovery mode"
    echo "  --module           Server is a Python module, not executable"
    echo "  --timeout SECONDS  Test timeout (default: $DEFAULT_TIMEOUT)"
    echo "  --list-only        Only list discovered tools, don't test"
    echo "  --help             Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 langextract-ollama                    # Test server from .mcp.json"
    echo "  $0 --module /path/to/server.py          # Test Python module"
    echo "  $0 --config custom.json my-server       # Use custom config"
    exit 1
}

log() {
    echo "$(date '+%H:%M:%S') $*"
}

error() {
    echo "❌ ERROR: $*" >&2
    exit 1
}

# Parse command line arguments
parse_args() {
    FORCE_DISCOVER=false
    IS_MODULE=false
    LIST_ONLY=false
    CUSTOM_CONFIG=""
    TIMEOUT=$DEFAULT_TIMEOUT
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --config)
                CUSTOM_CONFIG="$2"
                shift 2
                ;;
            --discover)
                FORCE_DISCOVER=true
                shift
                ;;
            --module)
                IS_MODULE=true
                shift
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --list-only)
                LIST_ONLY=true
                shift
                ;;
            --help)
                usage
                ;;
            -*)
                error "Unknown option: $1"
                ;;
            *)
                SERVER_INPUT="$1"
                shift
                ;;
        esac
    done
    
    [[ -z "${SERVER_INPUT:-}" ]] && usage
}

# Check if server exists in .mcp.json
check_existing_config() {
    local server_name="$1"
    local config_file="${CUSTOM_CONFIG:-$GLOBAL_MCP_CONFIG}"
    
    if [[ -f "$config_file" ]] && command -v jq >/dev/null 2>&1; then
        if jq -e ".mcpServers.\"$server_name\"" "$config_file" >/dev/null 2>&1; then
            log "✅ Found server '$server_name' in $config_file"
            echo "$config_file"
            return 0
        fi
    fi
    
    return 1
}

# Generate temporary MCP config for server
generate_temp_config() {
    local server_path="$1"
    local server_name
    server_name=$(basename "$server_path" .py | sed 's/_mcp_server$//' | sed 's/_server$//')
    
    local temp_config="/tmp/mcp-test-$$.json"
    
    if [[ "$IS_MODULE" == "true" ]]; then
        # Python module server
        cat > "$temp_config" << EOF
{
  "mcpServers": {
    "$server_name": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "$server_path"],
      "env": {}
    }
  }
}
EOF
    else
        # Executable server
        cat > "$temp_config" << EOF
{
  "mcpServers": {
    "$server_name": {
      "type": "stdio", 
      "command": "$server_path",
      "args": [],
      "env": {}
    }
  }
}
EOF
    fi
    
    echo "$temp_config"
}

# Discover tools from MCP server
discover_tools() {
    local config_file="$1"
    local server_name="$2"
    
    log "🔍 Discovering tools from server '$server_name'..."
    
    # Try Claude CLI tool discovery
    local tools_output
    if tools_output=$(timeout $((TIMEOUT/2)) claude --print \
        --dangerously-skip-permissions \
        --mcp-config "$config_file" \
        --strict-mcp-config \
        "List all available MCP tools with their descriptions" 2>/dev/null); then
        
        # Extract tool names from output
        local tools=($(echo "$tools_output" | grep -E "^[a-zA-Z_][a-zA-Z0-9_]*:" | cut -d: -f1 | sort -u))
        
        if [[ ${#tools[@]} -gt 0 ]]; then
            log "✅ Discovered ${#tools[@]} tools: ${tools[*]}"
            printf '%s\n' "${tools[@]}"
            return 0
        fi
    fi
    
    # Fallback: Try parsing Python source if available
    if [[ -f "$server_name" ]] && [[ "$server_name" == *.py ]]; then
        log "🔍 Fallback: Parsing Python source for @mcp.tool decorators..."
        local python_tools
        python_tools=$(grep -E "@mcp\.tool\(\)" "$server_name" -A 1 | grep "def " | sed 's/def \([^(]*\).*/\1/' | sort -u)
        
        if [[ -n "$python_tools" ]]; then
            log "✅ Found tools in source: $python_tools"
            echo "$python_tools"
            return 0
        fi
    fi
    
    log "⚠️  No tools discovered, will try generic test"
    return 1
}

# Load test patterns from JSON
load_test_patterns() {
    if [[ -f "$PATTERN_FILE" ]] && command -v jq >/dev/null 2>&1; then
        jq -r '.patterns | to_entries[] | "\(.key):\(.value)"' "$PATTERN_FILE"
    else
        # Fallback patterns if JSON file doesn't exist
        cat << 'EOF'
extract:Test with sample text: "Apple Inc. reported $45.3 billion in revenue with 15% growth. CEO Tim Cook said the results were strong."
list:List all available items
analyze:Analyze this data for insights and patterns
generate:Generate output based on the following input
save:Save this test data to output file
template:Show template details and usage examples
health:Check system health and status
EOF
    fi
}

# Generate test prompt for a tool
generate_test_prompt() {
    local tool_name="$1"
    local patterns
    patterns=$(load_test_patterns)
    
    # Match tool name against patterns
    local prompt=""
    while IFS=: read -r pattern description; do
        if [[ "$tool_name" == *"$pattern"* ]]; then
            prompt="$description"
            break
        fi
    done <<< "$patterns"
    
    # Default prompt if no pattern matches
    if [[ -z "$prompt" ]]; then
        prompt="Test the $tool_name functionality with sample data"
    fi
    
    echo "$prompt"
}

# Test individual tool
test_tool() {
    local tool_name="$1"
    local config_file="$2"
    local prompt
    prompt=$(generate_test_prompt "$tool_name")
    
    log "🧪 Testing $tool_name: \"$prompt\""
    
    local start_time=$(date +%s)
    local output
    local result=0
    
    if output=$(timeout $TIMEOUT claude --print \
        --dangerously-skip-permissions \
        --mcp-config "$config_file" \
        --strict-mcp-config \
        "Use the $tool_name tool to: $prompt" 2>&1); then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log "   ✅ PASS (${duration}s)"
        log "   Response: ${output:0:100}..."
        echo ""
        return 0
    else
        log "   ❌ FAIL - Error or timeout"
        log "   Error: ${output:0:100}..."
        echo ""
        return 1
    fi
}

# Clean up function
cleanup() {
    if [[ -n "${temp_config:-}" ]] && [[ -f "$temp_config" ]]; then
        rm -f "$temp_config"
    fi
}
trap cleanup EXIT

# Main execution
main() {
    parse_args "$@"
    
    log "🚀 Dynamic MCP Test - $SERVER_INPUT"
    
    local config_file=""
    local server_name=""
    
    # Determine configuration approach
    if existing_config=$(check_existing_config "$SERVER_INPUT"); then
        # Use existing configuration
        config_file="$existing_config"
        server_name="$SERVER_INPUT"
        log "📋 Using existing config: $config_file"
    else
        # Generate temporary configuration
        log "📋 Generating temporary config for: $SERVER_INPUT"
        
        # Validate server file exists if it's a path
        if [[ "$SERVER_INPUT" == *"/"* ]] || [[ "$SERVER_INPUT" == *.py ]]; then
            [[ -f "$SERVER_INPUT" ]] || error "Server file not found: $SERVER_INPUT"
            if [[ "$IS_MODULE" == "false" ]]; then
                [[ -x "$SERVER_INPUT" ]] || error "Server file not executable: $SERVER_INPUT"
            fi
        fi
        
        temp_config=$(generate_temp_config "$SERVER_INPUT")
        config_file="$temp_config"
        server_name=$(basename "$SERVER_INPUT" .py | sed 's/_mcp_server$//' | sed 's/_server$//')
    fi
    
    # Discover tools
    local tools=()
    if discovered_tools=$(discover_tools "$config_file" "$server_name"); then
        readarray -t tools <<< "$discovered_tools"
    else
        log "⚠️  Tool discovery failed, using generic test"
        tools=("generic_test")
    fi
    
    if [[ "$LIST_ONLY" == "true" ]]; then
        log "📋 Discovered tools:"
        printf '  - %s\n' "${tools[@]}"
        exit 0
    fi
    
    # Test tools
    echo ""
    log "🧪 TESTING TOOLS"
    echo "=================="
    
    local pass_count=0
    local total_tests=0
    
    for tool in "${tools[@]}"; do
        [[ -z "$tool" ]] && continue
        
        if test_tool "$tool" "$config_file"; then
            ((pass_count++))
        fi
        ((total_tests++))
    done
    
    # Summary
    echo ""
    log "📊 SUMMARY"
    log "=========================================="
    log "Server: $SERVER_INPUT"
    log "Tools Discovered: ${#tools[@]}"
    log "Tests: $pass_count/$total_tests passed"
    
    if [[ "$pass_count" -eq "$total_tests" ]]; then
        log "Status: ✅ ALL TESTS PASSED"
        exit 0
    else
        log "Status: ❌ SOME TESTS FAILED"
        exit 1
    fi
    log "=========================================="
}

main "$@"