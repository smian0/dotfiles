#!/usr/bin/env bash
# Test: Makefile Validation
# Description: Validates Makefile structure and command availability
# Category: quick
# Expected Duration: 10 seconds

set -euo pipefail

# Test configuration
TEST_NAME="Makefile Validation"
TEST_DESCRIPTION="Validate Makefile structure and commands"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() { echo -e "${BLUE}[${TEST_NAME}]${NC} $1"; }
success() { echo -e "${GREEN}✅ [${TEST_NAME}]${NC} $1"; }
error() { echo -e "${RED}❌ [${TEST_NAME}]${NC} $1"; }

# Expected commands that should exist
EXPECTED_COMMANDS=(
    "help"
    "install"
    "backup"
    "restore"
    "status"
    "test"
    "docs"
    "bootstrap"
)

# Cleanup function
cleanup() {
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        success "All Makefile validation tests passed"
    else
        error "Makefile validation failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up cleanup trap
trap cleanup EXIT

# Main test function
run_test() {
    log "Starting $TEST_DESCRIPTION..."
    
    # =================================================================
    # Test 1: Makefile exists and is readable
    # =================================================================
    log "Test 1: Makefile existence and readability"
    if [[ -f "Makefile" && -r "Makefile" ]]; then
        success "Makefile exists and is readable"
    else
        error "Makefile not found or not readable"
        return 1
    fi
    
    # =================================================================
    # Test 2: Help command works
    # =================================================================
    log "Test 2: Help command functionality"
    if make help >/dev/null 2>&1; then
        success "make help command works"
    else
        error "make help command failed"
        return 1
    fi
    
    # =================================================================
    # Test 3: Expected commands are available
    # =================================================================
    log "Test 3: Expected commands availability"
    local help_output
    help_output=$(make help 2>/dev/null)
    
    for cmd in "${EXPECTED_COMMANDS[@]}"; do
        if echo "$help_output" | grep -q "$cmd"; then
            success "Command '$cmd' is available"
        else
            error "Command '$cmd' is missing from help output"
            return 1
        fi
    done
    
    # =================================================================
    # Test 4: Documentation commands work
    # =================================================================
    log "Test 4: Documentation commands"
    if make docs-check >/dev/null 2>&1; then
        success "make docs-check works"
    else
        error "make docs-check failed"
        return 1
    fi
    
    # =================================================================
    # Test 5: Validate Makefile syntax
    # =================================================================
    log "Test 5: Makefile syntax validation"
    if make -n help >/dev/null 2>&1; then
        success "Makefile syntax is valid"
    else
        error "Makefile has syntax errors"
        return 1
    fi
    
    # =================================================================
    # Test 6: Check for grouped commands
    # =================================================================
    log "Test 6: Grouped command structure"
    if echo "$help_output" | grep -q "📦 End User Commands"; then
        success "End User Commands group found"
    else
        error "End User Commands group missing"
        return 1
    fi
    
    if echo "$help_output" | grep -q "Developer Commands"; then
        success "Developer Commands group found"
    else
        error "Developer Commands group missing"
        return 1
    fi
    
    success "All Makefile validation tests completed!"
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
log "Makefile validation completed successfully!"