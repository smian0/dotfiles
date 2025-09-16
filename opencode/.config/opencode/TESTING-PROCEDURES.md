# OpenCode Agent Transformation - Testing Procedures

## Overview

This document provides comprehensive testing procedures for the OpenCode agent transformation system, covering both `oc` binary wrapper and `opencode` shell function approaches.

## Test Environment Setup

### Prerequisites

```bash
# Ensure required components exist
ls -la bin/oc                                    # Original binary wrapper
ls -la ~/.local/bin/opencode                     # Universal binary wrapper  
ls -la opencode/.config/opencode/scripts/pre-launch-transform.js
type opencode                                     # Should show shell function

# Ensure test agent exists
ls -la claude/.claude/agents/claude-test-agent.md
```

### Test Data Preparation

```bash
# Create clean test environment
rm -rf ~/.config/opencode/agent/*.md             # Remove transformed files
touch claude/.claude/agents/claude-test-agent.md # Update timestamp
```

## Unit Tests

### 1. Core Transformation Logic Test

**Purpose**: Verify the transformation logic works correctly

```bash
# Test transformation script directly
cd opencode/.config/opencode
node tests/test-agent-transformer.js

# Expected output:
# ✅ PASS - Agent should work in OpenCode
# 📊 AUDIT SUMMARY: Size change: 259 → 191 chars (-68)
```

**Success Criteria**:
- [ ] Transformation completes without errors
- [ ] Output matches expected OpenCode format
- [ ] Content is preserved (agent instructions intact)
- [ ] File size reduction due to removed fields

### 2. Pre-Launch Transformation Test

**Purpose**: Verify the pre-launch script works independently

```bash
# Test pre-launch script directly
rm ~/.config/opencode/agent/*.md
node opencode/.config/opencode/scripts/pre-launch-transform.js

# Expected output:
# [Pre-Launch Transform] ✅ Transformed claude-test-agent.md
# [Pre-Launch Transform] Pre-launch transformation complete ✅

# Verify files created
ls -la ~/.config/opencode/agent/
# Should show: claude-test-agent.md
```

**Success Criteria**:
- [ ] Script runs without errors
- [ ] Transformed files created in target directory
- [ ] Transformed files have correct OpenCode format
- [ ] Script skips transformation when target is newer

### 3. Plugin System Test

**Purpose**: Verify OpenCode loads plugins correctly

```bash
# Test plugin loading (check logs)
opencode run --agent claude-test-agent "test plugins" 2>&1 | grep -E "(Plugin|Agent Transformer)"

# Expected output includes:
# [Agent Transformer] Patching filesystem at module load time
# [Agent Transformer] Plugin initializing
```

**Success Criteria**:
- [ ] Agent transformer plugin loads
- [ ] Filesystem patching activates
- [ ] Agent detection works
- [ ] No plugin loading errors

## Integration Tests

### 4. Binary Wrapper Test (`oc` command)

**Purpose**: Test the original `oc` binary wrapper end-to-end

```bash
# Clean environment
rm ~/.config/opencode/agent/*.md

# Test oc wrapper
./bin/oc run --agent claude-test-agent "Test oc wrapper functionality"

# Verify transformation occurred
ls -la ~/.config/opencode/agent/claude-test-agent.md
# Should exist with recent timestamp
```

**Success Criteria**:
- [ ] Pre-launch transformation runs automatically
- [ ] Agent loads successfully in OpenCode
- [ ] Agent responds correctly to prompt
- [ ] Transformed file created on disk

### 5. Shell Function Test (`opencode` command)

**Purpose**: Test the shell function wrapper end-to-end

```bash
# Clean environment
rm ~/.config/opencode/agent/*.md

# Test shell function (requires shell reload if recently added)
exec zsh  # Reload shell to ensure function is active
opencode run --agent claude-test-agent "Test shell function wrapper"

# Verify transformation occurred
ls -la ~/.config/opencode/agent/claude-test-agent.md
# Should exist with recent timestamp
```

**Success Criteria**:
- [ ] Shell function calls binary wrapper
- [ ] Pre-launch transformation runs automatically  
- [ ] Agent loads successfully in OpenCode
- [ ] Agent responds correctly to prompt
- [ ] Transformed file created on disk

### 6. Universal Coverage Test

**Purpose**: Verify both commands produce identical results

