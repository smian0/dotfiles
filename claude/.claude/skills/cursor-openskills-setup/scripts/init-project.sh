#!/usr/bin/env bash
# Initialize OpenSkills for Cursor IDE in a project
# This script sets up the OpenSkills system for use with Cursor
# Part of the cursor-openskills-setup skill (self-contained)

set -e

# Get script directory and skill base directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$SKILL_DIR/templates"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_error() {
    echo -e "${RED}✗ Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
}

# Check if openskills is installed
if ! command -v openskills &> /dev/null; then
    print_error "openskills CLI not found"
    print_info "Install with: npm i -g openskills"
    exit 1
fi

# Get project directory (current directory by default)
PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR" || exit 1

print_header "Initializing OpenSkills for Cursor IDE"
print_info "Project directory: $(pwd)"

# Step 1: Create AGENTS.md if it doesn't exist
print_info "Step 1: Creating AGENTS.md..."
if [[ -f "AGENTS.md" ]]; then
    print_warning "AGENTS.md already exists. Skipping creation."
else
    # Use bundled template
    if [[ -f "$TEMPLATE_DIR/AGENTS.md.template" ]]; then
        cp "$TEMPLATE_DIR/AGENTS.md.template" AGENTS.md
        print_success "AGENTS.md created from bundled template"
    else
        print_error "Template not found: $TEMPLATE_DIR/AGENTS.md.template"
        exit 1
    fi
fi

# Step 2: Prompt for skill installation
print_info "Step 2: Install skills (optional)..."
echo ""
echo "OpenSkills will automatically find skills at ~/.claude/skills/ (global)."
echo ""
echo "Do you want to install additional skills from Anthropic marketplace?"
echo "  1) Yes - Install from anthropics/skills"
echo "  2) No - Use existing global skills only"
echo ""
read -rp "Enter choice [1-2]: " choice

case "$choice" in
    1)
        print_info "Installing from Anthropic marketplace..."
        if openskills install anthropics/skills; then
            print_success "Installed Anthropic skills"
        else
            print_error "Failed to install from marketplace"
        fi
        ;;
    2)
        print_info "Using existing global skills at ~/.claude/skills/"
        ;;
    *)
        print_warning "Invalid choice. Using existing global skills."
        ;;
esac

# Step 3: Sync AGENTS.md
print_info "Step 3: Syncing AGENTS.md with installed skills..."
if openskills sync; then
    print_success "AGENTS.md updated with skill metadata"
else
    print_warning "Sync failed or no skills installed yet"
fi

# Step 4: Show next steps
print_header "Setup Complete!"
echo ""
print_success "OpenSkills is now configured for this project"
echo ""
print_info "How to use in Cursor IDE:"
echo "  1. Open this project in Cursor IDE"
echo "  2. Cursor will automatically read AGENTS.md"
echo "  3. In Cursor chat, invoke skills via: Bash(\"openskills read <skill-name>\")"
echo ""
print_info "How to use in Claude Code:"
echo "  1. Use the Skill tool to invoke skills automatically"
echo "  2. Skills are discovered from ~/.claude/skills/ (global)"
echo ""
print_info "Available skills:"
if command -v openskills &> /dev/null; then
    openskills list
fi
echo ""
print_info "For more info: https://github.com/numman-ali/openskills"
echo ""
