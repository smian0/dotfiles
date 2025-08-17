#!/usr/bin/env bash
# Generate comprehensive test report from Docker containers

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
REPORT_DIR="tests/reports/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$REPORT_DIR"

# Header
cat > "$REPORT_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Docker Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        h2 { color: #666; border-bottom: 1px solid #ccc; }
        .success { color: green; }
        .failure { color: red; }
        .warning { color: orange; }
        pre { background: #f4f4f4; padding: 10px; overflow-x: auto; }
        .container { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .symlink { color: blue; }
        .file { color: black; }
        .dir { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Docker Test Inspection Report</h1>
    <p>Generated: TIMESTAMP</p>
EOF

echo "TIMESTAMP: $(date)" >> "$REPORT_DIR/index.html"

# Function to inspect container
inspect_container() {
    local container="$1"
    local level="$2"
    
    echo "<div class='container'>" >> "$REPORT_DIR/index.html"
    echo "<h2>Container: $container (Level: $level)</h2>" >> "$REPORT_DIR/index.html"
    
    # Check if container exists
    if ! docker ps -a | grep -q "$container"; then
        echo "<p class='warning'>Container not found</p>" >> "$REPORT_DIR/index.html"
        echo "</div>" >> "$REPORT_DIR/index.html"
        return
    fi
    
    # Get container status
    local status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
    echo "<p>Status: <span class='$([ "$status" = "running" ] && echo "success" || echo "warning")'>$status</span></p>" >> "$REPORT_DIR/index.html"
    
    # Home directory listing
    echo "<h3>Home Directory Structure</h3>" >> "$REPORT_DIR/index.html"
    echo "<pre>" >> "$REPORT_DIR/index.html"
    docker exec "$container" ls -la /home/testuser 2>/dev/null | head -20 >> "$REPORT_DIR/index.html" || echo "Could not list directory" >> "$REPORT_DIR/index.html"
    echo "</pre>" >> "$REPORT_DIR/index.html"
    
    # Symlinks
    echo "<h3>Installed Symlinks</h3>" >> "$REPORT_DIR/index.html"
    echo "<pre>" >> "$REPORT_DIR/index.html"
    docker exec "$container" find /home/testuser -maxdepth 2 -type l -ls 2>/dev/null | head -20 >> "$REPORT_DIR/index.html" || echo "No symlinks found" >> "$REPORT_DIR/index.html"
    echo "</pre>" >> "$REPORT_DIR/index.html"
    
    # Test results
    echo "<h3>Test Output</h3>" >> "$REPORT_DIR/index.html"
    echo "<pre>" >> "$REPORT_DIR/index.html"
    docker logs "$container" 2>&1 | tail -50 >> "$REPORT_DIR/index.html" || echo "No logs available" >> "$REPORT_DIR/index.html"
    echo "</pre>" >> "$REPORT_DIR/index.html"
    
    # Export filesystem snapshot
    local export_dir="$REPORT_DIR/${level}-export"
    mkdir -p "$export_dir"
    docker cp "$container:/home/testuser" "$export_dir/home" 2>/dev/null || echo "Could not export filesystem"
    
    echo "<p>Filesystem exported to: $export_dir</p>" >> "$REPORT_DIR/index.html"
    echo "</div>" >> "$REPORT_DIR/index.html"
}

# Main execution
echo -e "${GREEN}Generating Docker Test Report...${NC}"

# Check for running containers
for level in quick unit integration e2e stress; do
    container="dotfiles-${level}-inspect"
    if docker ps -a | grep -q "$container"; then
        echo -e "${BLUE}Inspecting $container...${NC}"
        inspect_container "$container" "$level"
    fi
done

# Footer
cat >> "$REPORT_DIR/index.html" << 'EOF'
    <h2>Summary</h2>
    <p>Report saved to: REPORT_DIR</p>
</body>
</html>
EOF

sed -i.bak "s|REPORT_DIR|$REPORT_DIR|g" "$REPORT_DIR/index.html"
sed -i.bak "s|TIMESTAMP|$(date)|g" "$REPORT_DIR/index.html"
rm -f "$REPORT_DIR/index.html.bak"

echo -e "${GREEN}✓ Report generated: $REPORT_DIR/index.html${NC}"
echo "Open with: open $REPORT_DIR/index.html"

# Also generate text summary
cat > "$REPORT_DIR/summary.txt" << EOF
Docker Test Report Summary
==========================
Generated: $(date)
Report Directory: $REPORT_DIR

Containers Inspected:
EOF

docker ps -a --filter "name=dotfiles-" --format "- {{.Names}}: {{.Status}}" >> "$REPORT_DIR/summary.txt"

echo -e "\nVolumes:" >> "$REPORT_DIR/summary.txt"
docker volume ls --filter "name=test-home" --format "- {{.Name}}" >> "$REPORT_DIR/summary.txt"

echo -e "${GREEN}Text summary: $REPORT_DIR/summary.txt${NC}"