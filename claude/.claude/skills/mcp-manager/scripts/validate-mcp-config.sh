#!/bin/bash

# Comprehensive validation of MCP configurations
# Usage: validate-mcp-config.sh [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Options
SYNTAX_ONLY=false
CONSISTENCY_ONLY=false
FIX=false
REPORT=false
SCOPE="user"

# Usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --project           Validate project config instead of user"
    echo "  --syntax-only       Only check JSON syntax"
    echo "  --consistency-only  Only check server-permission consistency"
    echo "  --fix              Attempt to auto-fix common issues"
    echo "  --report           Generate detailed validation report"
    echo "  -h, --help         Show this help"
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project)
            SCOPE="project"
            shift
            ;;
        --syntax-only)
            SYNTAX_ONLY=true
            shift
            ;;
        --consistency-only)
            CONSISTENCY_ONLY=true
            shift
            ;;
        --fix)
            FIX=true
            shift
            ;;
        --report)
            REPORT=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Determine file paths
if [[ "$SCOPE" == "project" ]]; then
    MCP_FILE="./.claude/.mcp.json"
    SETTINGS_FILE="./.claude/settings.json"
else
    MCP_FILE="${HOME}/.claude/.mcp.json"
    SETTINGS_FILE="${HOME}/.claude/settings.json"
fi

# Validation counters
ERRORS=0
WARNINGS=0
FIXED=0

# Report file
if [[ "$REPORT" == true ]]; then
    REPORT_FILE="mcp-validation-report-$(date +%Y%m%d_%H%M%S).txt"
    exec > >(tee "$REPORT_FILE")
fi

# Header
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    MCP Configuration Validator           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Scope:${NC} $SCOPE"
echo -e "${CYAN}MCP Config:${NC} $MCP_FILE"
echo -e "${CYAN}Settings:${NC} $SETTINGS_FILE"
echo ""

# Check if files exist
if [[ ! -f "$MCP_FILE" ]]; then
    echo -e "${RED}✗ Configuration file not found: $MCP_FILE${NC}"
    exit 1
fi

# Syntax validation
if [[ "$CONSISTENCY_ONLY" != true ]]; then
    echo -e "${BLUE}═══ Syntax Validation ═══${NC}"
    echo ""

    # Validate .mcp.json syntax
    echo -n "Checking $MCP_FILE syntax... "
    if jq empty "$MCP_FILE" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo -e "${RED}Invalid JSON syntax${NC}"
        jq . "$MCP_FILE" 2>&1 || true
        ((ERRORS++))
    fi

    # Validate settings.json syntax if exists
    if [[ -f "$SETTINGS_FILE" ]]; then
        echo -n "Checking $SETTINGS_FILE syntax... "
        if jq empty "$SETTINGS_FILE" 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            echo -e "${RED}Invalid JSON syntax${NC}"
            jq . "$SETTINGS_FILE" 2>&1 || true
            ((ERRORS++))
        fi
    fi

    echo ""
fi

