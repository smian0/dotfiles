#!/bin/zsh
# =============================================================================
# AGENTS.md Functionality Test Suite
# =============================================================================
# Tests the automatic symlinking and migration features for AGENTS.md standard
# 
# Usage: zsh tests/agents-md-test.zsh
# =============================================================================

echo "========================================="
echo "AGENTS.md Functionality Test Suite"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create timestamped test run directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_RUN_DIR="$HOME/dotfiles/tests/test-runs/agents-md-${TIMESTAMP}"
mkdir -p "$TEST_RUN_DIR"

echo "${BLUE}Test Run Directory:${NC} $TEST_RUN_DIR"
echo ""

# Source the agents-md.zsh file
echo "Loading agents-md.zsh..."
source ~/dotfiles/zsh/agents-md.zsh

# Test results tracking
PASSED=0
FAILED=0

# Function to check test result
check_result() {
    if [[ $1 -eq 0 ]]; then
        echo "${GREEN}✓${NC} $2"
        ((PASSED++))
        return 0
    else
        echo "${RED}✗${NC} $2"
        ((FAILED++))
        return 1
    fi
}

# Test 1: Check if functions are loaded
echo ""
echo "Test 1: Checking if functions are loaded"
echo "-----------------------------------------"

type agents-init &>/dev/null
check_result $? "agents-init function loaded"

type agents-status &>/dev/null
check_result $? "agents-status function loaded"

type agents-sync &>/dev/null
check_result $? "agents-sync function loaded"

type _check_and_link_agents &>/dev/null
check_result $? "_check_and_link_agents function loaded"

# Test 2: Testing CLAUDE.md migration
echo ""
echo "Test 2: Testing CLAUDE.md migration"
echo "------------------------------------"

# Create test directory
TEST_DIR1="$TEST_RUN_DIR/test-migration"
mkdir -p "$TEST_DIR1"
cd "$TEST_DIR1"

echo "Test directory: $TEST_DIR1"

# Create CLAUDE.md with test content
cat > CLAUDE.md << 'EOF'
# Test CLAUDE Configuration

This is a test CLAUDE.md file with:
- Multiple lines
- Original content
- That should be preserved
EOF

echo "Created CLAUDE.md file"

# Simulate entering directory (trigger hook)
echo "Simulating directory entry..."
_check_and_link_agents

# Run agents-init
echo "Running agents-init..."
agents-init

# Check results
[[ -f AGENTS.md ]]
check_result $? "AGENTS.md created"

[[ -L CLAUDE.md ]]
check_result $? "CLAUDE.md is now a symlink"

if [[ -L CLAUDE.md ]]; then
    target=$(readlink CLAUDE.md)
    [[ "$target" == "AGENTS.md" ]]
    check_result $? "CLAUDE.md points to AGENTS.md"
fi

# Check content preservation
grep -q "Original content" AGENTS.md 2>/dev/null
check_result $? "Original content preserved in AGENTS.md"

grep -q "Multiple lines" AGENTS.md 2>/dev/null
check_result $? "Multi-line content preserved"

# Test 3: Testing auto-symlinking with AGENTS.md
echo ""
echo "Test 3: Testing auto-symlinking"
echo "--------------------------------"

# Create new test directory
TEST_DIR2="$TEST_RUN_DIR/test-autosymlink"
mkdir -p "$TEST_DIR2"
cd "$TEST_DIR2"

echo "Test directory: $TEST_DIR2"

# Create AGENTS.md
cat > AGENTS.md << 'EOF'
# Test AGENTS Configuration

Standard AGENTS.md content for testing auto-symlinking.

## Features
- Auto-creates CLAUDE.md symlink
- Maintains compatibility
EOF

echo "Created AGENTS.md file"

# Trigger auto-linking
echo "Triggering auto-linking..."
_check_and_link_agents

# Check if symlink was created
[[ -L CLAUDE.md ]]
check_result $? "CLAUDE.md symlink auto-created"

if [[ -L CLAUDE.md ]]; then
    [[ "$(readlink CLAUDE.md)" == "AGENTS.md" ]]
    check_result $? "Symlink points correctly to AGENTS.md"
fi

