# 🚀 New Machine Setup Guide

> **Quick Start**: Setting up a new Mac in under 5 minutes with automated dotfiles deployment

## Prerequisites

Before starting, ensure you have:
- [ ] Access to your GitHub account
- [ ] Your GPG key backup (or plan to create new)
- [ ] Your API keys ready (Anthropic, GitHub, etc.)
- [ ] Admin access on the new machine

## Installation

### Option 1: Quick Setup (Recommended)

```bash
# Clone and run automatic installation
git clone https://github.com/smian0/mac-dotfiles-secrets.git ~/mac-dotfiles-secrets
cd ~/mac-dotfiles-secrets
./install-master.sh --automatic
```

**Time**: ~5 minutes

### Option 2: Interactive Setup

```bash
# Clone and run with prompts
git clone https://github.com/smian0/mac-dotfiles-secrets.git ~/mac-dotfiles-secrets
cd ~/mac-dotfiles-secrets
./install-master.sh
```

**Time**: ~10 minutes

### Option 3: Minimal Setup

```bash
# Just the essentials (git, vim, zsh)
git clone https://github.com/smian0/mac-dotfiles-secrets.git ~/mac-dotfiles-secrets
cd ~/mac-dotfiles-secrets
./install-master.sh --minimal
```

**Time**: ~3 minutes

## Post-Installation

### 1. GPG Setup

If you have an existing GPG key:
```bash
# Import your key
gpg --import /path/to/your-key.asc
pass init YOUR-GPG-KEY-ID
```

For a new GPG key:
```bash
# Generate new key
gpg --full-generate-key

# Initialize pass
gpg --list-secret-keys --keyid-format LONG
pass init YOUR-GPG-KEY-ID
```

### 2. Add API Keys

```bash
# Add Anthropic API key (required for Claude)
pass insert api/anthropic

# Add other keys as needed
pass insert api/github
pass insert api/openai
```

### 3. Activate Configuration

```bash
# Reload shell configuration
source ~/.zshrc

# Verify Claude Code
claude doctor
```

## What Gets Installed

| Component | Location | Purpose |
|-----------|----------|---------|
| Dotfiles | `~/.dotfiles-master/dotfiles` | Central configuration repository |
| Password Store | `~/.password-store` | Encrypted credentials |
| Homebrew | `/opt/homebrew` | Package manager |
| GNU Stow | via Homebrew | Symlink manager |
| GPG | via Homebrew | Encryption |
| Pass | via Homebrew | Password manager |

## Verification

Run these commands to verify installation:

```bash
# Check installation
~/.dotfiles-master/dotfiles/scripts/validate-config.sh

# View symlinks
ls -la ~/ | grep "\->"

# Test pass
pass list

# Test Claude
claude --version
```

## Profiles

### Switching Claude Profiles

Default profile is installed automatically. To switch:

```bash
cd ~/.dotfiles-master/dotfiles

# Switch to experimental
stow -D claude-default
stow claude-experimental

# Switch back to default
stow -D claude-experimental
stow claude-default
```

## Troubleshooting

### Dry Run Mode

Test without making changes:
```bash
./install-master.sh --dry-run --automatic
```

### Clean Uninstall

```bash
# Remove everything
rm -rf ~/.dotfiles-master
rm -rf ~/.password-store
rm ~/.zshrc ~/.vimrc ~/.gitconfig ~/.claude ~/.claude.json

# Remove symlinks
cd ~
find . -maxdepth 1 -type l -delete
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Homebrew not found | The script will install it automatically |
| GPG key issues | Create new with `gpg --full-generate-key` |
| Symlink conflicts | Script backs up existing files to `~/.dotfiles-backup/` |
| Pass not initialized | Run `pass init YOUR-GPG-KEY-ID` |

## Advanced Options

### Custom Installation

```bash
# All available options
./install-master.sh --help

# Specific Claude profile
./install-master.sh --automatic --claude-profile experimental

# Verbose output
./install-master.sh --automatic --verbose

# Dry run with specific profile
./install-master.sh --dry-run --claude-profile experimental
```

### Manual Installation

If you prefer manual control, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## Updates

To update your dotfiles on an existing machine:

```bash
cd ~/.dotfiles-master
git pull
cd dotfiles
./install.sh
```

## Testing

Before deploying to a new machine:

```bash
# Run test suite
cd ~/mac-dotfiles-secrets
shellspec

# Run with coverage
./tests/generate-coverage.sh
```

---

**Setup Time**: 5 minutes | **Tested On**: macOS 15.5 | **Last Updated**: August 2024

For development and contribution, see [CONTRIBUTING.md](CONTRIBUTING.md)