#!/usr/bin/env bash
# Test: Security Validation
# Description: Validates security practices, secret detection, and permissions
# Category: unit
# Expected Duration: 1-2 minutes

set -euo pipefail

# Test configuration
TEST_NAME="Security Validation"
TEST_DESCRIPTION="Validate security practices and secret detection"

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

# Test patterns for secrets
SECRET_PATTERNS=(
    "AKIA[0-9A-Z]{16}"  # AWS Access Key
    "-----BEGIN RSA PRIVATE KEY-----"  # Private Key
    "-----BEGIN OPENSSH PRIVATE KEY-----"  # OpenSSH Key
    "ghp_[a-zA-Z0-9]{36}"  # GitHub Personal Access Token
    "ghs_[a-zA-Z0-9]{36}"  # GitHub Secret
    "sk-[a-zA-Z0-9]{48}"  # OpenAI API Key
    "AIza[0-9A-Za-z-_]{35}"  # Google API Key
    "xoxb-[0-9]{11}-[0-9]{13}-[a-zA-Z0-9]{24}"  # Slack Token
)

# Test results
SECURITY_ISSUES=0
WARNINGS=0

# Cleanup function
cleanup() {
    local exit_code=$?
    
    log "Security Test Summary:"
    log "  Security issues found: $SECURITY_ISSUES"
    log "  Warnings: $WARNINGS"
    
    # Clean up test files
    rm -f /tmp/test-secret-* 2>/dev/null || true
    rm -rf /tmp/test-security-* 2>/dev/null || true
    
    if [[ $SECURITY_ISSUES -eq 0 ]]; then
        success "No security issues found"
    else
        error "Found $SECURITY_ISSUES security issue(s)"
        exit_code=1
    fi
    
    exit $exit_code
}

# Set up cleanup trap
trap cleanup EXIT

# Check for secrets in a file
check_file_for_secrets() {
    local file="$1"
    local found_secrets=0
    
    # Skip binary files
    if file "$file" | grep -q "binary"; then
        return 0
    fi
    
    # Check each pattern
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -E "$pattern" "$file" >/dev/null 2>&1; then
            error "Potential secret found in $file (pattern: $pattern)"
            found_secrets=$((found_secrets + 1))
            SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
        fi
    done
    
    return $found_secrets
}

