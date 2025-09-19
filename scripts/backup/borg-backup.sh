#!/usr/bin/env bash
# Borg backup wrapper for dotfiles
# Requires borg and pass for encryption key retrieval
set -euo pipefail

# Default config paths
CONFIG_DIR="${HOME}/.dotfiles/backup/config"
REPO_PATH="${HOME}/.dotfiles-backups/borg-repo"
PASSPHRASE=$(pass show dotfiles/borg-passphrase 2>/dev/null || echo "")

usage(){
  echo "Usage: $0 [init|create|prune|list]"
  exit 1
}

if [[ -z "$PASSPHRASE" ]]; then
  echo "[WARN] Borg passphrase not found in password store. Using empty passphrase (insecure)."
fi

case "${1:-}" in
  init)
    echo "Initializing Borg repository at $REPO_PATH"
    export BORG_PASSPHRASE="$PASSPHRASE"
    borg init --encryption=repokey "$REPO_PATH"
    ;;
  create)
    echo "Creating Borg archive..."
    export BORG_PASSPHRASE="$PASSPHRASE"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    borg create "$REPO_PATH::dotfiles-$TIMESTAMP" "$HOME/.dotfiles" "$HOME/.config" "$HOME/.local/share"
    ;;
  prune)
    echo "Pruning old Borg archives..."
    export BORG_PASSPHRASE="$PASSPHRASE"
    borg prune -v --list "$REPO_PATH" --keep-daily=7 --keep-weekly=4 --keep-monthly=6
    ;;
  list)
    export BORG_PASSPHRASE="$PASSPHRASE"
    borg list "$REPO_PATH"
    ;;
  *)
    usage
    ;;
esac
