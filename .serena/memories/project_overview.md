# Dotfiles Project Overview

## Purpose

This is a personal dotfiles repository designed for consistent environment setup across macOS and Ubuntu Linux machines. It provides automated configuration management for development tools, shell environments, and AI development workflows.

## Core Architecture

### Package Management System
- **GNU Stow**: Primary tool for symlink management
- **Modular Packages**: Each top-level directory (git/, zsh/, vim/, etc.) is a Stow package
- **Profile System**: Multiple installation profiles (minimal, development, full, work, personal)
- **Cross-Platform**: Supports both macOS (Homebrew) and Ubuntu Linux (apt)

### Directory Structure
```
~/.dotfiles/
├── git/                 # Git configuration and aliases
├── zsh/                 # Zsh shell configuration with custom functions
├── vim/                 # Vim editor configuration  
├── claude/              # Global Claude Code settings
├── claude-project/      # Project-specific Claude settings
├── claude-user/         # User-specific Claude configurations
├── direnv/             # Directory environment management
├── scripts/            # Utility and management scripts
├── tests/              # Docker-based E2E testing
├── profiles/           # Installation profile definitions
├── docs/               # Comprehensive documentation
└── Makefile           # Main command interface
```

## Technology Stack

### Primary Technologies
- **Shell Scripting**: Bash (primary), Zsh configuration
- **Package Management**: GNU Stow for dotfiles, Homebrew (macOS), apt (Ubuntu)
- **Version Control**: Git with custom hooks and aliases
- **Testing**: Docker-based E2E tests, ShellSpec for unit tests
- **CI/CD**: GitHub Actions for automated testing
- **Encryption**: GPG and pass for secure credential management

### Development Tools
- **Linting**: shellcheck for shell script quality
- **Formatting**: shfmt for consistent shell script formatting  
- **Editor**: Vim with custom configuration
- **AI Integration**: Claude Code with multiple profiles
- **Task Management**: Task Master AI integration

### Key Dependencies
- GNU Stow (essential for symlink management)
- Git (version control)
- Homebrew (macOS package management)
- pass (password store for API keys)
- GPG (encryption)
- Docker (for testing)

## Project Features

### Multi-Profile Installation
- **minimal**: Essential tools only (servers, CI environments)
- **development**: Development tools with Claude Code (default)
- **full**: Complete setup with all packages
- **work**: Work-specific without personal tools
- **personal**: Personal machine with all customizations

### Security Features
- GPG-encrypted API key management
- Pre-commit hooks prevent secret commits
- Secure pass integration for credentials
- SSH key management and forwarding
- Browser forwarding for remote development

### AI Development Integration
- **Multiple Claude Profiles**: Global, user-specific, project-specific
- **MCP Environment Management**: Secure MCP server credentials
- **OAuth Token Management**: Automatic SSH session handling
- **Task Master Integration**: AI-powered project management

### Backup and Restore
- Timestamped backups in `~/.dotfiles-backups/`
- Homebrew package list preservation
- Selective backup (can exclude secrets)
- Automatic integrity verification

### Testing Infrastructure
- **Docker E2E Tests**: Full installation scenarios
- **ShellSpec Unit Tests**: Individual component testing
- **CI/CD Pipeline**: Automated testing on GitHub Actions
- **Multiple Test Scenarios**: basic, full, claude, switch profiles

## Installation Patterns

### New Machine Setup
1. Clone to `~/.dotfiles`
2. Run `make bootstrap` for complete setup
3. Profiles automatically detect environment
4. Backup created before major changes

### Development Workflow
1. Feature branches for all changes
2. Lint and format before commits
3. E2E testing validates changes
4. CI/CD ensures quality

## System Compatibility

### macOS Support
- Homebrew package management
- macOS-specific utilities and paths
- LaunchDaemon services (Chrome automation)
- Native terminal integration

### Ubuntu Linux Support  
- apt package management
- Linux-specific configurations
- Cross-platform script compatibility
- SSH and remote development support

## Key Design Principles

1. **Modularity**: Each component is independently manageable
2. **Cross-Platform**: Single repository works on macOS and Linux
3. **Security-First**: Encrypted credentials, secret detection
4. **Automation**: Minimal manual intervention required
5. **Testing**: Comprehensive validation of all changes
6. **Documentation**: Extensive guides for all use cases

This dotfiles system is designed for power users who need consistent, secure, and well-tested environment management across multiple machines and platforms.