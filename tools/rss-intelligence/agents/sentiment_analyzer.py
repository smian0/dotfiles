"""
Sentiment Analyzer Agent

Analyzes sentiment and emotional tone of news articles using structured outputs.

Recent Changes:
- 2025-11-14: Initial extraction from main workflow for better maintainability
"""

from agno.agent import Agent
from agno.models.ollama import Ollama

# Sentiment analysis instructions
INSTRUCTIONS = """
Analyze sentiment and emotional tone of news articles.

Classify as:
- Positive: optimistic, hopeful, celebratory
- Negative: pessimistic, critical, concerning
- Neutral: factual, balanced, informational

Also identify key emotions: anger, fear, joy, sadness, surprise, trust.

Return ExtractedData JSON format:
{
    "entities": [],
    "sentiment": {
        "overall_sentiment": "positive/negative/neutral",
        "confidence": 0.0-1.0,
        "key_emotions": ["emotion1", "emotion2"]
    },
    "topics": []
}

Populate ONLY the sentiment object.
"""


def create_sentiment_analyzer(output_schema):
    """
    Create Sentiment Analyzer agent.

    This agent analyzes sentiment and emotional tone of articles using
    structured outputs for consistent data quality.

    Args:
        output_schema: Pydantic model for ExtractedData structure

    Returns:
        Agent: Configured sentiment analyzer agent

    Model Configuration:
        - Model: GLM-4.6 cloud (198K context)
        - Context: 196K tokens (99% utilization)
        - Output: 2K tokens (sufficient for sentiment data)
        - Format: JSON with structured outputs
    """
    return Agent(
        name="Sentiment Analyzer",
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
