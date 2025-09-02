#!/bin/bash
# Force bash to run in mode that supports associative arrays
if [ -z "${BASH_VERSION}" ] || [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo "This script requires bash 4.0 or higher for associative arrays"
    exit 1
fi
# MCP Environment Status Checker
# Shows current status of all MCP environment variables and their pass store availability

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print section headers
print_header() {
    echo -e "\n${CYAN}===================================================${NC}"
    echo -e "${CYAN} $1${NC}"
    echo -e "${CYAN}===================================================${NC}"
}

print_subheader() {
    echo -e "\n${BLUE}--- $1 ---${NC}"
}

# Check if pass is available
if ! command -v pass >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: pass command not found${NC}"
    echo "Please install pass: brew install pass"
    exit 1
fi

# Check if launchctl is available
if ! command -v launchctl >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: launchctl command not found (macOS only)${NC}"
    exit 1
fi

print_header "MCP Environment Variable Status"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/env-mapping.conf"

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}❌ Error: Configuration file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Declare associative array for environment mappings
declare -A ENV_MAPPING

# Read the configuration file and populate the array
while IFS='=' read -r env_var pass_path || [[ -n "$env_var" ]]; do
    # Skip empty lines and comments
    if [[ -z "$env_var" || "$env_var" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Remove any whitespace
    env_var=$(echo "$env_var" | xargs)
    pass_path=$(echo "$pass_path" | xargs)
    
    if [[ -n "$env_var" && -n "$pass_path" ]]; then
        ENV_MAPPING["$env_var"]="$pass_path"
    fi
done < "$CONFIG_FILE"

echo -e "${BLUE}📋 Loaded ${#ENV_MAPPING[@]} environment mappings from: $CONFIG_FILE${NC}"

# Arrays to track status
available_vars=()
missing_vars=()
pass_available=()
pass_missing=()

print_subheader "Checking Environment Variables"

# Check each environment variable
for env_var in "${!ENV_MAPPING[@]}"; do
    pass_path="${ENV_MAPPING[$env_var]}"
    
    # Check if environment variable is set
    env_value=""
    if env_output=$(launchctl getenv "$env_var" 2>/dev/null); then
        env_value="$env_output"
    fi
    
    # Check if credential exists in pass
    pass_exists=false
    if pass show "$pass_path" >/dev/null 2>&1; then
        pass_exists=true
        pass_available+=("$env_var")
    else
        pass_missing+=("$pass_path")
    fi
    
    # Determine status
    if [[ -n "$env_value" ]]; then
        # Truncate value for security
        truncated_value="${env_value:0:8}...${env_value: -3}"
        if $pass_exists; then
            echo -e "  ${GREEN}✅ $env_var${NC} = ${truncated_value} (from pass:$pass_path)"
        else
            echo -e "  ${YELLOW}⚠️  $env_var${NC} = ${truncated_value} (set but no pass entry)"
        fi
        available_vars+=("$env_var")
    else
        if $pass_exists; then
            echo -e "  ${YELLOW}📦 $env_var${NC} = empty (available in pass:$pass_path)"
        else
            echo -e "  ${RED}❌ $env_var${NC} = empty (no pass entry: $pass_path)"
        fi
        missing_vars+=("$env_var")
    fi
done

# Summary statistics
print_subheader "Summary"
total_vars=${#ENV_MAPPING[@]}
available_count=${#available_vars[@]}
missing_count=${#missing_vars[@]}
pass_available_count=${#pass_available[@]}

echo -e "  ${BLUE}Total Variables Configured:${NC} $total_vars"
echo -e "  ${GREEN}Environment Variables Set:${NC} $available_count ($((available_count * 100 / total_vars))%)"
echo -e "  ${RED}Environment Variables Missing:${NC} $missing_count ($((missing_count * 100 / total_vars))%)"
echo -e "  ${CYAN}Available in Pass Store:${NC} $pass_available_count"

# Show missing credentials that need to be added to pass
if [ ${#pass_missing[@]} -gt 0 ]; then
    print_subheader "Missing Pass Credentials"
    echo -e "${YELLOW}Add these credentials to unlock MCP servers:${NC}"
    for pass_path in "${pass_missing[@]}"; do
        echo -e "  ${YELLOW}📝${NC} pass insert $pass_path"
    done
fi

# Show available credentials that aren't loaded
unloaded_vars=()
for env_var in "${!ENV_MAPPING[@]}"; do
    pass_path="${ENV_MAPPING[$env_var]}"
    env_value=$(launchctl getenv "$env_var" 2>/dev/null || echo "")
    
    if [[ -z "$env_value" ]] && pass show "$pass_path" >/dev/null 2>&1; then
        unloaded_vars+=("$env_var")
    fi
done

if [ ${#unloaded_vars[@]} -gt 0 ]; then
    print_subheader "Available but Not Loaded"
    echo -e "${CYAN}These credentials are in pass but not loaded to environment:${NC}"
    for env_var in "${unloaded_vars[@]}"; do
        echo -e "  ${CYAN}🔄${NC} $env_var (run: ./scripts/mcp-env/set-mcp-env-system.sh)"
    done
fi

# Check LaunchAgent status
print_subheader "LaunchAgent Status"
if launchctl list | grep -q "com.mcp.env.agent"; then
    echo -e "  ${GREEN}✅ MCP Environment Agent is running${NC}"
else
    echo -e "  ${RED}❌ MCP Environment Agent is not running${NC}"
    echo -e "     ${YELLOW}Fix: launchctl load ~/Library/LaunchAgents/com.mcp.env.agent.plist${NC}"
fi

# Check for recent logs
print_subheader "Recent Logs"
if [[ -f "/tmp/mcp-env-agent.log" ]]; then
    echo -e "  ${GREEN}📄 Agent log available:${NC} /tmp/mcp-env-agent.log"
    echo -e "  ${BLUE}Last run:${NC} $(tail -1 /tmp/mcp-env-agent.log 2>/dev/null || echo 'No recent logs')"
else
    echo -e "  ${YELLOW}⚠️  No agent log found${NC}"
fi

if [[ -f "/tmp/mcp-env-agent.error.log" ]]; then
    error_count=$(wc -l < /tmp/mcp-env-agent.error.log 2>/dev/null || echo 0)
    if [[ $error_count -gt 0 ]]; then
        echo -e "  ${RED}🚨 Errors found:${NC} /tmp/mcp-env-agent.error.log ($error_count lines)"
    fi
fi

# Quick action suggestions
print_subheader "Quick Actions"

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo -e "${YELLOW}To load available credentials:${NC}"
    echo -e "  ./scripts/mcp-env/set-mcp-env-system.sh"
fi

if [ ${#pass_missing[@]} -gt 0 ]; then
    echo -e "${YELLOW}To add missing high-priority credentials:${NC}"
    echo -e "  pass insert api/openai"
    echo -e "  pass insert api/anthropic"
    echo -e "  pass insert api/supabase"
fi

echo -e "${CYAN}To test MCP servers:${NC}"
echo -e "  npx -y @modelcontextprotocol/server-brave-search  # (should work)"

echo -e "\n${GREEN}Status check complete!${NC}"
