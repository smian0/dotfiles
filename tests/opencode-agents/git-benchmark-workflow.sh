#!/bin/bash
#
# Git-Integrated Benchmark Workflow Demonstration
# Shows how to track agent performance improvements alongside code changes
#

set -e

echo "🚀 Git-Integrated Benchmark Workflow Demonstration"
echo "================================================="

# Function to show current status
show_status() {
    echo ""
    echo "📊 Current Benchmark Status:"
    python benchmark_tracker.py trends | tail -10
    echo ""
    echo "🔍 Git Context:"
    git log -1 --oneline
    echo "   Branch: $(git branch --show-current)"
    echo "   Changed files: $(git diff --name-only HEAD~1..HEAD | wc -l) files"
}

# Step 1: Save current results with Git context
echo ""
echo "Step 1: Save baseline with Git context"
echo "======================================"

# Run evaluation to get fresh results
echo "Running evaluation..."
timeout 60s python demo_deepeval.py || echo "Evaluation completed (or timed out safely)"

# Save with Git integration (shows commit hash, branch, changed files)
python benchmark_tracker.py save --version "workflow_baseline_$(date +%H%M%S)"

show_status

# Step 2: Demonstrate performance tracking over time
echo ""
echo "Step 2: Performance History with Git Context"
echo "==========================================="

python benchmark_tracker.py git-history

# Step 3: Compare with baseline
echo ""
echo "Step 3: Performance Comparison"
echo "============================="

python benchmark_tracker.py compare

# Step 4: Show how to correlate improvements with code changes
echo ""
echo "Step 4: Code Change Correlation"
echo "==============================="

echo "🔗 Correlation Examples:"
echo "- When NewsRelevancy improved from 0.70 → 0.85:"
echo "  Git shows: Enhanced filtering logic in demo_deepeval.py"
echo "  Files changed: reporting/templates/, utils/deepeval_helpers.py"
echo ""
echo "- When issues reduced from 4 → 1:"
echo "  Git shows: Fixed template field mapping"
echo "  Commit: benchmark_tracker.py, template updates"

echo ""
echo "✅ Complete Git-Integrated Workflow Demonstrated!"
echo ""
echo "📈 Key Benefits:"
echo "  • Track performance alongside code changes"
echo "  • Correlate improvements with specific commits"  
echo "  • Maintain performance history in Git repository"
echo "  • Automated commit messages with performance deltas"
echo "  • Visualize trends over development timeline"

# Step 5: Future automation possibilities
echo ""
echo "🔮 Future Automation Ideas:"
echo "  • Pre-commit hooks that run evaluations"
echo "  • CI/CD integration for performance regression detection"
echo "  • Automatic performance reports in pull requests"
echo "  • Branch-based performance comparison"
echo "  • Performance-driven deployment gates"