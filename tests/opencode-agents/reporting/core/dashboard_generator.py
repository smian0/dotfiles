"""
DeepEval Overview Dashboard Generator
Creates a master dashboard that ties all individual reports together
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from jinja2 import Environment, FileSystemLoader

from .report_generator import DeepEvalReportGenerator


class DashboardGenerator:
    """Generate overview dashboard that links all reports together"""
    
    def __init__(self, results_dir: Path, templates_dir: Optional[Path] = None):
        self.results_dir = Path(results_dir)
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self.html_reports_dir = self.results_dir / "html_reports"
        self.benchmark_file = self.results_dir / "benchmarks.json"
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        self.jinja_env.filters['tojson'] = lambda x: json.dumps(x, default=str)
        
    def generate_dashboard(self, output_filename: str = None) -> Path:
        """Generate the overview dashboard HTML"""
        print("📊 Generating Overview Dashboard...")
        
        # Step 1: Scan for existing reports
        reports_data = self._scan_reports()
        
        # Step 2: Load benchmarks data
        benchmarks_data = self._load_benchmarks()
        
        # Step 3: Correlate reports with benchmarks
        correlated_data = self._correlate_reports_and_benchmarks(reports_data, benchmarks_data)
        
        # Step 4: Create timeline data
        timeline_data = self._create_timeline_data(correlated_data)
        
        # Step 5: Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(benchmarks_data)
        
        # Step 6: Prepare template data
        template_data = self._prepare_dashboard_template_data(
            reports_data, 
            benchmarks_data, 
            correlated_data,
            timeline_data,
            performance_metrics
        )
        
        # Step 7: Generate dashboard HTML
        output_path = self._generate_dashboard_html(template_data, output_filename)
        
        # Step 8: Create reports manifest
        self._create_reports_manifest(correlated_data)
        
        print(f"✅ Dashboard generated: {output_path}")
        return output_path
    
    def _scan_reports(self) -> List[Dict[str, Any]]:
        """Scan html_reports directory for existing reports"""
        reports = []
        
        if not self.html_reports_dir.exists():
            return reports
            
        for report_file in self.html_reports_dir.glob("*.html"):
            if report_file.name.startswith("dashboard"):
                continue  # Skip existing dashboards
                
            # Extract timestamp from filename
            timestamp_match = re.search(r"(\d{8}_\d{6})", report_file.name)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            else:
                timestamp = datetime.fromtimestamp(report_file.stat().st_mtime)
            
            # Get file size
            file_size = report_file.stat().st_size
            
            report_data = {
                "filename": report_file.name,
                "path": str(report_file),
                "relative_path": str(report_file.relative_to(self.results_dir)),
                "timestamp": timestamp,
                "timestamp_str": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "size_mb": round(file_size / (1024*1024), 2),
                "benchmark_version": None  # Will be filled by correlation
            }
            
            reports.append(report_data)
        
        # Sort by timestamp, newest first
        reports.sort(key=lambda x: x["timestamp"], reverse=True)
        
        print(f"📄 Found {len(reports)} reports")
        return reports
    
    def _load_benchmarks(self) -> List[Dict[str, Any]]:
        """Load benchmarks.json data"""
        if not self.benchmark_file.exists():
            return []
            
        try:
            with open(self.benchmark_file, 'r') as f:
                benchmarks = json.load(f)
            
            # Convert timestamp strings to datetime objects for easier processing
            for benchmark in benchmarks:
                if 'timestamp' in benchmark:
                    benchmark['timestamp_dt'] = datetime.fromisoformat(benchmark['timestamp'])
                    benchmark['timestamp_str'] = benchmark['timestamp_dt'].strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"📈 Found {len(benchmarks)} benchmarks")
            return benchmarks
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Error loading benchmarks: {e}")
            return []
    
    def _correlate_reports_and_benchmarks(self, reports: List[Dict], benchmarks: List[Dict]) -> List[Dict]:
        """Correlate reports with benchmark entries based on timestamps"""
        correlated = []
        
        for report in reports:
            # Find closest benchmark (within 10 minutes)
            closest_benchmark = None
            min_diff = None
            
            for benchmark in benchmarks:
                if 'timestamp_dt' not in benchmark:
                    continue
                    
                time_diff = abs((report["timestamp"] - benchmark["timestamp_dt"]).total_seconds())
                
                if time_diff <= 600:  # Within 10 minutes
                    if min_diff is None or time_diff < min_diff:
                        min_diff = time_diff
                        closest_benchmark = benchmark
            
            correlation_data = {
                "report": report,
                "benchmark": closest_benchmark,
                "correlation_strength": "exact" if min_diff and min_diff < 60 else "approximate" if min_diff else "none"
            }
            
            if closest_benchmark:
                report["benchmark_version"] = closest_benchmark["version"]
                correlation_data["performance_score"] = self._extract_main_score(closest_benchmark)
                correlation_data["issues_count"] = closest_benchmark.get("issues_count", 0)
                correlation_data["git_context"] = closest_benchmark.get("git_context", {})
            
            correlated.append(correlation_data)
        
        return correlated
    
    def _extract_main_score(self, benchmark: Dict) -> Optional[float]:
        """Extract main performance score from benchmark"""
        metrics = benchmark.get("metrics", {})
        if not metrics:
            return None
            
        # Get first agent's first metric as main score
        for agent_name, agent_metrics in metrics.items():
            for metric_name, score in agent_metrics.items():
                return float(score)
        
        return None
    
    def _create_timeline_data(self, correlated_data: List[Dict]) -> Dict[str, Any]:
        """Create timeline visualization data"""
        timeline_points = []
        
        for item in correlated_data:
            if item["benchmark"]:
                point = {
                    "timestamp": item["benchmark"]["timestamp"],
                    "version": item["benchmark"]["version"],
                    "score": self._extract_main_score(item["benchmark"]),
                    "issues": item["benchmark"].get("issues_count", 0),
                    "report_file": item["report"]["filename"],
                    "git_commit": item["benchmark"].get("git_context", {}).get("commit_hash", "")[:8] if item["benchmark"].get("git_context") else ""
                }
                timeline_points.append(point)
        
        # Sort by timestamp
        timeline_points.sort(key=lambda x: x["timestamp"])
        
        return {
            "points": timeline_points,
            "min_score": min([p["score"] for p in timeline_points if p["score"]], default=0),
            "max_score": max([p["score"] for p in timeline_points if p["score"]], default=1),
            "total_points": len(timeline_points)
        }
    
    def _calculate_performance_metrics(self, benchmarks: List[Dict]) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        if not benchmarks:
            return {}
        
        latest = benchmarks[-1] if benchmarks else {}
        baseline = benchmarks[0] if benchmarks else {}
        
        # Calculate trend
        latest_score = self._extract_main_score(latest)
        baseline_score = self._extract_main_score(baseline)
        
        performance_trend = "stable"
        score_change = 0
        
        if latest_score and baseline_score:
            score_change = latest_score - baseline_score
            if score_change > 0.01:
                performance_trend = "improving"
            elif score_change < -0.01:
                performance_trend = "declining"
        
        return {
            "total_benchmarks": len(benchmarks),
            "latest_version": latest.get("version", "unknown"),
            "baseline_version": baseline.get("version", "unknown"),
            "latest_score": latest_score,
            "baseline_score": baseline_score,
            "score_change": score_change,
            "performance_trend": performance_trend,
            "latest_issues": latest.get("issues_count", 0),
            "baseline_issues": baseline.get("issues_count", 0),
            "issues_change": latest.get("issues_count", 0) - baseline.get("issues_count", 0) if baseline else 0
        }
    
    def _prepare_dashboard_template_data(self, reports: List[Dict], benchmarks: List[Dict], 
                                       correlated: List[Dict], timeline: Dict, metrics: Dict) -> Dict[str, Any]:
        """Prepare data for dashboard template"""
        
        # Community circles data
        community_circles = {
            "reports": {
                "count": len(reports),
                "latest": reports[0] if reports else None,
                "total_size_mb": sum(r["size_mb"] for r in reports)
            },
            "benchmarks": {
                "count": len(benchmarks),
                "latest_score": metrics.get("latest_score", 0),
                "trend": metrics.get("performance_trend", "stable")
            },
            "git": {
                "commits_tracked": len([c for c in correlated if c.get("git_context")]),
                "branches": len(set(c.get("git_context", {}).get("branch", "") for c in correlated if c.get("git_context"))),
                "latest_commit": correlated[0].get("git_context", {}).get("commit_hash", "")[:8] if correlated and correlated[0].get("git_context") else ""
            }
        }
        
        return {
            "dashboard_title": "DeepEval Overview Dashboard",
            "generation_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "reports": reports,
            "benchmarks": benchmarks,
            "correlated_data": correlated,
            "timeline_data": timeline,
            "performance_metrics": metrics,
            "community_circles": community_circles,
            "latest_report": reports[0] if reports else None,
            "latest_benchmark": benchmarks[-1] if benchmarks else None
        }
    
    def _generate_dashboard_html(self, template_data: Dict[str, Any], output_filename: str = None) -> Path:
        """Generate the dashboard HTML file"""
        
        # Ensure output directory exists
        self.html_reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Default filename
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"dashboard_overview_{timestamp}.html"
        
        output_path = self.html_reports_dir / output_filename
        
        # Load and render template
        template = self.jinja_env.get_template('dashboard.html')
        html_content = template.render(template_data)
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create symlink to latest dashboard
        latest_link = self.html_reports_dir / "latest_dashboard.html"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(output_path.name)
        
        return output_path
    
    def _create_reports_manifest(self, correlated_data: List[Dict]) -> None:
        """Create a manifest file listing all reports for navigation"""
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "total_reports": len(correlated_data),
            "reports": []
        }
        
        for item in correlated_data:
            report_entry = {
                "filename": item["report"]["filename"],
                "timestamp": item["report"]["timestamp"].isoformat(),
                "benchmark_version": item["report"].get("benchmark_version"),
                "performance_score": item.get("performance_score"),
                "issues_count": item.get("issues_count"),
                "correlation": item["correlation_strength"]
            }
            manifest["reports"].append(report_entry)
        
        manifest_path = self.results_dir / "reports_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        print(f"📋 Created reports manifest: {manifest_path}")