#!/usr/bin/env bash
# Restore Cursor user rules from backup file
# Usage: ./restore-user-rules.sh <backup-file>

set -e

CURSOR_DB="$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_error() { echo -e "${RED}✗ $1${NC}" >&2; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Check arguments
if [[ -z "$1" ]]; then
    print_error "Usage: $0 <backup-file>"
    print_info "Available backups:"
    ls -1t "$HOME/dotfiles/cursor/user-rules/.backups" | head -5
    exit 1
fi

BACKUP_FILE="$1"

if [[ ! -f "$BACKUP_FILE" ]]; then
    print_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

if [[ ! -f "$CURSOR_DB" ]]; then
    print_error "Cursor database not found: $CURSOR_DB"
    exit 1
fi

print_warning "This will replace your current Cursor user rules!"
print_info "Current backup preview (first 5 lines):"
head -5 "$BACKUP_FILE"
echo ""
read -rp "Continue? (y/N): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    print_info "Restore cancelled"
    exit 0
fi

print_info "Restoring user rules from: $BACKUP_FILE"

# Read backup content
BACKUP_CONTENT=$(cat "$BACKUP_FILE")

# Escape single quotes for SQL
ESCAPED_CONTENT=$(echo "$BACKUP_CONTENT" | sed "s/'/''/g")

# Restore to database
sqlite3 "$CURSOR_DB" <<EOF
INSERT OR REPLACE INTO ItemTable (key, value)
VALUES ('aicontext.personalContext', '$ESCAPED_CONTENT');
EOF

if [[ $? -eq 0 ]]; then
    print_success "User rules restored successfully!"
    echo ""
    print_info "Restart Cursor IDE for changes to take effect"
else
    print_error "Failed to restore user rules"
    exit 1
fi
