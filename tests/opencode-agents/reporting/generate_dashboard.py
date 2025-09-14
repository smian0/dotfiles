#!/usr/bin/env python3
"""
DeepEval Dashboard Generator CLI
Command-line interface for generating overview dashboard
"""
import sys
from pathlib import Path

# Add the reporting core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.dashboard_generator import DashboardGenerator


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate overview dashboard that ties all reports together',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate dashboard from results directory
  python generate_dashboard.py ../results

  # Generate with custom filename
  python generate_dashboard.py ../results --output custom_dashboard.html

  # Auto-open in browser
  python generate_dashboard.py ../results --open
        """
    )
    
    parser.add_argument(
        'results_dir',
        help='Path to results directory containing benchmarks.json and html_reports/'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Custom output filename (default: dashboard_overview_TIMESTAMP.html)'
    )
    
    parser.add_argument(
        '--open', '-b',
        action='store_true',
        help='Open generated dashboard in browser'
    )
    
    args = parser.parse_args()
    
    # Validate results directory
    results_path = Path(args.results_dir)
    if not results_path.exists():
        print(f"❌ Results directory not found: {results_path}")
        return 1
    
    try:
        # Create dashboard generator
        generator = DashboardGenerator(results_path)
        
        # Generate dashboard
        output_path = generator.generate_dashboard(args.output)
        
        print(f"✅ Dashboard generated successfully!")
        print(f"📁 Location: {output_path}")
        print(f"🌐 URL: file://{output_path.absolute()}")
        
        # Create convenience symlink
        latest_link = output_path.parent / "index.html"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(output_path.name)
        print(f"🔗 Also available at: {latest_link}")
        
        # Open in browser if requested
        if args.open:
            import webbrowser
            webbrowser.open(f"file://{output_path.absolute()}")
            print("🚀 Opening in browser...")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())