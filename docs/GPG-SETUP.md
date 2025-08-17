# GPG and Pass Setup Guide

Complete guide for setting up GPG encryption and Pass password manager with macOS Keychain integration.

## Overview

This guide covers:
- GPG key generation and configuration
- Pass password manager setup
- macOS Keychain integration
- Backup and recovery procedures
- Troubleshooting common issues

## Prerequisites

```bash
# Required packages
brew install gnupg pinentry-mac pass
```

## Step 1: Generate GPG Key

Generate a new GPG key pair for encrypting your passwords:

```bash
gpg --full-generate-key
```

### Key Generation Settings

When prompted, choose:

| Setting | Recommended Value | Notes |
|---------|------------------|-------|
| Key type | RSA (default) | Most compatible |
| Key size | 4096 bits | Enhanced security |
| Expiration | 0 (no expiration) | Or 2-5 years |
| Real name | Your actual name | Used for key identification |
| Email | Your permanent email | Use personal, not GitHub noreply |
| Passphrase | Strong passphrase | Choose something memorable |

### Example Output

```
gpg: key 5D230F6271CC0BD7 marked as ultimately trusted
gpg: directory '/Users/username/.gnupg/openpgp-revocs.d' created
gpg: revocation certificate stored as '/Users/username/.gnupg/openpgp-revocs.d/8488076C54CB2B2CA56F48CA5D230F6271CC0BD7.rev'
public and secret key created and signed.
```

**Important**: Note your key ID (e.g., `5D230F6271CC0BD7`) - you'll need it for pass initialization.

## Step 2: Configure GPG Agent

Set up GPG agent with macOS Keychain integration and 30-day caching:

```bash
# Create GPG configuration directory
mkdir -p ~/.gnupg

# Configure GPG agent
cat > ~/.gnupg/gpg-agent.conf << EOF
pinentry-program /opt/homebrew/bin/pinentry-mac
default-cache-ttl 2592000
max-cache-ttl 2592000
EOF

# Set proper permissions
chmod 600 ~/.gnupg/gpg-agent.conf

# Restart GPG agent
gpgconf --kill gpg-agent
```

### Configuration Explained

- `pinentry-program`: Uses macOS-native password dialog
- `default-cache-ttl`: Cache passphrase for 30 days (2,592,000 seconds)
- `max-cache-ttl`: Maximum cache duration of 30 days

## Step 3: Initialize Pass

Install and set up the Pass password manager:

```bash
# Install pass (if not already installed)
brew install pass

# Get your GPG key ID
gpg --list-secret-keys --keyid-format LONG

# Initialize pass with your key ID
pass init YOUR_KEY_ID_HERE
```

Replace `YOUR_KEY_ID_HERE` with the key ID from step 1 (e.g., `5D230F6271CC0BD7`).

## Step 4: Create Directory Structure

Organize your password store with a logical structure:

```bash
# Create organized directories
mkdir -p ~/.password-store/{api,services,personal}
mkdir -p ~/.password-store/services/{cloud,dev}
mkdir -p ~/.password-store/personal/{banking,social}

# Verify structure
tree ~/.password-store
```

### Recommended Structure

```
~/.password-store/
├── api/                    # API keys and tokens
│   ├── anthropic          # Claude API key
│   ├── github             # GitHub token
│   └── openai             # OpenAI API key
├── services/              # Service accounts
│   ├── cloud/             # Cloud providers (AWS, GCP, etc.)
│   └── dev/               # Development tools
└── personal/              # Personal accounts
    ├── banking/           # Financial accounts
    └── social/            # Social media accounts
```

## Step 5: Test and Configure Keychain Integration

Test your setup and enable Keychain integration:

```bash
# Test pass by storing a test secret
pass insert api/test
```

**Important**: When the pinentry-mac dialog appears:
1. Enter your GPG passphrase
2. **Click "Save in Keychain"** checkbox
3. Click OK

This saves your GPG passphrase to macOS Keychain for automatic access.

### Verify Setup

```bash
# Verify pass works
pass show api/test

# List all stored passwords
pass

# Test automatic access (should not prompt for passphrase)
pass show api/test
```

## Step 6: Store Important Secrets

Add your essential API keys and passwords:

```bash
# Anthropic API key for Claude Code
pass insert api/anthropic

# GitHub personal access token
pass insert api/github

# Other development API keys
pass insert api/openai
pass insert api/perplexity

# Example service passwords
pass insert services/cloud/aws
pass insert personal/banking/primary
```

## Backup and Recovery

### Automatic Backups

Your revocation certificate is automatically saved:
```
~/.gnupg/openpgp-revocs.d/YOUR_KEY_FINGERPRINT.rev
```

**Critical**: Store this file securely - it allows you to revoke your key if compromised.

### Manual Key Export

Export your GPG key for backup:

