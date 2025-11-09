#!/usr/bin/env bash
# Backup current Cursor user rules from SQLite database
# Usage: ./backup-user-rules.sh [output-file]

set -e

CURSOR_DB="$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
USER_RULES_DIR="$HOME/dotfiles/cursor/user-rules"
BACKUP_DIR="$USER_RULES_DIR/.backups"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_error() { echo -e "${RED}✗ $1${NC}" >&2; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

# Check if Cursor DB exists
if [[ ! -f "$CURSOR_DB" ]]; then
    print_error "Cursor database not found: $CURSOR_DB"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Determine output file
if [[ -n "$1" ]]; then
    OUTPUT_FILE="$1"
else
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT_FILE="$BACKUP_DIR/user-rules-$TIMESTAMP.txt"
fi

print_info "Backing up Cursor user rules..."

# Extract current user rules
sqlite3 "$CURSOR_DB" \
    "SELECT value FROM ItemTable WHERE key = 'aicontext.personalContext';" \
    > "$OUTPUT_FILE" 2>/dev/null

if [[ $? -eq 0 ]]; then
    print_success "Backup saved to: $OUTPUT_FILE"
    echo ""
    print_info "Preview (first 10 lines):"
    head -10 "$OUTPUT_FILE"
else
    print_error "Failed to backup user rules"
    exit 1
fi
