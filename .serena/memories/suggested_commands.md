# Essential Commands for Dotfiles Development

This dotfiles repository uses a comprehensive Makefile as the main command interface. All commands should be run from the project root directory.

## Core Development Commands

### Installation and Setup
```bash
make bootstrap      # Complete setup for new machines (includes dependencies)
make install        # Install development profile (default)
make install-minimal # Install minimal profile (essential tools only)
make install-all    # Install all packages and configurations
```

### Testing and Validation
```bash
make test           # Run E2E tests in Docker (primary test command)
make test-all       # Run all E2E test scenarios (basic, full, claude, switch)
make lint           # Lint shell scripts with shellcheck
make format         # Format shell scripts with shfmt
make audit          # Run comprehensive configuration audit
make doctor         # Run health check and diagnostics
```

### Backup and Restore
```bash
make backup         # Create backup of current configurations
make restore        # Restore from latest backup
make list-backups   # List available backups
make verify-backup  # Verify latest backup integrity
```

### Status and Information
```bash
make status         # Show installation status and system info
make help           # Show all available commands
make info           # Show detailed system information
make debug          # Show debug information
```

### Package-Specific Operations
```bash
make install-git    # Install git configuration only
make install-zsh    # Install zsh configuration only  
make install-vim    # Install vim configuration only
make install-claude # Install Claude Code configurations
```

### Maintenance
```bash
make update         # Update repository and tools
make sync           # Sync with remote repositories
make clean          # Clean temporary files and caches
make clean-backups  # Clean old backups (keep last 5)
```

### API Key Management
```bash
make api-status     # Show API key status
make api-list       # List stored API keys
make api-sync       # Sync API keys with pass store
```

### Security
```bash
make check-secrets  # Check for accidentally committed secrets
make install-hooks  # Install git hooks
```

## Direct Script Commands

When Makefile commands are not sufficient, use these scripts directly:

### Profile Management
```bash
./scripts/profile-manager.sh list         # List available profiles
./scripts/profile-manager.sh status       # Show installation status
./scripts/profile-manager.sh install development
```

### OS Detection and Environment
```bash
./scripts/os-detect.sh --info            # Show OS information
./scripts/validate-config.sh --audit     # Detailed configuration audit
```

### API Key Management
```bash
./scripts/api-key-manager.sh add openai  # Add new API key
./scripts/api-key-manager.sh test anthropic # Test API key
./scripts/api-key-manager.sh status      # Show key status
```

### Backup/Restore
```bash
./scripts/backup-restore.sh backup --include-brew
./scripts/backup-restore.sh restore 20240117_120000
./scripts/backup-restore.sh list
```

## Git Commands (macOS-specific notes)

Standard git commands work, but note these dotfiles-specific hooks:
- Pre-commit hook runs secret detection
- Post-commit hook can sync configurations

## System Utilities (Darwin/macOS)

Essential commands for macOS development:
```bash
# Package management
brew install <package>    # Homebrew package installation
brew list                # List installed packages
brew update && brew upgrade # Update all packages

# File operations  
fd -e sh                 # Fast file finding (better than find)
rg "pattern" --type sh   # Fast text search (better than grep)
stow <package>           # Symlink package to home directory
stow -D <package>        # Remove symlinked package

# System utilities
sw_vers -productVersion  # macOS version
dscl . -list /Users      # List users
launchctl list          # List running services
```

## Testing Commands

### Docker E2E Testing
```bash
make test              # Run basic E2E test
make test-all          # Run all test scenarios
TEST=full make test    # Run specific test scenario
make test-clean        # Clean up Docker test environment
```

### Manual Testing
```bash
./install.sh --dry-run --profile development  # Test installation without changes
```

## Common Workflows

### New Feature Development
1. `git checkout -b feature/new-feature`
2. Make changes
3. `make lint && make format` 
4. `make test`
5. `git add -A && git commit -m "feature: description"`

### Task Completion Checklist
1. Run `make lint` to check shell script quality
2. Run `make format` to ensure consistent formatting  
3. Run `make test` to verify E2E functionality
4. Run `make check-secrets` to prevent secret leaks
5. Create backup with `make backup` if making system changes

### New Machine Setup
1. Clone to `~/.dotfiles`
2. `cd ~/.dotfiles`
3. `make bootstrap` (installs dependencies + default profile)
4. Verify with `make status`