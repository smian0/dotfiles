#!/usr/bin/env bash
# Wrapper for backup and restore operations
# Delegates to system script and supports new features
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_SCRIPT="$SCRIPT_DIR/../system/backup-restore.sh"

if [[ ! -f "$SYSTEM_SCRIPT" ]]; then
  echo "[ERROR] System backup script not found: $SYSTEM_SCRIPT"
  exit 1
fi

# Parse additional flags
INCREMENTAL=false
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --incremental)
      INCREMENTAL=true
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [[ "$INCREMENTAL" == true && "$1" == "backup" ]]; then
  # Run Borg incremental backup instead of basic backup
  exec "$SCRIPT_DIR/backup/borg-backup.sh" create
else
  exec "$SYSTEM_SCRIPT" "$@"
fi