```bash
# Export public key
gpg --armor --export YOUR_KEY_ID > gpg-public-key.asc

# Export private key (will prompt for passphrase)
gpg --armor --export-secret-keys YOUR_KEY_ID > gpg-private-key.asc

# Store these files securely (encrypted backup drive, etc.)
```

### Pass Store Backup

Back up your entire password store:

```bash
# Create compressed backup
tar -czf pass-backup-$(date +%Y%m%d).tar.gz ~/.password-store

# Or use Git for version control
cd ~/.password-store
git init
git add .
git commit -m "Initial password store backup"
```

## Git Integration and Multi-Device Sync

### GitHub Repository Setup

Your password store is already configured with Git and GitHub sync:

```bash
cd ~/.password-store

# Already configured - check status
git status
git remote -v  # Should show: origin git@github.com:smian0/pass-store.git
```

**Security Note**: Your Git repository is safe because all passwords are GPG-encrypted.

### Submodule Integration

Your password store is also integrated as a **submodule** in your main dotfiles repository:

```
mac-dotfiles-secrets/
├── dotfiles/                    # Configuration files submodule
├── pass-store/                  # Password store submodule (THIS ONE)
└── docs/                        # Documentation
```

#### Understanding the Two Locations

You have **one GitHub repository** with **two local copies**:

1. **`~/.password-store/`** - Your **working** password store (daily use)
2. **`pass-store/`** - A **submodule** in dotfiles repo (new machine setup)

#### Daily Workflow

**Adding passwords (daily use):**
```bash
# Add new password - works in ~/.password-store
pass insert api/service-name

# Pass automatically commits to Git
# Now sync to GitHub
cd ~/.password-store && git push origin main
```

**Update dotfiles submodule (when you want to update your dotfiles):**
```bash
# Go to your dotfiles repo
cd /Users/smian/workspaces/mac-dotfiles-secrets

# Update the submodule with latest passwords
git submodule update --remote pass-store

# Commit the submodule update
git add pass-store
git commit -m "Update pass-store with latest encrypted passwords"
git push origin main
```

#### New Machine Setup

When setting up a new machine:

```bash
# Clone main dotfiles repo
git clone --recursive https://github.com/smian0/mac-dotfiles-secrets.git

# Submodules (including pass-store) are automatically included
cd mac-dotfiles-secrets

# The pass-store/ submodule contains your encrypted passwords
# Installation script will set up ~/.password-store from the submodule
```

#### Workflow Summary

| Task | Location | Command |
|------|----------|---------|
| Add password | `~/.password-store` | `pass insert api/service` |
| Sync to GitHub | `~/.password-store` | `git push origin main` |
| Update dotfiles | `mac-dotfiles-secrets/` | `git submodule update --remote pass-store` |
| New machine | Clone with submodules | `git clone --recursive ...` |

**Key Point**: You only work daily in `~/.password-store`. The submodule is for deployment to new machines.

## Troubleshooting

### Common Issues

#### 1. Pinentry Not Working

```bash
# Check pinentry-mac installation
which pinentry-mac

# If missing, install:
brew install pinentry-mac

# Verify GPG agent config
cat ~/.gnupg/gpg-agent.conf

# Restart GPG agent
gpgconf --kill gpg-agent
```

#### 2. Passphrase Not Cached

```bash
# Check GPG agent is running
gpgconf --list-dirs agent-socket

# Verify cache settings
gpg-connect-agent 'getinfo version' /bye

# Restart agent with debug
gpg-connect-agent reloadagent /bye
```

#### 3. Keychain Integration Not Working

```bash
# Verify pinentry-mac version
pinentry-mac --version

# Test pinentry directly
echo "GETPIN" | pinentry-mac

# Check macOS Keychain Access for stored GPG passphrase
```

#### 4. Pass Commands Fail

```bash
# Verify pass installation
which pass
pass --version

# Check GPG key availability
gpg --list-secret-keys

# Verify pass initialization
cat ~/.password-store/.gpg-id
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# GPG debug
export GPG_TTY=$(tty)
gpg --debug-level basic --list-keys

# Pass debug
export PASSWORD_STORE_DEBUG=1
pass show api/test
```

## Security Considerations

### Best Practices

1. **Passphrase Security**
   - Use a strong, memorable passphrase
   - Consider storing in separate password manager as backup
   - Avoid writing down in plain text

2. **Key Management**
   - Keep revocation certificate safe and separate
   - Export key backup to secure location
   - Set reasonable expiration (2-5 years) for additional security

3. **Keychain Integration**
   - Keychain provides additional security layer
   - Passphrase encrypted at rest in Keychain
   - Automatic clearing on logout (depending on settings)

4. **Git Repository**
   - Always use private repository for pass store
   - All data is GPG-encrypted, but avoid public repos
   - Regular commits help with backup and sync

