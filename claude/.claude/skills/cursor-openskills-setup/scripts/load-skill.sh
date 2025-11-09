#!/usr/bin/env bash
# Helper script to load OpenSkills for Cursor IDE
# Usage: ./load-skill.sh [skill-name]

set -e

SKILL_NAME="${1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_error() {
    echo -e "${RED}Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if openskills is installed
if ! command -v openskills &> /dev/null; then
    print_error "openskills CLI not found. Install with: npm i -g openskills"
    exit 1
fi

# If no skill name provided, show available skills
if [[ -z "$SKILL_NAME" ]]; then
    print_info "Available skills:"
    echo ""
    openskills list
    echo ""
    print_info "Usage: $0 <skill-name>"
    exit 0
fi

# Load the skill
print_info "Loading skill: $SKILL_NAME"
echo ""

if openskills read "$SKILL_NAME"; then
    print_success "Skill loaded successfully!"
    echo ""
    print_info "Copy the output above and paste it into your Cursor chat to activate the skill."
else
    print_error "Failed to load skill: $SKILL_NAME"
    echo ""
    print_info "Check available skills with: $0"
    exit 1
fi
