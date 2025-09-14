#!/usr/bin/env python3
"""
DeepEval Benchmark Tracking Script
Tracks agent performance over time and shows trends
"""

import json
import os
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class BenchmarkTracker:
    """Track agent performance metrics over time with Git integration"""
    
    def __init__(self, results_dir: Path = Path("results")):
        self.results_dir = Path(results_dir)
        self.benchmark_file = self.results_dir / "benchmarks.json"
        self.git_enabled = self._check_git_repo()
        
    def save_benchmark(self, test_results: Dict[str, Any], version: str = None) -> None:
        """Save current test results as a benchmark"""
        if version is None:
            version = datetime.now().strftime("v%Y%m%d_%H%M%S")
            
        # Load existing benchmarks
        benchmarks = self._load_benchmarks()
        
        # Get Git context
        git_context = self._get_git_context() if self.git_enabled else {}
        
        # Extract key metrics
        benchmark_data = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "metrics": self._extract_metrics(test_results),
            "summary": test_results.get("summary", {}),
            "issues_count": self._count_issues(test_results),
            "recommendations_count": self._count_recommendations(test_results),
            "git_context": git_context
        }
        
        benchmarks.append(benchmark_data)
        
        # Save updated benchmarks
        with open(self.benchmark_file, 'w') as f:
            json.dump(benchmarks, f, indent=2)
            
        print(f"✅ Benchmark saved as {version}")
        
    def compare_with_baseline(self, baseline_version: str = None) -> Dict[str, Any]:
        """Compare current performance with baseline"""
        benchmarks = self._load_benchmarks()
        
        if len(benchmarks) < 2:
            return {"error": "Need at least 2 benchmarks to compare"}
            
        # Use latest as current, specified or oldest as baseline
        current = benchmarks[-1]
        if baseline_version:
            baseline = next((b for b in benchmarks if b["version"] == baseline_version), benchmarks[0])
        else:
            baseline = benchmarks[0]
            
        comparison = {
            "baseline": {
                "version": baseline["version"],
                "timestamp": baseline["timestamp"]
            },
            "current": {
                "version": current["version"], 
                "timestamp": current["timestamp"]
            },
            "improvements": [],
            "regressions": [],
            "summary": {}
        }
        
        # Compare metrics
        for agent in current["metrics"]:
            if agent in baseline["metrics"]:
                current_scores = current["metrics"][agent]
                baseline_scores = baseline["metrics"][agent]
                
                for metric, current_score in current_scores.items():
                    baseline_score = baseline_scores.get(metric, 0)
                    improvement = current_score - baseline_score
                    
                    if improvement > 0.05:  # Significant improvement
                        comparison["improvements"].append({
                            "agent": agent,
                            "metric": metric,
                            "improvement": f"+{improvement:.3f}",
                            "from": baseline_score,
                            "to": current_score
                        })
                    elif improvement < -0.05:  # Significant regression
                        comparison["regressions"].append({
                            "agent": agent,
                            "metric": metric,
                            "regression": f"{improvement:.3f}",
                            "from": baseline_score,
                            "to": current_score
                        })
        
        # Compare issue counts
        issues_diff = current["issues_count"] - baseline["issues_count"]
        comparison["summary"]["issues_change"] = f"{issues_diff:+d} issues"
        
        return comparison
        
    def show_trends(self) -> None:
        """Display performance trends over time"""
        benchmarks = self._load_benchmarks()
        
        if len(benchmarks) == 0:
            print("No benchmarks found. Run tests first.")
            return
            
        print("📈 Performance Trends")
        print("=" * 50)
        
        for i, benchmark in enumerate(benchmarks):
            print(f"\n{i+1}. {benchmark['version']} ({benchmark['timestamp'][:10]})")
            
            # Show metrics for each agent
            for agent, metrics in benchmark["metrics"].items():
                print(f"   {agent}:")
                for metric, score in metrics.items():
                    print(f"     {metric}: {score:.3f}")
                    
            print(f"   Issues: {benchmark['issues_count']}")
            print(f"   Recommendations: {benchmark['recommendations_count']}")
            
        # Show trend summary
        if len(benchmarks) >= 2:
            latest_comparison = self.compare_with_baseline()
            print(f"\n📊 Latest vs Baseline:")
            if latest_comparison["improvements"]:
                print("✅ Improvements:")
                for imp in latest_comparison["improvements"]:
                    print(f"   {imp['agent']}/{imp['metric']}: {imp['improvement']}")
            if latest_comparison["regressions"]:
                print("❌ Regressions:")
                for reg in latest_comparison["regressions"]:
                    print(f"   {reg['agent']}/{reg['metric']}: {reg['regression']}")
                    
    def _load_benchmarks(self) -> List[Dict[str, Any]]:
        """Load existing benchmarks from file"""
        if not self.benchmark_file.exists():
            return []
            
        try:
            with open(self.benchmark_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
            
    def _extract_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Extract metrics scores by agent"""
        metrics = {}
        
        for test_run in test_results.get("test_runs", []):
            # Extract agent name from test name
            agent_name = test_run.get("test_case_name", "").split("_")[0].lower()
            if not agent_name:
                agent_name = "unknown"
                
            if agent_name not in metrics:
                metrics[agent_name] = {}
                
            # Extract metric scores
            for metric in test_run.get("metrics", []):
                metric_name = metric.get("metric", "")
                score = metric.get("score", 0.0)
                metrics[agent_name][metric_name] = score
                
        return metrics
        
    def _count_issues(self, test_results: Dict[str, Any]) -> int:
        """Count total issues across all tests"""
        total = 0
        for test_run in test_results.get("test_runs", []):
            total += len(test_run.get("issues", []))
        return total
        
    def _count_recommendations(self, test_results: Dict[str, Any]) -> int:
        """Count total recommendations across all tests"""
        total = 0
        for test_run in test_results.get("test_runs", []):
            total += len(test_run.get("recommendations", []))
        return total
    
    def save_benchmark_with_commit(self, test_results: Dict[str, Any], version: str = None, 
                                 commit_message: str = None, auto_commit: bool = True) -> None:
        """Save benchmark and optionally commit to Git"""
        # Save benchmark first
        self.save_benchmark(test_results, version)
        
        if not self.git_enabled or not auto_commit:
            return
            
        # Get the version that was saved
        benchmarks = self._load_benchmarks()
        if not benchmarks:
            return
            
        latest = benchmarks[-1]
        version_name = latest["version"]
        
        # Generate commit message if not provided
        if not commit_message:
            commit_message = self._generate_commit_message(latest, benchmarks)
        
        try:
            # Add benchmark file to git
            self._run_git_command(["add", str(self.benchmark_file)])
            
            # Commit the changes
            self._run_git_command(["commit", "-m", commit_message])
            
            print(f"📦 Committed benchmark {version_name} to Git")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git commit failed: {e}")
    
    def show_git_history(self, limit: int = 10) -> None:
        """Show benchmark performance alongside Git history"""
        if not self.git_enabled:
            print("❌ Not in a Git repository")
            return
            
        benchmarks = self._load_benchmarks()
        if not benchmarks:
            print("No benchmarks found")
            return
            
        print("📊 Performance History with Git Context")
        print("=" * 60)
        
        # Show recent benchmarks with Git info
        for benchmark in benchmarks[-limit:]:
            git_ctx = benchmark.get("git_context", {})
            commit_hash = git_ctx.get("commit_hash", "unknown")[:8]
            branch = git_ctx.get("branch", "unknown")
            
            print(f"\n📌 {benchmark['version']} ({benchmark['timestamp'][:10]})")
            print(f"   Git: {commit_hash} on {branch}")
            
            # Show key metrics
            for agent, metrics in benchmark["metrics"].items():
                print(f"   {agent}:")
                for metric, score in metrics.items():
                    print(f"     {metric}: {score:.3f}")
                    
            # Show changes if available
            if git_ctx.get("files_changed"):
                files = git_ctx["files_changed"]
                print(f"   Files changed: {', '.join(files[:3])}{'...' if len(files) > 3 else ''}")
                
            print(f"   Issues: {benchmark['issues_count']}, Recommendations: {benchmark['recommendations_count']}")
    
    def _check_git_repo(self) -> bool:
        """Check if current directory is a Git repository"""
        try:
            self._run_git_command(["rev-parse", "--git-dir"])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_git_context(self) -> Dict[str, Any]:
        """Get current Git context (commit, branch, changed files)"""
        if not self.git_enabled:
            return {}
            
        try:
            # Get current commit hash
            commit_hash = self._run_git_command(["rev-parse", "HEAD"]).strip()
            
            # Get current branch
            try:
                branch = self._run_git_command(["branch", "--show-current"]).strip()
            except subprocess.CalledProcessError:
                # Fallback for detached HEAD
                branch = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
            
            # Get files changed since last commit
            try:
                changed_files = self._run_git_command(["diff", "--name-only", "HEAD"]).strip().split("\n")
                changed_files = [f for f in changed_files if f]  # Remove empty strings
            except subprocess.CalledProcessError:
                changed_files = []
            
            # Get commit message
            try:
                commit_message = self._run_git_command(["log", "-1", "--pretty=format:%s"]).strip()
            except subprocess.CalledProcessError:
                commit_message = ""
            
            return {
                "commit_hash": commit_hash,
                "branch": branch,
                "files_changed": changed_files,
                "commit_message": commit_message,
                "has_uncommitted_changes": bool(changed_files)
            }
            
        except Exception as e:
            print(f"Warning: Could not get Git context: {e}")
            return {}
    
    def _run_git_command(self, args: List[str]) -> str:
        """Run a Git command and return the output"""
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    
    def _generate_commit_message(self, latest_benchmark: Dict[str, Any], 
                               all_benchmarks: List[Dict[str, Any]]) -> str:
        """Generate descriptive commit message for benchmark"""
        version = latest_benchmark["version"]
        issues = latest_benchmark["issues_count"]
        
        # Calculate improvement if we have previous benchmarks
        if len(all_benchmarks) >= 2:
            previous = all_benchmarks[-2]
            
            # Find the best improvement
            best_improvement = None
            best_agent = None
            best_metric = None
            
            for agent in latest_benchmark["metrics"]:
                if agent in previous["metrics"]:
                    current_scores = latest_benchmark["metrics"][agent]
                    previous_scores = previous["metrics"][agent]
                    
                    for metric, current_score in current_scores.items():
                        previous_score = previous_scores.get(metric, 0)
                        improvement = current_score - previous_score
                        
                        if best_improvement is None or improvement > best_improvement:
                            best_improvement = improvement
                            best_agent = agent
                            best_metric = metric
            
            if best_improvement and best_improvement > 0.01:
                return f"benchmark: {version} - {best_agent} {best_metric} +{best_improvement:.3f} ({issues} issues)"
            elif best_improvement and best_improvement < -0.01:
                return f"benchmark: {version} - {best_agent} {best_metric} {best_improvement:.3f} ({issues} issues)"
        
        return f"benchmark: {version} - {issues} issues remaining"

def main():
    """CLI interface for benchmark tracking"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track DeepEval benchmarks over time")
    parser.add_argument("action", choices=["save", "save-commit", "compare", "trends", "git-history"], 
                       help="Action to perform")
    parser.add_argument("--version", help="Version name for benchmark")
    parser.add_argument("--baseline", help="Baseline version for comparison")
    parser.add_argument("--results", default="results/deepeval_results.json",
                       help="Path to test results JSON")
    parser.add_argument("--commit-message", help="Custom commit message for Git")
    
    args = parser.parse_args()
    
    tracker = BenchmarkTracker()
    
    if args.action == "save":
        # Load current test results
        results_file = Path(args.results)
        if not results_file.exists():
            print(f"❌ Results file not found: {results_file}")
            return
            
        with open(results_file) as f:
            test_results = json.load(f)
            
        tracker.save_benchmark(test_results, args.version)
        
    elif args.action == "save-commit":
        # Load current test results and save with Git commit
        results_file = Path(args.results)
        if not results_file.exists():
            print(f"❌ Results file not found: {results_file}")
            return
            
        with open(results_file) as f:
            test_results = json.load(f)
            
        tracker.save_benchmark_with_commit(test_results, args.version, args.commit_message)
        
    elif args.action == "compare":
        comparison = tracker.compare_with_baseline(args.baseline)
        
        if "error" in comparison:
            print(f"❌ {comparison['error']}")
            return
            
        print("📊 Performance Comparison")
        print("=" * 50)
        print(f"Baseline: {comparison['baseline']['version']} ({comparison['baseline']['timestamp'][:10]})")
        print(f"Current:  {comparison['current']['version']} ({comparison['current']['timestamp'][:10]})")
        
        if comparison["improvements"]:
            print(f"\n✅ Improvements ({len(comparison['improvements'])}):")
            for imp in comparison["improvements"]:
                print(f"   {imp['agent']}/{imp['metric']}: {imp['from']:.3f} → {imp['to']:.3f} ({imp['improvement']})")
                
        if comparison["regressions"]:
            print(f"\n❌ Regressions ({len(comparison['regressions'])}):")
            for reg in comparison["regressions"]:
                print(f"   {reg['agent']}/{reg['metric']}: {reg['from']:.3f} → {reg['to']:.3f} ({reg['regression']})")
                
        if not comparison["improvements"] and not comparison["regressions"]:
            print("\n📊 No significant changes detected")
            
        print(f"\nIssues: {comparison['summary']['issues_change']}")
        
    elif args.action == "trends":
        tracker.show_trends()
        
    elif args.action == "git-history":
        tracker.show_git_history()

if __name__ == "__main__":
    main()