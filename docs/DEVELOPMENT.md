# Development Guide

## Development Setup

### Prerequisites

```bash
# Install development dependencies
brew install shellspec bash bashcov
gem install bashcov simplecov

# Clone with submodules
git clone --recursive https://github.com/smian0/mac-dotfiles-secrets.git
cd mac-dotfiles-secrets
```

### GPG and Pass Setup

#### 1. Generate GPG Key

```bash
gpg --full-generate-key
```

**Key generation settings:**
- Key type: RSA (default)
- Key size: 4096 bits
- Expiration: 0 (no expiration) or 2-5 years
- Real name: Your actual name
- Email: Your permanent personal email
- Passphrase: Choose a strong passphrase you'll remember

#### 2. Configure GPG Agent (30-day cache)

```bash
mkdir -p ~/.gnupg
cat > ~/.gnupg/gpg-agent.conf << EOF
pinentry-program /opt/homebrew/bin/pinentry-mac
default-cache-ttl 2592000
max-cache-ttl 2592000
EOF

chmod 600 ~/.gnupg/gpg-agent.conf
gpgconf --kill gpg-agent
```

#### 3. Install and Initialize Pass

```bash
# Install pass
brew install pass

# Get your GPG key ID
gpg --list-secret-keys --keyid-format LONG

# Initialize pass with your key ID
pass init YOUR_KEY_ID_HERE

# Create directory structure
mkdir -p ~/.password-store/{api,services/cloud,services/dev,personal/banking,personal/social}
```

#### 4. Backup Your GPG Key

**Important:** Your revocation certificate is automatically saved at:
```
~/.gnupg/openpgp-revocs.d/YOUR_KEY_FINGERPRINT.rev
```

Store this file safely - it allows you to revoke your key if needed.

#### 5. Test GPG and Keychain Integration

```bash
# Test pass storage (will prompt for passphrase first time)
pass insert api/test

# When pinentry-mac prompts, click "Save in Keychain"
# Future access should be automatic for 30 days
```

#### 6. Store Important API Keys

```bash
# Anthropic API key for Claude
pass insert api/anthropic

# GitHub token if needed
pass insert api/github

# Any other development API keys
pass insert api/openai
```

#### 7. Install QtPass GUI (Optional)

For a graphical interface to manage passwords:

```bash
# Install QtPass
brew install --cask qtpass

# Remove quarantine attribute (bypass security warning)
xattr -dr com.apple.quarantine /Applications/QtPass.app

# Launch and configure
open -a QtPass
```

**QtPass Configuration:**
1. Go to **Programs** tab in settings
2. Select **"Use pass"** (not "Native Git/GPG")
3. Set pass path to: `/opt/homebrew/bin/pass`
4. Click OK

See `docs/GPG-SETUP.md` for complete GUI setup details.

#### 8. Understanding the Password Store Setup

Your password management uses a **dual-repository** approach:

- **`~/.password-store/`** - Your working password store (daily use)
- **`pass-store/`** - Submodule in this repo (new machine deployment)

**Daily workflow:**
```bash
# Add passwords (automatically commits to Git)
pass insert api/service-name

# Sync to GitHub
cd ~/.password-store && git push origin main

# Update dotfiles submodule (periodically)
cd /Users/smian/workspaces/mac-dotfiles-secrets
git submodule update --remote pass-store
git add pass-store && git commit -m "Update encrypted passwords"
```

**Key insight:** Both point to the same GitHub repository (`smian0/pass-store`) but serve different purposes - one for daily work, one for automated deployment.

## Project Structure

```
mac-dotfiles-secrets/
├── install-master.sh        # Main installation orchestrator
├── dotfiles/                # Dotfiles submodule
│   ├── install.sh          # Dotfiles installer
│   ├── scripts/            # Utility scripts
│   │   ├── os-detect.sh    # OS detection and package mapping
│   │   ├── validate-config.sh # Configuration validator
│   │   └── backup.sh       # Backup utility
│   └── [packages]/         # Individual dotfile packages
├── pass-store/             # Password store submodule
├── tests/                  # Test suite
│   ├── integration/        # Integration tests
│   ├── test-environment/   # Test sandbox
│   └── coverage/          # Coverage reports
└── docs/                  # Documentation

```

## Testing

### Running Tests

```bash
# Run all tests
shellspec

# Run specific test file
shellspec tests/integration/master_install_spec.sh

# Run with specific example
shellspec --example "supports dry-run mode"

# Run in random order
shellspec --random

# Run with parallel jobs
shellspec --jobs 8
```

### Test Coverage

