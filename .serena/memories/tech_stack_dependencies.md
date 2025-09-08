# Technology Stack and Dependencies

## Core Technologies

### Shell Environment
- **Primary Shell**: Bash (for scripts) and Zsh (for interactive use)
- **Version Requirements**: Bash 4.0+, Zsh 5.0+
- **Platform Support**: macOS (Darwin) and Ubuntu Linux

### Package Management
- **GNU Stow**: Essential dependency for symlink management
  - Installation: `brew install stow` (macOS), `apt install stow` (Ubuntu)
  - Purpose: Creates symlinks from dotfiles to home directory
  - Pattern: Each top-level directory is a "package" that can be stowed

- **Homebrew** (macOS): Primary package manager
  - Auto-installation in `install.sh`
  - Used for: Git, Stow, development tools, CLI utilities

- **APT** (Ubuntu): System package manager
  - Used for: System dependencies, development tools
  - Requires sudo access for package installation

### Development Tools

#### Required Tools
- **Git**: Version control (2.20+)
- **Vim**: Default editor configuration
- **GPG**: For encryption and credential management
- **Pass**: Password store for secure credential storage

#### Optional but Recommended
- **shellcheck**: Shell script linting (static analysis)
- **shfmt**: Shell script formatting
- **Docker**: For E2E testing (development workflows)
- **fd**: Fast file finder (better than find)
- **ripgrep (rg)**: Fast text search (better than grep)

### Testing Infrastructure
- **ShellSpec**: Unit testing framework for shell scripts
- **Docker**: Containerized E2E testing
- **GitHub Actions**: CI/CD pipeline

### AI Development Stack
- **Claude Code**: AI development assistant
  - Multiple profile support (default, experimental)
  - OAuth integration for SSH sessions
  - MCP server integration

- **MCP (Model Context Protocol)**: AI tool integration
  - Environment management in `scripts/mcp-env/`
  - Secure credential handling
  - Server configuration management

### Security Stack
- **GPG**: Encryption and signing
- **Pass**: Password store (built on GPG)
- **SSH**: Key management and forwarding
- **Git hooks**: Pre-commit security validation

## Dependency Installation Patterns

### Bootstrap Dependencies (Required First)
1. **Homebrew** (macOS) or **APT updates** (Ubuntu)
2. **GNU Stow** (essential for all operations)
3. **Git** (usually pre-installed)
4. **GPG** (for credential management)

### Profile-Specific Dependencies
Each installation profile has different dependency requirements:

#### Minimal Profile
- GNU Stow
- Git
- Basic shell utilities
- Claude Code CLI

#### Development Profile (Default)
- All minimal dependencies plus:
- Node.js and npm
- Development CLI tools (nodemon, typescript, etc.)
- Testing frameworks
- Linting tools (shellcheck, shfmt)

#### Full Profile
- All development dependencies plus:
- Vim with plugins
- Pass password store
- Additional CLI utilities
- Full npm development suite

## Platform-Specific Considerations

### macOS (Darwin)
- **Package Manager**: Homebrew
- **Shell**: Zsh (default since Catalina)
- **Path Considerations**: `/opt/homebrew/bin` (Apple Silicon), `/usr/local/bin` (Intel)
- **System Tools**: `sw_vers`, `dscl`, `launchctl`
- **Browser Integration**: Native `open` command

### Ubuntu Linux  
- **Package Manager**: APT
- **Shell**: Usually Bash by default
- **Path Considerations**: `/usr/bin`, `/usr/local/bin`
- **System Tools**: `lsb_release`, `systemctl`, `apt`
- **Display Forwarding**: X11 forwarding for remote development

## NPM Package Dependencies

### Core Development Packages
```json
{
  "@anthropic-ai/claude-cli": "AI development assistant",
  "npm-check-updates": "Dependency management",
  "nodemon": "Development server",
  "http-server": "Static file server",
  "typescript": "TypeScript support",
  "ts-node": "TypeScript execution"
}
```

### Extended Packages (Full Profile)
- Vue CLI, React tools, Vite
- PM2 process manager
- Testing frameworks (Jest, Mocha)
- Build tools and utilities

## Environment Variables

### Essential Environment Variables
- `XDG_CONFIG_HOME`, `XDG_DATA_HOME`: XDG specification compliance
- `EDITOR`, `VISUAL`: Editor preferences
- `BROWSER`: Browser command for CLI tools
- `PATH`: Tool discovery and execution

### AI Development Variables
- `CLAUDE_CODE_OAUTH_TOKEN`: Claude authentication (SSH sessions only)
- MCP server configurations in environment

### Security Variables
- GPG key management variables
- SSH agent configuration
- Pass store location

## Compatibility Matrix

| Tool | macOS | Ubuntu | Required | Profile |
|------|--------|--------|----------|---------|
| GNU Stow | ✅ | ✅ | Yes | All |
| Git | ✅ | ✅ | Yes | All |
| Homebrew | ✅ | ❌ | macOS only | All |
| APT | ❌ | ✅ | Ubuntu only | All |
| shellcheck | ✅ | ✅ | No | Development+ |
| shfmt | ✅ | ✅ | No | Development+ |
| Docker | ✅ | ✅ | No | Testing only |
| Pass | ✅ | ✅ | No | Full |
| Claude CLI | ✅ | ✅ | Yes | All |

## Installation Verification

### Dependency Check Commands
```bash
# Core dependencies
command -v stow || echo "Stow missing"
command -v git || echo "Git missing"  
command -v gpg || echo "GPG missing"

# Development dependencies
command -v shellcheck || echo "shellcheck missing"
command -v shfmt || echo "shfmt missing"

# AI development
command -v claude || echo "Claude CLI missing"
```

### Health Check
The `make doctor` command provides comprehensive dependency validation and system health assessment.

## Troubleshooting Common Issues

### Stow Conflicts
- **Issue**: "Stow: WARNING! stowing X would cause conflicts"
- **Solution**: Remove conflicting files or use `stow --adopt`

### Permission Issues
- **Issue**: Cannot write to system directories
- **Solution**: Use Homebrew/user-space installations, avoid sudo

### Shell Integration
- **Issue**: Changes not taking effect
- **Solution**: Source shell configuration or restart terminal

This technology stack is designed for robust, cross-platform development with emphasis on security, automation, and AI-enhanced workflows.