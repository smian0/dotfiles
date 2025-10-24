"""
Calculator Agent
================

Specialized agent for mathematical calculations and numerical operations.
Optimized for accuracy and precision.
"""

from agno.agent import Agent
from agno.models.anthropic import Claude

from .base import BaseAgent, AgentConfig


class CalculatorAgent(BaseAgent):
    """
    Agent specialized in mathematical calculations.

    Capabilities:
    - Arithmetic operations (+, -, *, /)
    - Statistical calculations (mean, median, percentages)
    - Unit conversions
    - Formula evaluation
    - Number formatting

    Best for:
    - "Calculate 39000000 / 163696"
    - "What is 15% of 250?"
    - "Convert 100 miles to kilometers"
    - "Calculate average of [10, 20, 30, 40]"
    """

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="CalculatorAgent",
            model_id="claude-sonnet-4",
            instructions="""You are a precise calculator specializing in mathematical operations.

Your responsibilities:
1. Perform accurate calculations
2. Return ONLY the numerical result (with units if applicable)
3. Round to 2 decimal places unless specified otherwise
4. Show your work only if explicitly asked
5. Handle unit conversions correctly

Response format:
- For simple calculations: Return just the number (e.g., "238.25")
- For calculations with units: Number + unit (e.g., "160.93 km")
- For multiple results: One result per line

Examples of good responses:
Input: "Calculate 39000000 / 163696"
Output: "238.25"

Input: "What is 15% of 250"
Output: "37.50"

Input: "Convert 100 miles to km"
Output: "160.93 km"

Avoid:
- Explanatory text unless asked
- Approximations (always compute exact values)
- Showing work steps unless requested""",
            temperature=0.0,  # Zero temperature for deterministic math
            max_tokens=500,   # Short responses
            markdown=False
        )

    def _create_agent(self) -> Agent:
        return Agent(
            model=Claude(id=self.config.model_id),
            instructions=self.config.instructions,
            markdown=self.config.markdown
        )

    def validate_input(self, prompt: str) -> tuple[bool, str | None]:
        """Calculator-specific validation"""
        is_valid, error = super().validate_input(prompt)
        if not is_valid:
            return is_valid, error

        # Calculator prompts should contain numbers or math terms
        has_number = any(char.isdigit() for char in prompt)
        math_terms = ['calculate', 'compute', 'what is', 'divide', 'multiply',
                      'add', 'subtract', 'convert', 'average', 'mean', 'sum']
        has_math_term = any(term in prompt.lower() for term in math_terms)

        if not (has_number or has_math_term):
            return False, "Calculator input should contain numbers or mathematical operations"

        return True, None
