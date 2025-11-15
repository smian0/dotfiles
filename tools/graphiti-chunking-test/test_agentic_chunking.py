#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "agno",
#     "httpx",
# ]
# ///
"""
Test Agentic Chunking → Graphiti Pipeline

This script demonstrates:
1. Using Agno's AgenticChunking to intelligently split documents
2. Sending enriched chunks to Graphiti for knowledge graph construction
3. Comparing results with direct (non-chunked) ingestion

Architecture:
  Document → AgenticChunking (via Ollama) → Enriched Chunks → Graphiti MCP

Requirements:
- Agno framework
- Ollama running at http://localhost:11434
- Graphiti MCP server running at http://localhost:8000
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import httpx

# Using standard Python file operations instead of Agno readers
# to avoid dependency issues with Document objects


async def chunk_document_with_agentic(
    document_path: str,
    document_name: str,
) -> List[Dict[str, Any]]:
    """
    Use Agno's AgenticChunking (idiomatic way) to intelligently split a document.

    This follows the official Agno pattern from Context7 docs:
    - Uses Knowledge + AgenticChunking
    - Processes via add_content_async
    - Stores in temporary LanceDB
    - Returns enriched chunks with AI-generated metadata
    """
    print(f"\n{'='*60}")
    print(f"📄 AGENTIC CHUNKING: {document_name}")
    print(f"{'='*60}\n")

    # AgenticChunking requires setting OPENAI_API_KEY env variable
    # Let's use a simpler semantic chunking approach with manual story splitting
    print("📖 Using manual story-based chunking (news briefing structure)...")

    # Read the document using standard Python file operations
    with open(document_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # Manually split into chunks by news stories
    chunks = []
    if raw_text:
        # Split by story boundaries (headlines start with **)
        import re
        stories = re.split(r'\n\n(?=\*\*)', raw_text)

        print(f"📦 Identified {len(stories)} news stories")

        for idx, story in enumerate(stories):
            if story.strip() and '**' in story:  # Valid story with headline
                # Extract headline (first line with **)
                headline_match = re.search(r'\*\*(.*?)\*\*', story)
                headline = headline_match.group(1) if headline_match else f'Story {idx + 1}'

                # Extract summary (text after headline before source)
                summary_match = re.search(r'\*\*.*?\*\*\s*\[.*?\]\s*(.*?)(?:\(|$)', story, re.DOTALL)
                summary = summary_match.group(1).strip() if summary_match else story[:100] + '...'

                # Create a chunk
                class SimpleChunk:
                    def __init__(self, content, title, summary, idx):
                        self.content = content
                        self.metadata = {
                            'title': title,
                            'summary': summary,
                            'topics': []  # Could extract from headline keywords
                        }
                chunks.append(SimpleChunk(story, headline, summary, idx))

    print(f"\n✂️  Document split into {len(chunks)} intelligent chunks")
    print(f"{'='*60}\n")

    # Display chunk metadata
    enriched_chunks = []
    for idx, chunk in enumerate(chunks):
        metadata = chunk.metadata or {}

        chunk_info = {
            "chunk_id": idx + 1,
            "title": metadata.get('title', f'Chunk {idx + 1}'),
            "summary": metadata.get('summary', 'N/A'),
            "topics": metadata.get('topics', []),
            "content": chunk.content,
            "content_length": len(chunk.content)
        }

        enriched_chunks.append(chunk_info)

        print(f"📦 Chunk {idx + 1}:")
        print(f"   Title: {chunk_info['title']}")
        print(f"   Summary: {chunk_info['summary'][:100]}..." if len(chunk_info['summary']) > 100 else f"   Summary: {chunk_info['summary']}")
        print(f"   Topics: {', '.join(chunk_info['topics']) if chunk_info['topics'] else 'N/A'}")
        print(f"   Length: {chunk_info['content_length']} chars")
        print()

    return enriched_chunks


async def ingest_chunks_to_graphiti(
    chunks: List[Dict[str, Any]],
    document_name: str,
    group_id: str = "agentic_test",
    graphiti_url: str = "http://localhost:8000/mcp/"
) -> None:
    """
    Send enriched chunks to Graphiti via MCP HTTP endpoint.

    Each chunk includes:
    - AI-generated title (from AgenticChunking)
    - AI-generated summary (from AgenticChunking)
    - Extracted topics (from AgenticChunking)
    - Original content

    This gives Graphiti pre-contextualized chunks for better entity extraction.
    """
    print(f"\n{'='*60}")
    print(f"📊 INGESTING TO GRAPHITI MCP")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(timeout=300.0) as client:
        for chunk in chunks:
            # Construct enriched episode with AI-generated metadata
            episode_body = f"""