### Recovery Scenarios

| Scenario | Solution |
|----------|----------|
| Forgot GPG passphrase | No recovery - generate new key |
| Lost GPG key | Restore from backup export |
| Compromised key | Use revocation certificate |
| New machine setup | Import GPG key, clone pass store |
| Keychain issues | Re-enter passphrase, save to Keychain |

## Integration with Development Workflow

### Claude Code Integration

Your pass store integrates seamlessly with Claude Code:

```bash
# Store Anthropic API key
pass insert api/anthropic

# Claude Code can automatically retrieve it
export ANTHROPIC_API_KEY=$(pass show api/anthropic)
```

### Environment Variables

Load secrets into environment:

```bash
# Add to your .zshrc or .bashrc
export ANTHROPIC_API_KEY=$(pass show api/anthropic)
export GITHUB_TOKEN=$(pass show api/github)
export OPENAI_API_KEY=$(pass show api/openai)
```

### Script Integration

Use pass in scripts securely:

```bash
#!/bin/bash

# Get API key from pass
API_KEY=$(pass show api/service)

# Use in script
curl -H "Authorization: Bearer $API_KEY" https://api.example.com
```

## Advanced Configuration

### Multiple GPG Keys

If you need separate keys for different purposes:

```bash
# Generate additional key
gpg --full-generate-key

# Initialize pass with specific key
pass init --path=work WORK_KEY_ID
pass init --path=personal PERSONAL_KEY_ID

# Use specific store
PASSWORD_STORE_DIR=~/.password-store-work pass show api/work-key
```

### Custom Pinentry

For different pinentry behavior:

```bash
# Use terminal-based pinentry
echo "pinentry-program /opt/homebrew/bin/pinentry-curses" >> ~/.gnupg/gpg-agent.conf

# Or GUI pinentry
echo "pinentry-program /opt/homebrew/bin/pinentry-gtk2" >> ~/.gnupg/gpg-agent.conf

# Restart agent
gpgconf --kill gpg-agent
```

## Maintenance

### Regular Tasks

```bash
# Update GPG keyring
gpg --refresh-keys

# Clean up old cache
gpg-connect-agent reloadagent /bye

# Backup pass store
tar -czf pass-backup-$(date +%Y%m%d).tar.gz ~/.password-store

# Sync with Git (if using)
cd ~/.password-store && git add . && git commit -m "Update $(date)" && git push
```

### Key Rotation

When rotating GPG keys:

```bash
# Generate new key
gpg --full-generate-key

# Re-encrypt pass store
pass init NEW_KEY_ID

# Update all systems with new public key
gpg --armor --export NEW_KEY_ID | pbcopy
```

## GUI Applications

### QtPass (Recommended GUI)

QtPass provides a user-friendly interface for managing your pass store:

```bash
# Install QtPass
brew install --cask qtpass

# Remove quarantine attribute (bypass macOS security warning)
xattr -dr com.apple.quarantine /Applications/QtPass.app

# Launch QtPass
open -a QtPass
```

#### Initial Configuration

When QtPass first launches, configure it in **Programs** tab:

1. **Select password storage program**: Choose **"Use pass"** (right side)
2. **Pass field**: Enter `/opt/homebrew/bin/pass`
3. **Click OK**

**Important**: Don't use "Native Git/GPG" option - it requires manual GPG/Git configuration. The "Use pass" option leverages your existing command-line setup.

#### QtPass Features

- ✅ Tree view of password store structure
- ✅ Search and filter passwords
- ✅ Copy passwords to clipboard with auto-clear
- ✅ Add, edit, and delete passwords via GUI
- ✅ Password generation with customizable length
- ✅ Git integration for syncing (if configured)

#### Troubleshooting QtPass

**"Please install GnuPG" error:**
- Go to QtPass Settings → Programs tab
- Verify pass path is set to `/opt/homebrew/bin/pass`
- Choose "Use pass" not "Native Git/GPG"

**Quarantine/Security warnings:**
```bash
# Remove macOS quarantine attribute
xattr -dr com.apple.quarantine /Applications/QtPass.app
```

### Alternative GUI Options

#### Pass for macOS (Menu Bar App)
```bash
# Download from GitHub releases
# https://github.com/adur1990/Pass-for-macOS/releases
# Note: Beta software, may have stability issues
```

#### PassFinch (Lightweight Menu Bar)
```bash
# Check availability
brew search passfinch
```

## Conclusion

This setup provides:
- ✅ Secure GPG encryption for all passwords
- ✅ macOS Keychain integration for convenience
- ✅ 30-day passphrase caching
- ✅ Organized password structure
- ✅ Command-line and GUI access (QtPass)
- ✅ Backup and recovery procedures
- ✅ Development workflow integration

Your secrets are now secure and easily accessible for development work!