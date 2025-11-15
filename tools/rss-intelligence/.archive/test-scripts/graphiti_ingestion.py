#!/usr/bin/env python3
"""
Graphiti Knowledge Graph Ingestion Script

This script ingests prepared episodes into Graphiti's knowledge graph.
It's designed to be called after the RSS intelligence workflow has
prepared episode data.

Note: This script is meant to be run by Claude Code which has access
to the Graphiti MCP tools. It cannot be run directly from the Agno
workflow because MCP tools are only available to the AI assistant,
not to Python code.
"""

import json
import sys
from pathlib import Path


def load_episodes_from_session(session_db_path: str = "rss_intelligence.db") -> list[dict]:
    """
    Load prepared episodes from the workflow session state.

    Args:
        session_db_path: Path to the SQLite database with session data

    Returns:
        List of episode dictionaries with name, body, source_type
    """
    import sqlite3

    conn = sqlite3.connect(session_db_path)
    cursor = conn.cursor()

    try:
        # Get the most recent session
        cursor.execute("""
            SELECT session_state
            FROM rss_intelligence_sessions
            ORDER BY created_at DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        if not row:
            print("❌ No session data found")
            return []

        session_state = json.loads(row[0])
        episodes = session_state.get("graphiti_episodes", [])

        print(f"📊 Found {len(episodes)} episodes in session state")
        return episodes

    finally:
        conn.close()


def print_episodes_for_claude(episodes: list[dict]) -> None:
    """
    Print episodes in a format that Claude Code can use to call
    the Graphiti MCP add_memory tool.

    This outputs instructions for Claude to execute the MCP tool calls.
    """
    print("\n" + "=" * 80)
    print("GRAPHITI INGESTION INSTRUCTIONS FOR CLAUDE CODE")
    print("=" * 80)
    print()
    print(f"Please use the mcp__graphiti__add_memory tool to add these {len(episodes)} episodes:")
    print()

    for i, episode in enumerate(episodes, 1):
        print(f"Episode {i}:")
        print(f"  Name: {episode['name']}")
        print(f"  Source: json")
        print(f"  Group ID: rss-intelligence")
        print()
        print(f"  Body:")
        print("  " + "-" * 76)
        body_preview = episode['body'][:500]
        print(f"  {body_preview}...")
        print("  " + "-" * 76)
        print()

    print("=" * 80)
    print(f"Total: {len(episodes)} episodes to ingest")
    print("=" * 80)
    print()
    print("NOTE: Claude Code should call mcp__graphiti__add_memory for each episode.")
    print()


def main():
    """Main entry point for Graphiti ingestion."""
    print("🔍 Graphiti Knowledge Graph Ingestion")
    print()

    # Load episodes from session database
    episodes = load_episodes_from_session()

    if not episodes:
        print("⚠️  No episodes found to ingest")
        return 1

    # Print instructions for Claude to execute
    print_episodes_for_claude(episodes)

    return 0


if __name__ == "__main__":
    sys.exit(main())
