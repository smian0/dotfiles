#!/bin/bash
# Workspace setup script for research skill
# Creates directory structure for research output

set -euo pipefail

# Get current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S %Z")
DATE_SHORT=$(date "+%Y-%m-%d")

# Create research output directories
mkdir -p ./research-output/{progress,sources,analysis,report}

echo "✅ Research workspace created:"
echo "   - ./research-output/progress/   (Coordinator status)"
echo "   - ./research-output/sources/    (Discovery & validation)"
echo "   - ./research-output/analysis/   (Deep analysis findings)"
echo "   - ./research-output/report/     (Executive & full reports)"
echo ""
echo "Timestamp: $TIMESTAMP"
echo "Date: $DATE_SHORT"
