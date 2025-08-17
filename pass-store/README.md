# Pass Store

GPG-encrypted password store for secure credential management across machines.

## ⚠️ Security Notice

This repository contains **GPG-encrypted passwords only**. Never commit unencrypted secrets.

## Prerequisites

- GPG key pair configured
- Pass password manager installed
- Git (for synchronization)

## Setup

### 1. Install pass

**macOS:**
```bash
brew install pass
```

**Ubuntu/Debian:**
```bash
sudo apt-get install pass
```

### 2. Import your GPG key

If you already have a GPG key:
```bash
# Import private key
gpg --import private-key.asc

# Trust the key
gpg --edit-key YOUR_KEY_ID
# Type: trust, 5, y, quit
```

If you need to create a new key:
```bash
gpg --full-generate-key
# Choose: RSA and RSA, 4096 bits, key doesn't expire
```

### 3. Initialize pass

```bash
# Initialize with your GPG key
pass init "Your Name <your.email@example.com>"

# Or use key ID
pass init YOUR_GPG_KEY_ID
```

### 4. Clone this repository

```bash
# Remove the default pass store
rm -rf ~/.password-store

# Clone this repository
git clone git@github.com:smian0/pass-store.git ~/.password-store
```

## Directory Structure

```
~/.password-store/
├── api/                 # API keys and tokens
│   ├── openai.gpg
│   ├── anthropic.gpg
│   └── github.gpg
├── services/           # Service credentials
│   └── github.com/
│       └── token.gpg
└── personal/          # Personal accounts
```

## Usage

### Adding passwords

```bash
# Add a new password interactively
pass insert api/openai

# Add from clipboard (macOS)
pbpaste | pass insert -m api/openai

# Generate a random password
pass generate services/github.com/token 32
```

### Retrieving passwords

```bash
# Display password
pass show api/openai

# Copy to clipboard (clears after 45 seconds)
pass -c api/openai

# Show entire tree
pass
```

### Editing passwords

```bash
pass edit api/openai
```

### Removing passwords

```bash
pass rm api/openai
```

## Synchronization

Pass automatically creates git commits for changes:

```bash
# Push changes to remote
pass git push

# Pull changes from remote
pass git pull

# Check status
pass git status
```

## Integration with Dotfiles

The dotfiles repository includes helper scripts that retrieve credentials from pass:

```bash
# Example: Claude API key helper
#!/bin/bash
pass show api/anthropic
```

## Backup and Recovery

### Backup GPG keys

**CRITICAL: Keep these backups secure and offline!**

```bash
# Export public key
gpg --export --armor YOUR_KEY_ID > public-key.asc

# Export private key (KEEP SECURE!)
gpg --export-secret-keys --armor YOUR_KEY_ID > private-key.asc

# Export trust database
gpg --export-ownertrust > trustdb.txt
```

### Restore GPG keys

```bash
# Import keys
gpg --import public-key.asc
gpg --import private-key.asc

# Import trust
gpg --import-ownertrust < trustdb.txt
```

### Backup password store

```bash
# Create encrypted backup
tar czf - ~/.password-store | gpg --encrypt --recipient YOUR_KEY_ID > pass-backup.tar.gz.gpg

# Restore from backup
gpg --decrypt pass-backup.tar.gz.gpg | tar xzf - -C ~/
```

## Security Best Practices

1. **Use a strong GPG passphrase** - Your passwords are only as secure as your GPG key
2. **Regular backups** - Keep encrypted backups of both GPG keys and password store
3. **Secure key storage** - Store GPG key backups offline (USB drive in safe)
4. **Audit access** - Regularly review git log for unexpected changes
5. **Rotate passwords** - Periodically update critical passwords
6. **Use subkeys** - Consider using GPG subkeys for different machines

## Multi-Machine Setup

1. Export GPG key on original machine
2. Import GPG key on new machine
3. Clone this repository on new machine
4. Verify with `pass show api/test` (create a test entry)

## Troubleshooting

### GPG agent not running
```bash
gpg-agent --daemon
```

### Pass not finding GPG key
```bash
# Check available keys
gpg --list-secret-keys

# Re-initialize with correct key
pass init YOUR_KEY_ID
```

### Permission issues
```bash
# Fix permissions
chmod 700 ~/.password-store
find ~/.password-store -type f -exec chmod 600 {} \;
```

### Git conflicts
```bash
# If you get conflicts, resolve manually
pass git status
pass git diff
# Edit conflicted files with pass edit
pass git add -A
pass git commit -m "Resolved conflicts"
```

## Emergency Access

Consider setting up emergency access:
1. Create a recovery key with a trusted person
2. Use Shamir's Secret Sharing for key recovery
3. Document recovery process securely

## License

Private repository - Not for public use