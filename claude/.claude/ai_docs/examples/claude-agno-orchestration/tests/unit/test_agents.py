"""
Unit Tests for Agents
======================

Tests for individual agent functionality in isolation.
"""

import pytest
from unittest.mock import Mock, patch

from orchestration.agents import (
    BaseAgent,
    AgentConfig,
    ResearchAgent,
    CalculatorAgent,
    CodeAnalyzerAgent
)


class TestAgentConfig:
    """Test AgentConfig dataclass"""

    def test_default_values(self):
        config = AgentConfig(name="Test")
        assert config.name == "Test"
        assert config.model_id == "claude-sonnet-4"
        assert config.temperature == 0.3
        assert config.max_tokens == 2000
        assert config.additional_params == {}

    def test_custom_values(self):
        config = AgentConfig(
            name="CustomAgent",
            model_id="gpt-4",
            temperature=0.7,
            max_tokens=4000
        )
        assert config.model_id == "gpt-4"
        assert config.temperature == 0.7


class TestResearchAgent:
    """Test ResearchAgent functionality"""

    def test_default_config(self):
        agent = ResearchAgent()
        assert agent.config.name == "ResearchAgent"
        assert agent.config.temperature == 0.3  # Low temp for factual accuracy

    def test_validate_input_empty(self):
        agent = ResearchAgent()
        is_valid, error = agent.validate_input("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_validate_input_too_short(self):
        agent = ResearchAgent()
        is_valid, error = agent.validate_input("Hi")
        assert not is_valid
        assert "10 characters" in error

    def test_validate_input_valid(self):
        agent = ResearchAgent()
        is_valid, error = agent.validate_input("What is Python?")
        assert is_valid
        assert error is None

    @patch('orchestration.agents.research.Agent')
    def test_run_success_mock(self, mock_agent_class):
        # Mock the Agno Agent
        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.content = "Python is a programming language"
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        # Test
        agent = ResearchAgent()
        result = agent.run("What is Python?")

        assert result.success
        assert "Python" in result.content
        assert result.duration >= 0
        assert result.metadata['agent_name'] == "ResearchAgent"


class TestCalculatorAgent:
    """Test CalculatorAgent functionality"""

    def test_default_config(self):
        agent = CalculatorAgent()
        assert agent.config.name == "CalculatorAgent"
        assert agent.config.temperature == 0.0  # Zero for deterministic math
        assert agent.config.max_tokens == 500  # Short responses

    def test_validate_input_no_numbers_or_math(self):
        agent = CalculatorAgent()
        is_valid, error = agent.validate_input("Hello world")
        assert not is_valid
        assert "mathematical" in error.lower()

    def test_validate_input_has_numbers(self):
        agent = CalculatorAgent()
        is_valid, error = agent.validate_input("Calculate 123 + 456")
        assert is_valid
        assert error is None

    def test_validate_input_has_math_term(self):
        agent = CalculatorAgent()
        is_valid, error = agent.validate_input("What is the average of these values")
        assert is_valid
        assert error is None

    @patch('orchestration.agents.calculator.Agent')
    def test_run_success_mock(self, mock_agent_class):
        # Mock
        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.content = "238.25"
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        # Test
        agent = CalculatorAgent()
        result = agent.run("Calculate 39000000 / 163696")

        assert result.success
        assert result.content == "238.25"


class TestCodeAnalyzerAgent:
    """Test CodeAnalyzerAgent functionality"""

    def test_default_config(self):
        agent = CodeAnalyzerAgent()
        assert agent.config.name == "CodeAnalyzerAgent"
        assert agent.config.markdown is True  # Markdown enabled for formatting

    def test_validate_input_no_code(self):
        agent = CodeAnalyzerAgent()
        is_valid, error = agent.validate_input("Just some text")
        assert not is_valid
        assert "code" in error.lower()

    def test_validate_input_has_code(self):
        agent = CodeAnalyzerAgent()
        code = "def hello():\n    print('hello')"
        is_valid, error = agent.validate_input(code)
        assert is_valid
        assert error is None

    @patch('orchestration.agents.code_analyzer.Agent')
    def test_run_success_mock(self, mock_agent_class):
        # Mock
        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.content = "## Code Quality: 8/10\n\nNo critical issues found."
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        # Test
        agent = CodeAnalyzerAgent()
        code = "def test():\n    return True"
        result = agent.run(f"Analyze this code:\n{code}")

        assert result.success
        assert "8/10" in result.content


class TestAgentMetrics:
    """Test agent metrics and statistics"""

    @patch('orchestration.agents.research.Agent')
    def test_execution_count(self, mock_agent_class):
        # Mock
        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.content = "Result"
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        # Test
        agent = ResearchAgent()
        assert agent.stats['execution_count'] == 0

        agent.run("What is AI research?")
        assert agent.stats['execution_count'] == 1

        agent.run("What is machine learning?")
        assert agent.stats['execution_count'] == 2

    @patch('orchestration.agents.research.Agent')
    def test_average_duration(self, mock_agent_class):
        # Mock
        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.content = "Result"
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        # Test
        agent = ResearchAgent()
        agent.run("What is AI research?")
        agent.run("What is machine learning?")

        assert agent.average_duration > 0
        assert agent.stats['total_duration'] > 0

    @patch('orchestration.agents.research.Agent')
    def test_reset_stats(self, mock_agent_class):
        # Mock
        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.content = "Result"
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        # Test
        agent = ResearchAgent()
        agent.run("What is AI research?")
        assert agent.stats['execution_count'] == 1

        agent.reset_stats()
        assert agent.stats['execution_count'] == 0
        assert agent.stats['total_duration'] == 0.0