```bash
# Test both commands with same prompt
rm ~/.config/opencode/agent/*.md
./bin/oc run --agent claude-test-agent "Test message" > oc_output.txt 2>&1 &
OC_PID=$!

rm ~/.config/opencode/agent/*.md  
opencode run --agent claude-test-agent "Test message" > opencode_output.txt 2>&1 &
OPENCODE_PID=$!

# Wait for both to complete
wait $OC_PID $OPENCODE_PID

# Compare outputs (should be very similar, minor differences in timing/logs okay)
echo "=== OC OUTPUT ==="
cat oc_output.txt
echo -e "\n=== OPENCODE OUTPUT ==="
cat opencode_output.txt

# Cleanup
rm oc_output.txt opencode_output.txt
```

**Success Criteria**:
- [ ] Both commands complete successfully
- [ ] Both produce similar transformation logs
- [ ] Both agents respond appropriately
- [ ] No significant differences in behavior

## Performance Tests

### 7. Transformation Speed Test

**Purpose**: Measure transformation performance

```bash
# Time pre-launch transformation
rm ~/.config/opencode/agent/*.md
time node opencode/.config/opencode/scripts/pre-launch-transform.js

# Expected: < 1 second for single agent
```

**Success Criteria**:
- [ ] Transformation completes in under 1 second
- [ ] Memory usage remains reasonable
- [ ] No performance degradation with multiple agents

### 8. Caching Efficiency Test

**Purpose**: Verify smart caching works

```bash
# First transformation (should transform)
rm ~/.config/opencode/agent/*.md
node opencode/.config/opencode/scripts/pre-launch-transform.js | grep "Transformed"
# Should show: ✅ Transformed claude-test-agent.md

# Second transformation (should skip due to caching)
node opencode/.config/opencode/scripts/pre-launch-transform.js | grep "Skipping"
# Should show: Skipping claude-test-agent.md (target is up-to-date)

# Force re-transformation by updating source
touch claude/.claude/agents/claude-test-agent.md
node opencode/.config/opencode/scripts/pre-launch-transform.js | grep "Transformed"
# Should show: ✅ Transformed claude-test-agent.md
```

**Success Criteria**:
- [ ] Initial transformation creates files
- [ ] Subsequent runs skip transformation (caching works)
- [ ] Source file updates trigger re-transformation
- [ ] Caching logic is correct

## Error Handling Tests

### 9. Missing Agent Test

**Purpose**: Test behavior with non-existent agents

```bash
# Test with non-existent agent
./bin/oc run --agent non-existent-agent "test"
opencode run --agent non-existent-agent "test"

# Both should fail gracefully with clear error messages
```

**Success Criteria**:
- [ ] Clear error message about missing agent
- [ ] No system crashes or hangs
- [ ] Graceful failure behavior

### 10. Malformed Agent Test

**Purpose**: Test behavior with invalid agent files

```bash
# Create malformed agent file
cat > claude/.claude/agents/malformed-agent.md << 'EOF'
This is not valid frontmatter
No YAML headers
Just plain text
EOF

# Test transformation handling
rm ~/.config/opencode/agent/*.md
node opencode/.config/opencode/scripts/pre-launch-transform.js

# Should handle gracefully, possibly skip malformed file
```

**Success Criteria**:
- [ ] Malformed files don't crash transformation
- [ ] Error logging is clear and helpful
- [ ] Valid files still transform correctly

### 11. Permission Test

**Purpose**: Test behavior with permission issues

```bash
# Create permission issue
chmod 000 ~/.config/opencode/agent 2>/dev/null || true

# Test transformation with permission problem
node opencode/.config/opencode/scripts/pre-launch-transform.js

# Restore permissions
chmod 755 ~/.config/opencode/agent
```

**Success Criteria**:
- [ ] Permission errors are caught and logged
- [ ] System doesn't crash on permission issues
- [ ] Clear error messages for debugging

## Regression Tests

### 12. Backward Compatibility Test

**Purpose**: Ensure existing functionality still works

```bash
# Test original oc functionality (should be unchanged)
./bin/oc --version
./bin/oc --help
./bin/oc run --agent claude-test-agent "backward compatibility test"

# All should work exactly as before
```

**Success Criteria**:
- [ ] All original `oc` functionality preserved
- [ ] No breaking changes to existing workflows
- [ ] Consistent behavior with previous versions

### 13. Environment Variable Test

**Purpose**: Test environment variable loading

```bash
# Test environment variable loading
DEBUG_MODE=true ./bin/oc --version 2>&1 | grep "Loaded.*API_KEY"
DEBUG_MODE=true opencode --version 2>&1 | grep "Loaded.*API_KEY"

# Should show API key loading logs
```

**Success Criteria**:
- [ ] Environment variables load correctly
- [ ] API keys are loaded from launchctl
- [ ] Debug mode shows loading information