```bash
# Generate coverage report
./tests/generate-coverage.sh

# Coverage report opens automatically
# Or view at: tests/coverage/index.html
```

### Writing Tests

Example test structure:

```bash
#!/bin/bash
# tests/integration/my_feature_spec.sh

Describe "My Feature"
  It "does something specific"
    When call my_function "arg"
    The output should include "expected"
    The status should be success
  End
  
  It "handles errors gracefully"
    When run my_script --invalid
    The status should be failure
    The error should include "Invalid"
  End
End
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit files
vim install-master.sh

# Test changes locally
./install-master.sh --dry-run --automatic
```

### 3. Write/Update Tests

```bash
# Add tests for new functionality
vim tests/integration/my_feature_spec.sh

# Run tests
shellspec tests/integration/my_feature_spec.sh
```

### 4. Validate Changes

```bash
# Run full test suite
shellspec

# Check coverage
./tests/generate-coverage.sh

# Validate configuration
./dotfiles/scripts/validate-config.sh
```

### 5. Commit and Push

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add new feature description"

# Push branch
git push origin feature/my-feature
```

## Testing Strategies

### Unit Testing

Test individual functions:

```bash
# Source the script
source dotfiles/scripts/os-detect.sh

# Test function
detect_os
echo $OS_TYPE  # Should output: macos
```

### Integration Testing

Test complete workflows:

```bash
# Test full installation
./install-master.sh --dry-run --automatic

# Test with different profiles
./install-master.sh --dry-run --claude-profile experimental
```

### Test Environment

The test environment simulates a home directory:

```bash
# Location
tests/test-environment/test-home/

# Reset test environment
rm -rf tests/test-environment
shellspec  # Will recreate it

# Inspect after tests
ls -la tests/test-environment/test-home/
```

## Adding New Features

### 1. New Dotfile Package

```bash
# Create package directory
mkdir dotfiles/mypackage

# Add configuration files
echo "config" > dotfiles/mypackage/.myconfig

# Test stow operation
cd dotfiles
stow -n -v mypackage  # Dry run
stow mypackage         # Actually stow
```

### 2. New Utility Script

```bash
# Create script
cat > dotfiles/scripts/my-utility.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Source common functions
source "$(dirname "${BASH_SOURCE[0]}")/os-detect.sh"

# Your functionality here
main() {
    log "Running my utility..."
}

main "$@"
EOF

chmod +x dotfiles/scripts/my-utility.sh
```

### 3. New Test Spec

```bash
# Create test file
cat > tests/integration/my_utility_spec.sh << 'EOF'
#!/bin/bash

Describe "My Utility"
  It "exists and is executable"
    When call test -x "$PROJECT_ROOT/dotfiles/scripts/my-utility.sh"
    The status should be success
  End
End
EOF

# Run test
shellspec tests/integration/my_utility_spec.sh
```

## Debugging

### Enable Debug Output

```bash
# Bash debug mode
bash -x ./install-master.sh

# Set verbose flag
./install-master.sh --verbose

# Enable shellspec debug
shellspec --debug
```

### Common Issues

| Issue | Debug Command |
|-------|--------------|
| Symlink problems | `stow -n -v package` |
| Path issues | `echo $PATH` |
| GPG problems | `gpg --list-keys --verbose` |
| Git submodules | `git submodule status` |

## Code Style

### Shell Scripts

- Use `#!/usr/bin/env bash` shebang
- Set `set -euo pipefail` for safety
- Use meaningful variable names
- Add comments for complex logic
- Follow ShellCheck recommendations

### Commit Messages

Follow conventional commits:

```
feat: add new feature
fix: resolve bug
docs: update documentation
test: add/update tests
refactor: code improvements
chore: maintenance tasks
```

## Release Process

### 1. Update Version

```bash
# Update version in install-master.sh
vim install-master.sh  # Update VERSION="1.0.1"
```

### 2. Update Documentation

```bash
# Update SETUP.md with any changes
vim SETUP.md

# Update CHANGELOG if maintained
vim CHANGELOG.md
```

### 3. Test Everything

```bash
# Full test suite
shellspec

# Coverage check
./tests/generate-coverage.sh

# Dry run on clean environment
./install-master.sh --dry-run --automatic
```

### 4. Tag and Release

```bash
# Tag version
git tag -a v1.0.1 -m "Release version 1.0.1"

# Push with tags
git push origin main --tags
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## Resources

- [ShellSpec Documentation](https://shellspec.info/)
- [GNU Stow Manual](https://www.gnu.org/software/stow/manual/)
- [Pass Documentation](https://www.passwordstore.org/)
- [Bash Best Practices](https://github.com/progrium/bashstyle)