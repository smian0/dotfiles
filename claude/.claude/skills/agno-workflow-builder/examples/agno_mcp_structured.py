#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "agno",
#   "ollama",
# ]
#
# [tool.uv.sources]
# agno = { path = "/Users/smian/github-smian0/agno-ck/libs/agno", editable = true }
# ///

"""
Agno with MCP Tools + Structured Output

Demonstrates combining:
- Context7 MCP tools for documentation lookup
- Structured JSON output using Pydantic models
- gpt-oss-120b as the parser model

Run:
   python examples/agno_mcp_structured.py
"""

# Disable Agno telemetry before importing agno modules
import os
os.environ["AGNO_TELEMETRY"] = "false"

import asyncio
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools


class LibraryDocumentation(BaseModel):
    """Simplified structured documentation for a library"""
    library_name: str = Field(..., description="Name of the library")
    summary: str = Field(..., description="One-sentence summary of what this library does")
    key_features: List[str] = Field(..., description="List of 5-7 key features (one line each)")
    use_cases: List[str] = Field(..., description="3-5 common use cases")
    getting_started: str = Field(..., description="Basic getting started code example")


async def async_main():
    """Async entry point for MCP workflow with structured output"""

    print("=== Agno with MCP Tools + Structured Output ===")
    print("MCP Model: glm-4.6:cloud (tool invocation)")
    print("Parser Model: gpt-oss-120b (structured output)")
    print("Testing: Documentation lookup + JSON parsing\n")

    # Initialize Context7 MCP tools
    mcp_tools = MCPTools(
        command="npx -y @upstash/context7-mcp",
        transport="stdio",
    )

    # CRITICAL: Use async context manager
    async with mcp_tools:
        # Initialize tools within the session
        await mcp_tools.initialize()

        print(f"✓ MCP tools initialized")
        print(f"  Available tools: {list(mcp_tools.functions.keys())}\n")

        # Create agent with MCP tools and structured output
        # glm-4.6:cloud handles tool calling, gpt-oss-120b parses to JSON
        agent = Agent(
            name="Documentation Parser",
            model=Ollama(
                id="glm-4.6:cloud",
                options={"num_ctx": 198000}
            ),
            parser_model=Ollama(id="gpt-oss:120b-cloud"),  # Dedicated parser for structured output
            tools=[mcp_tools],
            instructions=[
                "You are a documentation assistant that fetches and structures library documentation.",
                "WORKFLOW:",
                "1. Use resolve-library-id MCP tool to find the library",
                "2. Use get-library-docs MCP tool to fetch documentation",
                "3. Extract and structure the information into the required format",
                "4. ALWAYS include real code examples from the documentation",
                "NEVER answer from training data - always use MCP tools first.",
            ],
            output_schema=LibraryDocumentation,
            markdown=False,  # Disable markdown for JSON output
            exponential_backoff=True,
            retries=3,
            delay_between_retries=15,
        )

        # Test queries
        test_libraries = [
            "FastAPI",
            "Pydantic",
        ]

        print("="*70 + "\n")

        for library in test_libraries:
            query = f"Fetch and structure documentation for {library}"
            print(f"Query: {query}")
            print("-" * 70)

            try:
                # Execute agent with MCP tools
                response = await agent.arun(query)

                # Access structured output
                doc = response.content

                print("\n📚 STRUCTURED OUTPUT (JSON):")
                print("-" * 70)
                print(f"Library: {doc.library_name}")
                print(f"Summary: {doc.summary}\n")

                print("Key Features:")
                for i, feature in enumerate(doc.key_features, 1):
                    print(f"  {i}. {feature}")

                print(f"\nUse Cases:")
                for use_case in doc.use_cases:
                    print(f"  • {use_case}")

                print(f"\nGetting Started:")
                print(f"{doc.getting_started}")

                print("\n" + "="*70 + "\n")

            except Exception as e:
                print(f"Error: {e}\n")
                import traceback
                traceback.print_exc()
                continue

    # MCP session closes automatically when exiting context manager


def main():
    """Synchronous entry point that runs async workflow"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
