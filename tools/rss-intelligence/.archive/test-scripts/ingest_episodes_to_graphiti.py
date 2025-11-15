#!/usr/bin/env python3
"""
Ingest prepared RSS episodes into Graphiti knowledge graph.

This script reads episodes from graphiti_episodes_pending.json and ingests them
using the Graphiti MCP tools that Claude Code has access to.

Note: This script outputs instructions for Claude Code to execute, as only
Claude has direct access to the MCP tools.
"""

import json
import sys


def main():
    # Load episodes
    try:
        with open('graphiti_episodes_pending.json') as f:
            episodes = json.load(f)
    except FileNotFoundError:
        print("❌ No episodes file found. Run the workflow first.")
        return 1

    print(f"📊 Found {len(episodes)} episodes to ingest into Graphiti")
    print(f"🎯 Target group: rss-intelligence\n")

    # Print ingestion plan
    print("=" * 80)
    print("INGESTION PLAN")
    print("=" * 80)
    for i, ep in enumerate(episodes, 1):
        print(f"\n{i}. {ep['name']}")
        print(f"   Source type: {ep['source_type']}")
        print(f"   Body length: {len(ep['body'])} chars")

    print("\n" + "=" * 80)
    print(f"Ready to ingest {len(episodes)} episodes")
    print("=" * 80)
    print()
    print("✅ Episodes are prepared and ready")
    print("📝 Claude Code should now call mcp__graphiti__add_memory for each episode")

    return 0


if __name__ == "__main__":
    sys.exit(main())
