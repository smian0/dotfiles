"""
Entity Extractor Agent

Extracts named entities from news articles with high precision using structured outputs.

Recent Changes:
- 2025-11-14: Initial extraction from main workflow for better maintainability
"""

from agno.agent import Agent
from agno.models.ollama import Ollama

# Entity extraction instructions
INSTRUCTIONS = """
Extract named entities from news articles with high precision.

Focus on:
- People (politicians, CEOs, public figures)
- Organizations (companies, governments, NGOs)
- Locations (countries, cities, regions)
- Events (summits, elections, disasters)
- Concepts (policies, technologies, movements)

Return ExtractedData JSON format:
{
    "entities": [
        {"name": "entity name", "entity_type": "type", "context": "context", "confidence": 0.0-1.0}
    ],
    "sentiment": null,
    "topics": []
}

Populate ONLY the entities array. Use field name "entity_type" (not "type").
"""


def create_entity_extractor(output_schema):
    """
    Create Entity Extractor agent.

    This agent extracts named entities from articles using structured outputs
    to ensure consistent data quality.

    Args:
        output_schema: Pydantic model for ExtractedData structure

    Returns:
        Agent: Configured entity extractor agent

    Model Configuration:
        - Model: DeepSeek-V3.1:671b cloud (better reasoning)
        - Context: 159K tokens (99% utilization)
        - Output: 5K tokens (sufficient for entity lists)
        - Format: JSON with structured outputs
    """
    return Agent(
        name="Entity Extractor",
        model=Ollama(
            id="deepseek-v3.1:671b-cloud",
            format="json",
            options={"num_ctx": 159000, "num_predict": 5000}
        ),
        instructions=INSTRUCTIONS,
        output_schema=output_schema,
        use_json_mode=True,
        structured_outputs=True,
    )
