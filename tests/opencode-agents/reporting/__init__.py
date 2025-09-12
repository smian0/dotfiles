"""
DeepEval HTML Report Generator Package

A comprehensive reporting system for DeepEval test results that provides:
- Multi-dimensional analysis of agent performance
- Interactive HTML reports with charts and visualizations
- Generic design for any DeepEval metrics and agents
- Self-contained reports with embedded assets

Usage:
    from reporting import DeepEvalReportGenerator
    
    generator = DeepEvalReportGenerator('path/to/test/results')
    report_path = generator.generate_full_report()
"""

from .core.report_generator import DeepEvalReportGenerator
from .core.data_collector import DeepEvalDataCollector, TestResult, MetricResult
from .core.metric_analyzer import MetricAnalyzer, MetricSummary, AgentPerformance

__version__ = "1.0.0"
__author__ = "DeepEval Report Generator"

__all__ = [
    'DeepEvalReportGenerator',
    'DeepEvalDataCollector', 
    'MetricAnalyzer',
    'TestResult',
    'MetricResult',
    'MetricSummary',
    'AgentPerformance'
]