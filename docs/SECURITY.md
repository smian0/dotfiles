# Security Guide

This guide covers security best practices, GPG key management, and password store usage.

## Security Philosophy

- **Never commit secrets** - All sensitive data belongs in pass
- **Use GPG encryption** - Protect your password store with strong keys
- **Regular backups** - Maintain encrypted backups of GPG keys
- **Audit regularly** - Scan for accidental secret commits

## Quick Security Commands

```bash
make check-secrets       # Scan for leaked secrets
make install-hooks      # Install git security hooks
make doctor            # Comprehensive security audit
make audit             # Configuration security check
```

## GPG Key Management

### Generate New GPG Key
```bash
# Interactive key generation
gpg --full-generate-key

# Follow prompts for:
# - Key type: RSA (default)
# - Key size: 4096 bits
# - Expiration: 1-2 years
# - Name and email
# - Secure passphrase
```

### GPG Management Commands
```bash
# List keys
gpg --list-secret-keys

# Export public key
gpg --export --armor YOUR_KEY_ID > public-key.asc

# Export private key (for backup)
gpg --export-secret-keys --armor YOUR_KEY_ID > private-key.asc

# Import keys
gpg --import public-key.asc
gpg --import private-key.asc
```

### Using GPG Manager Script
```bash
# Export keys with script
./scripts/gpg-manager.sh export --key-id YOUR_KEY_ID

# Backup entire keyring
./scripts/gpg-manager.sh backup

# Restore from backup
./scripts/gpg-manager.sh restore --backup-file /path/to/backup

# List available keys
./scripts/gpg-manager.sh list
```

## Password Store (Pass) Setup

### Initialize Pass
```bash
# With new GPG key
pass init "Your Name <your.email@example.com>"

# With existing key ID
pass init YOUR_GPG_KEY_ID
```

### Basic Pass Commands
```bash
# Add password
pass insert service/account

# Generate password
pass generate service/account 20

# Retrieve password
pass service/account

# Edit entry
pass edit service/account

# List all entries
pass
```

### API Key Management
```bash
# Add API keys
pass insert api/openai
pass insert api/anthropic
pass insert api/github

# Use with scripts
./scripts/api-key-manager.sh add openai
./scripts/api-key-manager.sh test anthropic
./scripts/api-key-manager.sh status
```

### Remote Sync
```bash
# Initialize git repository
pass git init
pass git remote add origin git@github.com:username/pass-store.git

# Sync changes
pass git push -u origin main
pass git pull

# Using pass manager script
./scripts/pass-manager.sh sync
./scripts/pass-manager.sh status
```

## Pre-commit Security Hooks

The repository includes pre-commit hooks that scan for common secrets:

### Detected Patterns
- API keys (OpenAI, GitHub, AWS)
- Private keys (RSA, SSH, PGP)
- Passwords and tokens
- Cloud service credentials

### Hook Installation
```bash
# Install hooks automatically
make install-hooks

# Manual installation
cp git/hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### Bypassing Hooks (NOT Recommended)
```bash
# Only use in emergencies
git commit --no-verify
```

## Environment Security

### Environment Variables
```bash
# Check for exposed secrets
env | grep -E "(KEY|TOKEN|PASSWORD|SECRET)"

# Use pass for environment variables
export OPENAI_API_KEY=$(pass api/openai)
export GITHUB_TOKEN=$(pass services/github/token)
```

### Shell History
```bash
# Clear history if secrets were exposed
history -c
rm ~/.zsh_history ~/.bash_history

# Prevent specific commands from being saved
export HISTIGNORE="*pass*:*export*KEY*:*TOKEN*"
```

## File Permissions

### Secure File Permissions
```bash
# GPG directory
chmod 700 ~/.gnupg
chmod 600 ~/.gnupg/*

# SSH directory  
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/config

# Pass directory
chmod 700 ~/.password-store
```

### Check Permissions Script
```bash
# Audit file permissions
./scripts/validate-config.sh --audit

# Fix common permission issues
find ~/.gnupg -type f -exec chmod 600 {} \;
find ~/.gnupg -type d -exec chmod 700 {} \;
```

## Backup Security

### GPG Key Backup
```bash
# Backup to encrypted USB drive
gpg --export-secret-keys --armor YOUR_KEY_ID > /media/usb/gpg-backup.asc

# Backup to encrypted cloud storage
gpg --export-secret-keys --armor YOUR_KEY_ID | \
  gpg --symmetric --cipher-algo AES256 > gpg-backup.asc.gpg
```

### Password Store Backup
```bash
# Create encrypted backup
make backup              # Includes password store
make backup-minimal      # Excludes secrets

# Manual encrypted backup
tar -czf - ~/.password-store | \
  gpg --symmetric --cipher-algo AES256 > pass-backup.tar.gz.gpg
```

### Restore from Backup
```bash
# Restore GPG keys
gpg --import < /media/usb/gpg-backup.asc

# Restore password store
make restore
# OR
gpg --decrypt pass-backup.tar.gz.gpg | tar -xzf -
```

## Network Security

### SSH Configuration
```bash
# Generate secure SSH key
ssh-keygen -t ed25519 -b 4096 -f ~/.ssh/id_ed25519

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Configure SSH client
cat >> ~/.ssh/config << EOF
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
EOF
```

### Git Security
```bash
# Sign commits with GPG
git config --global commit.gpgsign true
git config --global user.signingkey YOUR_KEY_ID

# Verify signed commits
git log --show-signature
```

## Incident Response

### If Secrets Are Compromised

1. **Immediate Actions**
   ```bash
   # Revoke compromised keys immediately
   # Change passwords on affected services
   # Remove from git history if committed
   ```

2. **Clean Git History**
   ```bash
   # Remove from recent commits
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/secret/file' \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push (destructive)
   git push origin --force --all
   ```

3. **Audit and Prevention**
   ```bash
   # Scan entire repository
   make check-secrets
   
   # Update security practices
   make install-hooks
   make audit
   ```

### Regular Security Maintenance

```bash
# Weekly security check
make doctor

# Monthly audit
make audit
./scripts/validate-config.sh

# Quarterly key rotation
# Generate new GPG key
# Update pass with new key
# Backup old keys securely
```

## Security Tools

### Repository Scanning
- **Pre-commit hooks** - Real-time secret detection
- **make check-secrets** - Repository-wide scanning
- **make audit** - Configuration security review

### External Tools
```bash
# Install additional security tools
brew install git-secrets    # Git secrets scanner
brew install gitleaks       # Advanced secret detection
brew install age            # Modern encryption tool
```

### Integration with CI/CD
The repository includes GitHub Actions workflows that:
- Run security scans on all commits
- Check for exposed secrets
- Validate configuration integrity
- Test backup/restore procedures

## Best Practices Summary

1. **Use pass for all secrets** - Never store secrets in plain text
2. **Regular backups** - Backup GPG keys and password store
3. **Strong passphrases** - Use unique, complex passphrases
4. **Audit regularly** - Check for accidentally committed secrets
5. **Rotate keys** - Update keys and passwords periodically
6. **Secure transport** - Use encrypted channels for key exchange
7. **Minimal exposure** - Only grant necessary permissions
8. **Monitor access** - Review git logs and access patterns

For additional security questions, run `make doctor` for a comprehensive security health check.