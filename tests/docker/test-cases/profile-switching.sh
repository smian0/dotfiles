#!/usr/bin/env bash
# Test: Profile Switching
# Description: Tests switching between different installation profiles
# Category: integration
# Expected Duration: 3-5 minutes

set -euo pipefail

# Test configuration
TEST_NAME="Profile Switching"
TEST_DESCRIPTION="Test switching between different installation profiles"

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

# Profile configurations
PROFILES=("minimal" "development" "full" "work" "personal")
INSTALLED_PACKAGES=()

# Cleanup function
cleanup() {
    local exit_code=$?
    
    log "Cleaning up test environment..."
    
    # Unstow any test packages
    for package in "${INSTALLED_PACKAGES[@]}"; do
        stow -D -t "$HOME" -d . "$package" 2>/dev/null || true
    done
    
    # Remove test symlinks
    find "$HOME" -type l -name ".test-*" -delete 2>/dev/null || true
    
    if [[ $exit_code -eq 0 ]]; then
        success "All profile switching tests passed"
    else
        error "Profile switching tests failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up cleanup trap
trap cleanup EXIT

# Check if profile exists
check_profile() {
    local profile="$1"
    
    if [[ -f "profiles/${profile}.txt" ]]; then
        return 0
    else
        return 1
    fi
}

# Count installed symlinks
count_symlinks() {
    find "$HOME" -maxdepth 2 -type l 2>/dev/null | wc -l
}

# Main test function
run_test() {
    log "Starting $TEST_DESCRIPTION..."
    
    # =================================================================
    # Test 1: Profile manager script exists
    # =================================================================
    log "Test 1: Profile manager availability"
    
    if [[ -f "scripts/profile-manager.sh" && -x "scripts/profile-manager.sh" ]]; then
        success "Profile manager script exists and is executable"
    else
        error "Profile manager script not found or not executable"
        return 1
    fi
    
    # =================================================================
    # Test 2: List available profiles
    # =================================================================
    log "Test 2: Listing available profiles"
    
    if make profile-list 2>&1 | grep -E "(profile|Profile)" >/dev/null; then
        success "Profile listing works"
    else
        error "Profile listing failed"
        return 1
    fi
    
    # Check each expected profile
    for profile in "${PROFILES[@]}"; do
        if check_profile "$profile"; then
            success "Profile '$profile' exists"
        else
            warn "Profile '$profile' not found"
        fi
    done
    
    # =================================================================
    # Test 3: Minimal profile installation
    # =================================================================
    log "Test 3: Installing minimal profile"
    
    # Clean environment first
    find "$HOME" -maxdepth 1 -type l -delete 2>/dev/null || true
    
    # Install minimal profile
    if make install-minimal 2>&1 | grep -E "(install|Install)" >/dev/null; then
        success "Minimal profile installation executed"
        
        # Count symlinks created
        minimal_links=$(count_symlinks)
        log "Minimal profile created $minimal_links symlinks"
        
        # Track installed packages
        INSTALLED_PACKAGES+=("git" "zsh" "vim")
    else
        error "Minimal profile installation failed"
        return 1
    fi
    
    # =================================================================
    # Test 4: Switch to development profile
    # =================================================================
    log "Test 4: Switching to development profile"
    
    # Note current state
    before_switch=$(count_symlinks)
    
    # Install development profile (should add more packages)
    if ./install.sh --profile development 2>&1 | grep -E "(install|Install|stow)" >/dev/null; then
        success "Development profile installation executed"
        
        after_switch=$(count_symlinks)
        log "Development profile has $after_switch symlinks (was $before_switch)"
        
        if [[ $after_switch -ge $before_switch ]]; then
            success "Development profile added configurations"
        else
            warn "Development profile may not have added expected configurations"
        fi
    else
        error "Development profile installation failed"
        return 1
    fi
    
    # =================================================================
    # Test 5: Profile status check
    # =================================================================
    log "Test 5: Checking profile status"
    
    if make profile-status 2>&1 | tee /tmp/profile-status.log | grep -E "(status|Status|Profile)" >/dev/null; then
        success "Profile status command works"
        
        # Check if it shows installed packages
        if grep -E "(installed|Installed|active)" /tmp/profile-status.log >/dev/null 2>&1; then
            success "Profile status shows installed packages"
        else
            warn "Profile status output may be incomplete"
        fi
    else
        error "Profile status check failed"
        return 1
    fi
    
    # =================================================================
    # Test 6: Profile validation
    # =================================================================
    log "Test 6: Validating profile configurations"
    
    if make profile-check 2>&1 | grep -E "(valid|Valid|check|Check)" >/dev/null; then
        success "Profile validation passed"
    else
        warn "Profile validation may have issues"
    fi
    
    # =================================================================
    # Test 7: Dry run profile switch
    # =================================================================
    log "Test 7: Testing dry run mode"
    
    # Try dry run for full profile
    if ./install.sh --dry-run --profile full 2>&1 | grep -q "DRY RUN"; then
        success "Dry run mode works for profile switching"
        
        # Verify nothing was actually installed
        current_links=$(count_symlinks)
        if [[ $current_links -eq $after_switch ]]; then
            success "Dry run did not modify system"
        else
            error "Dry run modified the system unexpectedly"
            return 1
        fi
    else
        warn "Dry run mode may not be working correctly"
    fi
    
    # =================================================================
    # Test 8: Profile-specific package installation
    # =================================================================
    log "Test 8: Testing profile-specific packages"
    
    # Check if development profile includes specific tools
    if [[ -f "profiles/development.txt" ]]; then
        dev_packages=$(cat "profiles/development.txt")
        log "Development profile includes: $(echo $dev_packages | tr '\n' ' ')"
        
        # Verify at least some expected packages
        if echo "$dev_packages" | grep -q "git"; then
            success "Development profile includes git"
        fi
        
        if echo "$dev_packages" | grep -q "vim"; then
            success "Development profile includes vim"
        fi
    else
        error "Development profile definition not found"
        return 1
    fi
    
    # =================================================================
    # Test 9: Work profile specific configurations
    # =================================================================
    log "Test 9: Testing work profile configurations"
    
    if check_profile "work"; then
        # Check work profile contents
        work_packages=$(cat "profiles/work.txt" 2>/dev/null || echo "")
        
        if [[ -n "$work_packages" ]]; then
            success "Work profile has specific packages defined"
            log "Work profile includes: $(echo $work_packages | tr '\n' ' ')"
        else
            warn "Work profile may be empty"
        fi
    else
        warn "Work profile not found"
    fi
    
    # =================================================================
    # Test 10: Personal profile configurations
    # =================================================================
    log "Test 10: Testing personal profile configurations"
    
    if check_profile "personal"; then
        # Check personal profile contents
        personal_packages=$(cat "profiles/personal.txt" 2>/dev/null || echo "")
        
        if [[ -n "$personal_packages" ]]; then
            success "Personal profile has specific packages defined"
            log "Personal profile includes: $(echo $personal_packages | tr '\n' ' ')"
        else
            warn "Personal profile may be empty"
        fi
    else
        warn "Personal profile not found"
    fi
    
    # =================================================================
    # Test 11: Clean installation state
    # =================================================================
    log "Test 11: Cleaning installation state"
    
    # Try to unstow packages
    for package in git vim zsh; do
        if [[ -d "$package" ]]; then
            if stow -D -t "$HOME" -d . "$package" 2>/dev/null; then
                success "Unstowed $package successfully"
            else
                warn "Could not unstow $package (may not be stowed)"
            fi
        fi
    done
    
    # Verify cleanup
    final_links=$(count_symlinks)
    log "Final symlink count: $final_links"
    
    # =================================================================
    # Test 12: Full profile installation test
    # =================================================================
    log "Test 12: Testing full profile installation"
    
    # This is the most comprehensive profile
    if make install-full 2>&1 | grep -E "(install|Install)" >/dev/null; then
        success "Full profile installation executed"
        
        full_links=$(count_symlinks)
        log "Full profile created $full_links symlinks"
        
        if [[ $full_links -gt $minimal_links ]]; then
            success "Full profile is more comprehensive than minimal"
        else
            warn "Full profile may not include expected packages"
        fi
    else
        error "Full profile installation failed"
        return 1
    fi
    
    success "All profile switching tests completed!"
}

# =================================================================
# Script Entry Point
# =================================================================

# Check prerequisites
if [[ ! -f "Makefile" ]]; then
    error "This test must be run from the dotfiles root directory"
    exit 1
fi

if [[ ! -d "profiles" ]]; then
    error "Profiles directory not found"
    exit 1
fi

# Run the test
log "Starting ${TEST_NAME}..."
run_test
log "Profile switching tests completed successfully!"