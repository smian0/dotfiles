"""
Code Analyzer Agent
===================

Specialized agent for analyzing code quality, finding bugs, and suggesting improvements.
Optimized for thorough code review and actionable feedback.
"""

from agno.agent import Agent
from agno.models.anthropic import Claude

from .base import BaseAgent, AgentConfig


class CodeAnalyzerAgent(BaseAgent):
    """
    Agent specialized in code quality analysis and review.

    Capabilities:
    - Finding bugs and potential errors
    - Identifying security vulnerabilities
    - Suggesting performance improvements
    - Detecting code smells and anti-patterns
    - Rating code quality

    Best for:
    - Code reviews
    - Bug detection
    - Security analysis
    - Performance optimization suggestions
    - Code quality assessment
    """

    def _default_config(self) -> AgentConfig:
        return AgentConfig(
            name="CodeAnalyzerAgent",
            model_id="claude-sonnet-4",
            instructions="""You are a senior code reviewer specialized in finding bugs, security issues, and suggesting improvements.

Your responsibilities:
1. Analyze code for bugs and potential errors
2. Identify security vulnerabilities
3. Suggest performance improvements
4. Detect code smells and anti-patterns
5. Rate overall code quality (1-10)

Analysis structure:
## Critical Issues (🔴)
- Bug/security issue with HIGH impact
- Include: what, why, impact, fix

## Moderate Issues (🟡)
- Code smells, non-optimal patterns
- Include: what, why, better approach

## Minor Issues (🟢)
- Style, readability, minor improvements

## Code Quality Rating: X/10
- Brief justification

Example output:
```
## Critical Issues (🔴)

1. Division by Zero Risk
   - Line 5: `return total / len(numbers)`
   - Impact: Crashes on empty list
   - Fix: Add validation: `if not numbers: raise ValueError()`

## Code Quality Rating: 6/10
- Logic correct but lacks error handling
```

Be specific:
- Cite line numbers when possible
- Provide concrete examples
- Suggest actual code fixes
- Prioritize by severity""",
            temperature=0.5,  # Moderate temperature for balanced analysis
            max_tokens=4000,  # Longer responses for detailed analysis
            markdown=True     # Enable markdown for formatting
        )

    def _create_agent(self) -> Agent:
        return Agent(
            model=Claude(id=self.config.model_id),
            instructions=self.config.instructions,
            markdown=self.config.markdown
        )

    def validate_input(self, prompt: str) -> tuple[bool, str | None]:
        """Code analyzer-specific validation"""
        is_valid, error = super().validate_input(prompt)
        if not is_valid:
            return is_valid, error

        # Should contain code-related content
        code_indicators = ['def ', 'class ', 'function', '{', '}', 'import',
                          'const ', 'let ', 'var ', 'public ', 'private']

        has_code = any(indicator in prompt for indicator in code_indicators)

        if not has_code:
            return False, "Input should contain code to analyze"

        return True, None
