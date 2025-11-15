"""
Topic Extractor Agent

Classifies news articles into relevant topics with relevance scores using structured outputs.

Recent Changes:
- 2025-11-14: Initial extraction from main workflow for better maintainability
"""

from agno.agent import Agent
from agno.models.ollama import Ollama

# Topic classification instructions
INSTRUCTIONS = """
Classify news articles into relevant topics with relevance scores.

Common topics:
- Politics & Government
- Business & Economics
- Technology & Science
- Health & Medicine
- Environment & Climate
- Social Issues
- International Relations
- Security & Defense

Return ExtractedData JSON format:
{
    "entities": [],
    "sentiment": null,
    "topics": [
        {"topic": "topic name", "relevance": 0.0-1.0}
    ]
}

Populate ONLY the topics array. Use field name "relevance" (not "relevance_score").
"""


def create_topic_extractor(output_schema):
    """
    Create Topic Extractor agent.

    This agent classifies articles into topics with relevance scores using
    structured outputs for consistent data quality.

    Args:
        output_schema: Pydantic model for ExtractedData structure

    Returns:
        Agent: Configured topic extractor agent

    Model Configuration:
        - Model: GLM-4.6 cloud (198K context)
        - Context: 196K tokens (99% utilization)
        - Output: 2K tokens (sufficient for topic lists)
        - Format: JSON with structured outputs
    """
    return Agent(
        name="Topic Extractor",
        model=Ollama(
            id="glm-4.6:cloud",
            format="json",
            options={"num_ctx": 196000, "num_predict": 2000}
        ),
        instructions=INSTRUCTIONS,
        output_schema=output_schema,
        use_json_mode=True,
        structured_outputs=True,
    )