# Structure validation
if [[ "$CONSISTENCY_ONLY" != true ]] && [[ "$SYNTAX_ONLY" != true ]]; then
    echo -e "${BLUE}═══ Structure Validation ═══${NC}"
    echo ""

    # Check required fields in each server
    SERVERS=$(jq -r '.mcpServers | keys[]' "$MCP_FILE" 2>/dev/null)
    for server in $SERVERS; do
        echo -n "Checking server '$server'... "

        # Check required fields
        HAS_COMMAND=$(jq -e ".mcpServers[\"$server\"].command" "$MCP_FILE" >/dev/null 2>&1 && echo "yes" || echo "no")
        HAS_ARGS=$(jq -e ".mcpServers[\"$server\"].args" "$MCP_FILE" >/dev/null 2>&1 && echo "yes" || echo "no")

        if [[ "$HAS_COMMAND" == "no" ]]; then
            echo -e "${RED}✗${NC}"
            echo -e "  ${RED}Missing required field: command${NC}"
            ((ERRORS++))
        elif [[ "$HAS_ARGS" == "no" ]]; then
            echo -e "${YELLOW}⚠${NC}"
            echo -e "  ${YELLOW}Missing 'args' field (should be array)${NC}"
            ((WARNINGS++))
        else
            echo -e "${GREEN}✓${NC}"
        fi

        # Check for common issues
        COMMAND=$(jq -r ".mcpServers[\"$server\"].command" "$MCP_FILE" 2>/dev/null || echo "")

        # Warn about absolute paths
        if [[ "$COMMAND" == /* ]]; then
            echo -e "  ${YELLOW}⚠ Using absolute path: $COMMAND${NC}"
            echo -e "    Consider using relative paths or environment variables"
            ((WARNINGS++))
        fi
    done

    echo ""
fi

# Consistency validation
if [[ "$SYNTAX_ONLY" != true ]]; then
    echo -e "${BLUE}═══ Consistency Validation ═══${NC}"
    echo ""

    if [[ ! -f "$SETTINGS_FILE" ]]; then
        echo -e "${YELLOW}⚠ Settings file not found: $SETTINGS_FILE${NC}"
        echo "  Cannot validate permissions consistency"
        ((WARNINGS++))
    else
        # Get all servers
        SERVERS=$(jq -r '.mcpServers | keys[]' "$MCP_FILE" 2>/dev/null | sort)

        # Get all MCP permission prefixes
        PERMISSION_SERVERS=$(jq -r '.permissions.allow[] | select(startswith("mcp__"))' "$SETTINGS_FILE" 2>/dev/null | \
            awk -F'__' '{print $2}' | sort -u)

        # Check for servers without permissions
        echo -e "${CYAN}Checking servers have permissions...${NC}"
        for server in $SERVERS; do
            HAS_PERMISSIONS=$(echo "$PERMISSION_SERVERS" | grep -x "$server" || echo "")

            if [[ -z "$HAS_PERMISSIONS" ]]; then
                echo -e "  ${YELLOW}⚠ Server '$server' has no permissions${NC}"
                ((WARNINGS++))

                if [[ "$FIX" == true ]]; then
                    echo -e "    ${CYAN}[FIX] Add tool permissions manually to settings.json${NC}"
                fi
            else
                echo -e "  ${GREEN}✓ Server '$server' has permissions${NC}"
            fi
        done

        echo ""

        # Check for orphaned permissions
        echo -e "${CYAN}Checking for orphaned permissions...${NC}"
        for perm_server in $PERMISSION_SERVERS; do
            HAS_SERVER=$(echo "$SERVERS" | grep -x "$perm_server" || echo "")

            if [[ -z "$HAS_SERVER" ]]; then
                echo -e "  ${RED}✗ Orphaned permissions for '$perm_server'${NC}"
                ORPHANED_PERMS=$(jq -r ".permissions.allow[] | select(startswith(\"mcp__${perm_server}__\"))" "$SETTINGS_FILE")
                echo "$ORPHANED_PERMS" | sed 's/^/    /'
                ((ERRORS++))

                if [[ "$FIX" == true ]]; then
                    echo -e "    ${CYAN}[FIX] Removing orphaned permissions...${NC}"

                    # Remove orphaned permissions
                    JQ_FILTER=".permissions.allow |= map(select(startswith(\"mcp__${perm_server}__\") | not))"
                    jq "$JQ_FILTER" "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp"
                    mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"

                    echo -e "    ${GREEN}✓ Removed orphaned permissions${NC}"
                    ((FIXED++))
                fi
            fi
        done

        if [[ $(echo "$PERMISSION_SERVERS" | wc -w) -eq 0 ]]; then
            echo -e "  ${GREEN}✓ No orphaned permissions${NC}"
        fi

        echo ""
    fi
fi

# Summary
echo -e "${BLUE}═══ Validation Summary ═══${NC}"
echo ""

if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    SERVER_COUNT=$(jq '.mcpServers | length' "$MCP_FILE")
    echo -e "${CYAN}Total servers configured: $SERVER_COUNT${NC}"

    if [[ -f "$SETTINGS_FILE" ]]; then
        PERMISSION_COUNT=$(jq -r '.permissions.allow[] | select(startswith("mcp__"))' "$SETTINGS_FILE" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "${CYAN}Total MCP permissions: $PERMISSION_COUNT${NC}"
    fi
elif [[ $ERRORS -eq 0 ]]; then
    echo -e "${YELLOW}⚠ Validation completed with warnings${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    if [[ $FIXED -gt 0 ]]; then
        echo -e "${GREEN}Fixed: $FIXED${NC}"
    fi
else
    echo -e "${RED}✗ Validation failed${NC}"
    echo -e "${RED}Errors: $ERRORS${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    if [[ $FIXED -gt 0 ]]; then
        echo -e "${GREEN}Fixed: $FIXED${NC}"
    fi
fi

echo ""

if [[ "$REPORT" == true ]]; then
    echo -e "${CYAN}Report saved to: $REPORT_FILE${NC}"
fi

# Exit with appropriate code
if [[ $ERRORS -gt 0 ]]; then
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    exit 2
else
    exit 0
fi
