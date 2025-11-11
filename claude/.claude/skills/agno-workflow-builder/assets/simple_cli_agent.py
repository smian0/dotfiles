#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "ollama",
# ]
#
# [tool.uv.sources]
# agno = { path = "../../libs/agno", editable = true }
# ///

"""
Simple CLI Agent Template

A minimal Agno agent for interactive chat or single-task execution.
~15 lines of actual code for a fully functional AI assistant.

Usage:
  Interactive CLI:  ./simple_cli_agent.py
  Single prompt:    Uncomment the print_response line
"""

from agno.agent import Agent
from agno.models.ollama import Ollama

# Create agent with minimal configuration
agent = Agent(
    model=Ollama(id="glm-4.6:cloud"),
    instructions="""
        You are a helpful AI assistant.
        Provide clear, concise, and accurate responses.
        Be friendly and professional.
    """,
    markdown=True,
    # Automatic retry with exponential backoff (recommended)
    exponential_backoff=True,
    retries=3,
    retry_delay=15,  # With exponential backoff: 15s, 30s, 60s
)

if __name__ == "__main__":
    # Option 1: Interactive CLI (default)
    agent.cli_app(stream=True)

    # Option 2: Single prompt (uncomment to use)
    # agent.print_response("What is the capital of France?", stream=True)
