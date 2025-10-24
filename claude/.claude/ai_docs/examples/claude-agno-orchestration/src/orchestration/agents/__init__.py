"""
Orchestration Agents
====================

Collection of specialized agents for different tasks.

Available Agents:
- BaseAgent: Abstract base class for all agents
- ResearchAgent: Fact-finding and information gathering
- CalculatorAgent: Mathematical calculations
- CodeAnalyzerAgent: Code quality analysis
- DeepWebResearcherAgent: Comprehensive web research
- AdaptiveDeepResearchAgent: Advanced research with adaptive strategies
"""

from .base import BaseAgent, AgentConfig, AgentResult
from .research import ResearchAgent
from .calculator import CalculatorAgent
from .code_analyzer import CodeAnalyzerAgent
from .deep_web_researcher import DeepWebResearcherAgent
from .adaptive_deep_researcher import AdaptiveDeepResearchAgent, create_adaptive_researcher

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'AgentResult',
    'ResearchAgent',
    'CalculatorAgent',
    'CodeAnalyzerAgent',
    'DeepWebResearcherAgent',
    'AdaptiveDeepResearchAgent',
    'create_adaptive_researcher',
]
