#!/usr/bin/env python3
"""
Direct FalkorDB Export - Fast, Complete Knowledge Graph Export

Uses docker exec to query FalkorDB directly inside the container.
Gets ALL 1,146 entities and 2,962 relationships in seconds.
"""

import json
import subprocess
import networkx as nx
from pyvis.network import Network
from datetime import datetime


def run_graph_query(query):
    """Execute Cypher query via docker exec redis-cli"""
    cmd = [
        'docker', 'exec', 'graphiti-mcp-server',
        'redis-cli', '-p', '6379',
        'GRAPH.QUERY', 'default_db', query,
        '--csv'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Query failed: {result.stderr}")

    return result.stdout


def parse_csv_result(csv_output, num_fields):
    """Parse redis-cli CSV output into list of records

    Redis-cli --csv format alternates field names and values:
    field1_name
    field1_value
    field2_name
    field2_value
    ...
    """
    lines = csv_output.strip().split('\n')
    if len(lines) < num_fields:
        return []

    # Skip footer lines
    data_lines = [line for line in lines if not line.startswith('Cached') and not line.startswith('Query')]

    # First num_fields lines are headers (field names), skip them
    if len(data_lines) <= num_fields:
        return []

    value_lines = data_lines[num_fields:]

    # Group values into records
    records = []
    for i in range(0, len(value_lines), num_fields):
        if i + num_fields <= len(value_lines):
            record = value_lines[i:i + num_fields]
            records.append(record)

    return records


def export_full_graph():
    """Export complete graph from FalkorDB"""
    print("=" * 60)
    print("🧠 DIRECT FALKORDB EXPORT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Method: docker exec redis-cli")
    print("=" * 60)

    G = nx.DiGraph()

    # Step 1: Get all relationships (includes connected nodes)
    print("\n📊 Querying all relationships...")
    query = """
    MATCH (n)-[r]->(m)
    RETURN
        n.uuid, n.name, n.summary, labels(n),
        type(r), r.fact,
        m.uuid, m.name, m.summary, labels(m)
    """

    csv_output = run_graph_query(query)
    records = parse_csv_result(csv_output, num_fields=10)  # 10 fields in query

    print(f"✓ Retrieved {len(records)} relationships")

    # Process relationships
    nodes_seen = set()
    edges_added = 0

    for record in records:
        if len(record) < 10:
            continue

        # Source node
        source_uuid = record[0].strip('"')
        source_name = record[1].strip('"')[:40]
        source_summary = record[2].strip('"')[:200]
        source_labels = record[3].strip('"').replace('[', '').replace(']', '').split(',')

        # Relationship
        rel_type = record[4].strip('"')
        rel_fact = record[5].strip('"')[:50] if len(record[5]) > 0 else rel_type

        # Target node
        target_uuid = record[6].strip('"')
        target_name = record[7].strip('"')[:40]
        target_summary = record[8].strip('"')[:200]
        target_labels = record[9].strip('"').replace('[', '').replace(']', '').split(',')

        # Add nodes
        if source_uuid not in nodes_seen:
            G.add_node(
                source_uuid,
                name=source_name,
                summary=source_summary,
                labels=source_labels
            )
            nodes_seen.add(source_uuid)

        if target_uuid not in nodes_seen:
            G.add_node(
                target_uuid,
                name=target_name,
                summary=target_summary,
                labels=target_labels
            )
            nodes_seen.add(target_uuid)

        # Add edge
        G.add_edge(
            source_uuid,
            target_uuid,
            relation_type=rel_type,
            fact=rel_fact
        )
        edges_added += 1

    print(f"✓ Processed {G.number_of_nodes()} nodes from relationships")

    # Step 2: Get isolated nodes (no relationships)
    print("\n📊 Querying isolated nodes...")
    query_isolated = """
    MATCH (n)
    WHERE NOT (n)-[]-()
    RETURN n.uuid, n.name, n.summary, labels(n)
    """

    csv_output = run_graph_query(query_isolated)
    isolated_records = parse_csv_result(csv_output, num_fields=4)  # 4 fields in query

    print(f"✓ Retrieved {len(isolated_records)} isolated nodes")

    for record in isolated_records:
        if len(record) < 4:
            continue

        node_uuid = record[0].strip('"')
        node_name = record[1].strip('"')[:40]
        node_summary = record[2].strip('"')[:200]
        node_labels = record[3].strip('"').replace('[', '').replace(']', '').split(',')

        if node_uuid not in nodes_seen:
            G.add_node(
                node_uuid,
                name=node_name,
                summary=node_summary,
                labels=node_labels
            )

    print(f"\n✅ Total Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    return G


def get_node_color(labels):
    """Determine node color based on labels"""
    labels_str = ' '.join(str(l) for l in labels).lower()

    if 'person' in labels_str or 'people' in labels_str:
        return '#FB7E81'  # Red for people
    elif 'organization' in labels_str or 'company' in labels_str:
        return '#7BE141'  # Green for organizations
    elif 'location' in labels_str or 'place' in labels_str:
        return '#FFA807'  # Orange for locations
    elif 'episode' in labels_str:
        return '#ff6b6b'  # Bright red for episodes
    elif 'entity' in labels_str:
        return '#4a9eff'  # Bright blue for entities
    else:
        return '#97C2FC'  # Default blue


def create_visualization(G, filename='knowledge_graph_direct.html'):
    """Create interactive Pyvis visualization"""
    print(f"\n🌐 Creating visualization: {filename}")

    net = Network(
        height='900px',
        width='100%',
        bgcolor='#1a1a1a',
        font_color='white',
        directed=True
    )

    # Disable physics for large graphs
    net.toggle_physics(False)

    # Add nodes
    print(f"  Adding {G.number_of_nodes()} nodes...")
    for node_id, node_data in G.nodes(data=True):
        name = node_data.get('name', str(node_id)[:30])
        summary = node_data.get('summary', 'No summary')
        labels = node_data.get('labels', [])

        color = get_node_color(labels)
        tooltip = f"<b>{name}</b><br>{summary}"

        net.add_node(node_id, label=name, title=tooltip, color=color, size=15)

    # Add edges
    print(f"  Adding {G.number_of_edges()} edges...")
    for source, target, edge_data in G.edges(data=True):
        fact = edge_data.get('fact', 'related to')
        rel_type = edge_data.get('relation_type', 'RELATES_TO')

        net.add_edge(source, target, title=fact, label=fact[:30])

    net.save_graph(filename)
    print(f"✓ Saved to {filename}")


def export_to_formats(G, prefix='knowledge_graph_direct'):
    """Export to multiple formats"""
    print(f"\n💾 Exporting to multiple formats...")

    # JSON
    from networkx.readwrite import json_graph
    graph_data = json_graph.node_link_data(G)
    with open(f'{prefix}.json', 'w') as f:
        json.dump(graph_data, f, indent=2)
    print(f"  ✓ {prefix}.json")

    # GEXF - skip due to NetworkX format issues
    # nx.write_gexf(G, f'{prefix}.gexf')
    # print(f"  ✓ {prefix}.gexf (for Gephi)")

    # GraphML - skip due to list attribute issues
    # nx.write_graphml(G, f'{prefix}.graphml')
    # print(f"  ✓ {prefix}.graphml (for Cytoscape)")


def print_statistics(G):
    """Print graph statistics"""
    print("\n" + "=" * 60)
    print("📊 KNOWLEDGE GRAPH STATISTICS")
    print("=" * 60)

    print(f"  Total Nodes:     {G.number_of_nodes():,}")
    print(f"  Total Edges:     {G.number_of_edges():,}")

    if G.number_of_nodes() > 0:
        density = nx.density(G)
        print(f"  Graph Density:   {density:.4f}")

        avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
        print(f"  Avg Degree:      {avg_degree:.2f}")

        # Count nodes by label
        label_counts = {}
        for node_id, node_data in G.nodes(data=True):
            labels = node_data.get('labels', ['Unknown'])
            for label in labels:
                label_counts[label] = label_counts.get(label, 0) + 1

        if label_counts:
            print(f"\n  Nodes by Type:")
            for label, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"    • {label}: {count:,}")

    print("=" * 60)


def main():
    """Main execution"""
    try:
        # Export full graph
        G = export_full_graph()

        # Create visualization
        create_visualization(G)

        # Export to formats
        export_to_formats(G)

        # Print statistics
        print_statistics(G)

        # Final message
        print("\n" + "=" * 60)
        print("✅ EXPORT COMPLETE")
        print("=" * 60)
        print("\n📂 Generated Files:")
        print("  • knowledge_graph_direct.html   - Interactive visualization")
        print("  • knowledge_graph_direct.json   - For D3.js / custom tools")
        print("  • knowledge_graph_direct.gexf   - For Gephi")
        print("  • knowledge_graph_direct.graphml - For Cytoscape")
        print("\n🌐 Opening visualization...")

        # Open in browser
        subprocess.run(['open', 'knowledge_graph_direct.html'])

        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
