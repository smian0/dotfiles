# SSH Configuration Management

This package provides a **safe, version-controlled way** to manage SSH configurations without exposing sensitive data.

## ⚠️ Security First

**NEVER** commit the following to version control:
- Private SSH keys (`id_*` without `.pub`)
- Actual SSH config with sensitive hostnames/IPs
- Known_hosts file
- Any file containing passwords or tokens

## 📁 Package Contents

| File | Purpose | Safe to Commit |
|------|---------|----------------|
| `.ssh/config.template` | Template SSH configuration | ✅ Yes |
| `setup-ssh.sh` | Interactive setup script | ✅ Yes |
| `README.md` | This documentation | ✅ Yes |

## 🚀 Quick Start

### 1. Initial Setup (New Machine)

```bash
# Run the interactive setup
cd ~/dotfiles/ssh
./setup-ssh.sh

# Or run automated setup
./setup-ssh.sh --auto
```

### 2. Stow the Package

The SSH package is **special** - it only stows the template, not actual SSH files:

```bash
# Stow the ssh package (safe - only links documentation)
cd ~/dotfiles
stow ssh

# The actual SSH config is managed by the setup script
```

## 🔧 Setup Script Features

The `setup-ssh.sh` script provides:

1. **Full Setup** - Complete SSH environment configuration
2. **Config Deployment** - Deploy template config with backups
3. **Key Generation** - Interactive SSH key generation wizard
4. **SSH Agent Setup** - Configure and load SSH agent
5. **Connection Testing** - Test GitHub/GitLab connections
6. **Key Fingerprints** - Display current key fingerprints

## 📝 Configuration Guide

### GitHub Multiple Accounts

```bash
# Primary account
git clone git@github.com:username/repo.git

# Secondary account
git clone git@github-secondary:organization/repo.git

# Organization specific
git clone git@github-org:organization/repo.git
```

### Adding a New Host

1. Edit `~/.ssh/config` (NOT the template)
2. Add your host configuration
3. Generate a key if needed: `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_hostname`

### Using the Template

The template provides common patterns:
- GitHub/GitLab configurations
- Development server setups
- Jump host/bastion configurations
- SSH multiplexing for performance
- Security best practices

## 🔑 Key Management Best Practices

### Generate Keys Per Service

```bash
# GitHub
ssh-keygen -t ed25519 -C "your_email@github.com" -f ~/.ssh/id_ed25519_github

# GitLab
ssh-keygen -t ed25519 -C "your_email@gitlab.com" -f ~/.ssh/id_ed25519_gitlab

# Development server
ssh-keygen -t ed25519 -C "$USER@$(hostname)" -f ~/.ssh/id_ed25519_dev
```

### Key Permissions

Always ensure proper permissions:
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/id_*.pub
chmod 600 ~/.ssh/config
```

## 🔄 Backup Strategy

### Secure Backup of Keys

```bash
# Create encrypted backup
tar czf - ~/.ssh | gpg -c > ssh-backup-$(date +%Y%m%d).tar.gz.gpg

# Restore from backup
gpg -d ssh-backup-20240101.tar.gz.gpg | tar xzf - -C ~/
```

### Using Password Manager

Store SSH keys in a password manager like `pass`:
```bash
# Store a key
cat ~/.ssh/id_ed25519_github | pass insert -m ssh/github

# Retrieve a key
pass ssh/github > ~/.ssh/id_ed25519_github
chmod 600 ~/.ssh/id_ed25519_github
```

## 🚨 Troubleshooting

### Permission Denied

```bash
# Fix permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/id_*.pub
```

### Agent Not Running

```bash
# Start agent
eval "$(ssh-agent -s)"

# Add keys
ssh-add ~/.ssh/id_ed25519_*
```

### Test Connections

```bash
# Test GitHub
ssh -T git@github.com

# Test GitLab
ssh -T git@gitlab.com

# Verbose mode for debugging
ssh -vvv git@github.com
```

## 📋 Checklist for New Machines

- [ ] Run `./setup-ssh.sh` for initial setup
- [ ] Generate necessary SSH keys
- [ ] Add public keys to GitHub/GitLab/servers
- [ ] Test all connections
- [ ] Set up SSH agent auto-start in shell config
- [ ] Create secure backup of keys
- [ ] Document any custom configurations

## 🔗 Related Documentation

- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [GitLab SSH Documentation](https://docs.gitlab.com/ee/user/ssh.html)
- [SSH Academy](https://www.ssh.com/academy/ssh)

## ⚡ Quick Commands

```bash
# Show all SSH key fingerprints
for key in ~/.ssh/*.pub; do ssh-keygen -lf "$key"; done

# Copy public key to clipboard (macOS)
cat ~/.ssh/id_ed25519.pub | pbcopy

# Add key to ssh-agent with keychain (macOS)
ssh-add --apple-use-keychain ~/.ssh/id_ed25519

# Remove all keys from agent
ssh-add -D

# List keys in agent
ssh-add -l
```