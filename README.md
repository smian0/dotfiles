# Dotfiles

Personal dotfiles for consistent environment setup across macOS and Ubuntu Linux machines.

## 🚀 Quick Start

```bash
# Clone repository
git clone git@github.com:smian0/dotfiles.git ~/.dotfiles
cd ~/.dotfiles

# One-command setup
make bootstrap      # Complete setup for new machines
# OR
make install        # Development profile
make install-minimal # Essential tools only
```

## 🔧 Features

- **GNU Stow** for symlink management
- **Cross-platform** support (macOS & Ubuntu)
- **Multiple Claude Code profiles** for AI development
- **Secure API key management** with pass integration
- **Modular package organization** for selective installation
- **Task Master AI integration** for project management
- **Automated testing** and CI/CD
- **Backup/restore functionality**

## 📋 Commands

All operations are managed through the Makefile. Run `make help` to see all available commands.

### Essential Commands

```bash
make help             # Show all available commands
make install          # Install development profile
make backup           # Create backup of current configs
make status           # Show installation status
make test             # Run test suite
make docs             # Update this README with latest commands
```

### Quick Setup by Use Case

```bash
# New development machine
make bootstrap

# Minimal server setup
make install-minimal

# Full personal machine
make install-full

# Work/corporate environment
make install-work
```

## 📖 Documentation

Detailed documentation is available:

- **[Setup Guide](docs/SETUP.md)** - Detailed installation instructions
- **[Claude Configuration](docs/CLAUDE.md)** - Multi-level Claude Code setup
- **[Security Guide](docs/SECURITY.md)** - GPG and pass management
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🔒 Security

This repository includes security best practices:
- Pre-commit hooks to prevent secret commits
- GPG key management utilities
- Encrypted password store integration
- Audit and validation tools

Run `make check-secrets` and `make doctor` for security health checks.

## 🧪 Testing

Comprehensive testing ensures reliability:
- ShellSpec test framework
- GitHub Actions CI/CD
- Docker-based E2E testing
- Matrix testing across macOS versions

Run `make test` for the full test suite.

## 📦 Package Structure

```
~/.dotfiles/
├── git/                 # Git configuration
├── zsh/                 # Zsh shell configuration  
├── vim/                 # Vim editor configuration
├── claude-user/         # Global Claude Code settings
├── claude-project/      # Project Claude settings
├── direnv/             # Directory environment management
├── scripts/            # Utility and management scripts
└── Makefile           # Command interface (source of truth)
```

## 🤝 Contributing

This is a personal configuration repository. Feel free to fork and adapt!

## 📄 License

MIT

<!-- MAKEFILE_COMMANDS_START -->

## Available Commands

This project uses a Makefile for common operations. Run `make help` to see all available commands.

### Quick Start

```bash
make install          # Install with development profile
make install-minimal  # Install minimal profile
make backup           # Create backup
make test             # Run tests
make help             # Show all commands
```

### 📦 End User Commands

Common operations for daily use:

- **`make backup`** - Create a backup of current configurations
- **`make bootstrap`** - Bootstrap from scratch (for new machines)
- **`make clean`** - Clean temporary files and caches
- **`make help`** - Show this help message
- **`make install`** - Install dotfiles with development profile
- **`make list-backups`** - List available backups
- **`make restore`** - Restore from latest backup
- **`make status`** - Show installation status and system info
- **`make sync`** - Sync with remote repositories
- **`make update`** - Update dotfiles repository and tools
- **`make verify-backup`** - Verify latest backup integrity

### ⚙️ Configuration Commands

Profile and package management:

- **`make audit`** - Audit dotfiles configuration
- **`make check-secrets`** - Check for accidentally committed secrets
- **`make doctor`** - Run comprehensive health check
- **`make info`** - Show detailed system and dotfiles information
- **`make restore-from`** - Restore from specific backup (Usage: make restore-from BACKUP=20240117_120000)

### 🛠️ Developer Commands

Development and testing operations:

- **`make debug`** - Show debug information
- **`make demo`** - Run installation demo (dry-run)
- **`make dev-setup`** - Setup development environment
- **`make docker-test`** - Run tests in Docker container
- **`make docs`** - Update README with Makefile commands
- **`make format`** - Format shell scripts
- **`make lint`** - Lint shell scripts
- **`make test`** - Run all tests

---
*Documentation auto-generated from Makefile on 2025-08-17 12:51:16*

<!-- MAKEFILE_COMMANDS_END -->


