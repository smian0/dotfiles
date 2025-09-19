#!/usr/bin/env bash
# Backup health monitoring script
# Checks latest backup integrity and reports status
set -euo pipefail

# Path to the main backup script
BACKUP_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)/backup-restore.sh"

if [[ ! -x "$BACKUP_SCRIPT" ]]; then
  echo "[ERROR] Backup script not found or not executable: $BACKUP_SCRIPT"
  exit 1
fi

echo "Running backup verification..."
if "$BACKUP_SCRIPT" verify; then
  echo "[OK] Latest backup verified successfully."
else
  echo "[WARN] Backup verification failed."
  # Optionally extend to send alerts (email, push, etc.)
fi
