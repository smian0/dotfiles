#!/usr/bin/env bash
# Verify Cursor + OpenSkills setup
# Usage: ./verify-setup.sh [--verbose]

set -e

VERBOSE=false
if [[ "$1" == "--verbose" ]]; then
    VERBOSE=true
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_error() { echo -e "${RED}✗ $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

ERRORS=0

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}  Cursor + OpenSkills Verification${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Check 1: Node.js
echo "1. Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js not found"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: openskills CLI
echo "2. Checking openskills CLI..."
if command -v openskills &> /dev/null; then
    OPENSKILLS_VERSION=$(openskills --version)
    print_success "openskills installed: v$OPENSKILLS_VERSION"
else
    print_error "openskills not found"
    print_info "Install with: npm i -g openskills"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: AGENTS.md in current directory
echo "3. Checking for AGENTS.md in current directory..."
if [[ -f "AGENTS.md" ]]; then
    print_success "AGENTS.md found"

    # Check format
    if grep -q "SKILLS_TABLE_START" AGENTS.md; then
        print_success "  Proper markers found"
    else
        print_warning "  Missing SKILLS_TABLE_START marker"
        print_info "  AGENTS.md may have incorrect format"
    fi

    # Check for skills
    SKILL_COUNT=$(grep -c "<skill>" AGENTS.md || echo "0")
    if [[ $SKILL_COUNT -gt 0 ]]; then
        print_success "  $SKILL_COUNT skill(s) configured"
    else
        print_warning "  No skills found in AGENTS.md"
        print_info "  Run: openskills sync"
    fi
else
    print_warning "AGENTS.md not found in $(pwd)"
    print_info "This is OK if you're not setting up a specific project"
fi

# Check 4: Global skills directory
echo "4. Checking global skills..."
if [[ -d "$HOME/.claude/skills" ]]; then
    GLOBAL_SKILL_COUNT=$(ls -1 "$HOME/.claude/skills" | wc -l | tr -d ' ')
    print_success "Global skills directory exists"
    print_info "  $GLOBAL_SKILL_COUNT skill(s) in ~/.claude/skills/"
else
    print_warning "No global skills directory (~/.claude/skills/)"
    print_info "Skills can still be installed per-project"
fi

# Check 5: Cursor database
echo "5. Checking Cursor database..."
CURSOR_DB="$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
if [[ -f "$CURSOR_DB" ]]; then
    print_success "Cursor database found"

    # Check for user rules
    if sqlite3 "$CURSOR_DB" "SELECT value FROM ItemTable WHERE key = 'aicontext.personalContext';" 2>/dev/null | grep -q "OpenSkills"; then
        print_success "  OpenSkills user rule detected"
    else
        print_info "  No OpenSkills user rule found"
        print_info "  To add: ~/dotfiles/cursor/scripts/sync-user-rules.sh"
    fi
else
    print_warning "Cursor database not found"
    print_info "Cursor may not have been run yet"
fi

# Check 6: Dotfiles cursor package
echo "6. Checking dotfiles cursor package..."
if [[ -f "$HOME/dotfiles/cursor/user-rules/openskills.md" ]]; then
    print_success "Cursor user rule template found"
fi

if [[ -f "$HOME/dotfiles/cursor/scripts/sync-user-rules.sh" ]]; then
    print_success "Sync scripts available"
fi

# Summary
echo ""
echo -e "${BLUE}===================================${NC}"
if [[ $ERRORS -eq 0 ]]; then
    print_success "All critical checks passed!"
else
    print_error "$ERRORS error(s) found"
    echo ""
    print_info "See messages above for details"
fi
echo -e "${BLUE}===================================${NC}"

if [[ $VERBOSE == true ]]; then
    echo ""
    echo "Verbose output:"
    echo ""
    echo "Available skills:"
    if command -v openskills &> /dev/null; then
        openskills list
    fi
fi

exit $ERRORS
