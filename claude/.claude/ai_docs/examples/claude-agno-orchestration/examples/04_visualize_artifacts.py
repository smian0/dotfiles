#!/usr/bin/env python3
"""
Example 4: Visualizing Agent Execution Artifacts
=================================================

Demonstrates how to generate visual diagrams from orchestration artifacts
to understand agent execution flow, timing, and inputs/outputs.

This is especially useful for:
- Understanding complex orchestration flows
- Debugging performance issues
- Documentation and presentations
- Auditing research runs
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestration import ArtifactVisualizer, visualize_artifacts


def main():
    """Demonstrate artifact visualization capabilities."""

    print("=" * 80)
    print("Agent Execution Artifact Visualization")
    print("=" * 80)
    print()

    # Find the most recent research output
    outputs_dir = Path("outputs")

    if not outputs_dir.exists():
        print("❌ No outputs directory found. Run 03_polymarket_research.py first.")
        return

    # Get all research output directories
    research_dirs = sorted(
        [d for d in outputs_dir.iterdir() if d.is_dir()],
        key=lambda x: x.name,
        reverse=True
    )

    if not research_dirs:
        print("❌ No research outputs found. Run 03_polymarket_research.py first.")
        return

    # Use the most recent one
    latest_dir = research_dirs[0]
    artifacts_path = latest_dir / "artifacts.json"

    if not artifacts_path.exists():
        print(f"❌ No artifacts.json found in {latest_dir}")
        return

    print(f"📂 Using artifacts from: {latest_dir.name}")
    print()

    # ========================================================================
    # Example 1: Tree Visualization (Normal Detail)
    # ========================================================================

    print("\n" + "=" * 80)
    print("Example 1: Tree Visualization (Normal Detail)")
    print("=" * 80)
    print()

    visualizer = ArtifactVisualizer(artifacts_path)

    tree = visualizer.generate_tree(detail_level="normal")
    print(tree)

    # Save to file
    tree_output = latest_dir / "execution_tree.txt"
    visualizer.save_visualization(
        tree_output,
        mode="tree",
        detail_level="normal"
    )
    print(f"\n💾 Saved to: {tree_output}")

    # ========================================================================
    # Example 2: Tree Visualization (Minimal Detail)
    # ========================================================================

    print("\n" + "=" * 80)
    print("Example 2: Tree Visualization (Minimal Detail)")
    print("=" * 80)
    print()

    tree_minimal = visualizer.generate_tree(detail_level="minimal")
    print(tree_minimal)

    # ========================================================================
    # Example 3: Tree Visualization (Verbose Detail)
    # ========================================================================

    print("\n" + "=" * 80)
    print("Example 3: Tree Visualization (Verbose Detail)")
    print("=" * 80)
    print()

    tree_verbose = visualizer.generate_tree(
        detail_level="verbose",
        show_timestamps=True
    )
    print(tree_verbose)

    # Save verbose version
    tree_verbose_output = latest_dir / "execution_tree_verbose.txt"
    with open(tree_verbose_output, 'w') as f:
        f.write(tree_verbose)
    print(f"\n💾 Saved to: {tree_verbose_output}")

    # ========================================================================
    # Example 4: Compact Summary
    # ========================================================================

    print("\n" + "=" * 80)
    print("Example 4: Compact Summary")
    print("=" * 80)
    print()

    compact = visualizer.generate_compact_summary()
    print(compact)

    # ========================================================================
    # Example 5: Execution Timeline
    # ========================================================================

    print("\n" + "=" * 80)
    print("Example 5: Execution Timeline")
    print("=" * 80)
    print()

    timeline = visualizer.generate_timeline()
    print(timeline)

    # Save timeline
    timeline_output = latest_dir / "execution_timeline.txt"
    with open(timeline_output, 'w') as f:
        f.write(timeline)
    print(f"\n💾 Saved to: {timeline_output}")

    # ========================================================================
    # Example 6: Using Convenience Function
    # ========================================================================

    print("\n" + "=" * 80)
    print("Example 6: Using Convenience Function")
    print("=" * 80)
    print()

    # Quick one-liner to generate and save
    output_path = latest_dir / "quick_tree.txt"
    result = visualize_artifacts(
        artifacts_path,
        mode="tree",
        output_path=output_path,
        detail_level="normal"
    )

    print(f"✅ Generated and saved visualization using convenience function")
    print(f"💾 Saved to: {output_path}")

    # ========================================================================
    # Example 7: Compare Multiple Runs
    # ========================================================================

    print("\n" + "=" * 80)
    print("Example 7: Comparing Multiple Research Runs")
    print("=" * 80)
    print()

    if len(research_dirs) > 1:
        print(f"Found {len(research_dirs)} research runs. Comparing latest two:\n")

        for i, run_dir in enumerate(research_dirs[:2], 1):
            artifacts_file = run_dir / "artifacts.json"

            if artifacts_file.exists():
                compact_summary = visualize_artifacts(
                    artifacts_file,
                    mode="compact"
                )
                print(f"Run {i}: {run_dir.name}")
                print(compact_summary)
                print()
    else:
        print("Only one research run found. Run 03_polymarket_research.py again to compare.")

    # ========================================================================
    # Summary
    # ========================================================================

    print("\n" + "=" * 80)
    print("Summary of Generated Visualizations")
    print("=" * 80)
    print()

    visualization_files = [
        "execution_tree.txt",
        "execution_tree_verbose.txt",
        "execution_timeline.txt",
        "quick_tree.txt"
    ]

    print(f"📂 All visualizations saved to: {latest_dir}/")
    print()

    for filename in visualization_files:
        filepath = latest_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  ✓ {filename} ({size:,} bytes)")

    print()
    print("=" * 80)
    print("💡 Tips:")
    print("=" * 80)
    print()
    print("1. Use 'tree' mode for detailed hierarchical view")
    print("2. Use 'compact' mode for quick one-line summaries")
    print("3. Use 'timeline' mode to identify performance bottlenecks")
    print("4. Use detail_level='minimal' for presentations")
    print("5. Use detail_level='verbose' for debugging")
    print()
    print("Command-line usage:")
    print(f"  python -m orchestration.utils.artifact_visualizer {artifacts_path} tree")
    print()


if __name__ == "__main__":
    main()
