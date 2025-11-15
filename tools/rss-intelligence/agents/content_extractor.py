"""
Content Extractor Agent

Extracts full article content from RSS feed URLs using Newspaper4k tools.

Recent Changes:
- 2025-11-14: Initial extraction from main workflow for better maintainability
"""

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.newspaper4k import Newspaper4kTools

# Content extraction instructions
INSTRUCTIONS = """
Extract full article content from the provided URLs using the get_article_text tool.

You will receive a numbered list of article URLs. For each URL:
1. Call get_article_text(url) to extract the full content
2. Store the extracted content
3. If extraction fails, note the failure but continue with other URLs

Return a JSON object mapping article numbers to their extracted content:
{
    "1": "extracted content here...",
    "2": "extracted content here...",
    ...
}

If a URL fails, use null for that entry.
Be efficient - process articles systematically.
"""


def create_content_extractor():
    """
    Create Content Extractor agent.

    This agent uses Newspaper4k tools to extract full article content
    from RSS feed URLs.

    Returns:
        Agent: Configured content extractor agent

    Model Configuration:
        - Model: GLM-4.6 cloud (198K context, 16K max output)
        - Context: 196K tokens (99% utilization)
        - Output: 15K tokens (safe under 16K max)
        - Tools: Newspaper4kTools for web scraping
    """
    return Agent(
        name="Content Extractor",
        model=Ollama(
            id="glm-4.6:cloud",
            options={"num_ctx": 196000, "num_predict": 15000}
        ),
        tools=[Newspaper4kTools()],
        instructions=INSTRUCTIONS,
        markdown=True,
    )
