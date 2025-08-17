# Troubleshooting Guide

## Common Installation Issues

### Homebrew Installation Fails

**Problem**: Script fails when trying to install Homebrew

**Solution**:
```bash
# Install Homebrew manually
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (Apple Silicon)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"

# Retry installation
./install-master.sh --automatic
```

### GPG Key Issues

**Problem**: "No GPG key found" or "Cannot initialize pass"

**Solution**:
```bash
# Check existing keys
gpg --list-secret-keys

# If no keys, create new
gpg --full-generate-key

# Get key ID
gpg --list-secret-keys --keyid-format LONG | grep sec | awk '{print $2}' | cut -d'/' -f2

# Initialize pass with key
pass init YOUR-KEY-ID
```

### Symlink Conflicts

**Problem**: "File already exists" errors during stow

**Solution**:
```bash
# Check what's blocking
ls -la ~/ | grep -E "(.zshrc|.vimrc|.gitconfig|.claude)"

# Backup and remove conflicts
mv ~/.zshrc ~/.zshrc.backup
mv ~/.vimrc ~/.vimrc.backup

# Retry stow
cd ~/.dotfiles-master/dotfiles
stow zsh vim
```

### Claude Code Not Working

**Problem**: `claude doctor` fails or API key not found

**Solution**:
```bash
# Check if Claude is installed
which claude

# Verify API key helper is executable
chmod +x ~/.claude/anthropic_key_helper.sh

# Check if API key is in pass
pass show api/anthropic

# If missing, add it
pass insert api/anthropic
```

## Platform-Specific Issues

### macOS Ventura/Sonoma Issues

**Problem**: Security warnings about unsigned scripts

**Solution**:
```bash
# Allow scripts in System Settings > Privacy & Security

# Or remove quarantine attribute
xattr -d com.apple.quarantine install-master.sh
xattr -dr com.apple.quarantine dotfiles/
```

### Apple Silicon (M1/M2/M3) Issues

**Problem**: Homebrew installed in wrong location

**Solution**:
```bash
# Homebrew should be in /opt/homebrew on Apple Silicon
which brew
# Should output: /opt/homebrew/bin/brew

# If in /usr/local, reinstall:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Recovery Procedures

### Complete Uninstall

```bash
# Remove all symlinks
cd ~
find . -maxdepth 1 -type l -delete

# Remove repositories
rm -rf ~/.dotfiles-master
rm -rf ~/.password-store

# Remove backups
rm -rf ~/.dotfiles-backup

# Restore original files if backed up
mv ~/.zshrc.backup ~/.zshrc
mv ~/.vimrc.backup ~/.vimrc
mv ~/.gitconfig.backup ~/.gitconfig
```

### Restore from Backup

```bash
# List available backups
ls -la ~/.dotfiles-backup/

# Restore specific backup
cp -R ~/.dotfiles-backup/20240816_143022/* ~/
```

### Reset and Retry

```bash
# Clean everything
rm -rf ~/.dotfiles-master ~/.password-store
cd ~/mac-dotfiles-secrets

# Start fresh
./install-master.sh --dry-run  # Test first
./install-master.sh --automatic
```

## Debugging

### Enable Verbose Output

```bash
# Run with verbose flag
./install-master.sh --verbose --automatic

# Or enable bash debugging
bash -x ./install-master.sh --automatic
```

### Check Logs

```bash
# Installation creates backups with logs
cat ~/.dotfiles-backup/*/backup.log

# Check git status
cd ~/.dotfiles-master
git status

cd ~/.password-store
git status
```

### Validate Installation

```bash
# Run validation script
~/.dotfiles-master/dotfiles/scripts/validate-config.sh

# Check specific components
which stow
which pass
which gpg
gpg --version
pass version
```

## Network Issues

### GitHub Access Problems

**Problem**: Cannot clone repositories

**Solution**:
```bash
# Test GitHub access
ssh -T git@github.com

# If using HTTPS instead of SSH
git config --global url."https://github.com/".insteadOf git@github.com:

# Use personal access token
git clone https://YOUR-TOKEN@github.com/smian0/mac-dotfiles-secrets.git
```

### Proxy Configuration

**Problem**: Behind corporate proxy

**Solution**:
```bash
# Set proxy for git
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy http://proxy.company.com:8080

# Set proxy for curl (Homebrew)
export http_proxy=http://proxy.company.com:8080
export https_proxy=http://proxy.company.com:8080

# Run installation
./install-master.sh --automatic
```

## Getting Help

If you're still having issues:

1. Run the dry-run mode to see what would happen:
   ```bash
   ./install-master.sh --dry-run --verbose
   ```

2. Check the test suite:
   ```bash
   shellspec tests/integration/master_install_spec.sh
   ```

3. Open an issue on GitHub with:
   - Your macOS version
   - Error messages
   - Output of `./install-master.sh --dry-run --verbose`

## Quick Fixes

| Symptom | Quick Fix |
|---------|-----------|
| "Command not found: stow" | `brew install stow` |
| "Command not found: pass" | `brew install pass` |
| "gpg: no valid OpenPGP data found" | Create new key: `gpg --full-generate-key` |
| "pass: Password store not initialized" | `pass init YOUR-GPG-KEY-ID` |
| "fatal: not a git repository" | Re-clone the repository |
| "Permission denied" | `chmod +x install-master.sh` |