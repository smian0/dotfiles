# Dotfiles Profile Management

This dotfiles system supports multiple installation profiles for different use cases and environments.

## Available Profiles

### 🔹 **minimal**
Essential tools only - perfect for servers or CI environments
- **Packages**: git, zsh, claude-default
- **npm packages**: @anthropic-ai/claude-cli
- **Use case**: Servers, CI/CD, basic setups

### 🔸 **development** (default)
Development tools with Claude Code enhancements
- **Packages**: git, zsh, claude-default, claude-experimental, npm-configs, config, bin
- **npm packages**: claude-cli, ccstatusline, npm-check-updates, nodemon, http-server, typescript, ts-node
- **Use case**: Development machines, coding work

### 🔹 **full**
Complete setup with all packages and configurations
- **Packages**: git, zsh, vim, claude-default, claude-experimental, npm-configs, config, bin, pass
- **npm packages**: All development packages plus Vue CLI, React, Vite, PM2, testing tools
- **Use case**: Primary development machines, power users

### 🔸 **work**
Work-specific configuration without personal tools
- **Packages**: git, zsh, claude-default, npm-configs  
- **npm packages**: Basic development tools only
- **Use case**: Corporate machines, work environments

### 🔹 **personal**
Personal machine setup with all customizations
- **Packages**: git, zsh, vim, claude-default, claude-experimental, npm-configs, config, bin, pass
- **npm packages**: Full development suite
- **Use case**: Personal computers, home setups

## Usage

### Manual Profile Installation

```bash
# List available profiles
./scripts/profile-manager.sh list

# Install specific profile
./scripts/profile-manager.sh install development

# Check installation status
./scripts/profile-manager.sh status

# Interactive selection
./scripts/profile-manager.sh interactive

# Uninstall profile
./scripts/profile-manager.sh uninstall development
```

### Automatic Profile Detection

```bash
# Auto-detect environment and install appropriate profile
./scripts/install-by-environment.sh

# Override auto-detection
DOTFILES_PROFILE=full ./scripts/install-by-environment.sh
```

### Via Master Installer

```bash
# Install with specific profile
DOTFILES_PROFILE=minimal ./install-master.sh

# Development profile (default)
./install-master.sh
```

## Environment Variables

- `DOTFILES_PROFILE`: Override profile selection (minimal, development, full, work, personal)
- `CLAUDE_PROFILE`: Claude Code profile (default, experimental)
- `INSTALL_MODE`: Installation mode (interactive, automatic, minimal)

## Examples

### Personal Machine Setup
```bash
DOTFILES_PROFILE=personal ./install-master.sh
```

### Work Machine Setup  
```bash
DOTFILES_PROFILE=work ./install-master.sh
```

### Server/CI Setup
```bash
DOTFILES_PROFILE=minimal INSTALL_MODE=automatic ./install-master.sh
```

### Custom npm Packages per Profile

Each profile can have its own npm package list:
- `profile-minimal/scripts/npm-packages.sh`
- `profile-development/scripts/npm-packages.sh`  
- `profile-full/scripts/npm-packages.sh`

Modify these files to customize which npm packages are installed for each profile.

## Package Mapping

| Package | minimal | development | full | work | personal |
|---------|---------|-------------|------|------|----------|
| git | ✅ | ✅ | ✅ | ✅ | ✅ |
| zsh | ✅ | ✅ | ✅ | ✅ | ✅ |
| vim | ❌ | ❌ | ✅ | ❌ | ✅ |
| claude-default | ✅ | ✅ | ✅ | ✅ | ✅ |
| claude-experimental | ❌ | ✅ | ✅ | ❌ | ✅ |
| npm-configs | ❌ | ✅ | ✅ | ✅ | ✅ |
| config | ❌ | ✅ | ✅ | ❌ | ✅ |
| bin | ❌ | ✅ | ✅ | ❌ | ✅ |
| pass | ❌ | ❌ | ✅ | ❌ | ✅ |

## Creating Custom Profiles

1. Add profile to `PROFILES` array in `scripts/profile-manager.sh`
2. Define package mapping in `PROFILE_PACKAGES` array
3. Create profile-specific npm packages: `profile-<name>/scripts/npm-packages.sh`
4. Optional: Add post-install script: `profile-<name>/post-install.sh`

This flexible system allows you to maintain different configurations for different machines and use cases!