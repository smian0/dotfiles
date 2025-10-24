#!/usr/bin/env python3
"""
Custom Tool Workflow Template

A workflow that integrates custom tools via MCP servers,
similar to Agno's tool integration but using Claude Agent SDK patterns.

Pattern: Input → Agent with Custom Tools → Output

Usage:
    python custom_tool_workflow.py
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Any, Dict

# Add helpers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "helpers"))

from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeSDKClient,
    ClaudeAgentOptions
)
from workflow_helpers import (
    run_agent_task,
    print_message,
    get_user_input
)
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()


# ==================================================================
# Define Custom Tools
# ==================================================================

@tool("analyze_sentiment", "Analyze the sentiment of text (positive, negative, neutral)", {"text": str})
async def analyze_sentiment(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Custom tool: Analyze sentiment of text.

    Equivalent Agno pattern:
        @tool()
        def analyze_sentiment(text: str) -> str:
            ...
    """
    text = args['text'].lower()

    # Simple keyword-based sentiment analysis
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'horrible']

    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)

    if positive_count > negative_count:
        sentiment = "positive"
        confidence = min(positive_count / (positive_count + negative_count + 1), 0.95)
    elif negative_count > positive_count:
        sentiment = "negative"
        confidence = min(negative_count / (positive_count + negative_count + 1), 0.95)
    else:
        sentiment = "neutral"
        confidence = 0.5

    result = {
        "sentiment": sentiment,
        "confidence": f"{confidence:.2f}",
        "positive_indicators": positive_count,
        "negative_indicators": negative_count
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool("extract_keywords", "Extract key topics and keywords from text", {"text": str, "max_keywords": int})
async def extract_keywords(args: Dict[str, Any]) -> Dict[str, Any]:
    """Custom tool: Extract keywords from text."""
    text = args['text'].lower()
    max_keywords = args.get('max_keywords', 5)

    # Simple keyword extraction (split and count)
    words = text.split()
    # Filter out common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = [w for w in words if w not in stop_words and len(w) > 3]

    # Count frequency
    from collections import Counter
    word_counts = Counter(keywords)
    top_keywords = word_counts.most_common(max_keywords)

    result = {
        "keywords": [{"word": word, "count": count} for word, count in top_keywords],
        "total_words": len(words),
        "unique_keywords": len(set(keywords))
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool("summarize_stats", "Calculate basic statistics for a list of numbers", {"numbers": list})
async def summarize_stats(args: Dict[str, Any]) -> Dict[str, Any]:
    """Custom tool: Calculate statistics."""
    numbers = args['numbers']

    if not numbers:
        return {
            "content": [{
                "type": "text",
                "text": "No numbers provided"
            }]
        }

    result = {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "range": max(numbers) - min(numbers)
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


# ==================================================================
# Create MCP Server with Custom Tools
# ==================================================================

analysis_server = create_sdk_mcp_server(
    name="analysis",
    version="1.0.0",
    tools=[analyze_sentiment, extract_keywords, summarize_stats]
)


async def main():
    """
    Custom tool workflow example.

    Shows how to integrate custom tools into workflows,
    similar to Agno's tool integration pattern.
    """
    console = Console()

    # ==================================================================
    # Configuration with Custom Tools
    # ==================================================================

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        permission_mode="acceptEdits",
        setting_sources=["project"],
        # Add custom MCP server
        mcp_servers={"analysis": analysis_server},
        allowed_tools=[
            'Read', 'Write', 'Edit',
            # Enable custom tools (naming convention: mcp__<server>__<tool>)
            'mcp__analysis__analyze_sentiment',
            'mcp__analysis__extract_keywords',
            'mcp__analysis__summarize_stats',
            'TodoWrite'
        ]
    )

    console.print("[bold green]Custom Tool Workflow[/bold green]")
    console.print("This workflow demonstrates custom tool integration.\n")

    # ==================================================================
    # Execute Workflow with Custom Tools
    # ==================================================================

    async with ClaudeSDKClient(options=options) as client:

        # Example 1: Sentiment Analysis
        console.print("[bold cyan]Example 1: Sentiment Analysis[/bold cyan]")
        sentiment_prompt = """Use the analyze_sentiment tool to analyze the sentiment of this text:
"This product is absolutely fantastic! I love everything about it. Best purchase ever!"

Then explain what the sentiment is and why."""

        result1 = await run_agent_task(client, sentiment_prompt, show_tools=True, console=console)
        print_message("assistant", result1, console)

        # Example 2: Keyword Extraction
        console.print("\n[bold cyan]Example 2: Keyword Extraction[/bold cyan]")
        keyword_prompt = """Use the extract_keywords tool to extract keywords from this text:
"Machine learning and artificial intelligence are transforming technology.
Deep learning models enable computers to recognize patterns in data."

Extract the top 5 keywords and explain what topics this text covers."""

        result2 = await run_agent_task(client, keyword_prompt, show_tools=True, console=console)
        print_message("assistant", result2, console)

        # Example 3: Statistics
        console.print("\n[bold cyan]Example 3: Statistical Analysis[/bold cyan]")
        stats_prompt = """Use the summarize_stats tool to analyze these numbers:
[45, 67, 23, 89, 12, 56, 78, 34, 90, 45]

Provide insights about the data distribution."""

        result3 = await run_agent_task(client, stats_prompt, show_tools=True, console=console)
        print_message("assistant", result3, console)

        # Combined Analysis
        console.print("\n[bold cyan]Combined Analysis[/bold cyan]")
        combined_prompt = """Now use multiple custom tools together:
1. Extract keywords from: "Data science requires strong analytical skills"
2. Analyze sentiment of: "The data analysis results are disappointing"
3. Calculate stats for: [10, 20, 30, 40, 50]

Provide a comprehensive analysis combining all three tool results."""

        result4 = await run_agent_task(client, combined_prompt, show_tools=True, console=console)
        print_message("assistant", result4, console)

    console.print("\n[bold green]✓ Custom Tool Workflow Complete![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
