# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal dotfiles repository for consistent environment setup across macOS and Ubuntu Linux machines, featuring modular package management via GNU Stow, multiple Claude Code profiles for AI development, and integrated Task Master AI for project management.

## Core Architecture

### Package Management System
The repository uses **GNU Stow** for symlink management, where each top-level directory (e.g., `git/`, `zsh/`, `vim/`) is a Stow package that gets symlinked to the home directory. The installation system supports multiple profiles (minimal, development, full, work) defined in `profiles/` directory.

### Multi-Level Claude Configuration
- **Global settings**: `~/.claude/` (from `claude/` package)
- **User-specific**: Additional Claude configurations via `claude-user/` package
- **Project-specific**: `claude-project/` package for per-project settings
- Hierarchical CLAUDE.md files allow directory-specific configurations

### Installation & Profile System
The `install.sh` script detects OS (macOS/Ubuntu), installs dependencies (Homebrew/apt), and uses profile files to determine which packages to install. Profiles cascade - later profiles can override earlier ones.

## Essential Commands

### Build & Development
```bash
# Installation
make bootstrap      # Complete setup for new machines
make install        # Install development profile
make install-minimal # Essential tools only

# Development
make test           # Run full test suite
make lint           # Lint shell scripts
make format         # Format shell scripts

# Maintenance
make backup         # Create backup of configurations
make restore        # Restore from latest backup
make status         # Show installation status
make doctor         # Run comprehensive health check
make update         # Update repository and tools
```

### Testing
```bash
# Run specific test types
make test-quick     # Quick validation tests
make test-unit      # Unit tests only
make test-integration # Integration tests
make test-e2e       # End-to-end tests in Docker
make docker-test    # Run all tests in Docker container
```

### Task Master Integration
```bash
# If Task Master is initialized in a project
task-master next    # Get next task to work on
task-master show <id> # View task details
task-master set-status --id=<id> --status=done # Mark complete
```

## Key Scripts & Utilities

### API Key Management (`scripts/api-key-manager.sh`)
Manages encrypted API keys using `pass` password store. Keys are GPG-encrypted and can be synced across machines.

### Backup/Restore (`scripts/backup-restore.sh`)
Creates timestamped backups in `~/.dotfiles-backups/`, supports selective backup (exclude secrets), and includes Homebrew package lists.

### Deployment Scripts
- `deploy-claude-project.sh`: Deploy Claude configurations to projects
- `deploy-claude-user.sh`: Set up user-level Claude configurations
- `fix-claude-ssh-auth.sh`: Fix SSH authentication for remote Claude sessions

## Testing Infrastructure

The repository includes comprehensive testing via ShellSpec framework, Docker-based E2E testing environments, and GitHub Actions CI/CD. Test fixtures and helpers are in `tests/` directory.

## Security Considerations

- Pre-commit hooks prevent secret commits (`git/hooks/pre-commit`)
- GPG key management utilities in `scripts/gpg-manager.sh`
- Password store integration for API keys
- Audit commands: `make check-secrets` and `make audit`

## Package-Specific Notes

### Zsh Configuration
- Sources LLM tools from `zsh/llm-tools.zsh`
- Includes agents-md support via `zsh/agents-md.zsh`
- SSH agent auto-configuration for GitHub keys
- Claude OAuth token management for SSH sessions

### Chrome Automation
The `chrome-automation/` package includes Chrome keeper service for automated browser management with LaunchDaemon configuration for macOS.

## Development Workflow

1. Clone to `~/.dotfiles`
2. Run `make bootstrap` for initial setup
3. Use `make install-<profile>` for specific configurations
4. Create backups before major changes with `make backup`
5. Test changes with `make test` before committing

## Important File Locations

- Main Makefile: Source of truth for all commands
- Installation profiles: `profiles/*.txt`
- Stow ignore patterns: `.stow-global-ignore`
- Claude configurations: `claude/.claude/`
- Task Master config: `.taskmaster/`