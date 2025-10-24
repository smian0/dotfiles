"""
Direct Orchestrator
===================

Simplest orchestration pattern: Python functions call agents directly.

Best for:
- Simple workflows
- Sequential execution
- Scripts and automation
- Quick prototypes
"""

from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
import logging

from .base import BaseOrchestrator, OrchestrationResult, AgentExecutionArtifact, ArtifactReport
from ..agents.base import AgentResult

logger = logging.getLogger(__name__)


class DirectOrchestrator(BaseOrchestrator):
    """
    Direct orchestration pattern.

    Characteristics:
    - Agents called directly as Python functions
    - Explicit control flow
    - Sequential by default
    - Easy to understand and debug

    Usage:
        orch = DirectOrchestrator()
        orch.add_agent('research', ResearchAgent())
        orch.add_agent('calculator', CalculatorAgent())

        result = orch.run("What's California's population density?")

    The orchestrator will:
    1. Use research agent to get population and area
    2. Use calculator agent to compute density
    3. Synthesize results into final answer
    """

    def __init__(self, name: str = "DirectOrchestrator"):
        super().__init__(name)
        self._workflow: Optional[Callable] = None

    def set_workflow(self, workflow_func: Callable) -> None:
        """
        Set a custom workflow function.

        The workflow function receives (self, task, **kwargs) and should
        return a list of AgentResults and a final answer string.

        Example:
            def my_workflow(orch, task, **kwargs):
                # Custom logic
                results = []
                results.append(orch.agents['agent1'].run(task))
                return results, "final answer"

            orch.set_workflow(my_workflow)
        """
        self._workflow = workflow_func
        logger.info(f"{self.name}: Custom workflow set")

    def orchestrate(self, task: str, **kwargs) -> OrchestrationResult:
        """
        Execute direct orchestration.

        If custom workflow is set, uses that.
        Otherwise, uses intelligent default workflow.

        Args:
            task: Main task to orchestrate
            **kwargs: Additional parameters

        Returns:
            OrchestrationResult with final answer and detailed artifacts
        """
        start_time = datetime.now()
        steps = []

        try:
            if self._workflow:
                # Use custom workflow
                results, final_answer = self._workflow(self, task, **kwargs)
                workflow_type = 'custom'
            else:
                # Use intelligent default workflow
                results, final_answer = self._default_workflow(task, **kwargs)
                workflow_type = self._detect_workflow_type(results)

            # Build detailed artifacts
            agent_artifacts = []
            for result in results:
                # Get agent config info
                agent_name = result.metadata.get('agent_name', 'unknown')
                agent_obj = None
                for key, agent in self._agents.items():
                    if agent.config.name == agent_name:
                        agent_obj = agent
                        break

                # Create artifact with full details
                artifact = AgentExecutionArtifact(
                    agent_name=agent_name,
                    agent_type=agent_obj.__class__.__name__ if agent_obj else 'Unknown',
                    model_id=agent_obj.config.model_id if agent_obj else 'unknown',
                    temperature=agent_obj.config.temperature if agent_obj else 0.0,
                    max_tokens=agent_obj.config.max_tokens if agent_obj else 0,
                    input_prompt=result.metadata.get('prompt', task)[:500],  # Truncate for readability
                    output_content=result.content,
                    execution_time=result.duration,
                    success=result.success,
                    timestamp=datetime.now().isoformat(),
                    error=result.error,
                    token_usage=result.metadata.get('token_usage')
                )
                agent_artifacts.append(artifact)

                # Record steps (summary)
                steps.append({
                    'agent': agent_name,
                    'success': result.success,
                    'duration': result.duration,
                    'content_preview': result.content[:100] if result.content else None
                })

            duration = (datetime.now() - start_time).total_seconds()

            # Build comprehensive artifact report
            artifact_report = ArtifactReport(
                orchestrator_name=self.name,
                total_duration=duration,
                total_agents_used=len(results),
                workflow_type=workflow_type,
                agent_artifacts=agent_artifacts,
                orchestration_metadata={
                    'task': task[:200],
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'success': True,
                    'agent_sequence': [a.agent_name for a in agent_artifacts]
                }
            )

            return OrchestrationResult(
                success=True,
                final_answer=final_answer,
                steps=steps,
                duration=duration,
                metadata={
                    'orchestrator': self.name,
                    'agent_count': len(results),
                    'workflow_type': workflow_type
                },
                artifacts=artifact_report
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = f"Orchestration failed: {str(e)}"
            logger.error(f"{self.name}: {error_msg}")

            return OrchestrationResult(
                success=False,
                final_answer="",
                steps=steps,
                duration=duration,
                error=error_msg
            )

    def _detect_workflow_type(self, results: List[AgentResult]) -> str:
        """Detect which workflow pattern was used based on agent sequence"""
        if not results:
            return 'empty'
        if len(results) == 1:
            agent_name = results[0].metadata.get('agent_name', '')
            if 'Deep' in agent_name or 'Research' in agent_name:
                return 'deep_research'
            return 'single_agent'

        agent_names = [r.metadata.get('agent_name', '') for r in results]
        if 'ResearchAgent' in agent_names and 'CalculatorAgent' in agent_names:
            return 'research_calculate'
        if 'ResearchAgent' in agent_names and 'CodeAnalyzerAgent' in agent_names:
            return 'research_analyze'

        return 'sequential'

    def _default_workflow(self, task: str, **kwargs) -> tuple[List[AgentResult], str]:
        """
        Intelligent default workflow.

        Analyzes the task and decides which agents to use and in what order.

        Strategy:
        - If only 1 agent: Use it directly
        - If 2+ agents: Try to intelligently sequence them
        - Research → Calculate pattern (for density/ratio questions)
        - Research → Analysis pattern (for insight questions)

        Returns:
            Tuple of (agent_results, final_answer)
        """
        if not self._agents:
            raise ValueError("No agents registered")

        results = []

        # Single agent: Use it directly
        if len(self._agents) == 1:
            agent = list(self._agents.values())[0]
            result = agent.run(task)
            results.append(result)
            return results, result.content

        # Multiple agents: Intelligent sequencing
        agent_names = list(self._agents.keys())

        # Pattern 1: Research + Calculate
        if 'research' in agent_names and 'calculator' in agent_names:
            if self._is_calculation_task(task):
                return self._research_calculate_workflow(task)

        # Pattern 2: Research + Analysis
        if 'research' in agent_names and 'code_analyzer' in agent_names:
            return self._research_analyze_workflow(task)

        # Pattern 3: Deep Research
        if 'deep_web_researcher' in agent_names:
            agent = self._agents['deep_web_researcher']
            result = agent.run(task)
            results.append(result)
            return results, result.content

        # Fallback: Sequential execution of all agents
        return self._sequential_workflow(task)

    def _is_calculation_task(self, task: str) -> bool:
        """Determine if task requires calculation"""
        calc_keywords = ['density', 'ratio', 'percentage', 'divide', 'calculate',
                        'how many', 'average', 'rate', 'per']
        return any(keyword in task.lower() for keyword in calc_keywords)

    def _research_calculate_workflow(self, task: str) -> tuple[List[AgentResult], str]:
        """Research → Calculate workflow pattern"""
        results = []

        # Step 1: Research
        logger.info(f"{self.name}: Step 1 - Research")
        research = self._agents['research'].run(task)
        results.append(research)

        if not research.success:
            return results, "Research step failed"

        # Step 2: Calculate based on research
        logger.info(f"{self.name}: Step 2 - Calculate")

        # Extract numbers from research result for calculation
        calc_prompt = f"Based on this data: {research.content}. {task}"
        calculation = self._agents['calculator'].run(calc_prompt)
        results.append(calculation)

        # Synthesize
        final_answer = self._synthesize_research_calc(research, calculation, task)

        return results, final_answer

    def _research_analyze_workflow(self, task: str) -> tuple[List[AgentResult], str]:
        """Research → Analysis workflow pattern"""
        results = []

        # Step 1: Research/gather info
        logger.info(f"{self.name}: Step 1 - Research")
        research = self._agents['research'].run(task)
        results.append(research)

        # Step 2: Analyze
        logger.info(f"{self.name}: Step 2 - Analyze")
        analyzer = self._agents['code_analyzer']
        analysis = analyzer.run(research.content)
        results.append(analysis)

        # Synthesize
        final_answer = f"**Research Findings:**\n{research.content}\n\n**Analysis:**\n{analysis.content}"

        return results, final_answer

    def _sequential_workflow(self, task: str) -> tuple[List[AgentResult], str]:
        """Execute all agents sequentially"""
        results = []

        for name, agent in self._agents.items():
            logger.info(f"{self.name}: Executing {name}")
            result = agent.run(task)
            results.append(result)

        final_answer = self.synthesize_results(results)

        return results, final_answer

    def _synthesize_research_calc(
        self,
        research: AgentResult,
        calculation: AgentResult,
        original_task: str
    ) -> str:
        """Synthesize research + calculation into coherent answer"""
        if not calculation.success:
            return f"Based on research: {research.content}\n\nCalculation failed: {calculation.error}"

        return f"""**Answer:** {calculation.content}

**Details:**
- Research: {research.content}
- Calculation: {calculation.content}

This answers the question: "{original_task}"
"""

    def run_sequential(self, tasks: List[tuple[str, str]]) -> Dict[str, AgentResult]:
        """
        Run multiple agent tasks sequentially.

        Args:
            tasks: List of (agent_key, prompt) tuples

        Returns:
            Dictionary of agent_key -> AgentResult

        Example:
            results = orch.run_sequential([
                ('research', 'Find California stats'),
                ('calculator', 'Calculate 39000000 / 163696')
            ])
        """
        results = {}

        for agent_key, prompt in tasks:
            if agent_key not in self._agents:
                logger.warning(f"Agent '{agent_key}' not found, skipping")
                continue

            logger.info(f"{self.name}: Running {agent_key}")
            result = self._agents[agent_key].run(prompt)
            results[agent_key] = result

        return results
