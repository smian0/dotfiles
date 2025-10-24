"""
Base Agent Framework
====================

Abstract base class for all specialized agents in the orchestration system.
Provides standard interface, error handling, logging, and metrics collection.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from agno.agent import Agent

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an agent"""
    name: str
    model_id: str = "claude-sonnet-4"
    instructions: str = ""
    temperature: float = 0.3
    max_tokens: int = 2000
    markdown: bool = False
    additional_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    content: str
    duration: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    Responsibilities:
    - Provide standard interface for agent execution
    - Handle errors gracefully
    - Collect metrics (duration, success rate)
    - Validate inputs
    - Log execution details

    Usage:
        class MyAgent(BaseAgent):
            def _create_agent(self) -> Agent:
                return Agent(
                    model=Claude(id=self.config.model_id),
                    instructions=self.config.instructions
                )

        agent = MyAgent(config)
        result = agent.run("Your prompt here")
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the agent with configuration.

        Args:
            config: Agent configuration. If None, uses default config.
        """
        self.config = config or self._default_config()
        self._agent: Optional[Agent] = None
        self._execution_count = 0
        self._total_duration = 0.0

        logger.info(f"Initialized {self.__class__.__name__} with model {self.config.model_id}")

    @abstractmethod
    def _default_config(self) -> AgentConfig:
        """
        Provide default configuration for this agent type.

        Returns:
            Default AgentConfig for this agent
        """
        pass

    @abstractmethod
    def _create_agent(self) -> Agent:
        """
        Create the underlying Agno agent.

        This method should instantiate and return an Agno Agent with
        the appropriate model and instructions for this agent's specialty.

        Returns:
            Configured Agno Agent instance
        """
        pass

    @property
    def agent(self) -> Agent:
        """
        Lazy-load the Agno agent instance.

        Returns:
            Agno Agent instance
        """
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    def validate_input(self, prompt: str) -> tuple[bool, Optional[str]]:
        """
        Validate input before execution.

        Override this method to add agent-specific validation logic.

        Args:
            prompt: The input prompt to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not prompt or not prompt.strip():
            return False, "Prompt cannot be empty"

        if len(prompt) > 50000:
            return False, "Prompt exceeds maximum length of 50000 characters"

        return True, None

    def run(self, prompt: str, **kwargs) -> AgentResult:
        """
        Execute the agent with the given prompt.

        This method handles:
        - Input validation
        - Timing
        - Error handling
        - Metrics collection
        - Logging

        Args:
            prompt: The task/question for the agent
            **kwargs: Additional parameters passed to agent

        Returns:
            AgentResult with success status, content, and metadata
        """
        start_time = datetime.now()

        # Validate input
        is_valid, error_msg = self.validate_input(prompt)
        if not is_valid:
            logger.error(f"{self.config.name} validation failed: {error_msg}")
            return AgentResult(
                success=False,
                content="",
                duration=0.0,
                error=error_msg
            )

        try:
            logger.info(f"{self.config.name} processing: {prompt[:100]}...")

            # Execute agent
            result = self.agent.run(prompt, **kwargs)

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()

            # Update metrics
            self._execution_count += 1
            self._total_duration += duration

            logger.info(
                f"{self.config.name} completed in {duration:.2f}s "
                f"(avg: {self.average_duration:.2f}s)"
            )

            return AgentResult(
                success=True,
                content=result.content,
                duration=duration,
                metadata={
                    'agent_name': self.config.name,
                    'execution_count': self._execution_count,
                    'timestamp': start_time.isoformat(),
                    'prompt': prompt  # Capture input for artifact tracking
                }
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = f"Agent execution failed: {str(e)}"
            logger.error(f"{self.config.name} error: {error_msg}")

            return AgentResult(
                success=False,
                content="",
                duration=duration,
                error=error_msg,
                metadata={'agent_name': self.config.name}
            )

    @property
    def average_duration(self) -> float:
        """Calculate average execution duration"""
        if self._execution_count == 0:
            return 0.0
        return self._total_duration / self._execution_count

    @property
    def stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'name': self.config.name,
            'execution_count': self._execution_count,
            'total_duration': self._total_duration,
            'average_duration': self.average_duration
        }

    def reset_stats(self):
        """Reset execution statistics"""
        self._execution_count = 0
        self._total_duration = 0.0
        logger.info(f"{self.config.name} stats reset")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.config.name}', "
            f"model='{self.config.model_id}', "
            f"executions={self._execution_count})"
        )
