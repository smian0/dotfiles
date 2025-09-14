"""DeepEval utilities and SOURCE-BASED custom metrics for OpenCode agents"""
import yaml
from pathlib import Path
from typing import List, Dict, Any
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.metrics import FaithfulnessMetric, GEval, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCaseParams
import requests
import json
import logging

# Import our source-based custom metrics  
try:
    from .custom_metrics import SourceAttributionMetric, ContentStructureMetric, NewsCompletenessMetric
except ImportError:
    # Fallback for direct script execution
    from custom_metrics import SourceAttributionMetric, ContentStructureMetric, NewsCompletenessMetric

logger = logging.getLogger(__name__)

class OllamaModel(DeepEvalBaseLLM):
    """Custom DeepEval model using local Ollama - Fixed for reliability"""
    
    def __init__(self, model_id: str = "gemma3:latest", model_url: str = "http://localhost:11434", timeout: int = 60):
        self.model_id = model_id
        self.model_url = model_url.rstrip('/')
        self.timeout = timeout
        
        # Test connection to Ollama
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.model_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"Connected to Ollama at {self.model_url}")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama: {e}")
    
    def load_model(self):
        """Load model (no-op for Ollama)"""
        return self
    
    def generate(self, prompt: str) -> str:
        """Generate response using Ollama - Fixed with better timeout and error handling"""
        try:
            payload = {
                "model": self.model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent evaluation
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.model_url}/api/generate",
                json=payload,
                timeout=self.timeout  # Use configurable timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            # Fallback to a simple response for testing
            return "I cannot provide a detailed evaluation due to connection issues."
    
    async def a_generate(self, prompt: str) -> str:
        """Async generate (uses sync for simplicity)"""
        return self.generate(prompt)
    
    def get_model_name(self) -> str:
        return f"ollama/{self.model_id}"

def get_ollama_model() -> OllamaModel:
    """Get configured Ollama model for DeepEval - Fixed for reliability"""
    return OllamaModel(
        model_id="gemma3:latest",  # Use the available model
        model_url="http://localhost:11434",
        timeout=60  # Reasonable timeout to prevent hanging
    )

def load_agent_metrics(agent_name: str) -> List:
    """Load evaluation metrics for a specific agent"""
    config_path = Path(__file__).parent.parent / "config" / "agent_metrics.yaml"
    
    # Default metrics if config file doesn't exist
    default_metrics = {
        "news": [
            {
                "type": "faithfulness",
                "threshold": 0.7,
                "model": "ollama"
            },
            {
                "type": "custom",
                "name": "NewsRelevancy",
                "criteria": "Evaluate whether the news items are current, relevant, and truly newsworthy. Check if the content discusses recent events and actual news rather than outdated or irrelevant information.",
                "threshold": 0.7,
                "model": "ollama"
            },
            {
                "type": "custom", 
                "name": "BiasDetection",
                "criteria": "Assess whether the news presentation is balanced and avoids obvious political, cultural, or ideological bias. Look for neutral language and fair representation of different viewpoints.",
                "threshold": 0.6,
                "model": "ollama"
            }
        ]
    }
    
    # Load from config if exists
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        metrics_config = config.get(agent_name, default_metrics.get(agent_name, []))
    else:
        metrics_config = default_metrics.get(agent_name, [])
    
    # Convert config to DeepEval metrics
    metrics = []
    ollama_model = get_ollama_model()
    
    for metric_config in metrics_config:
        try:
            model_setting = metric_config.get("model", "")
            use_ollama = "ollama" in model_setting
            
            if metric_config["type"] == "faithfulness":
                metrics.append(FaithfulnessMetric(
                    threshold=metric_config.get("threshold", 0.7),
                    model=ollama_model if use_ollama else None
                ))
            elif metric_config["type"] == "answer_relevancy":
                metrics.append(AnswerRelevancyMetric(
                    threshold=metric_config.get("threshold", 0.75),
                    model=ollama_model if use_ollama else None
                ))
            elif metric_config["type"] == "source_attribution":
                metrics.append(SourceAttributionMetric(
                    threshold=metric_config.get("threshold", 0.7),
                    timeout=metric_config.get("timeout", 15),
                    include_reason=True,
                    async_mode=False
                ))
            elif metric_config["type"] == "content_structure":
                metrics.append(ContentStructureMetric(
                    threshold=metric_config.get("threshold", 0.7),
                    include_reason=True,
                    async_mode=False
                ))
            elif metric_config["type"] == "news_completeness":
                metrics.append(NewsCompletenessMetric(
                    threshold=metric_config.get("threshold", 0.6),
                    include_reason=True,
                    async_mode=False
                ))
            elif metric_config["type"] == "custom":
                metrics.append(GEval(
                    name=metric_config["name"],
                    criteria=metric_config["criteria"],
                    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
                    threshold=metric_config.get("threshold", 0.7),
                    model=ollama_model if use_ollama else None
            ))
            else:
                logger.warning(f"Unknown metric type: {metric_config['type']}")
        except Exception as e:
            logger.error(f"Failed to load metric {metric_config.get('name', 'unknown')}: {e}")
            continue
    
    logger.info(f"Loaded {len(metrics)} metrics for agent '{agent_name}'")
    return metrics

def load_test_scenarios(agent_name: str) -> List[Dict[str, Any]]:
    """Load test scenarios for a specific agent"""
    fixtures_path = Path(__file__).parent.parent / "fixtures" / f"{agent_name}_golden_tests.json"
    
    # Default test scenarios
    default_scenarios = {
        "news": [
            {
                "name": "breaking_news",
                "input": "Get latest breaking news",
                "category": "breaking",
                "expected_topics": ["current events", "recent developments"]
            },
            {
                "name": "tech_news",
                "input": "Latest technology news",
                "category": "technology", 
                "expected_topics": ["tech", "innovation", "companies"]
            },
            {
                "name": "general_news",
                "input": "What's happening in the world today?",
                "category": "general",
                "expected_topics": ["world events", "current affairs"]
            }
        ]
    }
    
    # Load from fixture file if exists
    if fixtures_path.exists():
        import json
        with open(fixtures_path, 'r') as f:
            scenarios = json.load(f)
    else:
        scenarios = default_scenarios.get(agent_name, [])
    
    logger.info(f"Loaded {len(scenarios)} test scenarios for agent '{agent_name}'")
    return scenarios