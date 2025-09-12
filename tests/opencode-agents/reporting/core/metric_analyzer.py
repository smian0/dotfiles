"""
Metric Analysis Engine
Provides multi-dimensional analysis of DeepEval results
"""
import statistics
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from .data_collector import TestResult, MetricResult


@dataclass
class MetricSummary:
    """Summary statistics for a metric"""
    name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    avg_score: float
    median_score: float
    min_score: float
    max_score: float
    std_dev: float
    threshold: Optional[float] = None


@dataclass
class AgentPerformance:
    """Performance summary for an agent"""
    agent_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    pass_rate: float
    avg_duration: float
    total_duration: float
    metric_scores: Dict[str, float]
    common_failures: List[Tuple[str, int]]


@dataclass
class TestCategoryAnalysis:
    """Analysis of test results by category"""
    category: str
    total_tests: int
    performance_metrics: Dict[str, float]
    failure_patterns: List[str]
    recommendations: List[str]


class MetricAnalyzer:
    """Analyzes DeepEval results across multiple dimensions"""
    
    def __init__(self, results: List[TestResult]):
        self.results = results
        self.metric_summaries: Dict[str, MetricSummary] = {}
        self.agent_performance: Dict[str, AgentPerformance] = {}
        
    def analyze_all(self) -> Dict[str, Any]:
        """Perform comprehensive analysis across all dimensions"""
        return {
            'overview': self.analyze_overview(),
            'metrics': self.analyze_metrics(),
            'agents': self.analyze_agents(),
            'categories': self.analyze_test_categories(),
            'trends': self.analyze_trends(),
            'correlations': self.analyze_correlations(),
            'failure_analysis': self.analyze_failures(),
            'recommendations': self.generate_recommendations()
        }
    
    def analyze_overview(self) -> Dict[str, Any]:
        """Generate high-level overview statistics"""
        if not self.results:
            return {'error': 'No test results available'}
        
        status_counts = Counter(result.status for result in self.results)
        total_tests = len(self.results)
        
        durations = [r.duration for r in self.results if r.duration > 0]
        avg_duration = statistics.mean(durations) if durations else 0
        total_duration = sum(durations)
        
        return {
            'total_tests': total_tests,
            'passed': status_counts.get('passed', 0),
            'failed': status_counts.get('failed', 0),
            'errors': status_counts.get('error', 0),
            'pass_rate': round((status_counts.get('passed', 0) / total_tests) * 100, 2),
            'avg_duration': round(avg_duration, 2),
            'total_duration': round(total_duration, 2),
            'agents_tested': len(set(r.agent_name for r in self.results)),
            'unique_metrics': len(set(
                metric_name 
                for result in self.results 
                for metric_name in result.metrics.keys()
            ))
        }
    
    def analyze_metrics(self) -> Dict[str, MetricSummary]:
        """Analyze performance by metric type"""
        metric_data = defaultdict(list)
        metric_thresholds = {}
        
        # Collect all metric scores
        for result in self.results:
            for metric_name, metric_result in result.metrics.items():
                if isinstance(metric_result, MetricResult):
                    score = metric_result.score
                    passed = metric_result.passed
                    threshold = metric_result.threshold
                elif isinstance(metric_result, dict):
                    score = metric_result.get('score', 0)
                    passed = metric_result.get('passed', True)
                    threshold = metric_result.get('threshold')
                else:
                    continue
                
                metric_data[metric_name].append({
                    'score': score,
                    'passed': passed
                })
                
                if threshold is not None:
                    metric_thresholds[metric_name] = threshold
        
        # Calculate summary statistics for each metric
        summaries = {}
        for metric_name, data_points in metric_data.items():
            if not data_points:
                continue
                
            scores = [dp['score'] for dp in data_points]
            passed_count = sum(1 for dp in data_points if dp['passed'])
            
            summaries[metric_name] = MetricSummary(
                name=metric_name,
                total_tests=len(data_points),
                passed_tests=passed_count,
                failed_tests=len(data_points) - passed_count,
                pass_rate=round((passed_count / len(data_points)) * 100, 2),
                avg_score=round(statistics.mean(scores), 3),
                median_score=round(statistics.median(scores), 3),
                min_score=round(min(scores), 3),
                max_score=round(max(scores), 3),
                std_dev=round(statistics.stdev(scores) if len(scores) > 1 else 0, 3),
                threshold=metric_thresholds.get(metric_name)
            )
        
        self.metric_summaries = summaries
        return summaries
    
    def analyze_agents(self) -> Dict[str, AgentPerformance]:
        """Analyze performance by agent"""
        agent_data = defaultdict(list)
        
        # Group results by agent
        for result in self.results:
            agent_data[result.agent_name].append(result)
        
        # Calculate performance for each agent
        performance = {}
        for agent_name, results in agent_data.items():
            status_counts = Counter(r.status for r in results)
            total_tests = len(results)
            
            durations = [r.duration for r in results if r.duration > 0]
            avg_duration = statistics.mean(durations) if durations else 0
            total_duration = sum(durations)
            
            # Calculate average metric scores
            metric_scores = defaultdict(list)
            for result in results:
                for metric_name, metric_result in result.metrics.items():
                    if isinstance(metric_result, MetricResult):
                        score = metric_result.score
                    elif isinstance(metric_result, dict):
                        score = metric_result.get('score', 0)
                    else:
                        continue
                    metric_scores[metric_name].append(score)
            
            avg_metric_scores = {
                metric: round(statistics.mean(scores), 3)
                for metric, scores in metric_scores.items()
            }
            
            # Identify common failure patterns
            failure_reasons = []
            for result in results:
                if result.status != 'passed' and result.error_message:
                    failure_reasons.append(result.error_message[:100])
            
            common_failures = Counter(failure_reasons).most_common(5)
            
            performance[agent_name] = AgentPerformance(
                agent_name=agent_name,
                total_tests=total_tests,
                passed_tests=status_counts.get('passed', 0),
                failed_tests=status_counts.get('failed', 0),
                error_tests=status_counts.get('error', 0),
                pass_rate=round((status_counts.get('passed', 0) / total_tests) * 100, 2),
                avg_duration=round(avg_duration, 2),
                total_duration=round(total_duration, 2),
                metric_scores=avg_metric_scores,
                common_failures=common_failures
            )
        
        self.agent_performance = performance
        return performance
    
    def analyze_test_categories(self) -> Dict[str, TestCategoryAnalysis]:
        """Analyze results by test category (derived from test names)"""
        categories = defaultdict(list)
        
        # Categorize tests based on naming patterns
        for result in self.results:
            category = self._categorize_test(result.test_name)
            categories[category].append(result)
        
        analyses = {}
        for category, results in categories.items():
            status_counts = Counter(r.status for r in results)
            total = len(results)
            
            # Calculate performance metrics
            performance_metrics = {
                'pass_rate': round((status_counts.get('passed', 0) / total) * 100, 2),
                'avg_duration': round(statistics.mean([r.duration for r in results if r.duration > 0]) if results else 0, 2),
                'error_rate': round((status_counts.get('error', 0) / total) * 100, 2)
            }
            
            # Identify failure patterns
            failure_patterns = []
            for result in results:
                if result.status != 'passed' and result.error_message:
                    failure_patterns.append(result.error_message[:50])
            
            failure_patterns = list(set(failure_patterns))[:5]
            
            # Generate recommendations
            recommendations = self._generate_category_recommendations(category, performance_metrics, failure_patterns)
            
            analyses[category] = TestCategoryAnalysis(
                category=category,
                total_tests=total,
                performance_metrics=performance_metrics,
                failure_patterns=failure_patterns,
                recommendations=recommendations
            )
        
        return analyses
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze trends over time (if timestamp data is available)"""
        # Sort results by timestamp
        timestamped_results = [r for r in self.results if r.timestamp]
        if len(timestamped_results) < 2:
            return {'error': 'Insufficient timestamp data for trend analysis'}
        
        timestamped_results.sort(key=lambda x: x.timestamp)
        
        # Calculate pass rates over time (if we have multiple test runs)
        # This is a simplified version - real implementation would need more sophisticated time binning
        trends = {
            'pass_rate_trend': 'stable',  # Would calculate actual trend
            'duration_trend': 'stable',   # Would calculate actual trend  
            'metric_trends': {}           # Would calculate per-metric trends
        }
        
        return trends
    
    def analyze_correlations(self) -> Dict[str, Any]:
        """Analyze correlations between metrics and outcomes"""
        correlations = {}
        
        # Collect data for correlation analysis
        metric_scores = defaultdict(list)
        durations = []
        outcomes = []  # 1 for pass, 0 for fail
        
        for result in self.results:
            durations.append(result.duration)
            outcomes.append(1 if result.status == 'passed' else 0)
            
            for metric_name, metric_result in result.metrics.items():
                if isinstance(metric_result, MetricResult):
                    score = metric_result.score
                elif isinstance(metric_result, dict):
                    score = metric_result.get('score', 0)
                else:
                    continue
                metric_scores[metric_name].append(score)
        
        # Calculate simple correlations (would use scipy.stats in real implementation)
        correlations['duration_vs_outcome'] = self._simple_correlation(durations, outcomes)
        
        for metric_name, scores in metric_scores.items():
            if len(scores) == len(outcomes):
                correlations[f'{metric_name}_vs_outcome'] = self._simple_correlation(scores, outcomes)
        
        return correlations
    
    def analyze_failures(self) -> Dict[str, Any]:
        """Deep analysis of test failures"""
        failed_results = [r for r in self.results if r.status != 'passed']
        
        if not failed_results:
            return {'message': 'No failures to analyze'}
        
        # Group failures by type
        failure_types = defaultdict(list)
        for result in failed_results:
            failure_type = self._classify_failure(result)
            failure_types[failure_type].append(result)
        
        # Analyze patterns in failures
        failure_analysis = {}
        for failure_type, failures in failure_types.items():
            failure_analysis[failure_type] = {
                'count': len(failures),
                'affected_agents': list(set(f.agent_name for f in failures)),
                'common_patterns': self._extract_failure_patterns(failures),
                'severity': self._assess_failure_severity(failures)
            }
        
        return {
            'total_failures': len(failed_results),
            'failure_types': failure_analysis,
            'most_problematic_agent': self._find_most_problematic_agent(),
            'recommendations': self._generate_failure_recommendations(failure_analysis)
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Overall pass rate recommendations
        overview = self.analyze_overview()
        if overview.get('pass_rate', 100) < 80:
            recommendations.append("🚨 Pass rate is below 80%. Consider reviewing test cases and agent implementations.")
        
        # Metric-specific recommendations
        for metric_name, summary in self.metric_summaries.items():
            if summary.pass_rate < 70:
                recommendations.append(f"📊 {metric_name} has low pass rate ({summary.pass_rate}%). Review threshold and implementation.")
        
        # Agent-specific recommendations
        for agent_name, performance in self.agent_performance.items():
            if performance.pass_rate < 75:
                recommendations.append(f"🤖 Agent '{agent_name}' needs attention - pass rate: {performance.pass_rate}%")
            
            if performance.avg_duration > 30:  # Assuming 30s is a reasonable threshold
                recommendations.append(f"⏱️ Agent '{agent_name}' is slow - avg duration: {performance.avg_duration}s")
        
        return recommendations
    
    def _categorize_test(self, test_name: str) -> str:
        """Categorize test based on naming patterns"""
        test_name_lower = test_name.lower()
        
        if 'functionality' in test_name_lower or 'basic' in test_name_lower:
            return 'functionality'
        elif 'quality' in test_name_lower or 'metric' in test_name_lower:
            return 'quality_metrics'
        elif 'edge' in test_name_lower or 'error' in test_name_lower:
            return 'edge_cases'
        elif 'performance' in test_name_lower or 'speed' in test_name_lower:
            return 'performance'
        else:
            return 'general'
    
    def _generate_category_recommendations(self, category: str, metrics: Dict, patterns: List[str]) -> List[str]:
        """Generate recommendations for a test category"""
        recommendations = []
        
        if metrics['pass_rate'] < 80:
            recommendations.append(f"Improve {category} test reliability")
        
        if metrics['error_rate'] > 10:
            recommendations.append(f"Address error handling in {category} tests")
        
        if patterns:
            recommendations.append(f"Common {category} issues: {', '.join(patterns[:2])}")
        
        return recommendations
    
    def _simple_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate simple correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            sum_y2 = sum(yi * yi for yi in y)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
        except:
            return 0.0
    
    def _classify_failure(self, result: TestResult) -> str:
        """Classify the type of failure"""
        if result.error_message:
            error_lower = result.error_message.lower()
            if 'timeout' in error_lower:
                return 'timeout'
            elif 'connection' in error_lower or 'network' in error_lower:
                return 'network'
            elif 'assertion' in error_lower:
                return 'assertion'
            elif 'exception' in error_lower:
                return 'runtime_error'
        
        return 'unknown'
    
    def _extract_failure_patterns(self, failures: List[TestResult]) -> List[str]:
        """Extract common patterns from failure messages"""
        patterns = []
        error_messages = [f.error_message for f in failures if f.error_message]
        
        # Simple pattern extraction (would use more sophisticated NLP in real implementation)
        common_words = Counter()
        for message in error_messages:
            words = message.lower().split()
            common_words.update(words)
        
        # Get most common non-trivial words
        for word, count in common_words.most_common(3):
            if len(word) > 3 and count > 1:
                patterns.append(f"{word} ({count} occurrences)")
        
        return patterns
    
    def _assess_failure_severity(self, failures: List[TestResult]) -> str:
        """Assess the severity of failures"""
        if len(failures) > 5:
            return 'high'
        elif len(failures) > 2:
            return 'medium'
        else:
            return 'low'
    
    def _find_most_problematic_agent(self) -> Optional[str]:
        """Find the agent with the most issues"""
        if not self.agent_performance:
            return None
        
        worst_agent = min(
            self.agent_performance.values(),
            key=lambda x: x.pass_rate,
            default=None
        )
        
        return worst_agent.agent_name if worst_agent else None
    
    def _generate_failure_recommendations(self, failure_analysis: Dict) -> List[str]:
        """Generate recommendations based on failure analysis"""
        recommendations = []
        
        for failure_type, analysis in failure_analysis.items():
            if analysis['severity'] == 'high':
                recommendations.append(f"🚨 High priority: Address {failure_type} failures ({analysis['count']} occurrences)")
            elif analysis['count'] > 3:
                recommendations.append(f"⚠️ Investigate {failure_type} failures affecting {len(analysis['affected_agents'])} agents")
        
        return recommendations