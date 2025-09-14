"""
DeepEval HTML Report Generator
Main orchestrator class for generating comprehensive HTML reports
"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template

from .data_collector import DeepEvalDataCollector, TestResult
from .metric_analyzer import MetricAnalyzer


class DeepEvalReportGenerator:
    """Main report generator that orchestrates all components"""
    
    def __init__(self, results_dir: Path, templates_dir: Optional[Path] = None):
        self.results_dir = Path(results_dir)
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self.output_dir = self.results_dir / "html_reports"
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Add custom filters
        self.jinja_env.filters['tojson'] = lambda x: json.dumps(x, default=str)
        
        # Components
        self.data_collector = DeepEvalDataCollector(self.results_dir)
        self.analyzer = None
        self.results = []
        
    def generate_full_report(self, 
                           report_title: str = "DeepEval Agent Analysis",
                           output_filename: str = None) -> Path:
        """Generate a complete HTML report with all sections"""
        
        # Step 1: Collect data from all sources
        print("📊 Collecting test results...")
        self.results = self.data_collector.collect_all_sources()
        
        if not self.results:
            print("❌ No test results found. Please run tests first.")
            return None
        
        print(f"✅ Found {len(self.results)} test results")
        
        # Step 2: Analyze the data
        print("🧠 Analyzing results...")
        self.analyzer = MetricAnalyzer(self.results)
        analysis = self.analyzer.analyze_all()
        
        # Step 3: Prepare template data
        template_data = self._prepare_template_data(report_title, analysis)
        
        # Step 4: Generate HTML report
        print("🎨 Generating HTML report...")
        output_path = self._generate_html_report(template_data, output_filename)
        
        # Step 5: Copy assets and create self-contained report
        self._make_self_contained(output_path)
        
        print(f"✅ Report generated: {output_path}")
        return output_path
    
    def generate_quick_summary(self, output_filename: str = None) -> Path:
        """Generate a quick summary report with key metrics only"""
        
        self.results = self.data_collector.collect_all_sources()
        if not self.results:
            return None
        
        self.analyzer = MetricAnalyzer(self.results)
        overview = self.analyzer.analyze_overview()
        metrics = self.analyzer.analyze_metrics()
        
        template_data = {
            'report_title': 'DeepEval Quick Summary',
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overview': overview,
            'metrics': metrics,
            'agents': {},
            'categories': {},
            'failure_analysis': {'message': 'Full analysis not run'},
            'recommendations': []
        }
        
        return self._generate_html_report(template_data, output_filename or "quick_summary.html")
    
    def generate_agent_comparison(self, agent_names: List[str] = None, output_filename: str = None) -> Path:
        """Generate a report focused on agent comparison"""
        
        self.results = self.data_collector.collect_all_sources()
        if not self.results:
            return None
        
        # Filter results for specific agents if requested
        if agent_names:
            self.results = [r for r in self.results if r.agent_name in agent_names]
        
        self.analyzer = MetricAnalyzer(self.results)
        analysis = self.analyzer.analyze_all()
        
        template_data = self._prepare_template_data("Agent Performance Comparison", analysis)
        
        return self._generate_html_report(template_data, output_filename or "agent_comparison.html")
    
    def generate_metric_deep_dive(self, metric_names: List[str] = None, output_filename: str = None) -> Path:
        """Generate a report focused on specific metrics"""
        
        self.results = self.data_collector.collect_all_sources()
        if not self.results:
            return None
        
        self.analyzer = MetricAnalyzer(self.results)
        all_analysis = self.analyzer.analyze_all()
        
        # Filter metrics if specified
        if metric_names:
            filtered_metrics = {
                name: metric for name, metric in all_analysis['metrics'].items()
                if name in metric_names
            }
            all_analysis['metrics'] = filtered_metrics
        
        template_data = self._prepare_template_data("Metric Deep Dive Analysis", all_analysis)
        
        return self._generate_html_report(template_data, output_filename or "metric_analysis.html")
    
    def export_raw_data(self, output_filename: str = None) -> Path:
        """Export raw analyzed data as JSON for external processing"""
        
        self.results = self.data_collector.collect_all_sources()
        if not self.results:
            return None
        
        self.analyzer = MetricAnalyzer(self.results)
        analysis = self.analyzer.analyze_all()
        
        # Add raw results to export
        analysis['raw_results'] = [
            {
                'test_name': r.test_name,
                'agent_name': r.agent_name,
                'status': r.status,
                'duration': r.duration,
                'metrics': r.metrics,
                'input_query': r.input_query,
                'actual_output': r.actual_output,
                'error_message': r.error_message,
                'timestamp': r.timestamp
            }
            for r in self.results
        ]
        
        output_filename = output_filename or f"deepeval_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = self.output_dir / output_filename
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"✅ Raw data exported: {output_path}")
        return output_path
    
    def _prepare_template_data(self, report_title: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        
        # Prepare detailed test results for debugging section
        test_results = []
        if hasattr(self, 'results') and self.results:
            for result in self.results:
                test_data = {
                    'test_case_name': result.test_name,
                    'success': result.status == 'passed',
                    'run_duration': result.duration,
                    'agent': getattr(result, 'agent_name', 'Unknown'),
                    'input': getattr(result, 'input', 'No input recorded'),
                    'actual_output': getattr(result, 'actual_output', ''),
                    'expected_output': getattr(result, 'expected_output', None),
                    'metrics': getattr(result, 'metrics', []),
                    'issues': getattr(result, 'issues', []),
                    'error_details': getattr(result, 'error_details', None),
                    'category': getattr(result, 'category', 'uncategorized')
                }
                test_results.append(test_data)
        
        # Convert complex objects to JSON-serializable dictionaries
        def serialize_object(obj):
            if hasattr(obj, '__dict__'):
                return {k: serialize_object(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, dict):
                return {k: serialize_object(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_object(item) for item in obj]
            else:
                return obj
        
        # Load performance history
        performance_history = self._load_performance_history()
        
        # Add navigation data
        dashboard_link = self._get_dashboard_link()
        report_navigation = self._get_report_navigation()
        
        return {
            'report_title': report_title,
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overview': serialize_object(analysis.get('overview', {})),
            'metrics': serialize_object(analysis.get('metrics', {})),
            'agents': serialize_object(analysis.get('agents', {})),
            'categories': serialize_object(analysis.get('categories', {})),
            'trends': serialize_object(analysis.get('trends', {})),
            'correlations': serialize_object(analysis.get('correlations', {})),
            'failure_analysis': serialize_object(analysis.get('failure_analysis', {})),
            'recommendations': analysis.get('recommendations', []),
            'test_results': test_results,  # Add detailed test results for debugging
            'performance_history': performance_history,  # Add performance history
            'dashboard_link': dashboard_link,  # Add dashboard link
            'report_navigation': report_navigation  # Add report navigation
        }
    
    def _load_performance_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Load recent performance history from benchmarks.json"""
        benchmark_file = self.results_dir / "benchmarks.json"
        
        if not benchmark_file.exists():
            return []
        
        try:
            with open(benchmark_file, 'r') as f:
                benchmarks = json.load(f)
            
            # Get last N benchmarks and calculate trends
            recent_benchmarks = benchmarks[-limit:] if len(benchmarks) > limit else benchmarks
            
            # Add trend indicators
            for i, benchmark in enumerate(recent_benchmarks):
                benchmark['trends'] = {}
                
                if i > 0:
                    prev_benchmark = recent_benchmarks[i-1]
                    
                    # Calculate trends for each agent/metric
                    for agent_name, metrics in benchmark.get('metrics', {}).items():
                        if agent_name in prev_benchmark.get('metrics', {}):
                            prev_metrics = prev_benchmark['metrics'][agent_name]
                            
                            agent_trends = {}
                            for metric_name, current_score in metrics.items():
                                if metric_name in prev_metrics:
                                    prev_score = prev_metrics[metric_name]
                                    diff = current_score - prev_score
                                    
                                    if diff > 0.01:
                                        trend = "↗️"  # Improvement
                                        trend_class = "improvement"
                                    elif diff < -0.01:
                                        trend = "↘️"  # Regression
                                        trend_class = "regression"
                                    else:
                                        trend = "➡️"  # Stable
                                        trend_class = "stable"
                                    
                                    agent_trends[metric_name] = {
                                        'icon': trend,
                                        'class': trend_class,
                                        'diff': diff,
                                        'prev_score': prev_score,
                                        'current_score': current_score
                                    }
                            
                            benchmark['trends'][agent_name] = agent_trends
            
            return recent_benchmarks
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Warning: Could not load performance history: {e}")
            return []
    
    def _generate_html_report(self, template_data: Dict[str, Any], output_filename: str = None) -> Path:
        """Generate the HTML report file"""
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default filename
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"deepeval_report_{timestamp}.html"
        
        output_path = self.output_dir / output_filename
        
        # Load and render template
        template = self.jinja_env.get_template('report.html')
        html_content = template.render(**template_data)
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _make_self_contained(self, html_path: Path):
        """Make the HTML report self-contained by inlining external resources"""
        
        # For now, we're using CDN links in the template
        # In a production version, you might want to download and inline CSS/JS
        # or bundle the assets with the HTML file
        
        # Create a companion assets directory if needed
        assets_dir = html_path.parent / f"{html_path.stem}_assets"
        if not assets_dir.exists():
            assets_dir.mkdir()
        
        # Copy any local assets (currently none, but placeholder for future enhancements)
        # This could include custom CSS, JS, or image files
        
        print(f"📁 Report assets directory: {assets_dir}")
    
    def generate_comparison_report(self, 
                                 baseline_results: Path,
                                 current_results: Path = None,
                                 output_filename: str = None) -> Path:
        """Generate a comparison report between two test runs"""
        
        # Load baseline results
        baseline_collector = DeepEvalDataCollector(baseline_results)
        baseline_data = baseline_collector.collect_all_sources()
        baseline_analyzer = MetricAnalyzer(baseline_data)
        baseline_analysis = baseline_analyzer.analyze_all()
        
        # Load current results (or use existing)
        if current_results:
            current_collector = DeepEvalDataCollector(current_results)
            current_data = current_collector.collect_all_sources()
        else:
            current_data = self.results or self.data_collector.collect_all_sources()
        
        current_analyzer = MetricAnalyzer(current_data)
        current_analysis = current_analyzer.analyze_all()
        
        # Calculate differences
        comparison_data = self._calculate_comparison_metrics(baseline_analysis, current_analysis)
        
        # Prepare template data
        template_data = {
            'report_title': 'DeepEval Comparison Report',
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'baseline': baseline_analysis,
            'current': current_analysis,
            'comparison': comparison_data
        }
        
        # Generate comparison-specific template (would need to create this)
        output_filename = output_filename or f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # For now, generate a regular report with comparison data
        # In a full implementation, you'd create a comparison-specific template
        return self._generate_html_report(template_data, output_filename)
    
    def _calculate_comparison_metrics(self, baseline: Dict, current: Dict) -> Dict[str, Any]:
        """Calculate comparison metrics between two analysis results"""
        
        comparison = {
            'overview_changes': {},
            'metric_changes': {},
            'agent_changes': {},
            'improvements': [],
            'regressions': []
        }
        
        # Compare overview metrics
        if 'overview' in baseline and 'overview' in current:
            base_overview = baseline['overview']
            curr_overview = current['overview']
            
            comparison['overview_changes'] = {
                'pass_rate_change': curr_overview.get('pass_rate', 0) - base_overview.get('pass_rate', 0),
                'duration_change': curr_overview.get('avg_duration', 0) - base_overview.get('avg_duration', 0),
                'test_count_change': curr_overview.get('total_tests', 0) - base_overview.get('total_tests', 0)
            }
        
        # Compare metric performance
        if 'metrics' in baseline and 'metrics' in current:
            base_metrics = baseline['metrics']
            curr_metrics = current['metrics']
            
            for metric_name in set(base_metrics.keys()) | set(curr_metrics.keys()):
                base_score = base_metrics.get(metric_name, {}).get('avg_score', 0) if metric_name in base_metrics else 0
                curr_score = curr_metrics.get(metric_name, {}).get('avg_score', 0) if metric_name in curr_metrics else 0
                
                change = curr_score - base_score
                comparison['metric_changes'][metric_name] = {
                    'baseline_score': base_score,
                    'current_score': curr_score,
                    'change': change,
                    'improvement': change > 0.05,  # 5% threshold
                    'regression': change < -0.05
                }
                
                if change > 0.05:
                    comparison['improvements'].append(f"📈 {metric_name} improved by {change:.3f}")
                elif change < -0.05:
                    comparison['regressions'].append(f"📉 {metric_name} declined by {abs(change):.3f}")
        
        return comparison
    
    def _get_dashboard_link(self) -> Optional[str]:
        """Get link to dashboard if it exists"""
        dashboard_files = [
            "index.html",
            "latest_dashboard.html"
        ]
        
        for dashboard_file in dashboard_files:
            dashboard_path = self.output_dir / dashboard_file
            if dashboard_path.exists():
                return dashboard_file
        
        # Look for any dashboard file
        for dashboard_file in self.output_dir.glob("dashboard_*.html"):
            return dashboard_file.name
        
        return None
    
    def _get_report_navigation(self) -> Optional[Dict[str, Any]]:
        """Get report navigation data (previous/next reports)"""
        try:
            # Load reports manifest
            manifest_path = self.results_dir / "reports_manifest.json"
            if not manifest_path.exists():
                return None
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            reports = manifest.get('reports', [])
            if len(reports) <= 1:
                return None
            
            # Find current report position (based on timestamp - we'll use the most recent)
            # In a full implementation, you'd pass the current report filename
            current_report = reports[0]  # Most recent
            current_index = 0
            
            navigation = {
                'total': len(reports),
                'current': {
                    'version': current_report.get('benchmark_version', 'unknown'),
                    'position': current_index + 1
                },
                'previous': None,
                'next': None
            }
            
            if current_index > 0:
                prev_report = reports[current_index - 1]
                navigation['previous'] = {
                    'filename': prev_report['filename'],
                    'version': prev_report.get('benchmark_version', 'unknown')
                }
            
            if current_index < len(reports) - 1:
                next_report = reports[current_index + 1]
                navigation['next'] = {
                    'filename': next_report['filename'],
                    'version': next_report.get('benchmark_version', 'unknown')
                }
            
            return navigation
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Warning: Could not load report navigation: {e}")
            return None


