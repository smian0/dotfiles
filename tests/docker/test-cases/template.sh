#!/usr/bin/env bash
# Test Template
# Description: [Describe what this test does]
# Category: [quick|unit|integration|e2e|stress]
# Expected Duration: [time estimate]

set -euo pipefail

# Test configuration
TEST_NAME="Template Test"
TEST_DESCRIPTION="Template for creating new tests"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() { echo -e "${BLUE}[${TEST_NAME}]${NC} $1"; }
success() { echo -e "${GREEN}✅ [${TEST_NAME}]${NC} $1"; }
error() { echo -e "${RED}❌ [${TEST_NAME}]${NC} $1"; }

# Cleanup function
cleanup() {
    local exit_code=$?
    log "Cleaning up test environment..."
    
    # Add cleanup logic here
    # rm -f /tmp/test-files
    # docker stop test-containers 2>/dev/null || true
    
    if [[ $exit_code -eq 0 ]]; then
        success "Test completed successfully"
    else
        error "Test failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up cleanup trap
trap cleanup EXIT

# Main test function
run_test() {
    log "Starting $TEST_DESCRIPTION..."
    
    # =================================================================
    # Test Setup
    # =================================================================
    log "Setting up test environment..."
    
    # Add setup logic here
    # mkdir -p /tmp/test-dir
    # export TEST_VAR="value"
    
    # =================================================================
    # Test Execution
    # =================================================================
    log "Executing test cases..."
    
    # Test Case 1: Basic validation
    log "Test Case 1: Basic validation"
    if [[ -f "Makefile" ]]; then
        success "Makefile exists"
    else
        error "Makefile not found"
        return 1
    fi
    
    # Test Case 2: Command execution
    log "Test Case 2: Command execution"
    if make help >/dev/null 2>&1; then
        success "make help command works"
    else
        error "make help command failed"
        return 1
    fi
    
    # Test Case 3: Custom validation
    log "Test Case 3: Custom validation"
    # Add your custom test logic here
    # if some_condition; then
    #     success "Custom test passed"
    # else
    #     error "Custom test failed"
    #     return 1
    # fi
    
    # =================================================================
    # Test Verification
    # =================================================================
    log "Verifying test results..."
    
    # Add verification logic here
    # Check files were created, services are running, etc.
    
    success "All test cases passed!"
}

# =================================================================
# Script Entry Point
# =================================================================

# Check prerequisites
if [[ ! -f "Makefile" ]]; then
    error "This test must be run from the dotfiles root directory"
    exit 1
fi

# Run the test
log "Starting ${TEST_NAME}..."
run_test
log "Test completed successfully!"

# Note: cleanup() will be called automatically via trap