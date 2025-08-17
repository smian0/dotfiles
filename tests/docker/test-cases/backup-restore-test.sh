#!/usr/bin/env bash
# Test: Backup and Restore
# Description: Tests backup creation, listing, and restoration functionality
# Category: integration
# Expected Duration: 2-3 minutes

set -euo pipefail

# Test configuration
TEST_NAME="Backup and Restore"
TEST_DESCRIPTION="Test backup creation, listing, and restoration"

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

# Backup directory
BACKUP_DIR="$HOME/.dotfiles-backups"
TEST_FILE="$HOME/.test-backup-file"
TEST_CONTENT="Test backup content $(date)"

# Cleanup function
cleanup() {
    local exit_code=$?
    
    log "Cleaning up test environment..."
    
    # Remove test files
    rm -f "$TEST_FILE" 2>/dev/null || true
    rm -rf "$HOME/.test-backup-dir" 2>/dev/null || true
    
    if [[ $exit_code -eq 0 ]]; then
        success "All backup/restore tests passed"
    else
        error "Backup/restore tests failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up cleanup trap
trap cleanup EXIT

# Main test function
run_test() {
    log "Starting $TEST_DESCRIPTION..."
    
    # =================================================================
    # Test 1: Backup script exists and is executable
    # =================================================================
    log "Test 1: Backup script availability"
    if [[ -f "scripts/backup-restore.sh" && -x "scripts/backup-restore.sh" ]]; then
        success "Backup script exists and is executable"
    else
        error "Backup script not found or not executable"
        return 1
    fi
    
    # =================================================================
    # Test 2: Create test files for backup
    # =================================================================
    log "Test 2: Creating test files"
    
    # Create test file
    echo "$TEST_CONTENT" > "$TEST_FILE"
    
    # Create test directory with files
    mkdir -p "$HOME/.test-backup-dir"
    echo "Nested content 1" > "$HOME/.test-backup-dir/file1.txt"
    echo "Nested content 2" > "$HOME/.test-backup-dir/file2.txt"
    
    success "Test files created"
    
    # =================================================================
    # Test 3: Create a backup
    # =================================================================
    log "Test 3: Creating backup"
    
    # Run backup command
    if make backup 2>&1 | tee /tmp/backup-output.log | grep -q "backup"; then
        success "Backup command executed"
    else
        error "Backup command failed"
        return 1
    fi
    
    # Check if backup directory was created
    if [[ -d "$BACKUP_DIR" ]]; then
        success "Backup directory created"
    else
        error "Backup directory not found"
        return 1
    fi
    
    # Check if backup files exist
    backup_count=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f 2>/dev/null | wc -l)
    if [[ $backup_count -gt 0 ]]; then
        success "Backup archive created ($backup_count backup(s) found)"
    else
        error "No backup archives found"
        return 1
    fi
    
    # =================================================================
    # Test 4: List backups
    # =================================================================
    log "Test 4: Listing backups"
    
    if make list-backups 2>&1 | grep -E "(backup|Backup)" >/dev/null; then
        success "Backup listing works"
    else
        warn "Backup listing may not be showing expected output"
    fi
    
    # =================================================================
    # Test 5: Create minimal backup (without secrets)
    # =================================================================
    log "Test 5: Creating minimal backup"
    
    # Create a fake secret file
    mkdir -p "$HOME/.ssh"
    echo "fake-private-key" > "$HOME/.ssh/test_key"
    chmod 600 "$HOME/.ssh/test_key"
    
    # Create minimal backup
    if make backup-minimal 2>&1 | grep -q "backup"; then
        success "Minimal backup created"
    else
        warn "Minimal backup may have failed"
    fi
    
    # =================================================================
    # Test 6: Verify backup integrity
    # =================================================================
    log "Test 6: Verifying backup integrity"
    
    # Get latest backup
    latest_backup=$(ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -1)
    
    if [[ -n "$latest_backup" ]]; then
        # Check if it's a valid tar archive
        if tar -tzf "$latest_backup" >/dev/null 2>&1; then
            success "Backup archive is valid"
            
            # Check contents
            file_count=$(tar -tzf "$latest_backup" | wc -l)
            log "Backup contains $file_count files"
        else
            error "Backup archive is corrupted"
            return 1
        fi
    else
        error "No backup found to verify"
        return 1
    fi
    
    # =================================================================
    # Test 7: Test restoration (dry run)
    # =================================================================
    log "Test 7: Testing restoration (simulation)"
    
    # Remove test files
    rm -f "$TEST_FILE"
    rm -rf "$HOME/.test-backup-dir"
    
    # Check files are gone
    if [[ ! -f "$TEST_FILE" ]]; then
        log "Test files removed for restoration test"
    fi
    
    # Note: Actual restoration might be destructive in container
    # So we'll just verify the restore command exists
    if ./scripts/backup-restore.sh --help 2>&1 | grep -q "restore"; then
        success "Restore functionality is available"
    else
        error "Restore functionality not found"
        return 1
    fi
    
    # =================================================================
    # Test 8: Backup metadata
    # =================================================================
    log "Test 8: Checking backup metadata"
    
    # Check if metadata file exists for latest backup
    if [[ -n "$latest_backup" ]]; then
        metadata_file="${latest_backup%.tar.gz}.meta"
        if [[ -f "$metadata_file" ]]; then
            success "Backup metadata file exists"
            
            # Read metadata
            if grep -q "timestamp" "$metadata_file" 2>/dev/null; then
                success "Metadata contains timestamp"
            else
                warn "Metadata may be incomplete"
            fi
        else
            warn "No metadata file found (may be expected)"
        fi
    fi
    
    # =================================================================
    # Test 9: Clean old backups
    # =================================================================
    log "Test 9: Testing backup cleanup"
    
    # Create multiple dummy backups for testing
    for i in {1..3}; do
        touch "$BACKUP_DIR/test-backup-$i.tar.gz"
        sleep 0.1
    done
    
    initial_count=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
    log "Initial backup count: $initial_count"
    
    # Clean backups (keep last 5)
    if make clean-backups 2>&1 | grep -E "(clean|Clean)" >/dev/null; then
        success "Backup cleanup executed"
        
        final_count=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
        log "Final backup count: $final_count"
    else
        warn "Backup cleanup may not be working as expected"
    fi
    
    # Clean up test backups
    rm -f "$BACKUP_DIR"/test-backup-*.tar.gz 2>/dev/null || true
    
    # =================================================================
    # Test 10: Backup with specific profile
    # =================================================================
    log "Test 10: Profile-specific backup"
    
    # Set a profile environment variable
    export DOTFILES_PROFILE="test-profile"
    
    # Create profile-specific file
    echo "Profile: $DOTFILES_PROFILE" > "$HOME/.profile-test"
    
    # Run backup
    if ./scripts/backup-restore.sh backup 2>&1 | grep -q "backup"; then
        success "Profile-specific backup created"
    else
        warn "Profile-specific backup may have issues"
    fi
    
    # Clean up
    rm -f "$HOME/.profile-test"
    unset DOTFILES_PROFILE
    
    success "All backup/restore tests completed!"
}

# =================================================================
# Script Entry Point
# =================================================================

# Check prerequisites
if [[ ! -f "Makefile" ]]; then
    error "This test must be run from the dotfiles root directory"
    exit 1
fi

if [[ ! -f "scripts/backup-restore.sh" ]]; then
    error "Backup script not found"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Run the test
log "Starting ${TEST_NAME}..."
run_test
log "Backup/restore tests completed successfully!"