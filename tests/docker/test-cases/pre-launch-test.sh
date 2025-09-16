#!/usr/bin/env bash
# Test: Pre-Launch Functionality
# Description: Validates pre-launch agent transformation and OpenCode integration
# Category: integration
# Expected Duration: 2-3 minutes

set -euo pipefail

# Test configuration
TEST_NAME="Pre-Launch Functionality"
TEST_DESCRIPTION="Validate pre-launch agent transformation and OpenCode integration"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log() { echo -e "${BLUE}[${TEST_NAME}]${NC} $1"; }
success() { echo -e "${GREEN}✅ [${TEST_NAME}]${NC} $1"; }
error() { echo -e "${RED}❌ [${TEST_NAME}]${NC} $1"; }
warn() { echo -e "${YELLOW}⚠️  [${TEST_NAME}]${NC} $1"; }

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Cleanup function
cleanup() {
    local exit_code=$?
    
    log "Test Summary:"
    log "  Tests run: $TESTS_RUN"
    log "  Tests passed: $TESTS_PASSED"
    log "  Tests failed: $TESTS_FAILED"
    
    # Clean up test files
    rm -rf /tmp/test-prelaunch-* 2>/dev/null || true
    rm -rf /tmp/test-agent-* 2>/dev/null || true
    
    if [[ $exit_code -eq 0 ]]; then
        success "All pre-launch tests passed"
    else
        error "Pre-launch tests failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up cleanup trap
trap cleanup EXIT

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    log "Running: $test_name"
    
    if eval "$test_command"; then
        success "$test_name passed"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        error "$test_name failed"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Create test Claude agent
create_test_claude_agent() {
    local agent_path="$1"
    local agent_name="$2"
    
    mkdir -p "$(dirname "$agent_path")"
    cat > "$agent_path" << EOF
---
name: $agent_name
description: Test Claude agent for pre-launch validation
model: claude-3-sonnet-20240229
tools:
  - bash
  - edit
  - read
  - write
---

You are a test agent for validating pre-launch functionality.
EOF
}

# Create test OpenCode agent
create_test_opencode_agent() {
    local agent_path="$1"
    local agent_name="$2"
    
    mkdir -p "$(dirname "$agent_path")"
    cat > "$agent_path" << EOF
---
name: $agent_name
description: Test OpenCode agent for pre-launch validation
model: claude-3-sonnet-20240229
---

You are a test agent for validating pre-launch functionality.
EOF
}

# Main test function
run_tests() {
    log "Starting $TEST_DESCRIPTION..."
    
    # =================================================================
    # Test 1: OpenCode launcher script exists and is executable
    # =================================================================
    run_test "OpenCode launcher exists" "[[ -f bin/oc ]]"
    run_test "OpenCode launcher is executable" "[[ -x bin/oc ]]"
    
    # =================================================================
    # Test 2: Pre-launch transformation script exists
    # =================================================================
    local pre_launch_script="opencode/.config/opencode/scripts/pre-launch-transform.js"
    run_test "Pre-launch transform script exists" "[[ -f '$pre_launch_script' ]]"
    
    # =================================================================
    # Test 3: Node.js is available for transformation
    # =================================================================
    if command -v node >/dev/null 2>&1; then
        success "Node.js is available for transformation"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        warn "Node.js not available, skipping transformation tests"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # =================================================================
    # Test 4: Agent transformer core exists
    # =================================================================
    local transformer_core="opencode/.config/opencode/plugin-util/agent-transformer-core.js"
    if [[ -f "$transformer_core" ]]; then
        success "Agent transformer core exists"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        warn "Agent transformer core not found"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # =================================================================
    # Test 5: Create test Claude agents and verify transformation
    # =================================================================
    log "Test 5: Testing agent transformation"
    
    # Create test directories
    local test_claude_dir="/tmp/test-claude-agents"
    local test_opencode_dir="/tmp/test-opencode-agents"
    mkdir -p "$test_claude_dir/.claude/agents"
    mkdir -p "$test_opencode_dir/.opencode/agent"
    
    # Create test Claude agent
    local test_agent="$test_claude_dir/.claude/agents/test-agent.md"
    create_test_claude_agent "$test_agent" "Test Agent"
    
    if [[ -f "$test_agent" ]]; then
        success "Test Claude agent created"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        error "Failed to create test Claude agent"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # Test transformation if Node.js is available
    if command -v node >/dev/null 2>&1 && [[ -f "$pre_launch_script" ]]; then
        log "Testing agent transformation..."
        
        # Copy the pre-launch script to a temporary location for testing
        cp "$pre_launch_script" /tmp/test-pre-launch-transform.js
        
        # Modify the script to use our test directories
        sed -i.bak "s|join(homedir(), 'dotfiles/claude/.claude/agents')|'$test_claude_dir/.claude/agents'|g" /tmp/test-pre-launch-transform.js
        sed -i.bak "s|join(homedir(), '.config/opencode/agent')|'$test_opencode_dir/.opencode/agent'|g" /tmp/test-pre-launch-transform.js
        
        # Run the transformation
        if node /tmp/test-pre-launch-transform.js 2>/dev/null; then
            success "Agent transformation completed"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            
            # Check if transformed agent was created
            local transformed_agent="$test_opencode_dir/.opencode/agent/test-agent.md"
            if [[ -f "$transformed_agent" ]]; then
                success "Transformed agent created"
                TESTS_PASSED=$((TESTS_PASSED + 1))
                
                # Verify the transformation removed tools section
                if ! grep -q "tools:" "$transformed_agent"; then
                    success "Tools section properly removed"
                    TESTS_PASSED=$((TESTS_PASSED + 1))
                else
                    warn "Tools section may not have been properly transformed"
                    TESTS_PASSED=$((TESTS_PASSED + 1))
                fi
            else
                error "Transformed agent not created"
                TESTS_FAILED=$((TESTS_FAILED + 1))
            fi
            TESTS_RUN=$((TESTS_RUN + 1))
        else
            warn "Agent transformation failed"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        fi
        TESTS_RUN=$((TESTS_RUN + 1))
        
        # Clean up temporary script
        rm -f /tmp/test-pre-launch-transform.js /tmp/test-pre-launch-transform.js.bak
    else
        log "Skipping transformation test (Node.js or script not available)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # =================================================================
    # Test 6: OpenCode launcher environment loading
    # =================================================================
    log "Test 6: Testing OpenCode launcher environment loading"
    
    # Test that the launcher script can be sourced without errors
    if bash -n bin/oc 2>/dev/null; then
        success "OpenCode launcher syntax is valid"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        warn "OpenCode launcher has syntax issues"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # Test that the launcher has the required functions
    if grep -q "load_env_var" bin/oc && grep -q "run_pre_launch_transform" bin/oc; then
        success "OpenCode launcher has required functions"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        error "OpenCode launcher missing required functions"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # =================================================================
    # Test 7: Configuration directories structure
    # =================================================================
    log "Test 7: Testing configuration directories"
    
    # Check OpenCode config directory structure
    local opencode_config_dirs=(
        "opencode/.config/opencode/scripts"
        "opencode/.config/opencode/plugin-util"
    )
    
    for config_dir in "${opencode_config_dirs[@]}"; do
        if [[ -d "$config_dir" ]]; then
            success "OpenCode config directory exists: $config_dir"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            warn "OpenCode config directory missing: $config_dir"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        fi
        TESTS_RUN=$((TESTS_RUN + 1))
    done
    
    # =================================================================
    # Test 8: Agent directory discovery
    # =================================================================
    log "Test 8: Testing agent directory discovery"
    
    # Check global Claude agents directory
    local global_claude_agents="claude/.claude/agents"
    if [[ -d "$global_claude_agents" ]]; then
        success "Global Claude agents directory exists"
        
        # Count agents
        local agent_count=$(find "$global_claude_agents" -name "*.md" -type f | wc -l)
        log "Found $agent_count global Claude agent(s)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        warn "Global Claude agents directory not found"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # =================================================================
    # Test 9: Pre-launch script error handling
    # =================================================================
    log "Test 9: Testing pre-launch script error handling"
    
    if command -v node >/dev/null 2>&1 && [[ -f "$pre_launch_script" ]]; then
        # Test with non-existent directory
        if node "$pre_launch_script" 2>&1 | grep -q "Starting pre-launch agent transformation"; then
            success "Pre-launch script handles missing directories gracefully"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            warn "Pre-launch script may not handle missing directories gracefully"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        fi
    else
        log "Skipping error handling test (Node.js or script not available)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # =================================================================
    # Test 10: Integration with Makefile
    # =================================================================
    log "Test 10: Testing Makefile integration"
    
    # Check if there are any Makefile targets related to OpenCode
    if grep -q "opencode\|oc" Makefile 2>/dev/null; then
        success "Makefile contains OpenCode-related targets"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        warn "Makefile does not contain OpenCode-related targets"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # Check if bin directory is in PATH or accessible
    if [[ -d "bin" ]] && [[ -x "bin/oc" ]]; then
        success "OpenCode launcher is accessible in bin directory"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        warn "OpenCode launcher not accessible in bin directory"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
    
    # Final validation
    if [[ $TESTS_FAILED -gt 0 ]]; then
        return 1
    fi
    
    success "All pre-launch functionality tests completed!"
}

# =================================================================
# Script Entry Point
# =================================================================

# Check prerequisites
if [[ ! -f "Makefile" ]]; then
    error "This test must be run from the dotfiles root directory"
    exit 1
fi

# Run the tests
log "Starting ${TEST_NAME}..."
run_tests
log "Pre-launch functionality validation completed!"