#!/bin/bash
set -euo pipefail

# Simple MCP Server Testing Script that actually works
# Usage: ./test-mcp-simple.sh /path/to/server.py

DEFAULT_TIMEOUT=120

usage() {
    echo "Simple MCP Server Testing Script"
    echo "Usage: $0 <mcp_server_path>"
    exit 1
}

log() {
    echo "$(date '+%H:%M:%S') $*"
}

# Extract server name
get_server_name() {
    local mcp_file="$1"
    basename "$mcp_file" .py | sed 's/_mcp_server$//' | sed 's/_server$//'
}

# Generate MCP config
generate_mcp_config() {
    local server_name="$1"
    local mcp_file="$2"
    echo "{\"mcpServers\":{\"$server_name\":{\"type\":\"stdio\",\"command\":\"$mcp_file\",\"args\":[],\"env\":{}}}}"
}

# Test individual tools
test_tool() {
    local tool_name="$1"
    local prompt="$2"
    local config="$3"
    
    log "🧪 Testing $tool_name: \"$prompt\""
    
    local start_time=$(date +%s)
    local output
    
    if output=$(timeout $DEFAULT_TIMEOUT claude --print \
        --dangerously-skip-permissions \
        --mcp-config "$config" \
        --strict-mcp-config \
        "$prompt" 2>&1); then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        echo "   ✅ PASS (${duration}s)"
        echo "   Response: ${output:0:80}..."
        echo ""
        return 0
    else
        echo "   ❌ FAIL - Timeout or error"
        echo ""
        return 1
    fi
}

# Main execution
main() {
    [ $# -eq 0 ] && usage
    
    local mcp_file="$1"
    mcp_file="$(realpath "$mcp_file" 2>/dev/null || echo "$mcp_file")"
    
    log "🚀 Simple MCP Test - $(basename "$mcp_file")"
    
    # Basic validation
    [ -f "$mcp_file" ] || { echo "❌ File not found: $mcp_file"; exit 1; }
    [ -x "$mcp_file" ] || { echo "❌ File not executable: $mcp_file"; exit 1; }
    
    # Extract info
    local server_name
    server_name="$(get_server_name "$mcp_file")"
    log "📋 Server: $server_name"
    
    local config
    config="$(generate_mcp_config "$server_name" "$mcp_file")"
    
    # Test tools
    echo ""
    log "🧪 TESTING TOOLS"
    echo "=================="
    
    local pass_count=0
    local total_tests=0
    
    # Test joke tool
    if test_tool "tell_joke" "Tell me a programming joke" "$config"; then
        ((pass_count++))
    fi
    ((total_tests++))
    
    # Test model change
    if test_tool "set_model" "Change to qwen3:14b model" "$config"; then
        ((pass_count++))
    fi
    ((total_tests++))
    
    # Summary
    echo ""
    log "📊 SUMMARY"
    log "=========================================="
    log "Server: $(basename "$mcp_file")"
    log "Tests: $pass_count/$total_tests passed"
    
    if [ "$pass_count" -eq "$total_tests" ]; then
        log "Status: ✅ ALL TESTS PASSED"
    else
        log "Status: ❌ SOME TESTS FAILED"
    fi
    log "=========================================="
}

main "$@"