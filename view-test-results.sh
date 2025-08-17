#!/usr/bin/env bash
# View test results from Docker E2E tests

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}Docker E2E Test Results${NC}"
echo "========================"
echo

EXPORT_DIR="tests/docker/exports"

if [[ ! -d "$EXPORT_DIR" ]]; then
    echo "No test results found. Run 'make test' first."
    exit 1
fi

# Find all test exports
for test_dir in "$EXPORT_DIR"/*; do
    if [[ -d "$test_dir" ]]; then
        test_name=$(basename "$test_dir" | cut -d'-' -f1)
        timestamp=$(basename "$test_dir" | cut -d'-' -f2-)
        
        echo -e "${BLUE}Test: $test_name${NC} (Run: $timestamp)"
        echo "----------------------------------------"
        
        # Count symlinks
        symlink_count=$(find "$test_dir" -maxdepth 1 -type l 2>/dev/null | wc -l)
        echo -e "  ${GREEN}Symlinks created:${NC} $symlink_count"
        
        # List symlinks
        echo -e "  ${YELLOW}Installed configs:${NC}"
        find "$test_dir" -maxdepth 1 -type l -exec basename {} \; 2>/dev/null | while read -r link; do
            target=$(readlink "$test_dir/$link" 2>/dev/null)
            echo "    $link → $target"
        done
        
        echo
    fi
done

echo -e "${BOLD}Quick Commands:${NC}"
echo "  Open latest results:  open $EXPORT_DIR/*/"
echo "  Browse symlinks:      ls -la $EXPORT_DIR/*/*.* | grep '^l'"
echo "  Clean old results:    rm -rf $EXPORT_DIR/*"