#!/usr/bin/env python3
"""
Single-run test for RSS intelligence workflow.
Tests all components without the infinite loop.
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "agno",
#     "feedparser",
#     "fastapi",
#     "newspaper4k",
#     "lxml_html_clean",
#     "ollama",
#     "mcp",
#     "sqlalchemy",
# ]
# ///

import asyncio
from rss_intelligence_workflow import create_rss_workflow

async def test_single_run():
    """Run workflow once for testing"""
    workflow = create_rss_workflow()

    print("🧪 Testing RSS Intelligence Workflow (Single Run)\n")

    result = await workflow.arun(
        input="Process all RSS feeds",
        session_state={"processed_urls": []},  # Empty list for JSON serializability
    )

    print("\n✅ Test complete!")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_single_run())
