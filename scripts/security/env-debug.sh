#!/bin/bash
# Environment Variable Diagnostic Tool
# Quickly compare system-wide (launchctl) vs shell environment variables

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Environment Variable Diagnostic${NC}"
echo "=================================="

# Key environment variables to check
VARS=(
    "GITHUB_TOKEN"
    "OPENAI_API_KEY" 
    "ANTHROPIC_API_KEY"
    "BRAVE_API_KEY"
    "OLLAMA_API_KEY"
    "DEEPSEEK_API_KEY"
    "GLM_API_KEY"
    "KIMI_API_KEY"
)

echo -e "\n${BLUE}📊 Comparison: System (launchctl) vs Shell Environment${NC}"
echo "--------------------------------------------------------"

for var in "${VARS[@]}"; do
    # Get system-wide value
    system_val=$(launchctl getenv "$var" 2>/dev/null || echo "")
    
    # Get shell environment value
    shell_val=$(printenv "$var" 2>/dev/null || echo "")
    
    # Compare values
    if [[ -n "$system_val" && -n "$shell_val" ]]; then
        if [[ "$system_val" == "$shell_val" ]]; then
            echo -e "${GREEN}✓${NC} $var: ${GREEN}MATCH${NC}"
        else
            echo -e "${RED}✗${NC} $var: ${RED}MISMATCH${NC}"
            echo -e "  System:  ${system_val:0:20}..."
            echo -e "  Shell:   ${shell_val:0:20}..."
        fi
    elif [[ -n "$system_val" && -z "$shell_val" ]]; then
        echo -e "${YELLOW}⚠${NC} $var: System set, Shell empty"
        echo -e "  System: ${system_val:0:20}..."
    elif [[ -z "$system_val" && -n "$shell_val" ]]; then
        echo -e "${YELLOW}⚠${NC} $var: Shell set, System empty"
        echo -e "  Shell: ${shell_val:0:20}..."
    else
        echo -e "${RED}○${NC} $var: Not set in either"
    fi
done

echo -e "\n${BLUE}🔧 Quick Fixes${NC}"
echo "=============="
echo "Fix shell environment:    export GITHUB_TOKEN=\$(launchctl getenv GITHUB_TOKEN)"
echo "Update system:           scripts/mcp-env/set-mcp-env-system.sh"
echo "Sync all to system:      source <(env-sync)"
echo "Check pass store:        pass show api/github-smian0"

# Show sources of potential conflicts
echo -e "\n${BLUE}🔍 Potential Conflict Sources${NC}"
echo "=============================="

# Check common locations where env vars might be set
conflict_files=(
    "$HOME/.zshrc"
    "$HOME/.bashrc" 
    "$HOME/.profile"
    "$PWD/.envrc"
    "$PWD/.env"
    "$PWD/.env.local"
)

for file in "${conflict_files[@]}"; do
    if [[ -f "$file" ]]; then
        if grep -q "GITHUB_TOKEN" "$file" 2>/dev/null; then
            echo -e "${YELLOW}⚠${NC} Found GITHUB_TOKEN in: $file"
        fi
    fi
done

# Check if direnv is active
if command -v direnv >/dev/null 2>&1 && [[ -f "$PWD/.envrc" ]]; then
    echo -e "${YELLOW}⚠${NC} direnv detected - check .envrc file"
fi

echo -e "\n${GREEN}💡 Tip: Run 'env-sync' to fix mismatches${NC}"