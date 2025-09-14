#!/usr/bin/env python3
"""
Complete DeepEval Analysis Generator
Runs evaluation, generates report, saves benchmark, and updates dashboard
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add reporting to path
sys.path.insert(0, str(Path(__file__).parent / "reporting"))

from reporting.core.report_generator import DeepEvalReportGenerator
from reporting.core.dashboard_generator import DashboardGenerator
from benchmark_tracker import BenchmarkTracker


def main():
    """Complete analysis workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Complete DeepEval analysis workflow: evaluate → report → benchmark → dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete analysis with auto-generated version
  python generate_full_analysis.py

  # Run with custom version name
  python generate_full_analysis.py --version "improved_filtering_v3"

  # Skip evaluation (use existing results) 
  python generate_full_analysis.py --skip-eval --version "dashboard_update"
  
  # Auto-commit benchmark to Git
  python generate_full_analysis.py --version "feature_xyz" --commit
  
  # Open results in browser when complete
  python generate_full_analysis.py --open
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        help='Version name for benchmark (default: auto-generated)'
    )
    
    parser.add_argument(
        '--skip-eval',
        action='store_true',
        help='Skip evaluation step (use existing results)'
    )
    
    parser.add_argument(
        '--commit', '-c',
        action='store_true',
        help='Auto-commit benchmark to Git with intelligent message'
    )
    
    parser.add_argument(
        '--open', '-o',
        action='store_true', 
        help='Open dashboard and latest report in browser'
    )
    
    parser.add_argument(
        '--results-dir',
        default='results',
        help='Results directory (default: results)'
    )
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    results_dir.mkdir(exist_ok=True)
    
    print("🚀 Complete DeepEval Analysis Workflow")
    print("=" * 50)
    
    # Step 1: Run Evaluation (unless skipped)
    if not args.skip_eval:
        print("\n📊 Step 1: Running DeepEval Assessment...")
        try:
            result = subprocess.run(
                ["python", "demo_deepeval.py"], 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Evaluation completed successfully")
            else:
                print(f"⚠️  Evaluation completed with warnings")
                print(f"Output: {result.stdout[-500:]}")  # Last 500 chars
                
        except subprocess.TimeoutExpired:
            print("⏱️  Evaluation timed out (using existing results)")
        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            print("Continuing with existing results...")
    else:
        print("\n📊 Step 1: Skipped evaluation (using existing results)")
    
    # Step 2: Generate Report
    print("\n📄 Step 2: Generating HTML Report...")
    try:
        generator = DeepEvalReportGenerator(results_dir)
        report_path = generator.generate_full_report("DeepEval Agent Analysis")
        
        if report_path:
            print(f"✅ Report generated: {report_path.name}")
            latest_report_path = report_path
        else:
            print("❌ Report generation failed")
            return 1
            
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return 1
    
    # Step 3: Save Benchmark
    print("\n📈 Step 3: Saving Benchmark...")
    try:
        # Load current results
        results_file = results_dir / "deepeval_results.json"
        if results_file.exists():
            with open(results_file) as f:
                test_results = json.load(f)
            
            # Initialize tracker and save benchmark
            tracker = BenchmarkTracker(results_dir)
            
            if args.commit:
                tracker.save_benchmark_with_commit(
                    test_results, 
                    args.version,
                    auto_commit=True
                )
            else:
                tracker.save_benchmark(test_results, args.version)
            
            print("✅ Benchmark saved successfully")
            
        else:
            print("⚠️  No results file found - skipping benchmark")
            
    except Exception as e:
        print(f"❌ Benchmark saving failed: {e}")
        # Continue anyway
    
    # Step 4: Update Dashboard
    print("\n📊 Step 4: Updating Dashboard...")
    try:
        dashboard_generator = DashboardGenerator(results_dir)
        dashboard_path = dashboard_generator.generate_dashboard()
        
        print(f"✅ Dashboard updated: {dashboard_path.name}")
        
    except Exception as e:
        print(f"❌ Dashboard update failed: {e}")
        return 1
    
    # Step 5: Show Results
    print("\n🎉 Analysis Complete!")
    print("=" * 50)
    print(f"📄 Latest Report: {latest_report_path}")
    print(f"📊 Dashboard: {dashboard_path}")
    print(f"🌐 Dashboard URL: file://{dashboard_path.absolute()}")
    
    # Optional: Open in browser
    if args.open:
        import webbrowser
        print("\n🚀 Opening in browser...")
        webbrowser.open(f"file://{dashboard_path.absolute()}")
        webbrowser.open(f"file://{latest_report_path.absolute()}")
    
    print("\n💡 Next Steps:")
    print(f"   • View dashboard: open {dashboard_path}")
    print(f"   • View latest report: open {latest_report_path}")
    print(f"   • Track performance: python benchmark_tracker.py trends")
    
    return 0


if __name__ == "__main__":
    exit(main())