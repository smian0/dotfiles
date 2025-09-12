#!/usr/bin/env python3
"""
DeepEval HTML Report Generator CLI
Simple command-line interface for generating comprehensive HTML reports
"""
import sys
from pathlib import Path

# Add the reporting core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.report_generator import DeepEvalReportGenerator


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate comprehensive HTML reports from DeepEval test results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full report from test results
  python generate_report.py ../results

  # Generate quick summary
  python generate_report.py ../results --type summary

  # Generate agent comparison report
  python generate_report.py ../results --type agents --agents news websearch

  # Generate metric analysis report
  python generate_report.py ../results --type metrics --metrics FaithfulnessMetric AnswerRelevancyMetric

  # Export raw data as JSON
  python generate_report.py ../results --export-data
        """
    )
    
    parser.add_argument('results_dir', 
                       help='Directory containing DeepEval test results (pytest reports, junit xml, etc.)')
    
    parser.add_argument('--output', '-o', 
                       help='Output filename (default: auto-generated with timestamp)')
    
    parser.add_argument('--title', '-t', 
                       default='DeepEval Agent Performance Report', 
                       help='Report title (default: DeepEval Agent Performance Report)')
    
    parser.add_argument('--type', 
                       choices=['full', 'summary', 'agents', 'metrics'], 
                       default='full', 
                       help='Report type (default: full)')
    
    parser.add_argument('--agents', 
                       nargs='*', 
                       help='Specific agents to analyze (for agents report type)')
    
    parser.add_argument('--metrics', 
                       nargs='*', 
                       help='Specific metrics to analyze (for metrics report type)')
    
    parser.add_argument('--export-data', 
                       action='store_true', 
                       help='Also export raw analysis data as JSON')
    
    parser.add_argument('--output-dir', 
                       help='Output directory (default: results_dir/html_reports)')
    
    parser.add_argument('--verbose', '-v', 
                       action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate results directory
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"❌ Error: Results directory '{results_dir}' does not exist")
        return 1
    
    if not results_dir.is_dir():
        print(f"❌ Error: '{results_dir}' is not a directory")
        return 1
    
    # Check for common result files
    common_files = ['report.json', 'junit.xml', 'deepeval_results.json']
    found_files = [f for f in common_files if (results_dir / f).exists()]
    
    if not found_files and args.verbose:
        print(f"⚠️  Warning: No common result files found in '{results_dir}'")
        print(f"   Looking for: {', '.join(common_files)}")
        print("   The generator will search for any .json or .xml files")
    
    try:
        # Initialize generator
        if args.verbose:
            print(f"🔧 Initializing report generator...")
        
        # Override output directory if specified
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            # Temporarily modify the generator to use custom output dir
            generator = DeepEvalReportGenerator(results_dir)
            generator.output_dir = output_dir
        else:
            generator = DeepEvalReportGenerator(results_dir)
        
        # Generate requested report type
        if args.verbose:
            print(f"📊 Generating {args.type} report...")
        
        output_path = None
        
        if args.type == 'full':
            output_path = generator.generate_full_report(args.title, args.output)
        
        elif args.type == 'summary':
            output_path = generator.generate_quick_summary(args.output)
        
        elif args.type == 'agents':
            if args.agents:
                output_path = generator.generate_agent_comparison(args.agents, args.output)
            else:
                output_path = generator.generate_agent_comparison(output_filename=args.output)
        
        elif args.type == 'metrics':
            if args.metrics:
                output_path = generator.generate_metric_deep_dive(args.metrics, args.output)
            else:
                output_path = generator.generate_metric_deep_dive(output_filename=args.output)
        
        # Check if report was generated successfully
        if not output_path or not output_path.exists():
            print("❌ Failed to generate report")
            print("   Possible causes:")
            print("   - No test results found in the specified directory")
            print("   - Test results are in an unsupported format")
            print("   - Insufficient permissions to write output file")
            return 1
        
        # Success message
        print("\n🎉 Report generated successfully!")
        print(f"📁 Location: {output_path}")
        print(f"🌐 Open in browser: file://{output_path.absolute()}")
        
        if args.verbose:
            print(f"📏 File size: {output_path.stat().st_size / 1024:.1f} KB")
        
        # Export raw data if requested
        if args.export_data:
            if args.verbose:
                print("📤 Exporting raw analysis data...")
            data_path = generator.export_raw_data()
            if data_path:
                print(f"📊 Raw data exported: {data_path}")
            else:
                print("⚠️  Warning: Failed to export raw data")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())