#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Ingest Agentic Chunks to Graphiti

This script reads the chunked analysis JSON and uses Claude Code's
Graphiti MCP tool to ingest each chunk as a separate episode.

Usage:
    python3 ingest_chunks_to_graphiti.py

Note: This script is designed to be run from Claude Code which has
access to the Graphiti MCP tool (mcp__graphiti__add_memory).
"""

import json
from pathlib import Path

def load_chunks(analysis_path: str) -> list:
    """Load chunks from analysis JSON file."""
    with open(analysis_path, 'r') as f:
        data = json.load(f)
    return data['chunks']

def main():
    """Load chunks and display instructions for Claude Code."""
    analysis_path = Path("/Users/smian/dotfiles/tools/graphiti-chunking-test/output/agentic_chunks_analysis.json")

    if not analysis_path.exists():
        print(f"❌ Analysis file not found: {analysis_path}")
        print("Run test_agentic_chunking.py first to generate chunks.")
        return

    chunks = load_chunks(str(analysis_path))

    print(f"\n{'='*60}")
    print(f"📊 LOADED {len(chunks)} CHUNKS FOR INGESTION")
    print(f"{'='*60}\n")

    print("Instructions for Claude Code:")
    print("-" * 60)
    print("Use the mcp__graphiti__add_memory tool for each chunk:")
    print()
    print("For each chunk in the analysis JSON:")
    print("1. name: 'September 2025 News Briefing - [chunk title]'")
    print("2. episode_body: Document metadata + chunk content")
    print("3. group_id: 'agentic_chunking_test'")
    print("4. source: 'agentic_chunk'")
    print("5. source_description: 'AI-enriched chunk from September 2025 News Briefing'")
    print()
    print("Example episode_body format:")
    print("""
Document: September 2025 News Briefing
Section: [chunk title]
Summary: [chunk summary]
Topics: [chunk topics or 'General']

------------------------------------------------------------
CONTENT:
[chunk content]
""")

    print(f"\n📦 First chunk preview:")
    print(f"   Title: {chunks[0]['title']}")
    print(f"   Summary: {chunks[0]['summary'][:80]}...")
    print(f"   Length: {chunks[0]['content_length']} chars")

if __name__ == "__main__":
    main()
