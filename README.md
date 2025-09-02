# Dotfiles

Personal dotfiles for consistent environment setup across macOS and Ubuntu Linux machines.

## Architecture

- **GNU Stow** for symlink management
- **Cross-platform** support (macOS & Ubuntu)
- **Multiple Claude Code profiles** for AI development
- **Secure API key management** with pass integration
- **Modular package organization** for selective installation
- **Task Master AI integration** for project management
- **Automated testing** and CI/CD
- **Backup/restore functionality**

## Quick Start

```bash
# Clone repository
git clone git@github.com:smian0/dotfiles.git ~/.dotfiles
cd ~/.dotfiles

# One-command setup
make bootstrap      # Complete setup for new machines
make install        # Development profile
make install-minimal # Essential tools only
```

## Core Commands

```bash
make help             # Show all available commands
make install          # Install development profile
make backup           # Create backup of current configs
make status           # Show installation status
make test             # Run test suite
```

## Package Structure

```
~/.dotfiles/
├── git/                 # Git configuration
├── zsh/                 # Zsh shell configuration  
├── vim/                 # Vim editor configuration
├── claude-user/         # Global Claude Code settings
├── claude-project/      # Project Claude settings
├── direnv/             # Directory environment management
├── scripts/            # Utility and management scripts
│   └── mcp-env/       # MCP environment management (self-contained)
└── Makefile           # Command interface (source of truth)
```

## Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed installation instructions
- **[Claude Configuration](docs/CLAUDE.md)** - Multi-level Claude Code setup
- **[MCP + Pass Integration](scripts/mcp-env/README.md)** - Quick start guide for secure MCP credentials
- **[Security Guide](docs/SECURITY.md)** - GPG and pass management
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## License

MIT


