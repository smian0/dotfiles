#!/usr/bin/env bash
# Pre-Launch Validation Script
# Quick validation of pre-launch functionality for OpenCode integration

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${BLUE}[Pre-Launch]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
warn() { echo -e "${YELLOW}⚠️${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1"; }

# Main validation
log "Validating pre-launch functionality..."

# Check OpenCode launcher
if [[ -f "bin/oc" ]] && [[ -x "bin/oc" ]]; then
    success "OpenCode launcher exists and is executable"
else
    error "OpenCode launcher missing or not executable"
    exit 1
fi

# Check pre-launch transformation script
if [[ -f "opencode/.config/opencode/scripts/pre-launch-transform.js" ]]; then
    success "Pre-launch transformation script exists"
else
    error "Pre-launch transformation script missing"
    exit 1
fi

# Check Node.js availability
if command -v node >/dev/null 2>&1; then
    success "Node.js is available for transformation"
else
    warn "Node.js not available - transformation will be skipped"
fi

# Check agent transformer core
if [[ -f "opencode/.config/opencode/plugin-util/agent-transformer-core.js" ]]; then
    success "Agent transformer core exists"
else
    error "Agent transformer core missing"
    exit 1
fi

# Check global Claude agents directory
if [[ -d "claude/.claude/agents" ]]; then
    agent_count=$(find "claude/.claude/agents" -name "*.md" -type f | wc -l)
    success "Global Claude agents directory exists with $agent_count agent(s)"
else
    warn "Global Claude agents directory not found"
fi

# Check OpenCode configuration directories
config_dirs=(
    "opencode/.config/opencode/scripts"
    "opencode/.config/opencode/plugin-util"
)

for config_dir in "${config_dirs[@]}"; do
    if [[ -d "$config_dir" ]]; then
        success "Config directory exists: $config_dir"
    else
        error "Config directory missing: $config_dir"
        exit 1
    fi
done

# Test transformation script syntax
if command -v node >/dev/null 2>&1; then
    if node -c "opencode/.config/opencode/scripts/pre-launch-transform.js" 2>/dev/null; then
        success "Pre-launch transformation script syntax is valid"
    else
        warn "Pre-launch transformation script has syntax issues"
    fi
fi

# Test launcher script syntax
if bash -n "bin/oc" 2>/dev/null; then
    success "OpenCode launcher script syntax is valid"
else
    error "OpenCode launcher script has syntax issues"
    exit 1
fi

# Check for required functions in launcher
if grep -q "load_env_var" "bin/oc" && grep -q "run_pre_launch_transform" "bin/oc"; then
    success "OpenCode launcher has required functions"
else
    error "OpenCode launcher missing required functions"
    exit 1
fi

# Summary
log "Pre-launch validation completed successfully!"
log "The system is ready for OpenCode integration."

# Show next steps
echo
log "Next steps:"
echo "  1. Run 'make test-pre-launch' for comprehensive testing"
echo "  2. Use 'bin/oc' to launch OpenCode with pre-launch transformation"
echo "  3. Check OpenCode agent transformation in ~/.config/opencode/agent/"
echo
success "Pre-launch functionality is ready!"