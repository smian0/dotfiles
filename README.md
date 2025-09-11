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
## Clone repository
git clone git@github.com:smian0/dotfiles.git ~/.dotfiles
cd ~/.dotfiles

## One-command setup
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

```text
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

### 📚 Complete Documentation Suite

| Document | Purpose | Audience |
|----------|---------|----------|
| **[📋 Project Overview](docs/PROJECT-OVERVIEW.md)** | Architecture and comprehensive guide | All users |
| **[🚀 Setup Guide](docs/SETUP.md)** | Detailed installation instructions | New users |
| **[📦 Package Guide](docs/PACKAGE-GUIDE.md)** | Configuration package details | Configuration users |
| **[👨‍💻 Developer Workflow](docs/DEVELOPER-WORKFLOW.md)** | Development and contribution guide | Contributors |
| **[📖 API Reference](docs/API-REFERENCE.md)** | Command and script reference | Power users |
| **[🤖 Claude Configuration](docs/CLAUDE.md)** | AI integration setup | AI developers |
| **[🔐 Security Guide](docs/SECURITY.md)** | Security best practices | Security-conscious users |
| **[🆘 Troubleshooting](docs/TROUBLESHOOTING.md)** | Problem resolution | Support |

### 🔧 Specialized Guides

| Guide | Description | Use Case |
|-------|-------------|----------|
| **[🔐 MCP + Pass Integration](scripts/mcp-env/README.md)** | Secure credential management for MCP services | AI developers working with multiple services |
| **[🔑 GPG Setup](docs/GPG-SETUP.md)** | Complete GPG key management and configuration | Security-focused development |
| **[⚙️ Profile System](PROFILES.md)** | Flexible installation profiles and customization | Tailored environment setup |
| **[🔄 CI/CD Guide](docs/CI.md)** | Automated testing and deployment workflows | DevOps and automation |

### 🎯 Quick Access

**First time here?** Start with [🚀 Setup Guide](docs/SETUP.md)  
**Need help?** Check [🆘 Troubleshooting](docs/TROUBLESHOOTING.md)  
**Want to contribute?** See [👨‍💻 Developer Workflow](docs/DEVELOPER-WORKFLOW.md)

## License

MIT License - see [LICENSE](LICENSE) file for details

---

> **✨ Pro Tip:** Use `make help` to discover all available commands and shortcuts

_Last updated: 2025-01-27_