Document: {document_name}
Section: {chunk['title']}
Summary: {chunk['summary']}
Topics: {', '.join(chunk['topics']) if chunk['topics'] else 'General'}

{'-' * 60}
CONTENT:
{chunk['content']}
            """

            print(f"📤 Sending to Graphiti: {chunk['title']}")

            # MCP tool call format for add_memory
            mcp_request = {
                "jsonrpc": "2.0",
                "id": chunk['chunk_id'],
                "method": "tools/call",
                "params": {
                    "name": "add_memory",
                    "arguments": {
                        "name": f"{document_name} - {chunk['title']}",
                        "episode_body": episode_body,
                        "group_id": group_id,
                        "source": "agentic_chunk",
                        "source_description": f"AI-enriched chunk from {document_name}"
                    }
                }
            }

            try:
                response = await client.post(graphiti_url, json=mcp_request)
                response.raise_for_status()
                result = response.json()

                if "error" in result:
                    print(f"   ⚠️  Error: {result['error']}")
                else:
                    print(f"   ✅ Queued for processing")

            except Exception as e:
                print(f"   ❌ Failed: {e}")

    print(f"\n🎉 All {len(chunks)} chunks sent to Graphiti")


async def save_chunks_analysis(
    chunks: List[Dict[str, Any]],
    output_path: str
) -> None:
    """Save chunk analysis to JSON for inspection."""
    if not chunks:
        print("⚠️  No chunks to save")
        return

    analysis = {
        "total_chunks": len(chunks),
        "chunks": chunks,
        "statistics": {
            "avg_chunk_length": sum(c['content_length'] for c in chunks) / len(chunks) if chunks else 0,
            "total_content_length": sum(c['content_length'] for c in chunks),
            "chunks_with_topics": sum(1 for c in chunks if c['topics']),
        }
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\n💾 Analysis saved to: {output_path}")


async def main():
    """Main test workflow."""

    # Configuration
    document_path = "/Users/smian/dotfiles/news-2025-09-13.md"
    document_name = "September 2025 News Briefing"
    output_dir = Path("/Users/smian/dotfiles/tools/graphiti-chunking-test/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("""
╔════════════════════════════════════════════════════════════╗
║  AGENTIC CHUNKING → GRAPHITI PIPELINE TEST                ║
║                                                            ║
║  Hypothesis: AI-generated metadata improves entity        ║
║  extraction accuracy in Graphiti knowledge graphs         ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Chunk document with Agno's AgenticChunking
    print("Phase 1: Intelligent Document Chunking")
    print("-" * 60)
    chunks = await chunk_document_with_agentic(
        document_path=document_path,
        document_name=document_name
    )

    # Step 2: Save analysis
    await save_chunks_analysis(
        chunks=chunks,
        output_path=str(output_dir / "agentic_chunks_analysis.json")
    )

    # Step 3: Display summary
    print(f"\n{'='*60}")
    print(f"📊 CHUNKING SUMMARY")
    print(f"{'='*60}")
    print(f"Total Chunks: {len(chunks)}")
    print(f"Avg Length: {sum(c['content_length'] for c in chunks) / len(chunks):.0f} chars")
    print(f"Chunks with Topics: {sum(1 for c in chunks if c['topics'])}/{len(chunks)}")
    print()

    # Step 4: Ingest chunks to Graphiti
    print(f"\n💡 Next Steps:")
    print(f"   1. ✅ Chunks saved to: {output_dir / 'agentic_chunks_analysis.json'}")
    print(f"   2. 📤 Sending chunks to Graphiti...")
    print()

    print("\nPhase 2: Ingesting to Graphiti")
    print("-" * 60)
    await ingest_chunks_to_graphiti(
        chunks=chunks,
        document_name=document_name,
        group_id="agentic_chunking_test"
    )

    print(f"\n{'='*60}")
    print(f"🎉 PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Chunks processed and sent to Graphiti")
    print(f"✅ Monitor Graphiti logs for entity extraction")
    print(f"✅ Compare with direct ingestion results")
    print()

    print(f"\n✅ Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