def main():
    """CLI interface for the report generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate DeepEval HTML Reports')
    parser.add_argument('results_dir', help='Directory containing test results')
    parser.add_argument('--output', '-o', help='Output filename')
    parser.add_argument('--title', '-t', default='DeepEval Report', help='Report title')
    parser.add_argument('--type', choices=['full', 'summary', 'agents', 'metrics'], 
                       default='full', help='Report type')
    parser.add_argument('--agents', nargs='*', help='Specific agents to analyze (for agents report)')
    parser.add_argument('--metrics', nargs='*', help='Specific metrics to analyze (for metrics report)')
    parser.add_argument('--export-data', action='store_true', help='Also export raw JSON data')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = DeepEvalReportGenerator(Path(args.results_dir))
    
    # Generate requested report type
    if args.type == 'full':
        output_path = generator.generate_full_report(args.title, args.output)
    elif args.type == 'summary':
        output_path = generator.generate_quick_summary(args.output)
    elif args.type == 'agents':
        output_path = generator.generate_agent_comparison(args.agents, args.output)
    elif args.type == 'metrics':
        output_path = generator.generate_metric_deep_dive(args.metrics, args.output)
    
    if output_path:
        print(f"\n🎉 Report generated successfully!")
        print(f"📁 Location: {output_path}")
        print(f"🌐 Open in browser: file://{output_path.absolute()}")
        
        # Export raw data if requested
        if args.export_data:
            data_path = generator.export_raw_data()
            print(f"📊 Raw data exported: {data_path}")
    else:
        print("❌ Failed to generate report. Check that test results exist in the specified directory.")


if __name__ == "__main__":
    main()