# Main test function
run_test() {
    log "Starting $TEST_DESCRIPTION..."
    
    # =================================================================
    # Test 1: Check for exposed secrets in repository
    # =================================================================
    log "Test 1: Scanning for exposed secrets"
    
    # Find all text files (exclude .git, node_modules, etc.)
    while IFS= read -r file; do
        check_file_for_secrets "$file"
    done < <(find . \
        -type f \
        -not -path "./.git/*" \
        -not -path "./node_modules/*" \
        -not -path "./.cache/*" \
        -not -path "./tests/logs/*" \
        -not -name "*.tar.gz" \
        -not -name "*.zip" \
        -not -name "*.png" \
        -not -name "*.jpg" \
        -not -name "*.gif" \
        2>/dev/null | head -100)  # Limit to first 100 files for speed
    
    if [[ $SECURITY_ISSUES -eq 0 ]]; then
        success "No secrets found in repository files"
    fi
    
    # =================================================================
    # Test 2: File permissions check
    # =================================================================
    log "Test 2: Checking file permissions"
    
    # Check for world-writable files
    world_writable=$(find . -type f -perm -002 2>/dev/null | head -10)
    if [[ -n "$world_writable" ]]; then
        warn "Found world-writable files:"
        echo "$world_writable" | head -5
        WARNINGS=$((WARNINGS + 1))
    else
        success "No world-writable files found"
    fi
    
    # Check SSH directory permissions (if exists)
    if [[ -d "$HOME/.ssh" ]]; then
        ssh_perms=$(stat -f "%A" "$HOME/.ssh" 2>/dev/null || stat -c "%a" "$HOME/.ssh" 2>/dev/null || echo "unknown")
        if [[ "$ssh_perms" == "700" ]]; then
            success "SSH directory has correct permissions (700)"
        else
            warn "SSH directory permissions may be too permissive: $ssh_perms"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
    
    # =================================================================
    # Test 3: GPG configuration check
    # =================================================================
    log "Test 3: GPG configuration validation"
    
    if command -v gpg >/dev/null 2>&1; then
        success "GPG is installed"
        
        # Check GPG directory permissions
        if [[ -d "$HOME/.gnupg" ]]; then
            gnupg_perms=$(stat -f "%A" "$HOME/.gnupg" 2>/dev/null || stat -c "%a" "$HOME/.gnupg" 2>/dev/null || echo "unknown")
            if [[ "$gnupg_perms" == "700" ]]; then
                success "GnuPG directory has correct permissions (700)"
            else
                warn "GnuPG directory permissions may be incorrect: $gnupg_perms"
                WARNINGS=$((WARNINGS + 1))
            fi
        else
            log "GnuPG directory not found (may be expected in container)"
        fi
    else
        warn "GPG not installed"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # =================================================================
    # Test 4: Git hooks for secret detection
    # =================================================================
    log "Test 4: Git hooks validation"
    
    if [[ -d ".git/hooks" ]]; then
        if [[ -f ".git/hooks/pre-commit" ]]; then
            success "Pre-commit hook exists"
            
            # Check if it's executable
            if [[ -x ".git/hooks/pre-commit" ]]; then
                success "Pre-commit hook is executable"
            else
                error "Pre-commit hook is not executable"
                SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
            fi
        else
            warn "Pre-commit hook not found"
            WARNINGS=$((WARNINGS + 1))
            
            # Try to install hooks
            if make install-hooks 2>/dev/null; then
                success "Git hooks installed successfully"
            else
                warn "Could not install git hooks"
            fi
        fi
    else
        log "Not in a git repository (expected in container)"
    fi
    
    # =================================================================
    # Test 5: Environment variable leakage
    # =================================================================
    log "Test 5: Checking for environment variable leakage"
    
    # Check for hardcoded API keys in common files
    suspicious_files=(".env.example" ".env.sample" "config.example.sh")
    for file in "${suspicious_files[@]}"; do
        if [[ -f "$file" ]]; then
            if grep -E "(api[_-]?key|token|secret|password)\s*=\s*['\"]?[A-Za-z0-9]{10,}" "$file" >/dev/null 2>&1; then
                error "Potential hardcoded credential in $file"
                SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
            else
                success "$file is clean"
            fi
        fi
    done
    
    # =================================================================
    # Test 6: Secure file handling in scripts
    # =================================================================
    log "Test 6: Checking script security practices"
    
    # Check for unsafe practices in shell scripts
    script_issues=0
    while IFS= read -r script; do
        # Check for eval usage
        if grep -q "eval " "$script" 2>/dev/null; then
            warn "Unsafe 'eval' usage in $script"
            WARNINGS=$((WARNINGS + 1))
            script_issues=$((script_issues + 1))
        fi
        
        # Check for unquoted variables in dangerous contexts
        if grep -E "rm -rf \$[A-Za-z_]" "$script" 2>/dev/null; then
            error "Unquoted variable in dangerous command in $script"
            SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
            script_issues=$((script_issues + 1))
        fi
    done < <(find . -name "*.sh" -type f 2>/dev/null | head -20)
    
    if [[ $script_issues -eq 0 ]]; then
        success "No obvious script security issues found"
    fi
    
    # =================================================================
    # Test 7: Audit command test
    # =================================================================
    log "Test 7: Running security audit"
    
    if make audit 2>&1 | grep -E "(audit|Audit|check)" >/dev/null; then
        success "Security audit command works"
    else
        warn "Security audit may have issues"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # =================================================================
    # Test 8: Test secret detection command
    # =================================================================
    log "Test 8: Testing secret detection"
    
    # Create a test file with a fake secret
    test_secret_file="/tmp/test-secret-file.txt"
    echo "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE" > "$test_secret_file"
    
    # Check if our security tools can detect it
    if make check-secrets 2>&1 | grep -E "(secret|Secret|credential)" >/dev/null; then
        success "Secret detection command available"
    else
        warn "Secret detection may need configuration"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Clean up test file
    rm -f "$test_secret_file"
    
    # =================================================================
    # Test 9: Password store security
    # =================================================================
    log "Test 9: Password store configuration"
    
    if command -v pass >/dev/null 2>&1; then
        success "Pass (password store) is installed"
        
        # Check if password store is initialized
        if [[ -d "$HOME/.password-store" ]]; then
            pass_perms=$(stat -f "%A" "$HOME/.password-store" 2>/dev/null || stat -c "%a" "$HOME/.password-store" 2>/dev/null || echo "unknown")
            if [[ "$pass_perms" == "700" ]]; then
                success "Password store has correct permissions"
            else
                warn "Password store permissions may be incorrect: $pass_perms"
                WARNINGS=$((WARNINGS + 1))
            fi
        else
            log "Password store not initialized (expected in container)"
        fi
    else
        log "Pass not installed (may be expected)"
    fi
    
    # =================================================================
    # Test 10: API key management
    # =================================================================
    log "Test 10: API key management validation"
    
    if [[ -f "scripts/api-key-manager.sh" ]]; then
        success "API key manager script exists"
        
        # Check if it has proper security measures
        if grep -q "gpg" "scripts/api-key-manager.sh" || grep -q "pass" "scripts/api-key-manager.sh"; then
            success "API key manager uses encryption"
        else
            warn "API key manager may not be using encryption"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        warn "API key manager not found"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Final summary
    if [[ $SECURITY_ISSUES -eq 0 ]]; then
        success "Security validation completed with no critical issues!"
    else
        error "Security validation found $SECURITY_ISSUES critical issue(s)"
    fi
    
    if [[ $WARNINGS -gt 0 ]]; then
        warn "Found $WARNINGS warning(s) that should be reviewed"
    fi
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
log "Security validation completed!"