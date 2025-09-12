"""PyTest fixtures for OpenCode agent testing"""
import pytest
import logging
import sys
from pathlib import Path

# Add the utils directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from opencode_client import OpenCodeClient
from deepeval_helpers import load_agent_metrics, load_test_scenarios, get_ollama_model

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def opencode_client():
    """Session-wide OpenCode client for agent invocation"""
    try:
        client = OpenCodeClient()
        logger.info("OpenCode client initialized successfully")
        return client
    except Exception as e:
        pytest.skip(f"Could not initialize OpenCode client: {e}")

@pytest.fixture
def news_agent(opencode_client):
    """News agent testing interface"""
    return opencode_client.get_agent("news")

@pytest.fixture
def websearch_agent(opencode_client):
    """WebSearch agent testing interface"""
    return opencode_client.get_agent("websearch")

@pytest.fixture
def reasoning_agent(opencode_client):
    """Reasoning agent testing interface"""
    return opencode_client.get_agent("reasoning")

@pytest.fixture
def news_metrics():
    """Load news agent evaluation metrics"""
    try:
        return load_agent_metrics("news")
    except Exception as e:
        logger.warning(f"Could not load news metrics: {e}")
        # Fallback to basic metrics
        from deepeval.metrics import AnswerRelevancyMetric
        return [AnswerRelevancyMetric(threshold=0.7, model=get_ollama_model())]

@pytest.fixture
def websearch_metrics():
    """Load websearch agent evaluation metrics"""
    try:
        return load_agent_metrics("websearch")
    except Exception as e:
        logger.warning(f"Could not load websearch metrics: {e}")
        from deepeval.metrics import AnswerRelevancyMetric
        return [AnswerRelevancyMetric(threshold=0.7, model=get_ollama_model())]

@pytest.fixture
def news_test_scenarios():
    """Load news agent test scenarios"""
    return load_test_scenarios("news")

@pytest.fixture
def ollama_model():
    """Get configured Ollama model for testing"""
    return get_ollama_model()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment"""
    logger.info("Setting up OpenCode agent test environment")
    
    # Create results directory if it doesn't exist
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Test Ollama connection
    try:
        ollama = get_ollama_model()
        ollama._test_connection()
        logger.info("Ollama connection verified")
    except Exception as e:
        logger.warning(f"Ollama connection issue: {e}")
    
    yield
    
    logger.info("Test environment cleanup complete")

# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "comprehensive: marks tests as comprehensive evaluations"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Mark slow tests
        if "comprehensive" in item.name or "slow" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.name or item.name.startswith("test_"):
            item.add_marker(pytest.mark.integration)