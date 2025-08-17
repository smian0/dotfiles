#!/usr/bin/env bash
# Simple E2E test for dotfiles
# Just run: ./test-dotfiles.sh

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}   Dotfiles E2E Test Suite${NC}"
echo -e "${BLUE}=====================================${NC}"
echo

# Run all scenarios
for scenario in basic claude full; do
    echo -e "\n${BLUE}Testing $scenario scenario...${NC}"
    echo "-------------------------------------"
    
    if docker-compose -f tests/docker/docker-compose.e2e.yml run --rm dotfiles-$scenario 2>&1 | tail -20; then
        echo -e "${GREEN}✅ $scenario test passed${NC}"
    else
        echo -e "${RED}❌ $scenario test failed${NC}"
    fi
done

echo
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}   All E2E Tests Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"

# Clean up
docker-compose -f tests/docker/docker-compose.e2e.yml down --volumes 2>/dev/null || true