# Verify content is accessible through symlink
grep -q "Auto-creates CLAUDE.md symlink" CLAUDE.md 2>/dev/null
check_result $? "Content accessible through CLAUDE.md symlink"

# Test 4: Testing agents-status
echo ""
echo "Test 4: Testing agents-status"
echo "------------------------------"

cd "$TEST_DIR2"
agents-status > "$TEST_RUN_DIR/status-output.txt" 2>&1
check_result $? "agents-status command executed"

grep -q "AGENTS.md exists" "$TEST_RUN_DIR/status-output.txt"
check_result $? "Status correctly identifies AGENTS.md"

# Test 5: Testing agents-sync
echo ""
echo "Test 5: Testing agents-sync"
echo "---------------------------"

cd "$TEST_DIR2"

# Remove symlink
rm -f CLAUDE.md
echo "Removed CLAUDE.md symlink"

# Run sync
agents-sync

[[ -L CLAUDE.md ]]
check_result $? "agents-sync recreated symlink"

# Test 6: Testing conflict detection
echo ""
echo "Test 6: Testing conflict detection"
echo "-----------------------------------"

TEST_DIR3="$TEST_RUN_DIR/test-conflict"
mkdir -p "$TEST_DIR3"
cd "$TEST_DIR3"

echo "Test directory: $TEST_DIR3"

# Create both files as regular files
echo "# AGENTS content" > AGENTS.md
echo "# CLAUDE content" > CLAUDE.md

echo "Created both AGENTS.md and CLAUDE.md as regular files"

# Capture output
_check_and_link_agents > "$TEST_RUN_DIR/conflict-output.txt" 2>&1

# Check if conflict was detected (should show message in interactive mode)
agents-status > "$TEST_RUN_DIR/conflict-status.txt" 2>&1
grep -q "separate file" "$TEST_RUN_DIR/conflict-status.txt"
check_result $? "Conflict detection working"

# Test 7: Testing template creation
echo ""
echo "Test 7: Testing template creation"
echo "----------------------------------"

TEST_DIR4="$TEST_RUN_DIR/test-template"
mkdir -p "$TEST_DIR4"
cd "$TEST_DIR4"

echo "Test directory: $TEST_DIR4"

# Run agents-init in empty directory
agents-init

[[ -f AGENTS.md ]]
check_result $? "AGENTS.md template created"

[[ -L CLAUDE.md ]]
check_result $? "CLAUDE.md symlink created with template"

grep -q "Project Overview" AGENTS.md
check_result $? "Template contains expected sections"

# Test 8: Testing non-interactive mode (no messages)
echo ""
echo "Test 8: Testing non-interactive mode"
echo "-------------------------------------"

TEST_DIR5="$TEST_RUN_DIR/test-noninteractive"
mkdir -p "$TEST_DIR5"
cd "$TEST_DIR5"

echo "# Test" > AGENTS.md

# Run in non-interactive mode (simulated)
output=$(zsh -c "source ~/dotfiles/zsh/agents-md.zsh && cd $TEST_DIR5 && _check_and_link_agents" 2>&1)

# Should create symlink but no output
[[ -L CLAUDE.md ]]
check_result $? "Symlink created in non-interactive mode"

[[ -z "$output" ]]
check_result $? "No output in non-interactive mode"

# Summary
echo ""
echo "========================================="
echo "Test Suite Complete"
echo "========================================="
echo ""
echo "${GREEN}Passed:${NC} $PASSED"
echo "${RED}Failed:${NC} $FAILED"
echo ""
echo "${BLUE}Test artifacts saved in:${NC}"
echo "$TEST_RUN_DIR"
echo ""
echo "Directory contents:"
ls -la "$TEST_RUN_DIR"
echo ""
echo "Test directories created:"
find "$TEST_RUN_DIR" -type d -name "test-*" | while read dir; do
    echo "  $(basename $dir):"
    ls -la "$dir" | grep -E "AGENTS|CLAUDE" | sed 's/^/    /'
done

# Return exit code based on failures
if [[ $FAILED -eq 0 ]]; then
    echo ""
    echo "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo ""
    echo "${RED}Some tests failed.${NC}"
    exit 1
fi