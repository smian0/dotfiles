#!/usr/bin/env python3
"""
Export Full Graphiti Knowledge Graph via MCP Server

Since direct FalkorDB access requires knowing the internal graph name,
this script uses the Graphiti MCP server to export all data.
"""

import asyncio
import json
import networkx as nx
from pyvis.network import Network
from agno.tools.mcp import MCPTools
from agno.agent import Agent
from agno.models.ollama import Ollama
from datetime import datetime
import os


async def get_all_episodes():
    """Get all episodes from Graphiti"""
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=120,
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()

        agent = Agent(
            name="Episode Getter",
            model=Ollama(id="glm-4.6:cloud"),
            tools=[graphiti_mcp],
            instructions="Call get_episodes with group_ids=['rss-intelligence'] and max_episodes=1000 to retrieve all episodes. Return raw JSON.",
            markdown=False,
        )

        result = await agent.arun(
            "get_episodes(group_ids=['rss-intelligence'], max_episodes=1000)"
        )

        # Parse response
        try:
            data = json.loads(result.content)
            return data.get('episodes', [])
        except:
            print("⚠️ Could not parse episodes response")
            print(result.content[:500])
            return []


async def search_all_entities(query="", max_nodes=1000):
    """Search for entities - empty query to get all"""
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=120,
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()

        agent = Agent(
            name="Entity Searcher",
            model=Ollama(id="glm-4.6:cloud"),
            tools=[graphiti_mcp],
            instructions="Execute search_nodes and return raw JSON with all results.",
            markdown=False,
        )

        # Try broad search terms to get all entities
        all_entities = []

        # Search for common terms that should match most entities
        search_terms = ["", "a", "e", "i", "o", "u"]  # Common letters

        for term in search_terms:
            result = await agent.arun(
                f"search_nodes(query='{term}', group_ids=['rss-intelligence'], max_nodes={max_nodes})"
            )

            try:
                import re
                json_match = re.search(r'\{.*\}|\[.*\]', result.content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    nodes = data.get('nodes', [])

                    # Add unique entities
                    for node in nodes:
                        if node.get('uuid') not in [e.get('uuid') for e in all_entities]:
                            all_entities.append(node)

                    print(f"   Found {len(nodes)} entities with term '{term}' (total unique: {len(all_entities)})")

                    if len(all_entities) >= max_nodes:
                        break
            except Exception as e:
                print(f"   Error parsing search for '{term}': {e}")
                continue

        return all_entities


async def search_all_facts(max_facts=5000):
    """Search for relationship facts"""
    graphiti_mcp = MCPTools(
        url="http://localhost:8000/mcp/",
        transport="streamable-http",
        timeout_seconds=120,
    )

    async with graphiti_mcp:
        await graphiti_mcp.initialize()

        agent = Agent(
            name="Fact Searcher",
            model=Ollama(id="glm-4.6:cloud"),
            tools=[graphiti_mcp],
            instructions="Execute search_memory_facts and return raw JSON.",
            markdown=False,
        )

        # Search broadly for facts
        all_facts = []
        search_terms = ["", "is", "has", "was", "are"]

        for term in search_terms:
            result = await agent.arun(
                f"search_memory_facts(query='{term}', group_ids=['rss-intelligence'], max_facts={max_facts})"
            )

            try:
                import re
                json_match = re.search(r'\{.*\}|\[.*\]', result.content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    facts = data.get('facts', [])

                    # Add unique facts
                    for fact in facts:
                        fact_id = fact.get('uuid') or str(fact)
                        if fact_id not in [f.get('uuid') or str(f) for f in all_facts]:
                            all_facts.append(fact)

                    print(f"   Found {len(facts)} facts with term '{term}' (total unique: {len(all_facts)})")

                    if len(all_facts) >= max_facts:
                        break
            except Exception as e:
                print(f"   Error parsing facts for '{term}': {e}")
                continue

        return all_facts


def create_graph_from_data(entities, facts):
    """Create NetworkX graph from entities and facts"""
    G = nx.DiGraph()

    print(f"\n📊 Building graph from {len(entities)} entities and {len(facts)} facts...")

    # Add nodes
    for entity in entities:
        G.add_node(
            entity['uuid'],
            name=entity.get('name', 'Unknown'),
            labels=entity.get('labels', []),
            summary=entity.get('summary', ''),
            created_at=entity.get('created_at', ''),
            group_id=entity.get('group_id', '')
        )

    # Add edges from facts
    edges_added = 0
    for fact in facts:
        # Facts should have source_uuid and target_uuid
        source = fact.get('source_uuid')
        target = fact.get('target_uuid')
        fact_text = fact.get('fact', str(fact))

        if source and target and G.has_node(source) and G.has_node(target):
            G.add_edge(source, target, fact=fact_text)
            edges_added += 1

    print(f"   ✓ Added {G.number_of_nodes()} nodes and {edges_added} edges")

    return G


def visualize_graph(G, filename='knowledge_graph_mcp.html'):
    """Create interactive visualization"""
    print(f"\n🌐 Creating visualization: {filename}")

    net = Network(
        height='900px',
        width='100%',
        bgcolor='#1a1a1a',
        font_color='white',
        directed=True
    )

    # Disable physics for large graphs
    if G.number_of_nodes() > 100:
        net.toggle_physics(False)
        print("   ⚠️ Physics disabled (large graph)")

    # Add nodes
    for node_id, node_data in G.nodes(data=True):
        name = node_data.get('name', str(node_id)[:30])
        summary = node_data.get('summary', 'No summary')[:200]
        labels = node_data.get('labels', [])

        # Color by label
        color = '#97C2FC'  # Default blue
        if 'Person' in labels:
            color = '#FB7E81'  # Red
        elif 'Organization' in labels:
            color = '#7BE141'  # Green
        elif 'Location' in labels:
            color = '#FFA807'  # Orange

        tooltip = f"<b>{name}</b><br>{summary}"

        net.add_node(node_id, label=name, title=tooltip, color=color, size=20)

    # Add edges
    for source, target, edge_data in G.edges(data=True):
        fact = edge_data.get('fact', 'related to')[:50]
        net.add_edge(source, target, title=fact, label=fact)

    net.save_graph(filename)
    print(f"   ✓ Saved to {filename}")


def export_to_formats(G, prefix='knowledge_graph_mcp'):
    """Export to various formats"""
    print(f"\n💾 Exporting to multiple formats...")

    # JSON
    from networkx.readwrite import json_graph
    graph_data = json_graph.node_link_data(G)
    with open(f'{prefix}.json', 'w') as f:
        json.dump(graph_data, f, indent=2)
    print(f"   ✓ {prefix}.json")

    # GEXF
    nx.write_gexf(G, f'{prefix}.gexf')
    print(f"   ✓ {prefix}.gexf")

    # GraphML
    nx.write_graphml(G, f'{prefix}.graphml')
    print(f"   ✓ {prefix}.graphml")


async def main():
    """Main execution"""
    print("="*60)
    print("🧠 GRAPHITI KNOWLEDGE GRAPH EXPORT VIA MCP")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Method: MCP Server API")
    print("="*60)

    # Get all entities
    print("\n🔍 Searching for all entities...")
    entities = await search_all_entities(max_nodes=2000)
    print(f"✓ Retrieved {len(entities)} unique entities")

    if len(entities) == 0:
        print("\n⚠️ No entities found. Graph may be empty.")
        return

    # Get all facts
    print("\n🔍 Searching for all relationship facts...")
    facts = await search_all_facts(max_facts=5000)
    print(f"✓ Retrieved {len(facts)} unique facts")

    # Create graph
    G = create_graph_from_data(entities, facts)

    # Export to formats
    export_to_formats(G)

    # Create visualization
    visualize_graph(G)

    # Print statistics
    print("\n" + "="*60)
    print("📊 KNOWLEDGE GRAPH STATISTICS")
    print("="*60)
    print(f"  Total Nodes:     {G.number_of_nodes():,}")
    print(f"  Total Edges:     {G.number_of_edges():,}")

    if G.number_of_nodes() > 0:
        density = nx.density(G)
        print(f"  Graph Density:   {density:.4f}")

        avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
        print(f"  Avg Degree:      {avg_degree:.2f}")

    print("="*60)

    # Final message
    print("\n✅ EXPORT COMPLETE")
    print("\n📂 Generated Files:")
    print("   • knowledge_graph_mcp.html   - Interactive visualization")
    print("   • knowledge_graph_mcp.json   - For D3.js / custom tools")
    print("   • knowledge_graph_mcp.gexf   - For Gephi")
    print("   • knowledge_graph_mcp.graphml - For Cytoscape")
    print("\n🌐 To view:")
    print(f"   open knowledge_graph_mcp.html")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
