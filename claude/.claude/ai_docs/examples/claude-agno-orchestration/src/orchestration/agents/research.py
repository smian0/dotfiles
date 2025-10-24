"""
Research Agent
==============

Specialized agent for finding factual information, statistics, and data.
Optimized for accuracy and conciseness.
"""

from agno.agent import Agent
from agno.models.anthropic import Claude

from .base import BaseAgent, AgentConfig


class ResearchAgent(BaseAgent):
    """
    Agent specialized in research and fact-finding.

    Capabilities:
    - Finding factual information
    - Gathering statistics and data
    - Providing concise, accurate answers
    - Citing sources when possible

    Best for:
    - "What is the population of California?"
    - "Find key statistics about Python adoption"
    - "What are the main features of React?"
    """

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="ResearchAgent",
            model_id="claude-sonnet-4",
            instructions="""You are a research specialist focused on finding factual information.

Your responsibilities:
1. Provide accurate, factual information
2. Be concise and to-the-point
3. Focus on numbers, statistics, and verifiable facts
4. Cite sources when possible
5. If uncertain, indicate confidence level

Format your responses clearly:
- Start with the key fact/answer
- Provide supporting details if needed
- Keep responses under 200 words unless specifically asked for more

Examples of good responses:
- "Population: 39.2 million (2024 estimate)"
- "Python ranks #1 in TIOBE Index as of 2024"
- "React has 3 core features: Components, JSX, Virtual DOM"

Avoid:
- Speculation or opinions
- Overly verbose explanations
- Tangential information""",
            temperature=0.3,  # Lower temperature for factual accuracy
            max_tokens=2000,
            markdown=False
        )

    def _create_agent(self) -> Agent:
        return Agent(
            model=Claude(id=self.config.model_id),
            instructions=self.config.instructions,
            markdown=self.config.markdown
        )

    def validate_input(self, prompt: str) -> tuple[bool, str | None]:
        """Research-specific validation"""
        is_valid, error = super().validate_input(prompt)
        if not is_valid:
            return is_valid, error

        # Research prompts should be questions or requests
        if len(prompt) < 10:
            return False, "Research query too short (minimum 10 characters)"

        return True, None