## Automated Test Suite

### Complete Test Runner

```bash
#!/bin/bash
# run-all-tests.sh - Comprehensive test suite

set -e

FAILED_TESTS=()
PASSED_TESTS=()

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo "🧪 Running: $test_name"
    
    if eval "$test_command"; then
        PASSED_TESTS+=("$test_name")
        echo "✅ PASSED: $test_name"
    else
        FAILED_TESTS+=("$test_name")
        echo "❌ FAILED: $test_name"
    fi
    echo ""
}

# Run all tests
run_test "Core Transformation Logic" "cd opencode/.config/opencode && node tests/test-agent-transformer.js >/dev/null"

run_test "Pre-Launch Script" "rm -f ~/.config/opencode/agent/*.md && node opencode/.config/opencode/scripts/pre-launch-transform.js >/dev/null"

run_test "OC Binary Wrapper" "rm -f ~/.config/opencode/agent/*.md && timeout 30s ./bin/oc run --agent claude-test-agent 'test' >/dev/null 2>&1"

run_test "Shell Function Wrapper" "rm -f ~/.config/opencode/agent/*.md && timeout 30s opencode run --agent claude-test-agent 'test' >/dev/null 2>&1"

run_test "Caching Logic" "node opencode/.config/opencode/scripts/pre-launch-transform.js 2>&1 | grep -q 'Skipping.*up-to-date'"

run_test "Environment Loading" "DEBUG_MODE=true ./bin/oc --version 2>&1 | grep -q 'Loaded.*API_KEY'"

# Summary
echo "========================================"
echo "TEST SUMMARY"
echo "========================================"
echo "✅ PASSED: ${#PASSED_TESTS[@]} tests"
echo "❌ FAILED: ${#FAILED_TESTS[@]} tests"

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo ""
    echo "Failed tests:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  - $test"
    done
    exit 1
else
    echo ""
    echo "🎉 All tests passed!"
    exit 0
fi
```

**Usage**:
```bash
chmod +x run-all-tests.sh
./run-all-tests.sh
```

## Manual Test Checklist

Use this checklist for manual testing:

### Basic Functionality
- [ ] `type opencode` shows shell function from ~/.zshrc
- [ ] `which opencode` shows ~/.local/bin/opencode or shell function
- [ ] `ls -la ~/.local/bin/opencode` shows executable binary wrapper
- [ ] `./bin/oc --version` works (original wrapper)
- [ ] `opencode --version` works (shell function wrapper)

### Transformation Pipeline
- [ ] Pre-launch script transforms agents correctly
- [ ] Both `oc` and `opencode` trigger transformation
- [ ] Transformed files appear in ~/.config/opencode/agent/
- [ ] Caching prevents unnecessary re-transformation
- [ ] Source file updates trigger re-transformation

### Agent Loading
- [ ] `./bin/oc run --agent claude-test-agent "test"` works
- [ ] `opencode run --agent claude-test-agent "test"` works
- [ ] Both commands produce identical results
- [ ] Agents respond appropriately to prompts
- [ ] Error handling works for missing agents

### Environment Integration
- [ ] Shell function works after shell reload (`exec zsh`)
- [ ] Function works in new terminal windows
- [ ] API keys load correctly from launchctl
- [ ] Debug mode shows detailed logs
- [ ] Both commands work from any directory

### Error Scenarios
- [ ] Missing agent files handled gracefully
- [ ] Malformed agent files don't crash system
- [ ] Permission issues show clear error messages
- [ ] Network/dependency issues handled appropriately

## Continuous Integration

### CI/CD Pipeline Test

For automated testing in CI/CD environments:

```yaml
# .github/workflows/test-opencode-transformation.yml
name: Test OpenCode Agent Transformation

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install OpenCode
        run: npm install -g @opencode/cli
        
      - name: Test Core Transformation
        run: |
          cd opencode/.config/opencode
          node tests/test-agent-transformer.js
          
      - name: Test Pre-Launch Script
        run: |
          mkdir -p ~/.config/opencode/agent
          node opencode/.config/opencode/scripts/pre-launch-transform.js
          
      - name: Test OC Wrapper
        run: |
          # Note: Shell function won't work in CI, only test oc binary
          timeout 30s ./bin/oc --version || true
          
      - name: Verify Transformation Output
        run: |
          ls -la ~/.config/opencode/agent/
          [ -f ~/.config/opencode/agent/claude-test-agent.md ]
```

This comprehensive testing framework ensures the OpenCode agent transformation system works reliably across all usage patterns and edge cases.