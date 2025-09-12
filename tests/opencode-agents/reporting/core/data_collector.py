"""
DeepEval Data Collector
Normalizes and collects DeepEval test results for reporting
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET


@dataclass
class TestResult:
    """Normalized test result structure"""
    test_name: str
    agent_name: str
    status: str  # passed, failed, error
    duration: float
    metrics: Dict[str, Any]
    input_query: str
    actual_output: str
    expected_output: Optional[str] = None
    error_message: Optional[str] = None
    issues: List[str] = None  # List of identified issues
    error_details: Optional[Dict[str, Any]] = None  # Technical error details
    category: str = 'uncategorized'  # Test category
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class MetricResult:
    """Individual metric result"""
    name: str
    score: float
    threshold: Optional[float] = None
    passed: bool = True
    reason: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DeepEvalDataCollector:
    """Collects and normalizes DeepEval test results from multiple sources"""
    
    def __init__(self, test_results_dir: Path):
        self.test_results_dir = Path(test_results_dir)
        self.results: List[TestResult] = []
        
    def collect_pytest_json(self, json_path: Path) -> List[TestResult]:
        """Collect results from PyTest JSON report"""
        results = []
        
        if not json_path.exists():
            return results
            
        try:
            with open(json_path) as f:
                data = json.load(f)
            
            for test in data.get('tests', []):
                test_result = self._parse_pytest_test(test)
                if test_result:
                    results.append(test_result)
                    
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing PyTest JSON: {e}")
            
        return results
    
    def collect_junit_xml(self, xml_path: Path) -> List[TestResult]:
        """Collect results from JUnit XML report"""
        results = []
        
        if not xml_path.exists():
            return results
            
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            for testcase in root.findall('.//testcase'):
                test_result = self._parse_junit_testcase(testcase)
                if test_result:
                    results.append(test_result)
                    
        except ET.ParseError as e:
            print(f"Error parsing JUnit XML: {e}")
            
        return results
    
    def collect_deepeval_json(self, json_path: Path) -> List[TestResult]:
        """Collect results from DeepEval JSON export"""
        results = []
        
        if not json_path.exists():
            return results
            
        try:
            with open(json_path) as f:
                data = json.load(f)
            
            for test_run in data.get('test_runs', []):
                test_result = self._parse_deepeval_test(test_run)
                if test_result:
                    results.append(test_result)
                    
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing DeepEval JSON: {e}")
            
        return results
    
    def collect_all_sources(self) -> List[TestResult]:
        """Collect from all available sources in results directory"""
        all_results = []
        
        # PyTest JSON reports
        pytest_json = self.test_results_dir / "report.json"
        all_results.extend(self.collect_pytest_json(pytest_json))
        
        # JUnit XML reports
        junit_xml = self.test_results_dir / "junit.xml"
        all_results.extend(self.collect_junit_xml(junit_xml))
        
        # DeepEval JSON exports
        deepeval_json = self.test_results_dir / "deepeval_results.json"
        all_results.extend(self.collect_deepeval_json(deepeval_json))
        
        # Look for additional files with naming patterns
        for file_path in self.test_results_dir.glob("*.json"):
            if "deepeval" in file_path.name and file_path != deepeval_json:
                all_results.extend(self.collect_deepeval_json(file_path))
        
        self.results = all_results
        return all_results
    
    def _parse_pytest_test(self, test_data: Dict) -> Optional[TestResult]:
        """Parse individual PyTest test result"""
        try:
            test_name = test_data.get('nodeid', '').split('::')[-1]
            agent_name = self._extract_agent_name(test_name)
            
            # Extract status
            outcome = test_data.get('outcome', 'unknown')
            status = 'passed' if outcome == 'passed' else 'failed' if outcome == 'failed' else 'error'
            
            # Extract duration
            duration = test_data.get('duration', 0.0)
            
            # Extract DeepEval metrics from call data
            metrics = self._extract_metrics_from_pytest(test_data)
            
            # Extract input/output from test data
            input_query, actual_output, expected_output = self._extract_test_data_pytest(test_data)
            
            # Extract error message if failed
            error_message = None
            if status != 'passed':
                error_message = test_data.get('call', {}).get('longrepr', '')
            
            return TestResult(
                test_name=test_name,
                agent_name=agent_name,
                status=status,
                duration=duration,
                metrics=metrics,
                input_query=input_query,
                actual_output=actual_output,
                expected_output=expected_output,
                error_message=error_message
            )
            
        except Exception as e:
            print(f"Error parsing PyTest test: {e}")
            return None
    
    def _parse_junit_testcase(self, testcase) -> Optional[TestResult]:
        """Parse individual JUnit test case"""
        try:
            test_name = testcase.get('name', '')
            agent_name = self._extract_agent_name(test_name)
            
            # Determine status
            if testcase.find('failure') is not None:
                status = 'failed'
                error_message = testcase.find('failure').text
            elif testcase.find('error') is not None:
                status = 'error'
                error_message = testcase.find('error').text
            else:
                status = 'passed'
                error_message = None
            
            duration = float(testcase.get('time', 0))
            
            # Extract metrics from system-out if available
            metrics = {}
            system_out = testcase.find('system-out')
            if system_out is not None:
                metrics = self._extract_metrics_from_output(system_out.text)
            
            return TestResult(
                test_name=test_name,
                agent_name=agent_name,
                status=status,
                duration=duration,
                metrics=metrics,
                input_query="",  # JUnit doesn't typically contain this
                actual_output="",
                error_message=error_message
            )
            
        except Exception as e:
            print(f"Error parsing JUnit testcase: {e}")
            return None
    
    def _parse_deepeval_test(self, test_run: Dict) -> Optional[TestResult]:
        """Parse individual DeepEval test run"""
        try:
            test_name = test_run.get('test_case_name', '')
            agent_name = self._extract_agent_name(test_name)
            
            status = 'passed' if test_run.get('success', False) else 'failed'
            duration = test_run.get('run_duration', 0.0)
            
            # Extract metrics
            metrics = {}
            for metric in test_run.get('metrics', []):
                metric_name = metric.get('metric', '')
                score = metric.get('score', 0.0)
                threshold = metric.get('threshold')
                passed = metric.get('success', True)
                reason = metric.get('reason', '')
                
                metrics[metric_name] = MetricResult(
                    name=metric_name,
                    score=score,
                    threshold=threshold,
                    passed=passed,
                    reason=reason
                )
            
            return TestResult(
                test_name=test_name,
                agent_name=agent_name,
                status=status,
                duration=duration,
                metrics=metrics,
                input_query=test_run.get('input', ''),
                actual_output=test_run.get('actual_output', ''),
                expected_output=test_run.get('expected_output'),
                issues=test_run.get('issues', []),
                error_details=test_run.get('error_details'),
                category=test_run.get('category', 'uncategorized')
            )
            
        except Exception as e:
            print(f"Error parsing DeepEval test: {e}")
            return None
    
    def _extract_agent_name(self, test_name: str) -> str:
        """Extract agent name from test name"""
        # Pattern: test_agent_name_* or test_*_agent_*
        patterns = [
            r'test_(\w+)_agent',
            r'test_agent_(\w+)',
            r'test_(\w+)_',
            r'(\w+)_agent'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, test_name.lower())
            if match:
                return match.group(1)
        
        return 'unknown'
    
    def _extract_metrics_from_pytest(self, test_data: Dict) -> Dict[str, MetricResult]:
        """Extract DeepEval metrics from PyTest data"""
        metrics = {}
        
        # Look for DeepEval assertions in call data
        call_data = test_data.get('call', {})
        longrepr = call_data.get('longrepr', '')
        
        if isinstance(longrepr, str):
            # Parse metric results from assertion output
            metric_patterns = [
                r'(\w+Metric).*?score:\s*([\d.]+)',
                r'(\w+).*?Score:\s*([\d.]+)',
                r'Metric\s+(\w+):\s*([\d.]+)'
            ]
            
            for pattern in metric_patterns:
                matches = re.findall(pattern, longrepr, re.IGNORECASE)
                for metric_name, score in matches:
                    metrics[metric_name] = MetricResult(
                        name=metric_name,
                        score=float(score)
                    )
        
        return metrics
    
    def _extract_metrics_from_output(self, output: str) -> Dict[str, MetricResult]:
        """Extract metrics from test output text"""
        metrics = {}
        
        # Parse common metric output patterns
        patterns = [
            r'(\w+):\s*([\d.]+)',
            r'(\w+)\s+score:\s*([\d.]+)',
            r'(\w+Metric).*?([\d.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            for metric_name, score in matches:
                metrics[metric_name] = MetricResult(
                    name=metric_name,
                    score=float(score)
                )
        
        return metrics
    
    def _extract_test_data_pytest(self, test_data: Dict) -> tuple[str, str, Optional[str]]:
        """Extract input query, actual output, and expected output from PyTest data"""
        # This would need to be customized based on how test data is stored
        # For now, return placeholders
        return "", "", None
    
    def export_normalized_data(self, output_path: Path) -> None:
        """Export normalized data to JSON"""
        output_data = {
            'collection_timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'results': [asdict(result) for result in self.results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"Exported {len(self.results)} test results to {output_path}")


if __name__ == "__main__":
    # Example usage
    collector = DeepEvalDataCollector(Path("./results"))
    results = collector.collect_all_sources()
    collector.export_normalized_data(Path("./normalized_results.json"))