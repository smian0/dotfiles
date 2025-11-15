#!/usr/bin/env python3
"""
Export Full Graphiti Knowledge Graph from FalkorDB

Exports the complete knowledge graph to:
- Interactive HTML visualization (Pyvis)
- JSON format (for D3.js)
- GEXF format (for Gephi)
- GraphML format (for Cytoscape)
"""

import json
import networkx as nx
from falkordb import FalkorDB
from pyvis.network import Network
import argparse
from datetime import datetime


class GraphitiExporter:
    """Export Graphiti knowledge graph from FalkorDB"""

    def __init__(self, host='localhost', port=6379, graph_name='graphiti'):
        """Initialize connection to FalkorDB

        Args:
            host: FalkorDB host
            port: FalkorDB port (default: 6379 for Redis)
            graph_name: Name of the graph in FalkorDB
        """
        self.host = host
        self.port = port
        self.graph_name = graph_name
        self.db = None
        self.graph = None
        self.G = nx.DiGraph()

    def connect(self):
        """Connect to FalkorDB"""
        try:
            print(f"📡 Connecting to FalkorDB at {self.host}:{self.port}...")
            self.db = FalkorDB(host=self.host, port=self.port)
            self.graph = self.db.select_graph(self.graph_name)
            print(f"✓ Connected to graph '{self.graph_name}'")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    def export_full_graph(self):
        """Export complete graph from FalkorDB to NetworkX

        Returns:
            NetworkX DiGraph with all nodes and edges
        """
        print("\n📊 Exporting full knowledge graph...")

        # Step 1: Query all relationships (includes connected nodes)
        print("   Querying all relationships...")
        query = "MATCH (n)-[r]->(m) RETURN n, r, m"

        try:
            result = self.graph.ro_query(query)
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return self.G

        edge_count = 0
        for record in result.result_set:
            source, relation, target = record

            # Add nodes with their properties
            self._add_node(source)
            self._add_node(target)

            # Add edge with relationship properties
            self._add_edge(source, relation, target)
            edge_count += 1

        print(f"   ✓ Processed {edge_count} relationships")

        # Step 2: Get isolated nodes (nodes without any edges)
        print("   Querying isolated nodes...")
        query_isolated = "MATCH (n) WHERE NOT (n)-[]-() RETURN n"

        try:
            result_isolated = self.graph.ro_query(query_isolated)
            isolated_count = 0

            for record in result_isolated.result_set:
                self._add_node(record[0])
                isolated_count += 1

            if isolated_count > 0:
                print(f"   ✓ Found {isolated_count} isolated nodes")
        except Exception as e:
            print(f"   ⚠ Could not query isolated nodes: {e}")

        print(f"\n✅ Export complete: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
        return self.G

    def _add_node(self, node):
        """Add node to NetworkX graph with properties

        Args:
            node: FalkorDB node object
        """
        node_id = self._get_node_id(node)

        if not self.G.has_node(node_id):
            # Extract node properties
            properties = self._get_properties(node)
            labels = self._get_labels(node)

            # Add node with all attributes
            self.G.add_node(
                node_id,
                labels=labels,
                label_str=', '.join(labels) if labels else 'Unknown',
                **properties
            )

    def _add_edge(self, source, relation, target):
        """Add edge to NetworkX graph with properties

        Args:
            source: Source node
            relation: Relationship object
            target: Target node
        """
        source_id = self._get_node_id(source)
        target_id = self._get_node_id(target)

        # Extract relationship properties
        rel_type = self._get_relation_type(relation)
        properties = self._get_properties(relation)

        # Add edge
        self.G.add_edge(
            source_id,
            target_id,
            relation_type=rel_type,
            **properties
        )

    def _get_node_id(self, node):
        """Extract unique node ID

        Args:
            node: FalkorDB node object

        Returns:
            Unique identifier for the node
        """
        # Try different ID attributes
        if hasattr(node, 'id'):
            return str(node.id)
        if hasattr(node, 'uuid'):
            return node.uuid
        if hasattr(node, 'properties') and 'uuid' in node.properties:
            return node.properties['uuid']

        # Fallback: use string representation
        return str(node)

    def _get_labels(self, node):
        """Extract node labels

        Args:
            node: FalkorDB node object

        Returns:
            List of label strings
        """
        if hasattr(node, 'labels'):
            return list(node.labels)
        return []

    def _get_relation_type(self, relation):
        """Extract relationship type

        Args:
            relation: FalkorDB relationship object

        Returns:
            Relationship type string
        """
        if hasattr(relation, 'type'):
            return relation.type
        if hasattr(relation, 'relationship'):
            return relation.relationship
        return 'RELATES_TO'

    def _get_properties(self, element):
        """Extract properties from node or relationship

        Args:
            element: FalkorDB node or relationship object

        Returns:
            Dictionary of properties
        """
        properties = {}

        # Try different property access methods
        if hasattr(element, 'properties'):
            properties = dict(element.properties)
        elif hasattr(element, '__iter__') and not isinstance(element, str):
            try:
                properties = dict(element)
            except:
                pass

        return properties

    def export_to_json(self, filename='knowledge_graph.json'):
        """Export graph to JSON format

        Args:
            filename: Output filename
        """
        from networkx.readwrite import json_graph

        print(f"\n💾 Exporting to JSON: {filename}")
        graph_data = json_graph.node_link_data(self.G)

        with open(filename, 'w') as f:
            json.dump(graph_data, f, indent=2)

        print(f"   ✓ Saved {len(graph_data['nodes'])} nodes, {len(graph_data['links'])} edges")

    def export_to_gexf(self, filename='knowledge_graph.gexf'):
        """Export graph to GEXF format (for Gephi)

        Args:
            filename: Output filename
        """
        print(f"\n💾 Exporting to GEXF: {filename}")
        nx.write_gexf(self.G, filename)
        print(f"   ✓ Saved (open in Gephi for advanced visualization)")

    def export_to_graphml(self, filename='knowledge_graph.graphml'):
        """Export graph to GraphML format (for Cytoscape)

        Args:
            filename: Output filename
        """
        print(f"\n💾 Exporting to GraphML: {filename}")
        nx.write_graphml(self.G, filename)
        print(f"   ✓ Saved (open in Cytoscape/yEd for visualization)")

    def visualize_interactive(self, filename='knowledge_graph.html', physics=True):
        """Create interactive HTML visualization with Pyvis

        Args:
            filename: Output HTML filename
            physics: Enable physics simulation (disable for large graphs)
        """
        print(f"\n🌐 Creating interactive visualization: {filename}")

        # Create Pyvis network
        net = Network(
            height='900px',
            width='100%',
            bgcolor='#1a1a1a',
            font_color='white',
            directed=True,
            notebook=False
        )

        # Configure physics
        if physics and self.G.number_of_nodes() <= 100:
            # Use physics for small graphs
            net.set_options("""
            {
              "physics": {
                "forceAtlas2Based": {
                  "gravitationalConstant": -50,
                  "centralGravity": 0.01,
                  "springLength": 100,
                  "springConstant": 0.08
                },
                "maxVelocity": 50,
                "solver": "forceAtlas2Based",
                "timestep": 0.35,
                "stabilization": {"iterations": 150}
              }
            }
            """)
        else:
            # Disable physics for large graphs (better performance)
            net.toggle_physics(False)
            print("   ⚠ Physics disabled for performance (large graph)")

        # Add nodes and edges from NetworkX
        print(f"   Adding {self.G.number_of_nodes()} nodes...")
        for node_id, node_data in self.G.nodes(data=True):
            # Extract properties
            labels = node_data.get('labels', [])
            name = node_data.get('name', str(node_id)[:30])
            summary = node_data.get('summary', 'No summary')

            # Determine color based on labels
            color = self._get_node_color(labels)

            # Create tooltip
            tooltip = f"<b>{name}</b><br>{summary[:200]}"
            if len(summary) > 200:
                tooltip += "..."

            # Add node
            net.add_node(
                node_id,
                label=name,
                title=tooltip,
                color=color,
                size=20
            )

        print(f"   Adding {self.G.number_of_edges()} edges...")
        for source, target, edge_data in self.G.edges(data=True):
            rel_type = edge_data.get('relation_type', 'RELATES_TO')

            # Add edge
            net.add_edge(
                source,
                target,
                title=rel_type,
                label=rel_type[:30] if len(rel_type) > 30 else rel_type
            )

        # Save HTML
        net.save_graph(filename)
        print(f"   ✓ Saved interactive visualization")
        print(f"   📂 Open {filename} in your browser to explore")

    def _get_node_color(self, labels):
        """Determine node color based on labels

        Args:
            labels: List of node labels

        Returns:
            Hex color string
        """
        if not labels:
            return '#97C2FC'  # Default blue

        # Check labels (case-insensitive)
        labels_str = ' '.join(labels).lower()

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

    def print_statistics(self):
        """Print graph statistics"""
        print("\n" + "="*60)
        print("📊 KNOWLEDGE GRAPH STATISTICS")
        print("="*60)

        print(f"  Total Nodes:     {self.G.number_of_nodes():,}")
        print(f"  Total Edges:     {self.G.number_of_edges():,}")

        if self.G.number_of_nodes() > 0:
            density = nx.density(self.G)
            print(f"  Graph Density:   {density:.4f}")

            avg_degree = sum(dict(self.G.degree()).values()) / self.G.number_of_nodes()
            print(f"  Avg Degree:      {avg_degree:.2f}")

            # Count nodes by label
            label_counts = {}
            for node_id, node_data in self.G.nodes(data=True):
                labels = node_data.get('labels', ['Unknown'])
                for label in labels:
                    label_counts[label] = label_counts.get(label, 0) + 1

            if label_counts:
                print(f"\n  Nodes by Type:")
                for label, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"    • {label}: {count:,}")

        print("="*60)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Export full Graphiti knowledge graph from FalkorDB'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='FalkorDB host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=6379,
        help='FalkorDB port (default: 6379)'
    )
    parser.add_argument(
        '--graph',
        default='graphiti',
        help='Graph name in FalkorDB (default: graphiti)'
    )
    parser.add_argument(
        '--no-physics',
        action='store_true',
        help='Disable physics simulation in visualization'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory for exported files (default: current directory)'
    )

    args = parser.parse_args()

    # Print header
    print("="*60)
    print("🧠 GRAPHITI KNOWLEDGE GRAPH EXPORTER")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Host:      {args.host}:{args.port}")
    print(f"Graph:     {args.graph}")
    print("="*60)

    # Initialize exporter
    exporter = GraphitiExporter(
        host=args.host,
        port=args.port,
        graph_name=args.graph
    )

    # Connect to FalkorDB
    if not exporter.connect():
        return 1

    # Export full graph
    G = exporter.export_full_graph()

    if G.number_of_nodes() == 0:
        print("\n⚠ Warning: Graph is empty!")
        print("   Make sure:")
        print("   1. FalkorDB is running")
        print("   2. Graph name is correct")
        print("   3. Graph contains data")
        return 1

    # Export to various formats
    print("\n" + "="*60)
    print("📦 EXPORTING TO FORMATS")
    print("="*60)

    import os
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    exporter.export_to_json(os.path.join(output_dir, 'knowledge_graph.json'))
    exporter.export_to_gexf(os.path.join(output_dir, 'knowledge_graph.gexf'))
    exporter.export_to_graphml(os.path.join(output_dir, 'knowledge_graph.graphml'))

    # Create interactive visualization
    print("\n" + "="*60)
    print("🎨 CREATING VISUALIZATION")
    print("="*60)

    exporter.visualize_interactive(
        os.path.join(output_dir, 'knowledge_graph.html'),
        physics=not args.no_physics
    )

    # Print statistics
    exporter.print_statistics()

    # Final instructions
    print("\n" + "="*60)
    print("✅ EXPORT COMPLETE")
    print("="*60)
    print("\n📂 Generated Files:")
    print(f"   • knowledge_graph.html   - Interactive visualization (open in browser)")
    print(f"   • knowledge_graph.json   - For D3.js / custom tools")
    print(f"   • knowledge_graph.gexf   - For Gephi")
    print(f"   • knowledge_graph.graphml - For Cytoscape / yEd")
    print("\n🌐 To view the graph:")
    print(f"   open {os.path.join(output_dir, 'knowledge_graph.html')}")
    print("="*60)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
