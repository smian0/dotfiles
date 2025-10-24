"""
Base Orchestrator Framework
============================

Abstract base class for agent orchestration patterns.
Handles agent composition, coordination, and result synthesis.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from ..agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class AgentExecutionArtifact:
    """Detailed artifact from a single agent execution"""
    agent_name: str
    agent_type: str
    model_id: str
    temperature: float
    max_tokens: int
    input_prompt: str
    output_content: str
    execution_time: float
    success: bool
    timestamp: str
    error: Optional[str] = None
    token_usage: Optional[Dict[str, int]] = None


@dataclass
class ArtifactReport:
    """Comprehensive execution artifacts for full transparency"""
    orchestrator_name: str
    total_duration: float
    total_agents_used: int
    workflow_type: str
    agent_artifacts: List[AgentExecutionArtifact]
    orchestration_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy display"""
        return {
            'orchestrator': self.orchestrator_name,
            'total_duration': self.total_duration,
            'total_agents': self.total_agents_used,
            'workflow': self.workflow_type,
            'agents': [
                {
                    'name': a.agent_name,
                    'type': a.agent_type,
                    'model': a.model_id,
                    'temperature': a.temperature,
                    'max_tokens': a.max_tokens,
                    'input_length': len(a.input_prompt),
                    'output_length': len(a.output_content),
                    'duration': a.execution_time,
                    'success': a.success,
                    'timestamp': a.timestamp
                }
                for a in self.agent_artifacts
            ],
            'metadata': self.orchestration_metadata
        }


@dataclass
class OrchestrationResult:
    """Result from orchestrator execution"""
    success: bool
    final_answer: str
    steps: List[Dict[str, Any]]
    duration: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    artifacts: Optional[ArtifactReport] = None  # Detailed execution artifacts

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseOrchestrator(ABC):
    """
    Abstract base class for all orchestrators.

    Responsibilities:
    - Manage collection of agents
    - Coordinate agent execution
    - Handle execution flow (sequential, parallel, conditional)
    - Synthesize results from multiple agents
    - Provide standard interface for orchestration

    Usage:
        class MyOrchestrator(BaseOrchestrator):
            def orchestrate(self, task: str) -> OrchestrationResult:
                # Custom orchestration logic
                pass

        orch = MyOrchestrator()
        orch.add_agent('research', ResearchAgent())
        result = orch.run("complex task")
    """

    def __init__(self, name: str = "Orchestrator"):
        """
        Initialize orchestrator.

        Args:
            name: Name of this orchestrator instance
        """
        self.name = name
        self._agents: Dict[str, BaseAgent] = {}
        self._execution_history: List[Dict[str, Any]] = []

        logger.info(f"Initialized {self.name}")

    def add_agent(self, key: str, agent: BaseAgent) -> None:
        """
        Add an agent to the orchestrator.

        Args:
            key: Unique key to identify this agent
            agent: Agent instance to add
        """
        if key in self._agents:
            logger.warning(f"Overwriting existing agent with key '{key}'")

        self._agents[key] = agent
        logger.info(f"{self.name}: Added agent '{key}' ({agent.__class__.__name__})")

    def add_agents(self, agents: Dict[str, BaseAgent]) -> None:
        """
        Add multiple agents at once.

        Args:
            agents: Dictionary of key -> agent mappings
        """
        for key, agent in agents.items():
            self.add_agent(key, agent)

    def remove_agent(self, key: str) -> bool:
        """
        Remove an agent from the orchestrator.

        Args:
            key: Key of agent to remove

        Returns:
            True if agent was removed, False if not found
        """
        if key in self._agents:
            del self._agents[key]
            logger.info(f"{self.name}: Removed agent '{key}'")
            return True
        return False

    def get_agent(self, key: str) -> Optional[BaseAgent]:
        """
        Get an agent by key.

        Args:
            key: Key of agent to retrieve

        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(key)

    @property
    def agents(self) -> Dict[str, BaseAgent]:
        """Get all registered agents"""
        return self._agents.copy()

    @property
    def agent_names(self) -> List[str]:
        """Get list of registered agent keys"""
        return list(self._agents.keys())

    @abstractmethod
    def orchestrate(self, task: str, **kwargs) -> OrchestrationResult:
        """
        Main orchestration logic.

        This method should:
        1. Break down the task into subtasks
        2. Delegate to appropriate agents
        3. Coordinate execution (sequential/parallel)
        4. Synthesize results
        5. Return final result

        Args:
            task: The main task to orchestrate
            **kwargs: Additional parameters

        Returns:
            OrchestrationResult with final answer and execution details
        """
        pass

    def run(self, task: str, **kwargs) -> OrchestrationResult:
        """
        Execute orchestration with logging and error handling.

        This wraps the orchestrate() method with standard handling.

        Args:
            task: The task to execute
            **kwargs: Additional parameters

        Returns:
            OrchestrationResult
        """
        logger.info(f"{self.name}: Starting orchestration for task: {task[:100]}...")

        try:
            result = self.orchestrate(task, **kwargs)

            # Record in history
            self._execution_history.append({
                'task': task,
                'success': result.success,
                'steps': len(result.steps),
                'duration': result.duration
            })

            logger.info(
                f"{self.name}: Completed in {result.duration:.2f}s "
                f"({len(result.steps)} steps)"
            )

            return result

        except Exception as e:
            error_msg = f"Orchestration failed: {str(e)}"
            logger.error(f"{self.name}: {error_msg}")

            return OrchestrationResult(
                success=False,
                final_answer="",
                steps=[],
                duration=0.0,
                error=error_msg
            )

    def synthesize_results(
        self,
        results: List[AgentResult],
        synthesis_prompt: Optional[str] = None
    ) -> str:
        """
        Synthesize results from multiple agents into final answer.

        Default implementation: concatenate results.
        Override for custom synthesis logic.

        Args:
            results: List of agent results to synthesize
            synthesis_prompt: Optional custom prompt for synthesis

        Returns:
            Synthesized final answer
        """
        if not results:
            return "No results to synthesize"

        # Default: Concatenate successful results
        successful = [r for r in results if r.success]

        if not successful:
            return "All agent executions failed"

        # Simple concatenation
        parts = []
        for i, result in enumerate(successful, 1):
            parts.append(f"**Agent {i} ({result.metadata.get('agent_name', 'unknown')})**:\n{result.content}")

        return "\n\n".join(parts)

    @property
    def stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        total_executions = len(self._execution_history)
        successful = sum(1 for h in self._execution_history if h['success'])

        return {
            'name': self.name,
            'total_executions': total_executions,
            'successful_executions': successful,
            'success_rate': successful / total_executions if total_executions > 0 else 0.0,
            'registered_agents': len(self._agents),
            'agent_names': self.agent_names
        }

    def reset_history(self):
        """Clear execution history"""
        self._execution_history = []
        logger.info(f"{self.name}: History cleared")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"agents={len(self._agents)})"
        )
