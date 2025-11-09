#!/usr/bin/env bash
# Sync version-controlled user rules to Cursor's SQLite database
# Usage: ./sync-user-rules.sh [rule-file]

set -e

CURSOR_DB="$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
USER_RULES_DIR="$HOME/dotfiles/cursor/user-rules"
DEFAULT_RULE="openskills.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_error() { echo -e "${RED}✗ $1${NC}" >&2; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Check if Cursor DB exists
if [[ ! -f "$CURSOR_DB" ]]; then
    print_error "Cursor database not found: $CURSOR_DB"
    print_info "Make sure Cursor IDE is installed and has been run at least once"
    exit 1
fi

# Get rule file
RULE_FILE="${1:-$DEFAULT_RULE}"
RULE_PATH="$USER_RULES_DIR/$RULE_FILE"

if [[ ! -f "$RULE_PATH" ]]; then
    print_error "Rule file not found: $RULE_PATH"
    print_info "Available rules:"
    ls -1 "$USER_RULES_DIR"
    exit 1
fi

print_info "Syncing user rule: $RULE_FILE"

# Read the rule content
RULE_CONTENT=$(cat "$RULE_PATH")

# Backup current user rules first
print_info "Creating backup..."
BACKUP_DIR="$HOME/dotfiles/cursor/user-rules/.backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sqlite3 "$CURSOR_DB" \
    "SELECT value FROM ItemTable WHERE key = 'aicontext.personalContext';" \
    > "$BACKUP_DIR/user-rules-$TIMESTAMP.txt" 2>/dev/null || true
print_success "Backup saved to: $BACKUP_DIR/user-rules-$TIMESTAMP.txt"

# Update the database
print_info "Updating Cursor database..."

# Escape single quotes for SQL
ESCAPED_CONTENT=$(echo "$RULE_CONTENT" | sed "s/'/''/g")

# Update or insert the rule
sqlite3 "$CURSOR_DB" <<EOF
INSERT OR REPLACE INTO ItemTable (key, value)
VALUES ('aicontext.personalContext', '$ESCAPED_CONTENT');
EOF

if [[ $? -eq 0 ]]; then
    print_success "User rule synced successfully!"
    echo ""
    print_info "Restart Cursor IDE for changes to take effect"
    print_info "Or reload the window: Cmd+Shift+P → 'Developer: Reload Window'"
else
    print_error "Failed to update database"
    print_warning "You can restore from backup: ./restore-user-rules.sh $BACKUP_DIR/user-rules-$TIMESTAMP.txt"
    exit 1
fi
