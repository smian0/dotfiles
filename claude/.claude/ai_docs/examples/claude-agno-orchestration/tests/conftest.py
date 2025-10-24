"""
PyTest Configuration and Fixtures
==================================

Shared test fixtures and configuration for the test suite.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestration.agents import AgentConfig, AgentResult


@pytest.fixture
def sample_agent_config():
    """Provide a sample agent configuration"""
    return AgentConfig(
        name="TestAgent",
        model_id="claude-sonnet-4",
        instructions="You are a test agent.",
        temperature=0.3,
        max_tokens=1000
    )


@pytest.fixture
def sample_agent_result():
    """Provide a sample successful agent result"""
    return AgentResult(
        success=True,
        content="Test response content",
        duration=1.5,
        metadata={'agent_name': 'TestAgent'}
    )


@pytest.fixture
def sample_failed_result():
    """Provide a sample failed agent result"""
    return AgentResult(
        success=False,
        content="",
        duration=0.5,
        error="Test error message",
        metadata={'agent_name': 'TestAgent'}
    )
