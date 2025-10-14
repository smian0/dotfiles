#!/usr/bin/env bash

# Backup current factory config
echo "Backing up current Factory configuration..."

# Backup current config
cp -f ~/.factory/config.json ~/.factory/config.json.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "No existing config.json to backup"

# Copy current config to this dotfiles package
cp ~/.factory/config.json ~/dotfiles/droid/.factory/ 2>/dev/null && echo "Configuration backed up successfully" || echo "Configuration backup completed from dotfiles"

echo "Current droid configuration:"
cat ~/dotfiles/droid/.factory/config.json | python3 -m json.tool
echo "Backup complete!"
