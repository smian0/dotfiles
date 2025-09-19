#!/usr/bin/env bash
# Cloud synchronization using rclone (Backblaze B2)
# Expects rclone config at ~/.config/rclone/rclone.conf (template provided)
set -euo pipefail

# Remote name (configured in rclone.conf)
REMOTE="b2-dotfiles"
# Local backup directory (uses existing backup dir)
LOCAL_BACKUP="$HOME/.dotfiles-backups"

usage(){
  echo "Usage: $0 [sync|list|check]"
  exit 1
}

case "${1:-}" in
  sync)
    echo "Syncing local backups to $REMOTE..."
    rclone sync "$LOCAL_BACKUP" "$REMOTE:backups" --progress
    ;;
  list)
    echo "Listing remote backup contents:"
    rclone lsd "$REMOTE:backups"
    ;;
  check)
    echo "Running integrity check on remote..."
    rclone check "$LOCAL_BACKUP" "$REMOTE:backups"
    ;;
  *)
    usage
    ;;
esac
