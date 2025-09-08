# Task Completion Workflow

When completing any task in the dotfiles repository, follow this systematic workflow to ensure quality, security, and functionality.

## Pre-Completion Quality Gates

### 1. Code Quality Validation
Run these commands before considering any task complete:

```bash
# Lint all shell scripts
make lint

# Format all shell scripts consistently  
make format

# Check for any accidentally committed secrets
make check-secrets
```

**Requirements:**
- All `shellcheck` issues must be resolved (errors and warnings)
- All scripts must be formatted with `shfmt` (4-space indentation)
- No secrets or credentials in the repository

### 2. Functionality Testing
Validate that changes work correctly:

```bash
# Run comprehensive E2E tests
make test

# For specific scenarios, use:
make test-all          # All test scenarios
TEST=full make test    # Specific profile testing
```

**Requirements:**
- All E2E tests must pass
- Installation scenarios must work correctly
- No breaking changes to existing functionality

### 3. Configuration Validation
Ensure system integrity:

```bash
# Run health check and diagnostics
make doctor

# Audit configuration completeness
make audit

# Show current status
make status
```

**Requirements:**
- All required dependencies present
- No configuration conflicts
- System health checks pass

## Security Validation Checklist

### Before Each Commit
1. **Secret Detection**: Run `make check-secrets`
2. **API Key Audit**: Verify no hardcoded credentials
3. **Permission Check**: Ensure appropriate file permissions
4. **GPG Verification**: Test encrypted storage if modified

### Git Hook Integration
The repository includes pre-commit hooks that automatically run:
- Secret detection
- Basic shellcheck validation
- File permission checks

**Never bypass these hooks** - they prevent security issues.

## Testing Requirements by Change Type

### Configuration Changes (git/, zsh/, vim/)
1. Test installation: `make install-<package>`
2. Verify symlinks: Check `~/.dotfiles` links
3. Test functionality: Use the configured tool
4. Profile validation: `make profile-status`

### Script Changes (scripts/*)
1. Lint: `make lint` 
2. Function test: Run script with test data
3. Error handling: Test failure scenarios
4. Integration test: `make test`

### Installation/Profile Changes
1. Docker test: `make test-all`
2. Clean install: Test on fresh system if possible
3. Profile switching: Test profile transitions
4. Backup/restore: Verify backup functionality

### Documentation Changes
1. Link validation: Check all internal links
2. Command verification: Test all documented commands
3. Accuracy check: Ensure examples work
4. Sync check: `make docs-check`

## Backup Strategy

### Before Risky Changes
Always create a backup before making significant changes:

```bash
# Create comprehensive backup
make backup

# For development changes, minimal backup:
make backup-minimal
```

### After Task Completion
If the task involved system changes:
1. Verify backup integrity: `make verify-backup`
2. Test restore process: `make list-backups`
3. Document any new backup requirements

## Documentation Updates

### When Documentation Must Be Updated
- New commands added to Makefile
- New scripts added to `scripts/`
- New installation profiles created
- New dependencies or requirements
- Security procedures changed

### Documentation Sync Process
```bash
# Update README with latest Makefile commands
make docs

# Verify documentation is current
make docs-check
```

## CI/CD Integration

### GitHub Actions Validation
All changes trigger automated testing that must pass:
- Shell script linting with shellcheck
- E2E installation testing
- Security scanning
- Documentation validation

### Branch Protection
- All changes must be on feature branches
- Main branch requires passing CI
- Pull requests require review

## Environment-Specific Testing

### macOS Testing
- Homebrew integration
- macOS version compatibility  
- Terminal app compatibility
- Keychain integration (if applicable)

### Linux Testing
- apt package management
- SSH forwarding functionality
- Cross-distribution compatibility
- Container environment testing

## Post-Completion Verification

### Final Validation Checklist
✅ **Code Quality**: `make lint && make format` passes  
✅ **Functionality**: `make test` passes  
✅ **Security**: `make check-secrets` passes  
✅ **Health**: `make doctor` shows no issues  
✅ **Backup**: Created if system changes made  
✅ **Documentation**: Updated if commands/features changed  
✅ **Git**: Committed to feature branch  
✅ **CI/CD**: Automated tests pass  

### Success Indicators
- All quality gates pass
- No regression in existing functionality  
- Documentation is current and accurate
- Backup available if needed
- Changes are reproducible on clean systems

## Cleanup After Completion

### Temporary File Cleanup
```bash
# Clean temporary files and caches
make clean

# Remove old backups if appropriate
make clean-backups
```

### Git Hygiene
- Feature branch with descriptive name
- Commit messages follow conventional format
- No merge commits on feature branches
- Clean, linear history

## Emergency Rollback Procedure

If task completion reveals issues:

```bash
# Restore from latest backup
make restore

# Or restore from specific backup
make restore-from BACKUP=20240117_120000

# Revert Git changes
git reset --hard HEAD~1  # Last commit
git reset --hard origin/main  # Reset to main
```

## Task Completion Documentation

### For Significant Changes
Create a brief completion summary:
- What was changed
- Commands used for validation
- Any new requirements or dependencies
- Backup location and restore procedure

This workflow ensures that every completed task maintains the repository's high standards for quality, security, and reliability.