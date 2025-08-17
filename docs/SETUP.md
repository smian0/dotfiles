# Detailed Setup Guide

This guide provides detailed installation instructions and configuration options.

## Prerequisites

- Git
- GNU Stow
- Pass (for password management)
- GPG (for encryption)

## Installation Methods

### Method 1: Bootstrap (Recommended for New Machines)

```bash
git clone git@github.com:smian0/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
make bootstrap
```

This will:
- Detect your OS (macOS/Ubuntu)
- Install missing dependencies
- Set up GPG and pass
- Install the development profile
- Configure shell hooks

### Method 2: Profile-Based Installation

```bash
# Choose your installation profile
make install-minimal     # Essential tools only
make install-development # Development tools (default)
make install-full        # Complete setup
make install-work        # Work environment
make install-personal    # Personal machine
```

### Method 3: Manual Package Selection

```bash
# Install specific packages
make install-git         # Git configuration
make install-zsh         # Zsh shell setup
make install-vim         # Vim editor config
make install-claude      # Claude Code settings
make install-direnv      # Directory environments
```

## Package Profiles

### Minimal Profile
- **Packages**: git, zsh, claude-default
- **Use case**: Servers, CI/CD, basic setups
- **Command**: `make install-minimal`

### Development Profile (Default)
- **Packages**: git, zsh, claude-default, claude-experimental, npm-configs, config, bin
- **Use case**: Development machines, coding work
- **Command**: `make install` or `make install-development`

### Full Profile
- **Packages**: All available packages
- **Use case**: Primary development machines, power users
- **Command**: `make install-full`

### Work Profile
- **Packages**: git, zsh, claude-default, npm-configs
- **Use case**: Corporate machines, work environments
- **Command**: `make install-work`

### Personal Profile
- **Packages**: git, zsh, vim, claude-default, claude-experimental, npm-configs, config, bin, pass
- **Use case**: Personal computers, home setups
- **Command**: `make install-personal`

## OS-Specific Setup

### macOS
```bash
# Install Homebrew (if not present)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Run setup
make bootstrap
```

### Ubuntu Linux
```bash
# Update package list
sudo apt-get update

# Run setup
make bootstrap
```

## GPG and Pass Setup

### First-time GPG Setup
```bash
# Generate GPG key
gpg --full-generate-key

# Initialize pass
pass init "Your Name <your.email@example.com>"
```

### Existing GPG Setup
```bash
# Import existing GPG key
gpg --import private-key.asc

# Initialize pass with existing key
pass init YOUR_GPG_KEY_ID
```

### Clone Existing Password Store
```bash
# Clone your password store
git clone git@github.com:yourusername/pass-store.git ~/.password-store
```

## API Key Management

### Adding API Keys
```bash
make api-status          # Check current keys
pass insert api/openai   # Add OpenAI key
pass insert api/anthropic # Add Claude key
pass insert services/github/token # Add GitHub token
make api-sync           # Sync with environment
```

### Environment Variables
Keys are automatically loaded from pass into environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY` 
- `GITHUB_TOKEN`

## Shell Completion Setup

```bash
# Install completions for all scripts
./config/completions/install.sh

# Restart your shell or source configs
source ~/.zshrc  # for zsh
source ~/.bashrc # for bash
```

## Directory Environment Setup

```bash
# Install direnv
make install-direnv

# Copy example .envrc to your project
cp ~/.config/direnv/envrc.example /path/to/project/.envrc

# Allow direnv in project
cd /path/to/project
direnv allow
```

## Verification

### Check Installation Status
```bash
make status              # Show installation status
make profile-status      # Check profile installation
make doctor             # Comprehensive health check
```

### Run Tests
```bash
make test               # Run all tests
make test-integration   # Integration tests only
make lint              # Check script quality
```

### Security Audit
```bash
make check-secrets      # Scan for leaked secrets
make audit             # Full configuration audit
```

## Backup and Restore

### Create Backups
```bash
make backup             # Full backup with Homebrew packages
make backup-minimal     # Backup excluding secrets
```

### Restore from Backup
```bash
make list-backups       # Show available backups
make restore           # Restore latest backup
make restore-from BACKUP=20240117_120000  # Restore specific backup
```

## Updating

### Update Repository and Tools
```bash
make update            # Update dotfiles and tools
make sync             # Sync with remote repositories
```

### Update Documentation
```bash
make docs             # Sync Makefile commands to README
make docs-check       # Verify docs are current
```

## Customization

### Adding New Packages
1. Create directory: `mkdir new-package`
2. Add configuration files in proper structure
3. Update Makefile with install target
4. Add to appropriate profile in `PROFILES.md`

### Modifying Existing Configs
1. Edit files in package directories
2. Test with `make demo` (dry-run)
3. Apply changes with `stow --restow package-name`

### Custom Profiles
1. Copy existing profile script
2. Modify package list in `profile-*` directories
3. Update `scripts/profile-manager.sh`
4. Add Makefile target

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.