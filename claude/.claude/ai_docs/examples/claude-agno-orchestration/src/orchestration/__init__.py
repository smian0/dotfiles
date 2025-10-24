"""
Claude + Agno Multi-Agent Orchestration System
===============================================

A production-ready framework for building multi-agent systems where
Claude Agent SDK orchestrates specialized Agno agents.

Key Components:
- **Agents**: Specialized workers (ResearchAgent, CalculatorAgent, etc.)
- **Orchestrators**: Coordination patterns (DirectOrchestrator, etc.)
- **Workflows**: Pre-built multi-agent systems

Quick Start:
    from orchestration import DirectOrchestrator, ResearchAgent, CalculatorAgent

    # Create orchestrator
    orch = DirectOrchestrator()

    # Add agents
    orch.add_agent('research', ResearchAgent())
    orch.add_agent('calculator', CalculatorAgent())

    # Execute
    result = orch.run("What's California's population density?")
    print(result.final_answer)
"""

# Agents
from .agents import (
    BaseAgent,
    AgentConfig,
    AgentResult,
    ResearchAgent,
    CalculatorAgent,
    CodeAnalyzerAgent,
    DeepWebResearcherAgent,
    AdaptiveDeepResearchAgent,
    create_adaptive_researcher,
)

# Orchestrators
from .orchestrators import (
    BaseOrchestrator,
    OrchestrationResult,
    DirectOrchestrator,
)

# Utilities
from .utils import (
    ResearchOutputManager,
    generate_summary,
    ArtifactVisualizer,
    visualize_artifacts,
)

__version__ = '0.1.0'

__all__ = [
    # Version
    '__version__',

    # Agent Base Classes
    'BaseAgent',
    'AgentConfig',
    'AgentResult',

    # Specialized Agents
    'ResearchAgent',
    'CalculatorAgent',
    'CodeAnalyzerAgent',
    'DeepWebResearcherAgent',
    'AdaptiveDeepResearchAgent',
    'create_adaptive_researcher',

    # Orchestrator Base Classes
    'BaseOrchestrator',
    'OrchestrationResult',

    # Orchestrator Implementations
    'DirectOrchestrator',

    # Utilities
    'ResearchOutputManager',
    'generate_summary',
    'ArtifactVisualizer',
    'visualize_artifacts',
]
