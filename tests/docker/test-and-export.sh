#!/usr/bin/env bash
# Run Docker test and automatically export results for review

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.incremental.yml"

# Parse arguments
LEVEL="${1:-quick}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EXPORT_DIR="$PROJECT_ROOT/tests/review/${LEVEL}-${TIMESTAMP}"

# Logging
log() { echo -e "${GREEN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }

# Main execution
main() {
    log "Running $LEVEL test with automatic export..."
    
    # Create export directory
    mkdir -p "$EXPORT_DIR"
    
    # Run the test in a container (not detached so we can see output)
    local service="dotfiles-$LEVEL"
    log "Starting test container..."
    
    # Build if needed
    docker-compose -f "$COMPOSE_FILE" build "$service" 2>/dev/null
    
    # Run the test
    log "Running $LEVEL tests..."
    docker-compose -f "$COMPOSE_FILE" run --name "${service}-export-${TIMESTAMP}" "$service" 2>&1 | tee "$EXPORT_DIR/test-output.log"
    
    # Get container ID
    local container_id=$(docker ps -aq -f "name=${service}-export-${TIMESTAMP}" | head -1)
    
    if [[ -z "$container_id" ]]; then
        error "Container not found after test"
        exit 1
    fi
    
    # Export the filesystem
    log "Exporting test results..."
    
    # Export home directory
    docker cp "$container_id:/home/testuser" "$EXPORT_DIR/home" 2>/dev/null || error "Could not export home directory"
    
    # Create a summary of what was installed
    log "Generating summary..."
    cat > "$EXPORT_DIR/REVIEW.md" << EOF
# Docker Test Review
**Test Level:** $LEVEL
**Date:** $(date)
**Container:** ${service}-export-${TIMESTAMP}

## Quick Review Commands

\`\`\`bash
# View test output
cat "$EXPORT_DIR/test-output.log"

# Check installed symlinks
ls -la "$EXPORT_DIR/home" | grep "^l"

# Browse the exported home directory
open "$EXPORT_DIR/home"  # macOS
# or
nautilus "$EXPORT_DIR/home"  # Linux

# View specific config files
ls -la "$EXPORT_DIR/home/.git*"
ls -la "$EXPORT_DIR/home/.zsh*"
\`\`\`

## Symlinks Created
\`\`\`
EOF
    
    # List symlinks (wait a moment for container to be ready)
    sleep 1
    docker exec "$container_id" find /home/testuser -maxdepth 2 -type l -exec ls -la {} \; 2>/dev/null >> "$EXPORT_DIR/REVIEW.md" || echo "No symlinks found" >> "$EXPORT_DIR/REVIEW.md"
    
    echo '```' >> "$EXPORT_DIR/REVIEW.md"
    echo "" >> "$EXPORT_DIR/REVIEW.md"
    echo "## Directory Structure" >> "$EXPORT_DIR/REVIEW.md"
    echo '```' >> "$EXPORT_DIR/REVIEW.md"
    docker exec "$container_id" ls -la /home/testuser 2>/dev/null >> "$EXPORT_DIR/REVIEW.md" || echo "Could not list directory" >> "$EXPORT_DIR/REVIEW.md"
    echo '```' >> "$EXPORT_DIR/REVIEW.md"
    
    # Test summary
    echo "" >> "$EXPORT_DIR/REVIEW.md"
    echo "## Test Summary" >> "$EXPORT_DIR/REVIEW.md"
    echo '```' >> "$EXPORT_DIR/REVIEW.md"
    tail -20 "$EXPORT_DIR/test-output.log" >> "$EXPORT_DIR/REVIEW.md"
    echo '```' >> "$EXPORT_DIR/REVIEW.md"
    
    # Clean up container
    log "Cleaning up container..."
    docker rm -f "$container_id" >/dev/null 2>&1
    
    # Success message
    echo
    success "Test complete and exported!"
    echo
    echo -e "${BOLD}📁 Review the results:${NC}"
    echo "   Directory: $EXPORT_DIR"
    echo "   Summary: $EXPORT_DIR/REVIEW.md"
    echo "   Home dir: $EXPORT_DIR/home/"
    echo
    echo -e "${BOLD}Quick commands:${NC}"
    echo "   cat $EXPORT_DIR/REVIEW.md    # View summary"
    echo "   ls -la $EXPORT_DIR/home/     # Browse home"
    echo "   open $EXPORT_DIR              # Open in Finder (macOS)"
    echo
}

# Run main
main